from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from typing import List, Tuple, Type, Dict
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import undetected_chromedriver as uc
import chromedriver_autoinstaller
import certifi
import ssl
import subprocess
import time
import random
import os
import shutil
import socket
import tempfile
import markdownify
import json
import hashlib
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.utility import pretty_print, animate_thinking
from sources.logger import Logger
from sources.browser_identity import BrowserIdentity, load_or_create_identity
from sources.crx_utils import extract_crx, extension_installed


def get_chrome_path() -> str:
    """Get the path to the Chrome executable."""
    if sys.platform.startswith("win"):
        paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe")  # User install
        ]
    elif sys.platform.startswith("darwin"):  # macOS
        paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"]
    else:  # Linux
        paths = ["/usr/bin/google-chrome",
                 "/opt/chrome/chrome",
                 "/usr/bin/chromium-browser",
                 "/usr/bin/chromium",
                 "/usr/local/bin/chrome",
                 "/opt/google/chrome/chrome-headless-shell",
                 #"/app/chrome_bundle/chrome136/chrome-linux64"
                ]

    for path in paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    print("Looking for Google Chrome in these locations failed:")
    print('\n'.join(paths))
    chrome_path_env = os.environ.get("CHROME_EXECUTABLE_PATH")
    if chrome_path_env and os.path.exists(chrome_path_env) and os.access(chrome_path_env, os.X_OK):
        return chrome_path_env
    path = input("Google Chrome not found. Please enter the path to the Chrome executable: ")
    if os.path.exists(path) and os.access(path, os.X_OK):
        os.environ["CHROME_EXECUTABLE_PATH"] = path
        print(f"Chrome path saved to environment variable CHROME_EXECUTABLE_PATH")
        return path
    return None

def get_chromedriver_version(chromedriver_path: str) -> str:
    """Get the major version of a chromedriver binary. Returns empty string on failure."""
    try:
        result = subprocess.run(
            [chromedriver_path, "--version"],
            capture_output=True, text=True, timeout=10
        )
        # Output format: "ChromeDriver 125.0.6422.78 (...)"
        return result.stdout.strip().split()[1].split('.')[0]
    except Exception:
        return ""

def is_chromedriver_compatible(chromedriver_path: str) -> bool:
    """Check if a chromedriver binary is compatible with the installed Chrome version."""
    try:
        chrome_version = chromedriver_autoinstaller.get_chrome_version()
        if not chrome_version:
            return True  # Can't determine Chrome version, assume compatible
        chrome_major = chrome_version.split('.')[0]
        driver_major = get_chromedriver_version(chromedriver_path)
        if not driver_major:
            return True  # Can't determine driver version, assume compatible
        return chrome_major == driver_major
    except Exception:
        return True  # On any error, assume compatible to avoid blocking

def install_chromedriver() -> str:
    """
    Install the ChromeDriver if not already installed. Return the path.
    Automatically updates the driver if the version does not match the installed Chrome.
    """
    # First try to use chromedriver in the project root directory (as per README)
    project_root_chromedriver = "./chromedriver"
    if os.path.exists(project_root_chromedriver) and os.access(project_root_chromedriver, os.X_OK):
        if is_chromedriver_compatible(project_root_chromedriver):
            print(f"Using ChromeDriver from project root: {project_root_chromedriver}")
            return project_root_chromedriver
        print("ChromeDriver in project root is outdated, attempting auto-update...")
    
    # Then try to use the system-installed chromedriver
    chromedriver_path = shutil.which("chromedriver")
    if chromedriver_path:
        if is_chromedriver_compatible(chromedriver_path):
            return chromedriver_path
        print(f"System ChromeDriver at {chromedriver_path} is outdated, attempting auto-update...")
    
    # In Docker environment, try the fixed path
    if os.path.exists('/.dockerenv'):
        docker_chromedriver_path = "/usr/local/bin/chromedriver"
        if os.path.exists(docker_chromedriver_path) and os.access(docker_chromedriver_path, os.X_OK):
            print(f"Using Docker ChromeDriver at {docker_chromedriver_path}")
            return docker_chromedriver_path
    
    # Auto-install matching ChromeDriver version
    try:
        print("Installing matching ChromeDriver version automatically...")
        chromedriver_path = chromedriver_autoinstaller.install()
    except Exception as e:
        raise FileNotFoundError(
            "ChromeDriver not found and could not be installed automatically. "
            "Please install it manually from https://chromedriver.chromium.org/downloads."
            "and ensure it's in your PATH or specify the path directly."
            "See know issues in readme if your chrome version is above 115."
        ) from e
    
    if not chromedriver_path:
        raise FileNotFoundError("ChromeDriver not found. Please install it or add it to your PATH.")
    return chromedriver_path

