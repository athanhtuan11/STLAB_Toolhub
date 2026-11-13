# Gate OTA (offline). Chay: runtime\.venv\Scripts\python.exe -m pytest test_ota.py -q
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "live"))
import ota_logic as o  # noqa: E402

S3 = {"chip_model_name": "esp32s3", "board": {"type": "stlab-s3"}, "application": {"version": "2.5.2"}}
MAN = {"version": "2.5.2.1", "file": "xiaozhi-2.5.2.1.bin"}


def test_a1s_none():
    a1s = {"chip_model_name": "esp32", "board": {"type": "stlab-a1s"}, "application": {"version": "1.0.0"}}
    assert o.pick_firmware(a1s, MAN, True, disabled=False) is None


def test_other_s3_board_none():
    x = {"chip_model_name": "esp32s3", "board": {"type": "bread-compact-wifi"}, "application": {"version": "2.5.2"}}
    assert o.pick_firmware(x, MAN, True, disabled=False) is None


def test_s3_old_gets_url():
    assert o.pick_firmware(S3, MAN, True, disabled=False) == "/xiaozhi/firmware/s3/xiaozhi-2.5.2.1.bin"


def test_s3_current_none():
    s = dict(S3, application={"version": "2.5.2.1"})
    assert o.pick_firmware(s, MAN, True, disabled=False) is None


def test_not_allowed_none():
    assert o.pick_firmware(S3, MAN, False, disabled=False) is None


def test_bad_sha_none(tmp_path):
    f = tmp_path / "xiaozhi-2.5.2.1.bin"
    f.write_bytes(b"abc")
    good = dict(MAN, sha256=hashlib.sha256(b"abc").hexdigest(), size=3)
    (tmp_path / "manifest.json").write_text(json.dumps(good))
    assert o.load_manifest(tmp_path) is not None
    (tmp_path / "manifest.json").write_text(json.dumps(dict(good, sha256="0" * 64)))
    assert o.load_manifest(tmp_path) is None
    (tmp_path / "manifest.json").write_text(json.dumps(good))
    f.unlink()
    assert o.load_manifest(tmp_path) is None


def test_bad_name_rejected():
    assert o.pick_firmware(S3, dict(MAN, file="../x"), True, disabled=False) is None
    assert not o.safe_name("../x") and not o.safe_name("..\\x.bin") and not o.safe_name("xiaozhi-1.0/../a.bin")
    assert o.safe_name("xiaozhi-2.5.2.1.bin")


def test_disable_env(monkeypatch):
    monkeypatch.setenv("STLAB_OTA_DISABLE", "1")
    assert o.pick_firmware(S3, MAN, True) is None
    monkeypatch.delenv("STLAB_OTA_DISABLE")
    assert o.pick_firmware(S3, MAN, True) is not None


def test_version_compare():
    assert o.parse_version("2.5.2.1") == [2, 5, 2, 1]
    assert o.parse_version("2.5.x") is None and o.parse_version("") is None
    assert o.is_newer("2.5.2.1", "2.5.2") and not o.is_newer("2.5.2", "2.5.2.1")
    assert not o.is_newer("2.5.2", "2.5.2") and not o.is_newer("2.5.3", "2.5.10")
    assert o.is_newer("2.5.10", "2.5.3") and not o.is_newer("bad", "2.5.2")
