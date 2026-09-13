"""
CRX extraction for AgenticSeek's anti-captcha extension.

Chrome's --load-extension flag needs an *unpacked* directory, but the repo
ships a packed CRX (crx/nopecha.crx). Loading a CRX through selenium's
add_extension() never worked here because --disable-extensions was always
passed alongside it - so the captcha solver was dead code in every mode.

A CRX file is a small header (CRX2/CRX3 container with signature data)
followed by a plain zip. We locate the zip payload, validate it, and unpack
it into a cache directory that --load-extension can consume.
"""

from __future__ import annotations

import io
import os
import shutil
import zipfile

_ZIP_LOCAL_HEADER = b"PK\x03\x04"


def _zip_offsets(data: bytes):
    """All plausible zip start offsets in a CRX blob (first is usually right)."""
    offsets, start = [], 0
    while True:
        idx = data.find(_ZIP_LOCAL_HEADER, start)
        if idx == -1:
            return offsets
        offsets.append(idx)
        start = idx + 1


def default_extract_dir(crx_path: str) -> str:
    name = os.path.splitext(os.path.basename(crx_path))[0] or "extension"
    return os.path.abspath(os.path.join(os.getcwd(), ".browser_profile", "extensions", name))


def _safe_members(zf: zipfile.ZipFile):
    """Reject absolute or traversing paths (basic zip-slip guard)."""
    for name in zf.namelist():
        if name.startswith(("/", "\\")) or ".." in name.replace("\\", "/").split("/"):
            raise ValueError(f"unsafe zip member: {name}")


def extract_crx(crx_path: str, dest_dir: str | None = None, force: bool = False) -> str | None:
    """
    Unpack a packed CRX into an unpacked-extension directory.

    Returns the directory (usable with --load-extension), or None when the
    file is missing/invalid. Extraction is cached: a second call with the
    extracted manifest already present is a no-op. Concurrent callers race
    safely through a temp dir + rename.
    """
    if not crx_path or not os.path.exists(crx_path):
        return None
    dest_dir = dest_dir or default_extract_dir(crx_path)
    manifest = os.path.join(dest_dir, "manifest.json")
    if os.path.exists(manifest) and not force:
        return dest_dir

    try:
        with open(crx_path, "rb") as f:
            data = f.read()
    except OSError:
        return None

    for offset in _zip_offsets(data):
        try:
            zf = zipfile.ZipFile(io.BytesIO(data[offset:]))
            if "manifest.json" not in zf.namelist():
                continue
            _safe_members(zf)
            os.makedirs(os.path.dirname(dest_dir) or ".", exist_ok=True)
            tmp_dir = f"{dest_dir}.tmp{os.getpid()}"
            shutil.rmtree(tmp_dir, ignore_errors=True)
            zf.extractall(tmp_dir)
            if os.path.exists(manifest) and not force:
                shutil.rmtree(tmp_dir, ignore_errors=True)  # another process won
                return dest_dir
            shutil.rmtree(dest_dir, ignore_errors=True)
            os.replace(tmp_dir, dest_dir)
            return dest_dir
        except Exception:
            continue
    return None


def extension_installed(crx_path: str = "./crx/nopecha.crx") -> bool:
    """True when the CRX is already unpacked in the cache (cheap check)."""
    return os.path.exists(os.path.join(default_extract_dir(crx_path), "manifest.json"))
