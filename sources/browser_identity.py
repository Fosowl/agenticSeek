"""
Consistent browser identity for AgenticSeek's stealth layer.

A BrowserIdentity describes one complete, internally consistent browser
persona: user agent, platform, client hints, screen, CPU class, languages.
Every layer (chrome flags, CDP overrides, injected JS) derives from the same
instance so they can never contradict each other. GPU and canvas output stay
real: Web Workers expose them unspoofed, so any main-thread lie is visible.

The identity is persisted on disk and reused across runs as long as the
installed Chrome major version still matches: a stable fingerprint is far
less suspicious than a randomly regenerated one.

This module is stdlib-only on purpose: it must stay importable and testable
without selenium/chrome installed.
"""

from __future__ import annotations

import datetime
import json
import os
import random
import sys
import tempfile

SCHEMA_VERSION = 1
DEFAULT_CHROME_MAJOR = 125

# ---------------------------------------------------------------------------
# Device profiles.
# Every entry is internally consistent: OS <-> navigator.platform <->
# client-hints platform <-> screen <-> CPU class.
# WebIDL values below mimic what a real Chrome of that class reports.
# ---------------------------------------------------------------------------

DEVICE_PROFILES = [
    {
        "label": "win11-desktop-nvidia",
        "os": "windows",
        "navigator_platform": "Win32",
        "client_hint_platform": "Windows",
        "platform_version": "15.0.0",
        "architecture": "x86",
        "bitness": "64",
        "screen": {"width": 1920, "height": 1080, "avail_width": 1920, "avail_height": 1040,
                    "avail_left": 0, "avail_top": 0},
        "hardware_concurrency": 12,
        "device_memory": 8,
    },
    {
        "label": "win10-desktop-intel",
        "os": "windows",
        "navigator_platform": "Win32",
        "client_hint_platform": "Windows",
        "platform_version": "10.0.0",
        "architecture": "x86",
        "bitness": "64",
        "screen": {"width": 1920, "height": 1080, "avail_width": 1920, "avail_height": 1040,
                    "avail_left": 0, "avail_top": 0},
        "hardware_concurrency": 8,
        "device_memory": 8,
    },
    {
        "label": "macbook-pro-14-m1pro",
        "os": "macos",
        "navigator_platform": "MacIntel",
        "client_hint_platform": "macOS",
        "platform_version": "14.6.1",
        "architecture": "arm",
        "bitness": "64",
        "screen": {"width": 1728, "height": 1117, "avail_width": 1728, "avail_height": 1092,
                    "avail_left": 0, "avail_top": 25},
        "hardware_concurrency": 10,
        "device_memory": 8,
    },
    {
        "label": "macbook-air-13-m2",
        "os": "macos",
        "navigator_platform": "MacIntel",
        "client_hint_platform": "macOS",
        "platform_version": "14.5.0",
        "architecture": "arm",
        "bitness": "64",
        "screen": {"width": 1470, "height": 956, "avail_width": 1470, "avail_height": 931,
                    "avail_left": 0, "avail_top": 25},
        "hardware_concurrency": 8,
        "device_memory": 8,
    },
    {
        "label": "linux-desktop-intel",
        "os": "linux",
        "navigator_platform": "Linux x86_64",
        "client_hint_platform": "Linux",
        "platform_version": "6.5.0",
        "architecture": "x86",
        "bitness": "64",
        "screen": {"width": 1920, "height": 1080, "avail_width": 1920, "avail_height": 1048,
                    "avail_left": 0, "avail_top": 0},
        "hardware_concurrency": 8,
        "device_memory": 8,
    },
]

# Chrome freezes the OS token in the UA string; these are the frozen forms.
UA_TEMPLATES = {
    "windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    "macos": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    "linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
}

# Chromium's GREASE brand inputs (components/embedder_support/user_agent_utils.cc).
# The major version seeds the brand name, its version and the brand order.
GREASE_CHARS = [" ", "(", ":", "-", ".", "/", ")", ";", "=", "?", "_"]
GREASE_VERSIONS = ["8", "99", "24"]
BRAND_ORDERS = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
FULL_VERSION_SUFFIX = ".0.0.0"


