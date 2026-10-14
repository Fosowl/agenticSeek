"""Read-only HTTP access to the agent workspace (WORK_DIR) for the frontend Files view.

Paths in requests and responses are POSIX-style and relative to the workspace
root; the empty string designates the root itself. Every path is resolved with
symlinks followed and rejected if it escapes the workspace.
"""

from __future__ import annotations

import mimetypes
import os
import stat

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from sources.api_auth import require_api_token
from sources.workspace import get_work_dir, is_within_directory, resolve_workspace_path

MAX_TEXT_BYTES = 1024 * 1024
BINARY_SNIFF_BYTES = 8192

# Raw files are only served for <img> previews. The CSP sandbox keeps an SVG
# opened directly in a tab from running script on the API origin.
RAW_RESPONSE_HEADERS = {
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
    "X-Content-Type-Options": "nosniff",
}

router = APIRouter(prefix="/files", dependencies=[Depends(require_api_token)])


def _resolve(path: str) -> tuple[str, str, str]:
    """Return (resolved absolute path, workspace root, normalized relative path)."""
    work_dir = get_work_dir()
    if not path.strip():
        return work_dir, work_dir, ""
    try:
        resolved = resolve_workspace_path(path, work_dir)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Path is outside the agent workspace")
    relative = os.path.relpath(os.path.join(work_dir, path.strip()), work_dir)
    relative = "" if relative == "." else relative.replace(os.sep, "/")
    return resolved, work_dir, relative


def _require_file(path: str) -> tuple[str, str]:
    resolved, _, relative = _resolve(path)
    if not os.path.exists(resolved):
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=400, detail="Path is not a file")
    return resolved, relative


def _image_mime(path: str) -> str | None:
    mime, _ = mimetypes.guess_type(path)
    return mime if mime and mime.startswith("image/") else None


@router.get("/list")
def list_directory(path: str = Query("")):
    directory, work_dir, relative = _resolve(path)
    if not os.path.exists(directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail="Path is not a directory")

    entries = []
    try:
        with os.scandir(directory) as iterator:
            for entry in iterator:
                target = os.path.realpath(entry.path)
                if not is_within_directory(target, work_dir):
                    continue
                try:
                    info = os.stat(target)
                except OSError:  # broken symlink or vanished entry
                    continue
                is_dir = stat.S_ISDIR(info.st_mode)
                entries.append({
                    "name": entry.name,
                    "path": f"{relative}/{entry.name}" if relative else entry.name,
                    "type": "directory" if is_dir else "file",
                    "size": None if is_dir else info.st_size,
                    "modified": info.st_mtime,
                })
    except PermissionError:
        raise HTTPException(status_code=403, detail="Directory is not readable")

    entries.sort(key=lambda item: (item["type"] != "directory", item["name"].lower()))
    return {"path": relative, "entries": entries}


@router.get("/content")
def read_file(path: str = Query(...)):
    file_path, relative = _require_file(path)
    size = os.path.getsize(file_path)
    result = {
        "path": relative,
        "name": os.path.basename(relative),
        "size": size,
        "mime": None,
        "kind": "binary",
        "content": None,
        "truncated": False,
    }

    mime = _image_mime(file_path)
    if mime:
        result.update(kind="image", mime=mime)
        return result

    try:
        with open(file_path, "rb") as handle:
            data = handle.read(MAX_TEXT_BYTES)
    except PermissionError:
        raise HTTPException(status_code=403, detail="File is not readable")

    if b"\x00" in data[:BINARY_SNIFF_BYTES]:
        return result

    result.update(
        kind="text",
        mime=mimetypes.guess_type(file_path)[0] or "text/plain",
        content=data.decode("utf-8", errors="replace"),
        truncated=size > MAX_TEXT_BYTES,
    )
    return result


@router.get("/raw")
def raw_image(path: str = Query(...)):
    file_path, _ = _require_file(path)
    mime = _image_mime(file_path)
    if not mime:
        raise HTTPException(status_code=415, detail="Only image files can be served raw")
    return FileResponse(file_path, media_type=mime, headers=RAW_RESPONSE_HEADERS)
