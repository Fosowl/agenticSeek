import pytest

from sources.tools.fileFinder import FileFinder


@pytest.fixture
def finder(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("WORK_DIR", str(workspace))
    monkeypatch.setenv("AGENT_RUNTIME_DIR", str(tmp_path / "runtime"))
    tool = FileFinder()
    yield tool
    for handler in tool.logger.logger.handlers[:]:
        handler.close()
        tool.logger.logger.removeHandler(handler)


def test_read_file_returns_utf8_content_regardless_of_locale(finder, tmp_path):
    # save_block and the workspace API write UTF-8; read_file must not depend
    # on the platform locale (e.g. cp936/cp1252 on Windows) to round-trip them.
    (tmp_path / "workspace" / "notes.txt").write_bytes("café: 你好".encode("utf-8"))
    assert finder.read_file("notes.txt") == "café: 你好"


def test_read_file_reports_no_error_on_non_utf8_bytes(finder, tmp_path):
    # Byte sequences that are invalid UTF-8 (e.g. a cp1252-saved file) must not
    # crash the read: the tool reports an error string instead of file content
    # today, which makes the agent believe the file is unreadable.
    (tmp_path / "workspace" / "legacy.txt").write_bytes(b"caf\xe9: r\xe9sum\xe9")
    content = finder.read_file("legacy.txt")
    assert not content.startswith("Error reading file:"), content
