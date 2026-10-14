"""
Import the user's main Chrome login sessions into the agent browser profile.

The agent browser runs on its own user-data-dir (".browser_profile/chrome_data").
This module copies the session-bearing files (cookies, localStorage, IndexedDB,
login metadata) from the user's real Chrome user-data-dir into that profile, so
the agent browser starts already logged in on the sites the user is logged in
on. Chrome itself decrypts the copied files: same OS user, same Chrome binary,
so no decryption code lives here. Requires Google Chrome to be fully quit:
copying a live SQLite/LevelDB store corrupts it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.browser import persistent_profile_dir, profile_in_use, get_chrome_path
from sources.errors import AgenticSeekError
from sources.utility import pretty_print

# Files inside a Chrome profile dir ("Default/") that carry login state.
PROFILE_FILES = (
    "Cookies", "Cookies-journal",
    "Login Data", "Login Data-journal",
    "Login Data For Account", "Login Data For Account-journal",
    "Web Data", "Web Data-journal",
    "Preferences", "Secure Preferences",
)
# Dirs inside a Chrome profile dir that carry login state. "Network" holds the
# Cookies store on Chrome 96+ layouts; older layouts use "Cookies" directly.
PROFILE_DIRS = (
    "Network",
    "Local Storage",
    "Session Storage",
    "IndexedDB",
    "WebStorage",
)
# Root-level files of the user-data-dir. "Local State" holds profile pointers
# and, on some platforms, wrapped cookie-encryption keys.
ROOT_FILES = ("Local State",)
# The agent browser always uses the "Default" profile inside its user-data-dir.
AGENT_PROFILE_NAME = "Default"
MARKER_FILENAME = "session_import.json"


@dataclass
class ImportReport:
    """What an import did, for logs and for the CLI smoke output."""
    source_user_data_dir: str
    source_profile: str
    target_dir: str
    copied: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    backup_dir: Optional[str] = None

    def __str__(self) -> str:
        backup = self.backup_dir or "none"
        return (f"imported {len(self.copied)} entries from "
                f"{os.path.join(self.source_user_data_dir, self.source_profile)} "
                f"into {self.target_dir} (previous agent profile kept at: {backup})")


def chrome_profile_not_found_error(tried: List[str]) -> AgenticSeekError:
    """Error for: no Chrome user-data-dir on this machine."""
    return AgenticSeekError(
        "Chrome profile not found",
        "Session import needs your Chrome user-data-dir, but it was not found.",
        causes=[f"Looked for: {', '.join(tried)}",
                "Chrome is not installed, or its data sits in a non-standard place."],
        fixes=["Install Google Chrome and log in to your usual sites, then retry.",
               "Or set CHROME_USER_DATA_DIR=/path/to/Chrome/User Data in your environment.",
               "Or set import_user_profile = False in config.ini to skip session import."])


def chrome_running_error() -> AgenticSeekError:
    """Error for: the user's Chrome is running while we need it closed."""
    return AgenticSeekError(
        "Google Chrome must be closed for session import",
        "Your Chrome profile files are locked by the running browser. "
        "Copying them now could corrupt your cookies.",
        causes=["Google Chrome is running with the profile you asked to import."],
        fixes=["Quit Google Chrome completely (Cmd+Q on macOS, Quit from the menu elsewhere) and start agenticSeek again.",
               "Or set import_user_profile = False in config.ini to skip session import."])


def agent_browser_running_error() -> AgenticSeekError:
    """Error for: another agenticSeek browser already holds the agent profile."""
    return AgenticSeekError(
        "agenticSeek browser is already running",
        "The agent browser profile cannot be replaced while another agenticSeek "
        "browser session is using it.",
        causes=["Another agenticSeek instance (cli.py or api.py) is running."],
        fixes=["Close the other agenticSeek instance, then start this one again.",
               "Or set import_user_profile = False in config.ini to skip session import."])


