"""
Agent workspace and runtime directory resolution.

Agents may only read/write files inside WORK_DIR. Application runtime data
(logs, screenshots, conversation history) lives in AGENT_RUNTIME_DIR so the
application source tree can stay read-only in Docker.
"""

from __future__ import annotations

import configparser
import os

DEFAULT_RUNTIME_DIR = ".agent-data"


def _read_config_work_dir() -> str | None:
    if not os.path.exists("config.ini"):
        return None
    config = configparser.ConfigParser()
    config.read("config.ini")
    if "MAIN" not in config:
        return None
    value = config["MAIN"].get("work_dir", fallback="").strip()
    return value or None


def get_runtime_dir() -> str:
    """Directory for backend runtime files (logs, screenshots, sessions)."""
    path = os.getenv("AGENT_RUNTIME_DIR", DEFAULT_RUNTIME_DIR).strip()
    if not path:
        path = DEFAULT_RUNTIME_DIR
    return os.path.realpath(os.path.abspath(path))


def get_work_dir() -> str:
    """Directory where agents may read, write, and execute code."""
    path = os.getenv("WORK_DIR", "").strip() or _read_config_work_dir()
    if not path:
        path = os.path.join(get_runtime_dir(), "workspace")
    return os.path.realpath(os.path.abspath(path))


def ensure_directory(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def ensure_work_dir() -> str:
    return ensure_directory(get_work_dir())


def ensure_runtime_dir() -> str:
    return ensure_directory(get_runtime_dir())


def runtime_subdir(name: str) -> str:
    return ensure_directory(os.path.join(get_runtime_dir(), name))


def is_within_directory(path: str, directory: str) -> bool:
    """Return True when path resolves inside directory (no traversal escape)."""
    try:
        path_real = os.path.realpath(os.path.abspath(path))
        dir_real = os.path.realpath(os.path.abspath(directory))
        return os.path.commonpath([path_real, dir_real]) == dir_real
    except ValueError:
        return False


def resolve_workspace_path(path: str, work_dir: str | None = None) -> str:
    """
    Resolve a user or model-provided path inside the agent workspace.

    Raises:
        ValueError: empty path
        PermissionError: resolved path escapes the workspace
    """
    if path is None or not str(path).strip():
        raise ValueError("Empty path")

    base = work_dir or get_work_dir()
    candidate = str(path).strip()
    if os.path.isabs(candidate):
        resolved = os.path.realpath(candidate)
    else:
        resolved = os.path.realpath(os.path.join(base, candidate))

    if not is_within_directory(resolved, base):
        raise PermissionError(
            f"Path '{path}' is outside the agent workspace ({base})"
        )
    return resolved
