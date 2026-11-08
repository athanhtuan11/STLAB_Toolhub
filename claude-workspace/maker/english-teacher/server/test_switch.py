# Gate NHAN CAU "DOI BAI" (Claude viet, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_switch.py
# Tuan 2026-11-08: be noi "Doi bai di co" thi co dong y nhung lai quay ve tu cu -> cau noi phai NHAN cau doi bai (chu ASR co dau/
# khong dau/nham nhe) va goi Curriculum.switch(); cau binh thuong / tu tieng Anh dang hoc KHONG duoc tinh la doi bai.
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent / "live"))
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


from curriculum import wants_switch  # noqa: E402

YES = ["Đổi bài đi cô.", "doi bai di co", "Cô ơi đổi bài khác đi", "Học bài khác đi cô", "Con muốn học cái khác",
       "Chơi trò khác đi cô", "Đổi trò khác", "cô đổi bài đi", "Bài khác!", "Chơi cái khác đi", "đổi bài"]
NO = ["One.", "Two!", "Con là bạn Thỏ.", "Dạ.", "Con thích bài này", "Cô ơi con muốn nghe lại", "Hello cô",
      "Con đổi màu xanh", "Bài hát hay quá", "Khác gì đâu", "", "Con không biết"]
for t in YES:
    ok(wants_switch(t) is True, f"doi bai: {t!r}")
for t in NO:
    ok(wants_switch(t) is False, f"khong phai doi bai: {t!r}")
print("\n%s test_switch (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
