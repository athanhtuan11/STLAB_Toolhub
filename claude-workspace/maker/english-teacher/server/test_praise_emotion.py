# Gate mat Khen (offline, 2026-11-28). Chay: runtime\.venv\Scripts\python.exe -m pytest test_praise_emotion.py -q
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "live"))
from intent import praise_said  # noqa: E402


def test_praise():
    for t in ("Good job, Kay!", "Giỏi quá con ơi!", "Tuyệt vời!", "Đúng rồi, con giỏi lắm", "Well done!", "Yay! You did it!"):
        assert praise_said(t), t


def test_not_praise():
    for t in ("Let's count: one, two, three.", "Con nói lại nhé", "What color is this?", "Cô chưa nghe rõ", "", "goodbye", "Cô giới thiệu con vật mới nhé", "Thế giới động vật"):
        assert not praise_said(t), t


def test_bridge_wired():
    s = (Path(__file__).parent / "live" / "bridge.py").read_text(encoding="utf-8")
    assert "praise_said(self.reply_txt[self.praise_at:])" in s
    assert '"type": "llm", "emotion": "happy"' in s
    assert "self.praise_at = 0" in s
