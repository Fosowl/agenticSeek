"""HTTP access to the agent workspace (WORK_DIR) for the frontend.

The Files view reads the workspace through the GET routes. The chat uploads
user files into WORK_DIR/.user_uploads through POST /files/upload.

Paths in requests and responses are POSIX-style and relative to the workspace
root; the empty string designates the root itself. Every path is resolved with
symlinks followed and rejected if it escapes the workspace.
"""

from __future__ import annotations

import itertools
import mimetypes
import os
import shutil
import stat
from typing import NamedTuple

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from sources.api_auth import require_api_token
from sources.tools.sandbox import hand_over_fd
from sources.workspace import (
    ensure_work_dir,
    get_work_dir,
    is_within_directory,
    resolve_workspace_path,
)

MEBIBYTE = 1024 * 1024
MAX_TEXT_BYTES = MEBIBYTE
BINARY_SNIFF_BYTES = 8192

UPLOAD_DIR_NAME = ".user_uploads"
MAX_UPLOAD_BYTES = 50 * MEBIBYTE
UPLOAD_CHUNK_BYTES = MEBIBYTE
UPLOAD_FILE_MODE = 0o644
# Filesystem name limit, minus room for a " (12)" suffix.
MAX_UPLOAD_NAME_BYTES = 255 - 16
# O_EXCL never replaces an entry, and never follows a symlink.
UPLOAD_OPEN_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
# O_NOFOLLOW: refuse a symlinked upload directory.
DIRECTORY_OPEN_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
# Windows has no dir_fd, and never drops privileges.
CAN_PIN_DIRECTORY = os.open in os.supports_dir_fd
# Upload paths go in a comma list inside <files>...</files>.
TAG_BREAKING_CHARS = "<>,"

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


class UploadDir(NamedTuple):
    """Directory that upload_files writes into.

    path: Absolute path of WORK_DIR/.user_uploads.
    fd: Open descriptor of that directory, or None where dir_fd is unsupported.
    """

    path: str
    fd: int | None


def _clean_upload_name(raw_name: str | None) -> str:
    """Make a safe file name from the name that the browser sends.

    upload_files calls this for each file of an upload request.
    It keeps only the last path part, removes control characters, and
    replaces the characters that break the <files> list in the agent prompt.

    Args:
        raw_name (str | None): File name of one multipart part, from the browser.

    Returns:
        str: File name without directory parts.

    Raises:
        HTTPException: 400 when no usable name remains, or when the name is too long.
    """
    base = (raw_name or "").replace("\\", "/").rsplit("/", 1)[-1]
    printable = "".join(char for char in base if char.isprintable()).strip()
    name = "".join("_" if char in TAG_BREAKING_CHARS else char for char in printable)
    if name in ("", ".", ".."):
        raise HTTPException(status_code=400, detail=f"Invalid file name: {raw_name!r}")
    if len(name.encode()) > MAX_UPLOAD_NAME_BYTES:
        raise HTTPException(status_code=400, detail=f"File name is too long: {name}")
    return name


def _require_upload_size(upload: UploadFile) -> None:
    """Refuse a file that is larger than MAX_UPLOAD_BYTES.

    upload_files calls this for each file before it writes any file.
    The server has already received the file into a temporary file.

    Args:
        upload (UploadFile): One uploaded file, from the multipart request.

    Raises:
        HTTPException: 413 when the file is too large.
    """
    if upload.size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"{upload.filename} is larger than the {MAX_UPLOAD_BYTES // MEBIBYTE} MB upload limit",
        )


