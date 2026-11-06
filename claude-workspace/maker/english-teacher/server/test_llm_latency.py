"""Gate do tre Gemini qua duong goi that cua may chu (GeminiLLM.response sau khi run.py va).
Chay: runtime\\.venv\\Scripts\\python.exe -X utf8 test_llm_latency.py [--n 20]
PASS khi: khong luot nao la cau du phong (429/loi), p50 TTFT <= 1.2 s, p95 <= 2.5 s, khong luot nao > 12 s, moi luot co chu, khong co chu Trung (CJK).
Goi API that (can GOOGLE_API_KEY); khong in khoa.
"""
import argparse
import os
import re
import sys
import time
from pathlib import Path

H = Path(__file__).resolve().parent
RT = H / "runtime"

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=12)
ap.add_argument("--gap", type=float, default=4.0, help="giay giua 2 luot (gia lap be noi; Gemini free gioi han/phut)")
a = ap.parse_args()

sys.path.insert(0, str(H))
import run  # noqa: E402

key = run.get_key()
os.chdir(RT)
sys.path.insert(0, str(RT))
run.patch_llm(key)  # phai co trong run.py: va GeminiLLM (REST SSE + hedge)

from core.providers.llm.gemini.gemini import LLMProvider  # noqa: E402

assert getattr(LLMProvider._generate, "_stlab", False), "GeminiLLM._generate chua duoc va boi run.patch_llm"

sys_prompt = (RT / "stlab-base-prompt.txt").read_text(encoding="utf-8")[:3000]
llm = LLMProvider({"type": "gemini", "api_key": key, "model_name": "gemini-3.1-flash-lite"})
asks = ["Bạn trả lời giúp tôi.", "Hello teacher!", "Con mèo màu gì?", "Apple. Red apple.", "Cô ơi con muốn học số."]
cjk = re.compile(r"[一-鿿]")
ttft, fails = [], []
for i in range(a.n):
    if i:
        time.sleep(a.gap)
    q = asks[i % len(asks)]
    dlg = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": q}]
    t0 = time.time()
    first, text = None, ""
    try:
        for piece in llm.response(f"gate-{i}", dlg):
            if piece:
                first = first or (time.time() - t0)
                text += piece
    except Exception as e:  # noqa: BLE001
        fails.append(f"{i}: loi {type(e).__name__}: {e}")
        continue
    total = time.time() - t0
    if not first or not text.strip():
        fails.append(f"{i}: khong co chu")
        continue
    if "chưa nghe rõ" in text:
        fails.append(f"{i}: cau du phong (Gemini loi/429)")
        continue
    if cjk.search(text):
        fails.append(f"{i}: co chu Trung")
    if total > 12:
        fails.append(f"{i}: tong {total:.1f} s > 12 s")
    ttft.append(first)
    print(f"{i:2d} ttft={first:.2f}s tong={total:.2f}s {text[:50]!r}", flush=True)

ttft.sort()
if ttft:
    p50 = ttft[len(ttft) // 2]
    p95 = ttft[min(len(ttft) - 1, int(round(0.95 * (len(ttft) - 1))))]
    print(f"p50={p50:.2f}s p95={p95:.2f}s max={ttft[-1]:.2f}s n={len(ttft)}/{a.n}")
    if p50 > 1.2:
        fails.append(f"p50 {p50:.2f} > 1.2 s")
    if p95 > 2.5:
        fails.append(f"p95 {p95:.2f} > 2.5 s")
if len(ttft) < a.n:
    fails.append(f"chi {len(ttft)}/{a.n} luot co chu")
print("FAIL\n  " + "\n  ".join(fails) if fails else "PASS")
sys.exit(1 if fails else 0)