def profile_not_found_error(profile_name: str, available: List[str]) -> AgenticSeekError:
    """Error for: the configured Chrome profile name does not exist."""
    return AgenticSeekError(
        f"Chrome profile not found: {profile_name}",
        "The Chrome profile to import does not exist in your user-data-dir.",
        causes=[f"config.ini [BROWSER] import_profile_name = {profile_name} "
                "does not match any Chrome profile directory."],
        fixes=[f"Use one of: {', '.join(available)}",
               "Chrome shows profile dir names at chrome://version, 'Profile Path'."])


def _binary_user_data_dir() -> Optional[str]:
    """User-data-dir of the browser binary the agent will actually run, when known."""
    try:
        binary = get_chrome_path()
    except AgenticSeekError:
        return None
    if not binary:
        return None
    lowered = binary.lower()
    home = os.path.expanduser("~")
    if sys.platform.startswith("darwin"):
        support = os.path.join(home, "Library", "Application Support")
        mapping = {
            "chrome beta": os.path.join(support, "Google", "Chrome Beta"),
            "brave": os.path.join(support, "BraveSoftware", "Brave-Browser"),
            "chromium": os.path.join(support, "Chromium"),
            "chrome": os.path.join(support, "Google", "Chrome"),
        }
    elif sys.platform.startswith("win"):
        local = os.environ.get("LOCALAPPDATA", "")
        mapping = {
            "chrome beta": os.path.join(local, "Google", "Chrome Beta", "User Data"),
            "brave": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data"),
            "chrome": os.path.join(local, "Google", "Chrome", "User Data"),
        }
    else:
        mapping = {
            "chrome-beta": os.path.join(home, ".config", "google-chrome-beta"),
            "brave": os.path.join(home, ".config", "BraveSoftware", "Brave-Browser"),
            "chromium": os.path.join(home, ".config", "chromium"),
            "chrome": os.path.join(home, ".config", "google-chrome"),
        }
    # Order matters: "chrome beta" must be tested before "chrome".
    for mark, path in mapping.items():
        if mark in lowered and os.path.isdir(path):
            return path
    return None


def _default_user_data_dirs() -> List[str]:
    """Where to look for the user's browser data: the agent's own browser first."""
    candidates = []
    binary_dir = _binary_user_data_dir()
    if binary_dir:
        candidates.append(binary_dir)
    home = os.path.expanduser("~")
    if sys.platform.startswith("darwin"):
        candidates.append(os.path.join(home, "Library", "Application Support", "Google", "Chrome"))
    elif sys.platform.startswith("win"):
        candidates.append(os.path.join(os.environ.get("LOCALAPPDATA", ""),
                                       "Google", "Chrome", "User Data"))
    else:
        candidates.append(os.path.join(home, ".config", "google-chrome"))
    return candidates


def user_data_dir() -> str:
    """
    Locate the user's main Chrome user-data-dir.

    Who uses it: import_sessions, before any file is copied. The CLI helper
    calls import_sessions, which calls this.

    What it does: it returns the directory set in CHROME_USER_DATA_DIR when
    that environment variable is set. Else it returns the first standard
    Chrome directory of this OS that exists.

    Args:
        None.

    Returns:
        str: absolute path of the Chrome user-data-dir.

    Raises:
        AgenticSeekError: no Chrome user-data-dir was found.
    """
    override = os.environ.get("CHROME_USER_DATA_DIR")
    candidates = [override] if override else _default_user_data_dirs()
    for candidate in candidates:
        if candidate and os.path.isdir(candidate):
            return os.path.abspath(candidate)
    raise chrome_profile_not_found_error(candidates)


def _lock_is_live(source_dir: str) -> bool:
    """True when Chrome's SingletonLock in source_dir points to a live process."""
    lock = os.path.join(source_dir, "SingletonLock")
    if not os.path.lexists(lock):
        return False
    try:
        target = os.readlink(lock)  # format: "<hostname>-<pid>"
        host, _, pid_part = target.rpartition("-")
        pid = int(pid_part)
        return bool(host) and host == _hostname() and _pid_alive(pid) and _pid_is_browser(pid)
    except (ValueError, OSError):
        # A lock we cannot read still means "treat as closed"; the process
        # check below is the safety net.
        return False


def _hostname() -> str:
    """This machine's hostname, or "" when unknown."""
    import socket
    try:
        return socket.gethostname()
    except OSError:
        return ""