def _open_upload_dir(work_dir: str) -> UploadDir:
    """Create the upload directory when it is missing, and open it.

    upload_files calls this once for each request.
    Files are then created through the directory descriptor, so agent code
    cannot redirect them outside the workspace with a symlink.

    Args:
        work_dir (str): Real path of the agent workspace, from ensure_work_dir.

    Returns:
        UploadDir: Path and open descriptor of the upload directory.

    Raises:
        HTTPException: 409 when .user_uploads is a symlink or not a directory.
    """
    path = os.path.join(work_dir, UPLOAD_DIR_NAME)
    try:
        os.mkdir(path)
        is_new = True
    except FileExistsError:
        is_new = False
    if not CAN_PIN_DIRECTORY:
        return UploadDir(path, None)
    try:
        dir_fd = os.open(path, DIRECTORY_OPEN_FLAGS)
    except OSError:
        raise HTTPException(status_code=409, detail=f"{UPLOAD_DIR_NAME} must be a directory, not a file or symlink")
    if is_new:
        hand_over_fd(dir_fd)
    return UploadDir(path, dir_fd)


def _create_unique_file(upload_dir: UploadDir, name: str) -> tuple[int, str]:
    """Create a new empty file, and never replace a file that exists.

    _save_upload calls this with a cleaned file name.
    When the name is taken, it tries "name (1).ext", "name (2).ext", and so on.

    Args:
        upload_dir (UploadDir): Upload directory, from _open_upload_dir.
        name (str): Cleaned file name, from _clean_upload_name.

    Returns:
        tuple[int, str]: Open file descriptor, and name of the new file.
    """
    stem, extension = os.path.splitext(name)
    for index in itertools.count():
        candidate = name if index == 0 else f"{stem} ({index}){extension}"
        target = candidate if upload_dir.fd is not None else os.path.join(upload_dir.path, candidate)
        try:
            return os.open(target, UPLOAD_OPEN_FLAGS, UPLOAD_FILE_MODE, dir_fd=upload_dir.fd), candidate
        except FileExistsError:
            continue


def _save_upload(upload: UploadFile, name: str, upload_dir: UploadDir) -> str:
    """Write one uploaded file into the upload directory.

    upload_files calls this for each file after all checks pass.
    It writes the bytes into a new file and gives the file to the agent uid.

    Args:
        upload (UploadFile): Uploaded file, from the multipart request.
        name (str): Cleaned file name, from _clean_upload_name.
        upload_dir (UploadDir): Upload directory, from _open_upload_dir.

    Returns:
        str: Workspace-relative POSIX path of the saved file.
    """
    fd, saved_name = _create_unique_file(upload_dir, name)
    with os.fdopen(fd, "wb") as target:
        shutil.copyfileobj(upload.file, target, UPLOAD_CHUNK_BYTES)
        hand_over_fd(target.fileno())
    return f"{UPLOAD_DIR_NAME}/{saved_name}"


@router.post("/upload")
def upload_files(files: list[UploadFile] = File(...)):
    """Save the files that the user attaches in the chat into the workspace.

    The frontend calls this before it sends a query that names the files.
    It checks all names and sizes first, then writes each file to
    WORK_DIR/.user_uploads without replacing existing files.

    Args:
        files (list[UploadFile]): Multipart "files" parts, from the browser.

    Returns:
        dict: {"paths": list[str]} with workspace-relative POSIX paths, in request order.
    """
    names = [_clean_upload_name(upload.filename) for upload in files]
    for upload in files:
        _require_upload_size(upload)
    upload_dir = _open_upload_dir(ensure_work_dir())
    try:
        return {"paths": [_save_upload(upload, name, upload_dir) for upload, name in zip(files, names)]}
    finally:
        if upload_dir.fd is not None:
            os.close(upload_dir.fd)


if __name__ == "__main__":
    import tempfile

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    os.environ["WORK_DIR"] = tempfile.mkdtemp()
    os.environ["AGENTICSEEK_API_TOKEN"] = "smoke-token"
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app, headers={"Authorization": "Bearer smoke-token"})
    upload = [("files", ("report.txt", b"hello", "text/plain"))] * 2
    paths = client.post("/files/upload", files=upload).json()["paths"]
    assert paths == [".user_uploads/report.txt", ".user_uploads/report (1).txt"], paths
    saved = os.stat(os.path.join(os.environ["WORK_DIR"], paths[0]))
    print(f"ok: uploads saved as {paths}, owner uid={saved.st_uid}")
