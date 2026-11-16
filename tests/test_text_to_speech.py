import pytest

from sources.text_to_speech import Speech


@pytest.mark.parametrize(
    ("language", "text", "expected"),
    [
        (
            "ja",
            "「こんにちは。」資料を確認しました。",
            "「こんにちは。」資料を確認しました。",
        ),
        ("fr", "À Montréal, l’été est agréable.", "À Montréal, l’été est agréable."),
        ("zh", "你好，我已经核对了资料。", "你好，我已经核对了资料。"),
        ("en", "Read `file.txt` at https://example.com first.", "Read at first."),
    ],
)
def test_prepare_speech_in_selected_language(
    monkeypatch, tmp_path, language, text, expected
):
    monkeypatch.chdir(tmp_path)
    speech = Speech(enable=False, language=language, voice_idx=0)

    assert speech.clean_sentence(text) == expected
