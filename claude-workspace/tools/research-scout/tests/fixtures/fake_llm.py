# AI gia cho test: doc prompt tu stdin, tra loi co dinh + so dong bat dau bang "- " trong prompt
import sys
p = sys.stdin.read()
n = sum(1 for l in p.splitlines() if l.startswith("- "))
print(f"GOI Y TUAN: {n} muc. Uu tien esp32-robot-kit cho line-bot.")