def chrome_brands(chrome_major: int, version: str, full: bool = False) -> list:
    """
    Build the client-hint brand list exactly as Chromium does.
    BrowserIdentity calls this for the CDP user-agent metadata.
    It places the GREASE brand, "Chromium" and "Google Chrome" in the order
    that Chromium derives from the major version.

    Args:
        chrome_major (int): Chrome major version, from the identity.
        version (str): version string for the real brands (major or full).
        full (bool): True for the fullVersionList form ("8.0.0.0").
    Returns:
        list[dict]: [{"brand": str, "version": str}, ...] with 3 entries.
    """
    grease_brand = (f"Not{GREASE_CHARS[chrome_major % len(GREASE_CHARS)]}A"
                    f"{GREASE_CHARS[(chrome_major + 1) % len(GREASE_CHARS)]}Brand")
    grease_version = GREASE_VERSIONS[chrome_major % len(GREASE_VERSIONS)]
    if full:
        grease_version += FULL_VERSION_SUFFIX
    order = BRAND_ORDERS[chrome_major % len(BRAND_ORDERS)]
    brands = [None, None, None]
    brands[order[0]] = {"brand": grease_brand, "version": grease_version}
    brands[order[1]] = {"brand": "Chromium", "version": version}
    brands[order[2]] = {"brand": "Google Chrome", "version": version}
    return brands


_LOCALE_MAP = {
    "en": "en-US", "zh": "zh-CN", "fr": "fr-FR", "de": "de-DE", "es": "es-ES",
    "ja": "ja-JP", "pt": "pt-PT", "ru": "ru-RU", "ko": "ko-KR", "it": "it-IT",
}


def locale_for(lang: str) -> str:
    """Map a bare language code to a real BCP-47 locale (en -> en-US)."""
    lang = (lang or "en").strip().lower().replace("-", "_").split("_")[0]
    return _LOCALE_MAP.get(lang, f"{lang}-{lang.upper()}")


def detect_chrome_version():
    """
    Return (major, full_version) of the installed Chrome, or (None, None).
    Never raises: stealth must not break browser startup.
    """
    try:
        import chromedriver_autoinstaller
        version = chromedriver_autoinstaller.get_chrome_version()
        if version:
            parts = version.split(".")
            if parts and parts[0].isdigit():
                return int(parts[0]), version
    except Exception:
        pass
    return None, None


def host_iana_timezone():
    """Best-effort IANA timezone of the host, or None (then no override)."""
    try:
        tz = datetime.datetime.now().astimezone().tzinfo
        key = getattr(tz, "key", None)
        if key:
            return key
    except Exception:
        pass
    try:
        real = os.path.realpath("/etc/localtime")
        if "/zoneinfo/" in real:
            return real.split("/zoneinfo/")[-1]
    except Exception:
        pass
    return None


