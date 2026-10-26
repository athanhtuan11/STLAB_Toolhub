# Cham bai giao viec: so chi tiet nguoi thuc thi dung (part.step) voi chi tiet MAU (STEP cung he toa do).
# Chi Claude/nguoi duyet chay - chi tiet mau KHONG dat trong thu muc giao viec.
#   freecadcmd compare.py <part.step> <ref.step>
# In: the tich 2 ben, phan THUA (co o part, khong co o mau), phan THIEU (nguoc lai), % lech theo the tich mau.
import sys
import Part

a = [x for x in sys.argv[1:] if not x.endswith(".py")]
p, r = Part.read(a[0]), Part.read(a[1])
extra, miss = p.cut(r).Volume, r.cut(p).Volume
print("COMPARE vol_part %.1f vol_ref %.1f thua %.1f mm3 thieu %.1f mm3 lech %.2f %%" % (
    p.Volume, r.Volume, extra, miss, 100.0 * (extra + miss) / r.Volume), flush=True)