def bypass_ssl() -> str:
    """
    This is a fallback for stealth mode to bypass SSL verification. Which can fail on some setup.
    """
    pretty_print("Bypassing SSL verification issues, we strongly advice you update your certifi SSL certificate.", color="warning")
    ssl._create_default_https_context = ssl._create_unverified_context

def get_free_port() -> int:
    """Find and return a free TCP port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def persistent_profile_dir() -> str:
    """
    Stable, on-disk Chrome profile under .browser_profile/chrome_data.
    Cookies, history and anti-bot clearance tokens surviving restarts is
    worth far more than the per-run randomization the old /tmp profiles had.
    """
    return os.path.abspath(os.path.join(os.getcwd(), ".browser_profile", "chrome_data"))


def profile_in_use(profile_dir: str) -> bool:
    """True when a live Chrome instance holds the profile's singleton lock."""
    lock = os.path.join(profile_dir, "SingletonLock")
    if os.path.lexists(lock):
        try:
            target = os.readlink(lock)  # format: "<hostname>-<pid>"
            pid = int(target.rsplit("-", 1)[1])
            os.kill(pid, 0)  # raises when the process is dead
            return True
        except (ValueError, IndexError, OSError):
            # stale lock from a crashed Chrome: remove it, do not block forever
            try:
                os.unlink(lock)
            except OSError:
                pass
            return False
    if sys.platform.startswith("win") and os.path.exists(os.path.join(profile_dir, "lockfile")):
        return True
    return False


def clone_profile(profile_dir: str) -> str:
    """
    Copy the profile to a temp dir so a second browser instance can run
    beside the first (e.g. cli.py while api.py is up). Locks and caches are
    excluded; cookies and preferences carry over.
    """
    clone = tempfile.mkdtemp(prefix="chrome_profile_clone_")
    shutil.copytree(profile_dir, clone, dirs_exist_ok=True, symlinks=True,
                    ignore=shutil.ignore_patterns(
                        "Singleton*", "lockfile", "Cache", "Code Cache",
                        "GPUCache", "ScriptCache"))
    return clone


def resolve_profile_dir() -> str:
    """The persistent profile, or a clone of it when it is already in use."""
    profile_dir = persistent_profile_dir()
    if os.path.isdir(profile_dir) and profile_in_use(profile_dir):
        pretty_print("Browser profile is in use by another instance; using a temporary clone (cookies carried over).", color="warning")
        return clone_profile(profile_dir)
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir


_legacy_profiles_cleaned = False
def cleanup_legacy_profiles(max_age_hours: int = 24) -> None:
    """Best-effort removal of the /tmp/chrome_profile_* dirs old versions leaked."""
    global _legacy_profiles_cleaned
    if _legacy_profiles_cleaned:
        return
    _legacy_profiles_cleaned = True
    try:
        for name in os.listdir(tempfile.gettempdir()):
            if not name.startswith("chrome_profile_"):
                continue
            path = os.path.join(tempfile.gettempdir(), name)
            try:
                if time.time() - os.path.getmtime(path) > max_age_hours * 3600:
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                continue
    except OSError:
        pass