def host_os() -> str:
    """The OS class of the machine running the browser."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform.startswith("darwin"):
        return "macos"
    return "linux"


def default_state_path() -> str:
    return os.path.join(os.getcwd(), ".browser_profile", "identity.json")


class BrowserIdentity:
    """One consistent browser persona; all stealth layers derive from it."""

    def __init__(self, profile: dict, chrome_major: int, chrome_full_version: str,
                 languages: list, timezone: str | None):
        self.label = profile["label"]
        self.os = profile["os"]
        self.navigator_platform = profile["navigator_platform"]
        self.client_hint_platform = profile["client_hint_platform"]
        self.platform_version = profile["platform_version"]
        self.architecture = profile["architecture"]
        self.bitness = profile["bitness"]
        self.screen = dict(profile["screen"])
        self.hardware_concurrency = profile["hardware_concurrency"]
        self.device_memory = profile["device_memory"]
        self.languages = list(languages)
        self.timezone = timezone
        self.chrome_major = chrome_major
        self.chrome_full_version = chrome_full_version
        self.created_at = datetime.datetime.now().isoformat(timespec="seconds")

    # ------------------------------------------------------------------ views

    @property
    def user_agent(self) -> str:
        # Modern Chrome freezes the UA minor version: Chrome/<major>.0.0.0
        return UA_TEMPLATES[self.os].format(version=f"{self.chrome_major}.0.0.0")

    @property
    def locale(self) -> str:
        return self.languages[0]

    @property
    def accept_lang(self) -> str:
        # comma list for the --accept-lang flag. No q-values: Chrome derives
        # the Accept-Language header itself, and a q-suffix otherwise leaks
        # into worker navigator.languages as a bogus "en;q=0.9" tag.
        base = self.languages[0].split("-")[0].lower()
        parts, seen = [], set()
        for part in list(self.languages) + [base]:
            if part.lower() not in seen:
                seen.add(part.lower())
                parts.append(part)
        return ",".join(parts)

    @property
    def window_size(self):
        # keep the window inside the spoofed available screen (taskbar/dock)
        return (self.screen["width"], self.screen["avail_height"])

    def to_cdp_user_agent_metadata(self) -> dict:
        """
        CDP UserAgentMetadata for Network.setUserAgentOverride.
        Chrome serves it both as the HTTP sec-ch-ua-* headers and through the
        real navigator.userAgentData (page and workers), so no JS fake is needed.
        """
        return {
            "brands": chrome_brands(self.chrome_major, str(self.chrome_major)),
            "fullVersionList": chrome_brands(self.chrome_major, self.chrome_full_version, full=True),
            "fullVersion": self.chrome_full_version,
            "platform": self.client_hint_platform,
            "platformVersion": self.platform_version,
            "architecture": self.architecture,
            "model": "",
            "mobile": False,
            "bitness": self.bitness,
            "wow64": False,
            "formFactors": ["Desktop"],
        }

    def to_js(self) -> dict:
        """The JSON embedded into spoofing.js; key names match the script."""
        return {
            "navigator": {"languages": self.languages},
            "screen": self.screen,
        }

    # ------------------------------------------------------------ persistence

    def to_state(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "label": self.label,
            "chrome_major": self.chrome_major,
            "chrome_full_version": self.chrome_full_version,
            "languages": self.languages,
            "timezone": self.timezone,
            "created_at": self.created_at,
        }

    @classmethod
    def from_state(cls, state: dict):
        profile = next((p for p in DEVICE_PROFILES if p["label"] == state.get("label")), None)
        if profile is None:
            raise ValueError(f"unknown device profile: {state.get('label')}")
        return cls(
            profile=profile,
            chrome_major=int(state["chrome_major"]),
            chrome_full_version=state.get("chrome_full_version") or f"{state['chrome_major']}.0.0.0",
            languages=list(state.get("languages") or ["en-US", "en"]),
            timezone=state.get("timezone"),
        )


def _atomic_write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_or_create_identity(state_file: str | None = None,
                            chrome_major: int | None = None,
                            chrome_full_version: str | None = None,
                            lang: str = "en") -> BrowserIdentity:
    """
    Return the persistent identity for this machine.

    Reuse rules:
      - same schema + same chrome major -> reuse as-is (stability across runs)
      - chrome major changed -> keep nothing that encodes the version, pick a
        new random profile and persist it
    Any storage failure degrades to an in-memory identity instead of crashing.
    """
    if chrome_major is None:
        detected_major, detected_full = detect_chrome_version()
        chrome_major = detected_major or DEFAULT_CHROME_MAJOR
        if chrome_full_version is None:
            chrome_full_version = detected_full
    if not chrome_full_version:
        chrome_full_version = f"{chrome_major}.0.0.0"

    locale = locale_for(lang)
    languages = list(dict.fromkeys([locale, locale.split("-")[0].lower()]))
    state_file = state_file or default_state_path()

    state = None
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
            state = None
    except Exception:
        state = None

    def _stored_major(s):
        try:
            return int(s.get("chrome_major"))
        except (TypeError, ValueError):
            return -1  # corrupt state: force a re-pick below

    identity = None
    if state and _stored_major(state) == int(chrome_major):
        try:
            state.setdefault("languages", languages)
            identity = BrowserIdentity.from_state(state)
        except Exception:
            identity = None
        if identity is not None and identity.os != host_os():
            # The persona OS must match the host: Web Workers report the real
            # navigator (no script injection reaches them), so a mismatched
            # platform/hardware claim is exactly what bot detectors compare.
            identity = None

    if identity is None:
        previous_label = (state or {}).get("label")
        matching = [p for p in DEVICE_PROFILES if p["os"] == host_os()] or DEVICE_PROFILES
        candidates = [p for p in matching if p["label"] != previous_label] or matching
        profile = random.choice(candidates)
        identity = BrowserIdentity(
            profile=profile,
            chrome_major=chrome_major,
            chrome_full_version=chrome_full_version,
            languages=languages,
            timezone=host_iana_timezone(),
        )
        try:
            _atomic_write_json(state_file, identity.to_state())
        except Exception as e:
            print(f"[identity] could not persist browser identity: {e}")

    # languages follow the configured language; the rest of the persona is fixed
    if identity.languages != languages:
        identity.languages = languages
        try:
            _atomic_write_json(state_file, identity.to_state())
        except Exception:
            pass

    # keep timezone aligned with the host when it is resolvable (it must match the IP)
    host_tz = host_iana_timezone()
    if host_tz and identity.timezone != host_tz:
        identity.timezone = host_tz
        try:
            _atomic_write_json(state_file, identity.to_state())
        except Exception:
            pass

    return identity
