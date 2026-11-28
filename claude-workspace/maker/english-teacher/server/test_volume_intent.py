# Gate am luong + chan play_music (offline). Chay: runtime\.venv\Scripts\python.exe -m pytest test_volume_intent.py -q
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "live"))
from intent import parse_volume_intent, music_requested  # noqa: E402

TITLES = ["Twinkle Twinkle Little Star"]


def test_volume():
    assert parse_volume_intent("mở tối đa volume") == ("set", 100)
    assert parse_volume_intent("hết cỡ") == ("set", 100)
    assert parse_volume_intent("mở to lên") == ("delta", 30)
    assert parse_volume_intent("nói nhỏ lại") == ("delta", -30)
    for down in ("giảm âm lượng", "giảm âm lượng xuống", "Cô ơi giảm xuống", "to quá", "ồn quá", "nói nhỏ thôi",
                 "vặn nhỏ lại", "nhỏ một chút", "bớt to đi"):
        assert parse_volume_intent(down) == ("delta", -30), down
    for up in ("tăng âm lượng", "nhỏ quá", "khó nghe quá", "vặn to lên"):
        assert parse_volume_intent(up) == ("delta", 30), up
    assert parse_volume_intent("good morning cô ơi") is None
    assert parse_volume_intent("con nghe cô nói") is None
    assert parse_volume_intent("mở nhạc đi") is None
    assert parse_volume_intent("mở") is None
    assert parse_volume_intent("") is None


def test_music_requested():
    assert music_requested(["Cùng nghe nhạc"], TITLES)
    assert not music_requested([""], TITLES)
    assert not music_requested(["mở tối đa"], TITLES)
    assert music_requested(["Twinkle"], TITLES)
