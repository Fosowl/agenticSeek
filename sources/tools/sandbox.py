"""Process isolation for the code that agents execute.

Agents run shell, Python, C, Go and Java code written by an LLM, and that
code can be steered by prompt injection from web pages or files. Two layers
limit what it can reach:

- Secret scrubbing: environment variables whose names look like credentials
  (provider API keys, the API token) are removed from the child environment.
- Privilege drop (Docker): when the backend runs as root and
  AGENTICSEEK_EXEC_UID is set, children run as that unprivileged uid. They
  then cannot read the backend's /proc/<pid>/environ or the 0700 runtime
  directory (sessions, browser profile, API token).
"""

from __future__ import annotations

import os

EXEC_UID_ENV = "AGENTICSEEK_EXEC_UID"
EXEC_GID_ENV = "AGENTICSEEK_EXEC_GID"
SECRET_NAME_SUFFIXES = ("_KEY", "_TOKEN", "_SECRET", "_PASSWORD", "_CREDENTIALS")
ROOT_UID = 0


def scrubbed_env() -> dict[str, str]:
    """Copy the backend environment without credential variables.

    The interpreters call this before they start a child process.
    It drops every variable whose upper-case name ends with a secret suffix.

    Returns:
        dict[str, str]: Environment for the child process.
    """
    return {
        name: value
        for name, value in os.environ.items()
        if not name.upper().endswith(SECRET_NAME_SUFFIXES)
    }


def exec_identity() -> tuple[int, int] | None:
    """Find the unprivileged uid and gid for agent code, if a drop applies.

    subprocess_isolation and hand_over_path call this for every execution.
    A drop applies only when the backend runs as root and AGENTICSEEK_EXEC_UID
    is a non-zero uid; AGENTICSEEK_EXEC_GID defaults to the uid.

    Returns:
        tuple[int, int] | None: (uid, gid) to run as, or None for no drop.

    Raises:
        ValueError: When AGENTICSEEK_EXEC_UID or AGENTICSEEK_EXEC_GID is not an integer.
    """
    raw_uid = os.getenv(EXEC_UID_ENV, "").strip()
    if not raw_uid or os.name != "posix" or os.geteuid() != ROOT_UID:
        return None
    uid = int(raw_uid)
    if uid == ROOT_UID:
        return None
    gid = int(os.getenv(EXEC_GID_ENV, "").strip() or uid)
    return uid, gid


def _home_for(uid: int, fallback: str) -> str:
    """Find the home directory of a uid.

    subprocess_isolation calls this to give the child a writable HOME.

    Args:
        uid (int): The unprivileged uid that runs agent code.
        fallback (str): Directory to use when the uid has no passwd entry.

    Returns:
        str: Home directory path.
    """
    import pwd  # POSIX-only; a uid drop never happens elsewhere

    try:
        return pwd.getpwuid(uid).pw_dir
    except KeyError:
        return fallback


def subprocess_isolation(work_dir: str) -> dict:
    """Build the keyword arguments that isolate one child process.

    The interpreters pass the result to subprocess.run or subprocess.Popen.
    It always scrubs secrets; under a privilege drop it also sets the uid,
    gid, empty supplementary groups, and HOME/USER of the unprivileged user.

    Args:
        work_dir (str): Agent workspace, used as HOME when the uid has no home.

    Returns:
        dict: Keyword arguments for the subprocess call.
    """
    env = scrubbed_env()
    identity = exec_identity()
    if identity is None:
        return {"env": env}
    uid, gid = identity
    env["HOME"] = _home_for(uid, work_dir)
    env["USER"] = env["LOGNAME"] = str(uid)
    return {"env": env, "user": uid, "group": gid, "extra_groups": []}


def hand_over_path(path: str) -> None:
    """Give a file or directory that the backend created to the agent uid.

    The interpreters call this for temporary build directories, and Tools
    calls it for code blocks it saves into the workspace, so agent code can
    later read and change them. It does nothing when no drop applies.

    Args:
        path (str): Path the backend (root) just created.
    """
    identity = exec_identity()
    if identity is not None:
        os.chown(path, *identity)


def hand_over_fd(fd: int) -> None:
    """Give an open file or directory that the backend created to the agent uid.

    The upload API calls this for the files that the user sends and for the
    upload directory. A descriptor stays on the same file, even when agent
    code puts a symlink in its path. It does nothing when no drop applies.

    Args:
        fd (int): Open descriptor of a file or directory that the backend (root) just created.
    """
    identity = exec_identity()
    if identity is not None:
        os.fchown(fd, *identity)


if __name__ == "__main__":
    import subprocess

    os.environ["DEMO_API_KEY"] = "must-not-leak"
    kwargs = subprocess_isolation(os.getcwd())
    child_env = subprocess.run(["env"], capture_output=True, text=True, **kwargs).stdout
    assert "DEMO_API_KEY" not in child_env and "PATH=" in child_env
    print(f"ok: secrets scrubbed; privilege drop={exec_identity()}")
