import json
from pathlib import Path

import pytest

from sources.memory import Memory


@pytest.mark.parametrize("has_usable_session", [True, False])
def test_recovery_skips_invalid_sessions(tmp_path, monkeypatch, has_usable_session):
    monkeypatch.setenv("AGENT_RUNTIME_DIR", str(tmp_path))
    memory = Memory("Current system prompt", memory_compression=False)
    session_dir = Path(memory.conversation_folder) / "casual_agent"
    session_dir.mkdir(parents=True)
    if has_usable_session:
        for time, answer in [("09-00-00", "older"), ("10-00-00", "latest usable")]:
            history = [
                {"role": "system", "content": "Saved system prompt"},
                {"role": "assistant", "content": answer},
                {"role": "user", "content": "Unanswered turn"},
            ]
            (session_dir / f"memory_2026-11-15_{time}.txt").write_text(
                json.dumps(history), encoding="utf-8"
            )
    (session_dir / "memory_2026-11-15_11-00-00.txt").write_text("[]", encoding="utf-8")
    (session_dir / "memory_2026-11-15_12-00-00.txt").write_text(
        '[{"role": "system"', encoding="utf-8"
    )

    memory.load_memory()

    if has_usable_session:
        assert memory.get() == [
            {"role": "system", "content": "Saved system prompt"},
            {"role": "assistant", "content": "latest usable"},
        ]
    else:
        assert memory.get() == [{"role": "system", "content": "Current system prompt"}]