def _pid_is_zombie(pid: int) -> bool:
    """True when the process is dead but not yet reaped (ps state Z). Never raises."""
    try:
        state = subprocess.run(["ps", "-o", "state=", "-p", str(pid)],
                               capture_output=True, text=True, timeout=5).stdout
        return state.strip().upper().startswith("Z")
    except (OSError, subprocess.SubprocessError):
        return False


def _pid_alive(pid: int) -> bool:
    """True when a live (not zombie) process with this pid exists. Never raises."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    # os.kill succeeds for zombies too: a dead-but-unreaped Chrome holds nothing.
    return not _pid_is_zombie(pid)


BROWSER_PROCESS_MARKS = ("chrome", "brave", "chromium", "edge")


def _pid_is_browser(pid: int) -> bool:
    """True when the process is a browser binary (ps comm). Never raises."""
    try:
        comm = subprocess.run(["ps", "-o", "comm=", "-p", str(pid)],
                              capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        # Cannot tell: assume it is the browser, the safe direction.
        return True
    name = comm.strip().lower()
    return bool(name) and any(mark in name for mark in BROWSER_PROCESS_MARKS)


def _browser_process_names(source_dir: str) -> List[str]:
    """OS process names of the browser family that owns source_dir."""
    lowered = source_dir.lower()
    if "brave" in lowered:
        names = ["Brave Browser", "brave-browser", "brave", "brave.exe"]
    elif "edge" in lowered:
        names = ["Microsoft Edge", "microsoft-edge", "msedge.exe"]
    elif "chromium" in lowered:
        names = ["Chromium", "chromium", "chromium-browser", "chromium.exe"]
    else:
        # Google Chrome family, including Beta.
        names = ["Google Chrome", "Google Chrome Beta", "google-chrome", "chrome", "chrome.exe"]
    suffix = ".exe" if sys.platform.startswith("win") else ""
    return [name for name in names if name.endswith(suffix)] or [names[-1]]


def _browser_process_running(process_names: List[str]) -> bool:
    """True when a process from process_names is found by the OS process list."""
    for name in process_names:
        if sys.platform.startswith("win"):
            cmd = ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"]
        else:
            cmd = ["pgrep", "-x", name]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if sys.platform.startswith("win"):
                if name in (result.stdout or ""):
                    return True
            elif result.returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def chrome_is_running(source_dir: str) -> bool:
    """
    Check if the user's Chrome holds this user-data-dir open.

    Who uses it: import_sessions, as a guard before copying files.

    What it does: it returns True when the SingletonLock of the directory
    points to a live process, or when a process of the browser family that
    owns the directory is found.

    Args:
        source_dir (str): path of a Chrome user-data-dir.

    Returns:
        bool: True when Chrome seems to be running.
    """
    return _lock_is_live(source_dir) or _browser_process_running(_browser_process_names(source_dir))

def _agent_profile_in_use(target_dir: str) -> bool:
    """
    Check if the agent browser profile is held open by a live Chrome.

    Who uses it: import_sessions, as a guard before the agent profile is
    replaced.

    What it does: it returns True when the profile's SingletonLock points to
    a live process. A lock held by a dead (zombie) Chrome is removed first:
    Chrome cannot start under such a lock either. On Windows, where Chrome
    uses a "lockfile" instead, profile_in_use of sources.browser decides.

    Args:
        target_dir (str): path of the agent browser user-data-dir.

    Returns:
        bool: True when a live browser session holds the profile.
    """
    lock = os.path.join(target_dir, "SingletonLock")
    if os.path.lexists(lock):
        if _lock_is_live(target_dir):
            return True
        try:
            os.unlink(lock)
        except OSError:
            pass
    return sys.platform.startswith("win") and profile_in_use(target_dir)


def available_profiles(source_dir: str) -> List[str]:
    """Profile dir names inside source_dir (dirs that hold a Preferences file)."""
    found = []
    try:
        for name in sorted(os.listdir(source_dir)):
            if os.path.isfile(os.path.join(source_dir, name, "Preferences")):
                found.append(name)
    except OSError:
        pass
    return found


def _marker_path() -> str:
    """Path of the 'import already done' marker file."""
    return os.path.join(os.path.dirname(persistent_profile_dir()), MARKER_FILENAME)


def _marker_data() -> dict:
    """The marker file as a dict; empty when missing or unreadable."""
    try:
        with open(_marker_path(), "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError):
        return {}


def import_needed(profile_name: str = "Default") -> bool:
    """True when an import would do work: no marker yet, or another profile."""
    return _marker_data().get("source_profile") != profile_name


def _rotate_existing_target(target_dir: str) -> Optional[str]:
    """Move the current agent profile aside; never delete it. Returns its new path."""
    if not os.path.isdir(target_dir):
        return None
    backup = f"{target_dir}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.move(target_dir, backup)
    return backup



def _copy_profile_state(source_profile_dir: str, target_profile_dir: str) -> Tuple[List[str], List[str]]:
    """Copy the session-bearing files and dirs; returns (copied, missing) names."""
    copied, missing = [], []
    os.makedirs(target_profile_dir, exist_ok=True)
    for name in PROFILE_FILES:
        src = os.path.join(source_profile_dir, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(target_profile_dir, name))
            copied.append(name)
        else:
            missing.append(name)
    for name in PROFILE_DIRS:
        src = os.path.join(source_profile_dir, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(target_profile_dir, name),
                            dirs_exist_ok=True, symlinks=True,
                            ignore=shutil.ignore_patterns("Singleton*", "lockfile"))
            copied.append(name)
        else:
            missing.append(name)
    return copied, missing


def _copy_root_files(source_dir: str, target_dir: str) -> List[str]:
    """Copy root-level files (Local State) into the target user-data-dir."""
    copied = []
    for name in ROOT_FILES:
        src = os.path.join(source_dir, name)
        if os.path.isfile(src):
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(src, os.path.join(target_dir, name))
            copied.append(name)
    return copied


def _rewrite_profile_pointers(local_state_path: str, source_profile: str) -> None:
    """
    Point the copied Local State at the "Default" profile dir.

    Who uses it: import_sessions, after the files are copied.

    What it does: it sets profile.last_used and profile.last_active_profiles
    to "Default", and renames the info_cache entry of the source profile to
    "Default". This makes Chrome open the imported data, no matter which
    profile dir name the source used.

    Args:
        local_state_path (str): path of the copied "Local State" file.
        source_profile (str): profile dir name the data came from, e.g. "Profile 1".

    Returns:
        None. The file is rewritten in place. A file that cannot be parsed is
        left unchanged: Chrome can still recover from it.
    """
    try:
        with open(local_state_path, "r", encoding="utf-8") as handle:
            state = json.load(handle)
        profile = state.setdefault("profile", {})
        profile["last_used"] = AGENT_PROFILE_NAME
        profile["last_active_profiles"] = [AGENT_PROFILE_NAME]
        cache = profile.setdefault("info_cache", {})
        if source_profile != AGENT_PROFILE_NAME and source_profile in cache:
            cache[AGENT_PROFILE_NAME] = cache.pop(source_profile)
        with open(local_state_path, "w", encoding="utf-8") as handle:
            json.dump(state, handle, separators=(",", ":"))
    except (ValueError, OSError):
        pass


def _write_marker(report: ImportReport) -> None:
    """Write the marker that stops repeat imports on every start."""
    payload = {
        "source_user_data_dir": report.source_user_data_dir,
        "source_profile": report.source_profile,
        "imported_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "copied": report.copied,
    }
    os.makedirs(os.path.dirname(_marker_path()), exist_ok=True)
    with open(_marker_path(), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def no_cookie_store_error(source_profile_dir: str) -> AgenticSeekError:
    """Error for: the source profile holds no cookie store at all."""
    return AgenticSeekError(
        "No cookie store found in the Chrome profile",
        f"{source_profile_dir} holds no Cookies file and no Network dir, "
        "so there are no login sessions to import.",
        causes=["The directory is not a real Chrome profile.",
                "CHROME_USER_DATA_DIR points at the wrong directory."],
        fixes=["Check the path with chrome://version, 'Profile Path'.",
               "Or set import_user_profile = False in config.ini."])


def _validate_cookie_store(source_profile_dir: str) -> None:
    """
    Fail before anything is copied when the source holds no cookies.

    Who uses it: import_sessions, before the agent profile is moved aside.

    What it does: it raises when the profile has neither a Cookies file nor
    a Network dir. Checking first keeps a failed import from replacing the
    agent profile with a half copy.

    Args:
        source_profile_dir (str): path of the Chrome profile dir to import.

    Returns:
        None.
    """
    has_cookies = (os.path.isfile(os.path.join(source_profile_dir, "Cookies"))
                   or os.path.isdir(os.path.join(source_profile_dir, "Network")))
    if not has_cookies:
        raise no_cookie_store_error(source_profile_dir)

def import_sessions(profile_name: str = "Default") -> ImportReport:
    """
    Copy the user's Chrome login sessions into the agent browser profile.

    Who uses it: import_sessions_if_configured (called by cli.py and api.py
    before the browser starts), and the module smoke block. Callers decide
    whether an import is needed; this function always imports.

    What it does: it checks that the source holds cookies and that its
    browser is closed, moves the current agent profile to a backup, copies
    cookies, localStorage, IndexedDB, saved logins and autofill data into
    the agent profile, and writes a marker file.

    Args:
        profile_name (str): Chrome profile dir to import, e.g. "Default" or
            "Profile 1". Comes from config.ini [BROWSER] import_profile_name.

    Returns:
        ImportReport: what was copied and where the backup went.

    Raises:
        AgenticSeekError: no Chrome data found, no cookie store, the browser
            is running, the profile name is unknown, or another agenticSeek
            browser holds the agent profile.
    """
    source_dir = user_data_dir()
    source_profile_dir = os.path.join(source_dir, profile_name)
    if not os.path.isdir(source_profile_dir):
        raise profile_not_found_error(profile_name, available_profiles(source_dir))
    _validate_cookie_store(source_profile_dir)
    if chrome_is_running(source_dir):
        raise chrome_running_error()
    target_dir = persistent_profile_dir()
    if _agent_profile_in_use(target_dir):
        raise agent_browser_running_error()
    backup_dir = _rotate_existing_target(target_dir)
    report = ImportReport(source_user_data_dir=source_dir, source_profile=profile_name,
                          target_dir=target_dir, backup_dir=backup_dir)
    report.copied.extend(_copy_root_files(source_dir, target_dir))
    copied, missing = _copy_profile_state(source_profile_dir,
                                          os.path.join(target_dir, AGENT_PROFILE_NAME))
    report.copied.extend(copied)
    report.missing = missing
    _rewrite_profile_pointers(os.path.join(target_dir, "Local State"), profile_name)
    _write_marker(report)
    return report


def import_sessions_if_configured(config, headless: bool = True) -> None:
    """
    Run the session import when the user turned it on in config.ini.

    Who uses it: cli.py and api.py, right before create_driver().

    What it does: it returns at once when import_user_profile is off, or when
    the import marker already exists. Else it runs import_sessions, prints a
    summary, and warns that the first run should show the browser window
    (macOS keychain consent and new-device checks need a person).

    Args:
        config (configparser.ConfigParser): the app config, section [BROWSER].
        headless (bool): True when the browser will start without a window.

    Returns:
        None. AgenticSeekError propagates to the caller's error panel.
    """
    if not config.getboolean("BROWSER", "import_user_profile", fallback=False):
        return
    profile_name = config.get("BROWSER", "import_profile_name", fallback="Default")
    if not import_needed(profile_name):
        return
    report = import_sessions(profile_name=profile_name)
    pretty_print(f"Chrome sessions imported: {report}", color="success")
    if headless:
        pretty_print("First run after import: set headless_browser = False once, so keychain "
                     "consent and any new-device login checks can be answered by you.",
                     color="warning")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    name = next((arg for arg in sys.argv[1:] if not arg.startswith("-")), "Default")
    pretty_print(f"Importing Chrome sessions (profile: {name})...", color="status")
    print(import_sessions(profile_name=name))