def create_chrome_options(headless=False, stealth_mode=True, crx_path="./crx/nopecha.crx", lang="en", identity=None, anticaptcha=True) -> Options:
    """Create Chrome options - separated for reusability.

    Every identity-derived flag (user-agent, accept-lang, window-size) comes
    from a single BrowserIdentity, so the HTTP layer, the JS layer and the
    window geometry can never contradict each other.
    """
    if identity is None:
        identity = load_or_create_identity(lang=lang)
    chrome_options = Options()
    chrome_path = get_chrome_path()
    
    if not chrome_path:
        raise FileNotFoundError("Google Chrome not found. Please install it.")
    chrome_options.binary_location = chrome_path
    
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        # Restore software WebGL: Chrome >= 137 returns a null WebGL context in
        # headless without it, and "no WebGL" contradicts the spoofed identity
        # (the SwiftShader backend itself is masked by the spoofed strings).
        chrome_options.add_argument("--enable-unsafe-swiftshader")
        # --disable-webgl intentionally removed: a missing WebGL context
        # contradicts the spoofed WebGL identity and is itself a bot signal.
    
    profile_dir = resolve_profile_dir()
    
    # Core options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument(f"--accept-lang={identity.accept_lang}")
    # Anti-captcha extension (NopeCHA) loaded as an unpacked directory: the
    # old packed-CRX path could never work (--disable-extensions was always
    # passed too). --headless=new supports extensions since Chrome 112.
    extension_dir = extract_crx(crx_path) if anticaptcha else None
    if extension_dir:
        chrome_options.add_argument(f"--disable-extensions-except={extension_dir}")
        chrome_options.add_argument(f"--load-extension={extension_dir}")
    else:
        chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument(f'--remote-debugging-port={get_free_port()}')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--autoplay-policy=user-gesture-required")
    chrome_options.add_argument("--disable-features=SitePerProcess,IsolateOrigins")
    chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f'user-agent={identity.user_agent}')
    chrome_options.add_argument(f'--window-size={identity.window_size[0]},{identity.window_size[1]}')
    # NOTE: --timezone=Europe/Paris removed: not a real Chromium switch (it
    # was silently ignored); timezone is emulated via CDP in
    # apply_stealth_injection, consistent with the identity and the host IP.
    
    if not stealth_mode:
        security_prefs = {
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 0,
            "profile.default_content_setting_values.camera": 0,
            "profile.default_content_setting_values.microphone": 0,
            "profile.default_content_setting_values.midi_sysex": 0,
            "profile.default_content_setting_values.clipboard": 0,
            "profile.default_content_setting_values.media_stream": 0,
            "profile.default_content_setting_values.background_sync": 0,
            "profile.default_content_setting_values.sensors": 0,
            "profile.default_content_setting_values.accessibility_events": 0,
            "safebrowsing.enabled": True,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "webkit.webprefs.accelerated_2d_canvas_enabled": True,
            "webkit.webprefs.force_dark_mode_enabled": False,
            "webkit.webprefs.accelerated_2d_canvas_msaa_sample_count": 4,
            "enable_webgl": True,
            "enable_webgl2_compute_context": True
        }
        chrome_options.add_experimental_option("prefs", security_prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options

def ad_hoc_codesign(binary_path: str) -> bool:
    """Re-sign a patched binary with an ad-hoc signature. macOS only."""
    if not sys.platform.startswith("darwin"):
        return False
    try:
        result = subprocess.run(
            ["codesign", "--force", "--sign", "-", binary_path],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def prepare_uc_chromedriver(chromedriver_path: str) -> str:
    """
    Hand undetected-chromedriver a writable, version-matched driver binary.

    uc.Chrome ignores any provided Service and always runs its own Patcher on
    `driver_executable_path`. Left alone, that patcher downloads the newest
    Chrome-for-Testing milestone (e.g. 153), which mismatches the installed
    browser (e.g. Docker's pinned 134) and kills the session with
    "This version of ChromeDriver only supports Chrome version XXX".
    With an explicit executable path, uc only patches that binary in place and
    never downloads. We copy to a cache first so the system/container binary
    stays pristine (and to avoid patching a file another process may hold).
    """
    try:
        with open(chromedriver_path, "rb") as f:
            digest = hashlib.md5(f.read()).hexdigest()[:10]
        cache_dir = os.path.join(os.getcwd(), ".browser_profile")
        os.makedirs(cache_dir, exist_ok=True)
        cached = os.path.join(cache_dir, f"uc_chromedriver_{digest}")
        if not os.path.exists(cached):
            tmp = f"{cached}.tmp"
            shutil.copy2(chromedriver_path, tmp)
            os.chmod(tmp, 0o755)
            os.replace(tmp, cached)
        return cached
    except Exception as e:
        pretty_print(f"Stealth: could not cache chromedriver copy ({e}); using original path.", color="warning")
        return chromedriver_path


def create_undetected_chromedriver(service, chrome_options, identity=None, lang="en", crx_path="./crx/nopecha.crx", anticaptcha=True) -> webdriver.Chrome:
    """
    Create an undetected ChromeDriver instance with proper error handling.

    The version-matched driver from install_chromedriver() (via `service.path`)
    is passed explicitly as driver_executable_path: uc patches that binary and
    skips its "download latest milestone" logic entirely (see
    prepare_uc_chromedriver).
    """
    patched_driver = prepare_uc_chromedriver(service.path)
    try:
        driver = uc.Chrome(driver_executable_path=patched_driver, options=chrome_options)
    except Exception as e:
        pretty_print(f"Failed to create Chrome driver: {str(e)}. Trying to bypass SSL...", color="failure")
        try:
            bypass_ssl()
            # Create NEW options object from the SAME identity - this is the key fix
            fresh_options = create_chrome_options(
                headless=any("--headless" in arg for arg in chrome_options.arguments),
                stealth_mode=True,  # We're in stealth mode if we reach this point
                crx_path=crx_path,
                lang=lang,
                identity=identity,
                anticaptcha=anticaptcha
            )
            driver = uc.Chrome(driver_executable_path=patched_driver, options=fresh_options)
        except Exception as e:
            # macOS/Apple Silicon: uc's in-place patch invalidates the binary's
            # code signature and the kernel SIGKILLs it (service exit -9).
            # Re-sign ad hoc and retry: uc now sees the binary as already
            # patched and starts it with a valid (ad-hoc) signature.
            if ad_hoc_codesign(patched_driver):
                try:
                    pretty_print("Stealth: re-signed the patched chromedriver, retrying.", color="status")
                    retry_options = create_chrome_options(
                        headless=any("--headless" in arg for arg in chrome_options.arguments),
                        stealth_mode=True,
                        crx_path=crx_path,
                        lang=lang,
                        identity=identity,
                        anticaptcha=anticaptcha
                    )
                    driver = uc.Chrome(driver_executable_path=patched_driver, options=retry_options)
                    return driver
                except Exception as retry_error:
                    pretty_print(f"Failed to create Chrome driver after re-sign:\n{str(retry_error)}.", color="failure")
            pretty_print(f"Failed to create Chrome driver, fallback failed:\n{str(e)}.", color="failure")
            raise e
    # navigator.webdriver is set to false by the spoofing script injected on
    # every new document (the old one-shot "undefined" patch was itself a
    # tell: a real Chrome reports false, not undefined).
    return driver

def build_stealth_source(identity: BrowserIdentity) -> str:
    """
    Build the spoofing script injected into every new document.
    The identity is embedded as a script-scoped const: page scripts cannot
    read it and it never appears on `window`.
    """
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_scripts", "spoofing.js")
    with open(script_path, "r", encoding="utf-8") as f:
        body = f.read()
    identity_json = json.dumps(identity.to_js(), separators=(",", ":"))
    return f"const __IDENTITY__ = {identity_json};\n{body}"


def apply_stealth_injection(driver, identity: BrowserIdentity) -> None:
    """
    Apply one identity to an existing driver:
      - register the spoofing script on every new document, so it runs before
        page scripts (the old one-shot execute_script was lost on navigation)
      - override the user agent AND its client hints, so the HTTP sec-ch-ua-*
        headers match the JS layer
      - emulate timezone and locale consistently
      - run the script once on the currently open document, if any
    Failures degrade gracefully: a partial stealth layer still beats none.
    """
    source = build_stealth_source(identity)
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": source})
    except Exception as e:
        pretty_print(f"Stealth: document injection unavailable: {e}", color="warning")
    try:
        override = {"userAgent": identity.user_agent, "userAgentMetadata": identity.to_cdp_user_agent_metadata()}
        try:
            driver.execute_cdp_cmd("Network.setUserAgentOverride", override)
        except Exception:
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.setUserAgentOverride", override)
    except Exception as e:
        pretty_print(f"Stealth: user agent override unavailable: {e}", color="warning")
    if identity.timezone:
        try:
            driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": identity.timezone})
        except Exception:
            pass
    try:
        driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": identity.locale})
    except Exception:
        pass
    try:
        driver.execute_script(source)  # cover the document already open, if any
    except Exception:
        pass


def create_driver(headless=False, stealth_mode=True, crx_path="./crx/nopecha.crx", lang="en", anticaptcha=True) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver with specified options.

    One BrowserIdentity is created (or reused from disk) and drives every
    layer: chrome flags, the driver, the CDP overrides and the injected JS.
    The injection is applied on both the undetected and the plain path, so a
    configuration mistake cannot leave the browser unspoofed.
    """
    # Warn if trying to run non-headless in Docker
    if not headless and os.path.exists('/.dockerenv'):
        print("[WARNING] Running non-headless browser in Docker may fail!")
        print("[WARNING] Consider setting headless=True or headless_browser=True in config.ini")
    
    identity = load_or_create_identity(lang=lang)
    cleanup_legacy_profiles()
    chrome_options = create_chrome_options(headless, stealth_mode, crx_path, lang, identity=identity, anticaptcha=anticaptcha)
    chromedriver_path = install_chromedriver()
    service = Service(chromedriver_path)
    
    if stealth_mode:
        try:
            driver = create_undetected_chromedriver(service, chrome_options, identity=identity, lang=lang, crx_path=crx_path)
        except Exception as e:
            pretty_print(f"Undetected ChromeDriver failed ({e}).\nFalling back to the standard ChromeDriver; identity spoofing stays active.", color="warning")
            # fresh profile dir: the failed uc attempt may still hold a lock on it
            fresh_options = create_chrome_options(
                headless=headless, stealth_mode=True, crx_path=crx_path, lang=lang,
                identity=identity, anticaptcha=anticaptcha)
            driver = webdriver.Chrome(service=service, options=fresh_options)
    else:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    apply_stealth_injection(driver, identity)
    return driver

class Browser:
    def __init__(self, driver, anticaptcha_manual_install=False):
        """Initialize the browser with optional AntiCaptcha installation."""
        self.js_scripts_folder = "./sources/web_scripts/" if not __name__ == "__main__" else "./web_scripts/"
        self.anticaptcha = "https://chrome.google.com/webstore/detail/nopecha-captcha-solver/dknlfmjaanfblgfdfebhijalfmhmjjjo/related"
        self.logger = Logger("browser.log")
        self.screenshot_folder = os.path.join(os.getcwd(), ".screenshots")
        self.tabs = []
        try:
            self.driver = driver
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")
        self.setup_tabs()
        # the Web Store page is a dead end in headless; only fall back to it
        # when the bundled CRX could not be loaded automatically
        if anticaptcha_manual_install and not extension_installed():
            self.load_anticatpcha_manually()
    
    def setup_tabs(self):
        self.tabs = self.driver.window_handles
        try:
            self.driver.get("about:blank")  # neutral start page: a google.com warmup is a CAPTCHA magnet
        except Exception as e:
            self.logger.log(f"Failed to setup initial tab:" + str(e))
            pass
        self.screenshot()
    
    def switch_control_tab(self):
        self.logger.log("Switching to control tab.")
        self.driver.switch_to.window(self.tabs[0])
            
    def load_anticatpcha_manually(self):
        pretty_print("You might want to install the AntiCaptcha extension for captchas.", color="warning")
        try:
            self.driver.get(self.anticaptcha)
        except Exception as e:
            self.logger.log(f"Failed to setup initial tab:" + str(e))
            pass

    def human_move(element):
        actions = ActionChains(driver)
        x_offset = random.randint(-5,5)
        for _ in range(random.randint(2,5)):
            actions.move_by_offset(x_offset, random.randint(-2,2))
            actions.pause(random.uniform(0.1,0.3))
        actions.click().perform()

    def human_scroll(self):
        for _ in range(random.randint(1, 3)):
            scroll_pixels = random.randint(150, 1200)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            time.sleep(random.uniform(0.5, 2.0))
            if random.random() < 0.4:
                self.driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 300)});")
                time.sleep(random.uniform(0.3, 1.0))

    def go_to(self, url:str) -> bool:
        """Navigate to a specified URL."""
        time.sleep(random.uniform(0.4, 2.5))
        try:
            initial_handles = self.driver.window_handles
            self.driver.get(url)
            time.sleep(random.uniform(0.01, 0.3))
            try:
                wait = WebDriverWait(self.driver, timeout=10)
                wait.until(
                    lambda driver: (
                        not any(keyword in driver.page_source.lower() for keyword in ["checking your browser", "captcha"])
                    ),
                    message="stuck on 'checking browser' or verification screen"
                )
            except TimeoutException:
                self.logger.warning("Timeout while waiting for page to bypass 'checking your browser'")
            self.apply_web_safety()
            time.sleep(random.uniform(0.01, 0.2))
            self.human_scroll()
            self.logger.log(f"Navigated to: {url}")
            return True
        except TimeoutException as e:
            self.logger.error(f"Timeout waiting for {url} to load: {str(e)}")
            return False
        except WebDriverException as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Fatal error with go_to method on {url}:\n{str(e)}")
            raise e

    def is_sentence(self, text:str) -> bool:
        """Check if the text qualifies as a meaningful sentence or contains important error codes."""
        text = text.strip()

        if any(c.isdigit() for c in text):
            return True
        words = re.findall(r'\w+', text, re.UNICODE)
        word_count = len(words)
        has_punctuation = any(text.endswith(p) for p in ['.', '，', ',', '!', '?', '。', '！', '？', '।', '۔'])
        is_long_enough = word_count > 4
        return (word_count >= 5 and (has_punctuation or is_long_enough))

    def get_text(self) -> str | None:
        """Get page text as formatted Markdown"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            for element in soup(['script', 'style', 'noscript', 'meta', 'link']):
                element.decompose()
            markdown_converter = markdownify.MarkdownConverter(
                heading_style="ATX",
                strip=['a'],
                autolinks=False,
                bullets='•',
                strong_em_symbol='*',
                default_title=False,
            )
            markdown_text = markdown_converter.convert(str(soup.body))
            lines = []
            for line in markdown_text.splitlines():
                stripped = line.strip()
                if stripped and self.is_sentence(stripped):
                    cleaned = ' '.join(stripped.split())
                    lines.append(cleaned)
            result = "[Start of page]\n\n" + "\n\n".join(lines) + "\n\n[End of page]"
            result = re.sub(r'!\[(.*?)\]\(.*?\)', r'[IMAGE: \1]', result)
            self.logger.info(f"Extracted text: {result[:100]}...")
            self.logger.info(f"Extracted text length: {len(result)}")
            return result[:32768]
        except Exception as e:
            self.logger.error(f"Error getting text: {str(e)}")
            return None
    
    def clean_url(self, url:str) -> str:
        """Clean URL to keep only the part needed for navigation to the page"""
        clean = url.split('#')[0]
        parts = clean.split('?', 1)
        base_url = parts[0]
        if len(parts) > 1:
            query = parts[1]
            essential_params = []
            for param in query.split('&'):
                if param.startswith('_skw=') or param.startswith('q=') or param.startswith('s='):
                    essential_params.append(param)
                elif param.startswith('_') or param.startswith('hash=') or param.startswith('itmmeta='):
                    break
            if essential_params:
                return f"{base_url}?{'&'.join(essential_params)}"
        return base_url
    
    def is_link_valid(self, url:str) -> bool:
        """Check if a URL is a valid link (page, not related to icon or metadata)."""
        if len(url) > 72:
            self.logger.warning(f"URL too long: {url}")
            return False
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            self.logger.warning(f"Invalid URL: {url}")
            return False
        if re.search(r'/\d+$', parsed_url.path):
            return False
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        metadata_extensions = ['.ico', '.xml', '.json', '.rss', '.atom']
        for ext in image_extensions + metadata_extensions:
            if url.lower().endswith(ext):
                return False
        return True

    def get_navigable(self) -> List[str]:
        """Get all navigable links on the current page."""
        try:
            links = []
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                href = element.get_attribute("href")
                if href and href.startswith(("http", "https")):
                    links.append({
                        "url": href,
                        "text": element.text.strip(),
                        "is_displayed": element.is_displayed()
                    })
            
            self.logger.info(f"Found {len(links)} navigable links")
            return [self.clean_url(link['url']) for link in links if (link['is_displayed'] == True and self.is_link_valid(link['url']))]
        except Exception as e:
            self.logger.error(f"Error getting navigable links: {str(e)}")
            return []

    def click_element(self, xpath: str) -> bool:
        """Click an element specified by XPath."""
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            if not element.is_displayed():
                return False
            if not element.is_enabled():
                return False
            try:
                self.logger.error(f"Scrolling to element for click_element.")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
                time.sleep(0.1)
                element.click()
                self.logger.info(f"Clicked element at {xpath}")
                return True
            except ElementClickInterceptedException as e:
                self.logger.error(f"Error click_element: {str(e)}")
                return False
        except TimeoutException:
            self.logger.warning(f"Timeout clicking element.")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error clicking element at {xpath}: {str(e)}")
            return False
        
    def load_js(self, file_name: str) -> str:
        """Load javascript from script folder to inject to page."""
        path = os.path.join(self.js_scripts_folder, file_name)
        self.logger.info(f"Loading js at {path}")
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError as e:
            raise Exception(f"Could not find: {path}") from e
        except Exception as e:
            raise e

    def find_all_inputs(self, timeout=3):
        """Find all inputs elements on the page."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            self.logger.error(f"Error waiting for input element: {str(e)}")
            return []
        time.sleep(0.5)
        script = self.load_js("find_inputs.js")
        input_elements = self.driver.execute_script(script)
        return input_elements

    def get_form_inputs(self) -> List[str]:
        """Extract all input from the page and return them."""
        try:
            input_elements = self.find_all_inputs()
            if not input_elements:
                self.logger.info("No input element on page.")
                return ["No input forms found on the page."]

            form_strings = []
            for element in input_elements:
                input_type = element.get("type") or "text"
                if input_type in ["hidden", "submit", "button", "image"] or not element["displayed"]:
                    continue
                input_name = element.get("text") or element.get("id") or input_type
                if input_type == "select":
                    options = element.get("options", [])
                    options_str = ", ".join(opt["text"] for opt in options if opt["text"])
                    selected = next((opt["text"] for opt in options if opt.get("selected")), "")
                    form_strings.append(f"[{input_name}](select: {selected}) options: [{options_str}]")
                elif input_type == "textarea":
                    form_strings.append(f"[{input_name}]("")")
                elif input_type == "file":
                    form_strings.append(f"[{input_name}](file: )")
                elif input_type == "checkbox" or input_type == "radio":
                    try:
                        checked_status = "checked" if element.is_selected() else "unchecked"
                    except Exception as e:
                        continue
                    form_strings.append(f"[{input_name}]({checked_status})")
                else:
                    form_strings.append(f"[{input_name}]("")")
            return form_strings

        except Exception as e:
            raise e

    def get_buttons_xpath(self) -> List[str]:
        """
        Find buttons and return their type and xpath.
        """
        buttons = self.driver.find_elements(By.TAG_NAME, "button") + \
                  self.driver.find_elements(By.XPATH, "//input[@type='submit']")
        result = []
        for i, button in enumerate(buttons):
            if not button.is_displayed() or not button.is_enabled():
                continue
            text = (button.text or button.get_attribute("value") or "").lower().replace(' ', '')
            xpath = f"(//button | //input[@type='submit'])[{i + 1}]"
            result.append((text, xpath))
        result.sort(key=lambda x: len(x[0]))
        return result

    def wait_for_submission_outcome(self, timeout: int = 10) -> bool:
        """
        Wait for a submission outcome (e.g., URL change or new element).
        """
        try:
            self.logger.info("Waiting for submission outcome...")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                lambda driver: driver.current_url != self.driver.current_url or
                               driver.find_elements(By.XPATH, "//*[contains(text(), 'success')]")
            )
            self.logger.info("Detected submission outcome")
            return True
        except TimeoutException:
            self.logger.warning("No submission outcome detected")
            return False

    def find_and_click_btn(self, btn_type: str = 'login', timeout: int = 5) -> bool:
        """Find and click a submit button matching the specified type."""
        buttons = self.get_buttons_xpath()
        if not buttons:
            self.logger.warning("No visible buttons found")
            return False

        for button_text, xpath in buttons:
            if btn_type.lower() in button_text.lower() or btn_type.lower() in xpath.lower():
                try:
                    wait = WebDriverWait(self.driver, timeout)
                    element = wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath)),
                        message=f"Button with XPath '{xpath}' not clickable within {timeout} seconds"
                    )
                    if self.click_element(xpath):
                        self.logger.info(f"Clicked button '{button_text}' at XPath: {xpath}")
                        return True
                    else:
                        self.logger.warning(f"Button '{button_text}' at XPath: {xpath} not clickable")
                        return False
                except TimeoutException:
                    self.logger.warning(f"Timeout waiting for '{button_text}' button at XPath: {xpath}")
                    return False
                except Exception as e:
                    self.logger.error(f"Error clicking button '{button_text}' at XPath: {xpath} - {str(e)}")
                    return False
        self.logger.warning(f"No button matching '{btn_type}' found")
        return False

    def tick_all_checkboxes(self) -> bool:
        """
        Find and tick all checkboxes on the page.
        Returns True if successful, False if any issues occur.
        """
        try:
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            if not checkboxes:
                self.logger.info("No checkboxes found on the page")
                return True

            for index, checkbox in enumerate(checkboxes, 1):
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(checkbox)
                    )
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});", checkbox
                    )
                    if not checkbox.is_selected():
                        try:
                            checkbox.click()
                            self.logger.info(f"Ticked checkbox {index}")
                        except ElementClickInterceptedException:
                            self.driver.execute_script("arguments[0].click();", checkbox)
                            self.logger.warning(f"Click checkbox {index} intercepted")
                    else:
                        self.logger.info(f"Checkbox {index} already ticked")
                except TimeoutException:
                    self.logger.warning(f"Timeout waiting for checkbox {index} to be clickable")
                    continue
                except Exception as e:
                    self.logger.error(f"Error ticking checkbox {index}: {str(e)}")
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Error finding checkboxes: {str(e)}")
            return False

    def find_and_click_submission(self, timeout: int = 10) -> bool:
        possible_submissions = ["login", "submit", "register", "continue", "apply",
                                "ok", "confirm", "proceed", "accept", 
                                "done", "finish", "start", "calculate"]
        for submission in possible_submissions:
            if self.find_and_click_btn(submission, timeout):
                self.logger.info(f"Clicked on submission button: {submission}")
                return True
        self.logger.warning("No submission button found")
        return False
    
    def find_input_xpath_by_name(self, inputs, name: str) -> str | None:
        for field in inputs:
            if name in field["text"]:
                return field["xpath"]
        return None

    def fill_form_inputs(self, input_list: List[str]) -> bool:
        """Fill inputs based on a list of [name](value) strings."""
        if not isinstance(input_list, list):
            self.logger.error("input_list must be a list")
            return False
        inputs = self.find_all_inputs()
        try:
            for input_str in input_list:
                match = re.match(r'\[(.*?)\]\((.*?)\)', input_str)
                if not match:
                    self.logger.warning(f"Invalid format for input: {input_str}")
                    continue

                name, value = match.groups()
                name = name.strip()
                value = value.strip()
                xpath = self.find_input_xpath_by_name(inputs, name)
                if not xpath:
                    self.logger.warning(f"Input field '{name}' not found")
                    continue
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                except TimeoutException:
                    self.logger.error(f"Timeout waiting for element '{name}' to be clickable")
                    continue
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                if not element.is_displayed() or not element.is_enabled():
                    self.logger.warning(f"Element '{name}' is not interactable (not displayed or disabled)")
                    continue
                input_type = (element.get_attribute("type") or "text").lower()
                tag_name = (element.tag_name or "").lower()
                if tag_name == "select":
                    try:
                        select = Select(element)
                        select.select_by_visible_text(value)
                        self.logger.info(f"Selected '{value}' for {name}")
                    except Exception:
                        try:
                            select.select_by_value(value)
                            self.logger.info(f"Selected value '{value}' for {name}")
                        except Exception as sel_e:
                            self.logger.warning(f"Could not select '{value}' for {name}: {sel_e}")
                elif tag_name == "textarea":
                    element.clear()
                    element.send_keys(value)
                    self.logger.info(f"Filled textarea {name}")
                elif input_type == "file":
                    if os.path.isabs(value) and os.path.exists(value):
                        element.send_keys(value)
                        self.logger.info(f"Uploaded file '{value}' for {name}")
                    else:
                        self.logger.warning(f"File not found: {value}")
                elif input_type in ["checkbox", "radio"]:
                    is_checked = element.is_selected()
                    should_be_checked = value.lower() == "checked"

                    if is_checked != should_be_checked:
                        element.click()
                        self.logger.info(f"Set {name} to {value}")
                else:
                    element.clear()
                    element.send_keys(value)
                    self.logger.info(f"Filled {name} with {value}")
            return True
        except Exception as e:
            self.logger.error(f"Error filling form inputs: {str(e)}")
            return False
    
    def fill_form(self, input_list: List[str]) -> bool:
        """Fill form inputs based on a list of [name](value) and submit."""
        if not isinstance(input_list, list):
            self.logger.error("input_list must be a list")
            return False
        if self.fill_form_inputs(input_list):
            self.logger.info("Form filled successfully")
            self.tick_all_checkboxes()
            if self.find_and_click_submission():
                if self.wait_for_submission_outcome():
                    self.logger.info("Submission outcome detected")
                    return True
                else:
                    self.logger.warning("No submission outcome detected")
            else:
                self.logger.warning("Failed to submit form")
        self.logger.warning("Failed to fill form inputs")
        return False

    def get_current_url(self) -> str:
        """Get the current URL of the page."""
        return self.driver.current_url

    def get_page_title(self) -> str:
        """Get the title of the current page."""
        return self.driver.title

    def scroll_bottom(self) -> bool:
        """Scroll to the bottom of the page."""
        try:
            self.logger.info("Scrolling to the bottom of the page...")
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(0.5)
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {str(e)}")
            return False
    
    def get_screenshot(self) -> str:
        return self.screenshot_folder + "/updated_screen.png"

    def screenshot(self, filename:str = 'updated_screen.png') -> bool:
        """Take a screenshot of the current page, attempt to capture the full page by zooming out."""
        self.logger.info("Taking full page screenshot...")
        time.sleep(0.1)
        try:
            original_zoom = self.driver.execute_script("return document.body.style.zoom || 1;")
            self.driver.execute_script("document.body.style.zoom='75%'")
            time.sleep(0.1)
            path = os.path.join(self.screenshot_folder, filename)
            if not os.path.exists(self.screenshot_folder):
                os.makedirs(self.screenshot_folder)
            self.driver.save_screenshot(path)
            self.logger.info(f"Full page screenshot saved as {filename}")
        except Exception as e:
            self.logger.error(f"Error taking full page screenshot: {str(e)}")
            return False
        finally:
            self.driver.execute_script(f"document.body.style.zoom='1'")
        return True

    def apply_web_safety(self):
        """
        Apply security measures to block any website malicious/annoying execution, privacy violation etc..
        """
        self.logger.info("Applying web safety measures...")
        script = self.load_js("inject_safety_script.js")
        input_elements = self.driver.execute_script(script)

if __name__ == "__main__":
    driver = create_driver(headless=False, stealth_mode=True, crx_path="../crx/nopecha.crx")
    browser = Browser(driver, anticaptcha_manual_install=True)
    
    input("press enter to continue")
    print("AntiCaptcha / Form Test")
    browser.go_to("https://bot.sannysoft.com")
    time.sleep(5)
    #txt = browser.get_text()
    browser.go_to("https://home.openweathermap.org/users/sign_up")
    inputs_visible = browser.get_form_inputs()
    print("inputs:", inputs_visible)
    #inputs_fill = ['[q](checked)', '[q](checked)', '[user[username]](mlg)', '[user[email]](mlg.fcu@gmail.com)', '[user[password]](placeholder_P@ssw0rd123)', '[user[password_confirmation]](placeholder_P@ssw0rd123)']
    #browser.fill_form(inputs_fill)
    input("press enter to exit")

# Test sites for browser fingerprinting and captcha
# https://nowsecure.nl/
# https://bot.sannysoft.com
# https://browserleaks.com/
# https://bot.incolumitas.com/
# https://fingerprintjs.github.io/fingerprintjs/
# https://antoinevastel.com/bots/