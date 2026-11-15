import pytest

from sources.tools.fileFinder import FileFinder


@pytest.fixture
def finder(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "present.txt").write_text("kept content", encoding="utf-8")
    monkeypatch.setenv("WORK_DIR", str(workspace))
    monkeypatch.setenv("AGENT_RUNTIME_DIR", str(tmp_path / "runtime"))
    tool = FileFinder()
    yield tool
    for handler in tool.logger.logger.handlers[:]:
        handler.close()
        tool.logger.logger.removeHandler(handler)


@pytest.mark.parametrize(
    "names",
    [
        ["present.txt", "missing.txt"],
        ["missing.txt", "present.txt", "other-missing.txt"],
        ["missing.txt", "other-missing.txt"],
        ["missing.txt"],
        ["present.txt"],
    ],
)
def test_batch_preserves_each_file_result_in_order(finder, names):
    output = finder.execute([f"action=read\nname={name}" for name in names])
    expected = [
        "Content:\nkept content" if name == "present.txt" else f"File: {name} - not found"
        for name in names
    ]
    offset = 0
    for result in expected:
        position = output.find(result, offset)
        assert position >= offset, output
        offset = position + len(result)
