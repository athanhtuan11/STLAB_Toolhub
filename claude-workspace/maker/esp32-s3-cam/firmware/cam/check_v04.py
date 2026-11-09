# Gate tinh v0.4.0: ghi clip AVI MJPEG (khong can mach). python check_v04.py
# 1) kiem tinh ma (idx1/avih/'00dc'/khong format the/chan '..'/khong chep MJPEG2SD)
# 2) dich phan thuc cua avi_build_header (main/avi_mjpeg.h) sang Python va kiem cau truc RIFF/AVI that
import re, struct, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
main = H / "main"
src = "\n".join(p.read_text(encoding="utf-8") for p in sorted(main.glob("*.c")))
hdr_src = (main / "avi_mjpeg.h").read_text(encoding="utf-8")
html = (main / "index.html").read_text(encoding="utf-8")
fails = []
def need(c, m):
    if not c:
        fails.append(m)

# ---------- 1. kiem tinh ----------
need(re.search(r'CAM_VERSION\s+"0\.4\.0"', src) is not None, 'CAM_VERSION "0.4.0"')
need('"idx1"' in src + hdr_src, "co chunk idx1")
need('"avih"' in hdr_src and '"strh"' in hdr_src and '"strf"' in hdr_src and '"hdrl"' in hdr_src and '"movi"' in hdr_src,
     "co avih/strh/strf/hdrl/movi")
need('"00dc"' in src + hdr_src, "co chunk 00dc")
need('"MJPG"' in hdr_src and '"vids"' in hdr_src, "MJPG + vids")
need(re.search(r"format_if_mount_failed\s*=\s*true", src) is None, "cam format the (format_if_mount_failed = true)")
need("format_if_mount_failed = false" in src, "format_if_mount_failed = false van con")
need(re.search(r"strstr\(\s*f\s*,\s*\"\.\.\"\s*\)", src) is not None, "/sd chan '..'")
need("video/x-msvideo" in src and ".avi" in src, "/sd cho .avi + Content-Type video/x-msvideo")
need("httpd_resp_send_chunk" in src, "/sd gui theo khoi")
for v in ["clip", "clip_fps", "pre_s", "post_s"]:
    need(re.search(r'strcmp\(var,\s*"%s"\)' % v, src) is not None, "/control thieu var " + v)
for k in ["clip", "clip_rec", "clip_count", "clip_drop"]:
    need(('\\"%s\\"' % k) in src, "/status thieu truong " + k)
need('\\"clip\\":' in src, "/events co truong clip")
need(re.search(r"clip_valid[\s\S]{0,300}clip_fps\s*>=\s*1\s*&&\s*c->clip_fps\s*<=\s*10", src) is not None, "clip_fps 1..10")
need(re.search(r"pre_s\s*>=\s*0\s*&&\s*c->pre_s\s*<=\s*5", src) is not None, "pre_s 0..5")
need(re.search(r"post_s\s*>=\s*2\s*&&\s*c->post_s\s*<=\s*30", src) is not None, "post_s 2..30")
need(re.search(r"CLIP_RING_BYTES\s*\(2\s*\*\s*1024\s*\*\s*1024\)", src) is not None, "bo dem truoc su kien <= 2 MB")
need(re.search(r"CLIP_MAX_S\s+60", src) is not None, "toi da 60 s / clip")
need(re.search(r"CLIP_WBUF\s+(\d+)", src) is not None and int(re.search(r"CLIP_WBUF\s+(\d+)", src).group(1)) >= 16384,
     "dem ghi >= 16 KB")
need("s_clip_drop++" in src, "dem clip_drop khi queue day")
need("nvs_set_blob(h, \"clip\"" in src, "tham so clip luu NVS")
need(len(re.findall(r"esp_camera_fb_get\(", src)) <= 2, "chi task camera goi esp_camera_fb_get")
need(not re.findall(r"\)\s*\{\s*\}", src), "co khoi lenh rong")
need("s_sd_ok" in src and "g_clip.clip && s_sd_ok" in src, "chi chay khi clip=1 va sd_ok")
for k in ["clip", "sw-clip", "in-pre", "in-post"]:
    need(k in html, "index.html thieu " + k)
need("xem clip" in html, "index.html: link clip trong danh sach su kien")
need(len(html.encode("utf-8")) <= 40 * 1024, "index.html <= 40 KB")
need("MJPEG2SD" not in src and "mjpeg2sd" not in src.lower() or "KHONG" in src, "khong nhac/chep MJPEG2SD")

# ---------- 2. dich avi_build_header sang Python ----------
body = re.search(r"static inline void avi_build_header\([^)]*\)\s*\{(.*?)\n\}", hdr_src, re.S).group(1)
def build(w, ht, fps_milli, frames, max_chunk, chunk_bytes, idx_bytes):
    h = bytearray(224)
    env = dict(w=w, ht=ht, fps_milli=fps_milli or 1000, frames=frames, max_chunk=max_chunk,
               chunk_bytes=chunk_bytes, idx_bytes=idx_bytes)
    for m in re.finditer(r"avi_(p32|p16|tag)\(h \+ (\d+), (.*)\);", body):
        kind, off, expr = m.group(1), int(m.group(2)), m.group(3).strip()
        if kind == "tag":
            h[off:off + 4] = expr.strip('"').encode()
            continue
        e = re.sub(r"\(uint32_t\)", "", expr)
        e = re.sub(r"\b(\d+|0x[0-9A-Fa-f]+)(ULL|u|U)\b", r"\1", e)
        e = e.replace("/", "//")
        v = eval(e, {}, env) & (0xFFFFFFFF if kind == "p32" else 0xFFFF)
        h[off:off + (4 if kind == "p32" else 2)] = v.to_bytes(4 if kind == "p32" else 2, "little")
    return bytes(h)

def jpeg(w, ht, n):  # JPEG gia: SOI, APP0, SOF0, SOS, rac, EOI
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, ht, w, 1) + b"\x01\x11\x00"
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + sof + b"\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00" + bytes(n) + b"\xff\xd9"

def make_avi(frames_len, w=800, ht=600, fps_milli=5000):
    chunks, idx, off, cb = [], [], 4, 0
    for L in frames_len:
        j = jpeg(w, ht, L)
        pad = len(j) & 1
        chunks.append(b"00dc" + struct.pack("<I", len(j)) + j + (b"\0" if pad else b""))
        idx.append(b"00dc" + struct.pack("<III", 0x10, off, len(j)))
        off += 8 + len(j) + pad
        cb += 8 + len(j) + pad
    idxb = b"idx1" + struct.pack("<I", 16 * len(idx)) + b"".join(idx)
    hd = build(w, ht, fps_milli, len(frames_len), max(len(c) - 8 for c in chunks), cb, 16 * len(idx))
    return hd + b"".join(chunks) + idxb, cb

def parse(data, nframes, w, ht):
    errs = []
    if data[0:4] != b"RIFF" or data[8:12] != b"AVI ":
        return ["khong phai RIFF AVI"]
    if struct.unpack_from("<I", data, 4)[0] != len(data) - 8:
        errs.append("RIFF size sai")
    p, found = 12, {}
    while p + 8 <= len(data):
        tag, size = data[p:p + 4], struct.unpack_from("<I", data, p + 4)[0]
        if tag == b"LIST":
            found[data[p + 8:p + 12]] = (p, size)
            if data[p + 8:p + 12] == b"hdrl":
                p += 12  # di vao hdrl: avih, LIST strl
                a = p
                if data[a:a + 4] != b"avih" or struct.unpack_from("<I", data, a + 4)[0] != 56:
                    errs.append("avih sai")
                else:
                    f = struct.unpack_from("<14I", data, a + 8)[0:12]
                    if f[3] != 0x10: errs.append("avih thieu AVIF_HASINDEX")
                    if f[4] != nframes: errs.append("avih dwTotalFrames %d != %d" % (f[4], nframes))
                    if f[6] != 1: errs.append("dwStreams != 1")
                    if (f[8], f[9]) != (w, ht): errs.append("avih kich thuoc sai")
                    if f[0] != 200000: errs.append("dwMicroSecPerFrame %d" % f[0])
                s = a + 8 + 56
                if data[s:s + 4] != b"LIST" or data[s + 8:s + 12] != b"strl":
                    errs.append("thieu LIST strl")
                else:
                    sl_size = struct.unpack_from("<I", data, s + 4)[0]
                    q = s + 12
                    if data[q:q + 4] != b"strh" or data[q + 8:q + 12] != b"vids" or data[q + 12:q + 16] != b"MJPG":
                        errs.append("strh sai (vids/MJPG)")
                    else:
                        scale, rate, start, length = struct.unpack_from("<4I", data, q + 8 + 20)
                        if rate / scale != 5.0: errs.append("strh rate/scale != 5 fps")
                        if length != nframes: errs.append("strh dwLength sai")
                    q2 = q + 8 + 56
                    if data[q2:q2 + 4] != b"strf" or struct.unpack_from("<I", data, q2 + 4)[0] != 40:
                        errs.append("strf sai")
                    else:
                        bi = struct.unpack_from("<IiiHH4sI", data, q2 + 8)
                        if bi[0] != 40 or bi[1] != w or bi[2] != ht or bi[3] != 1 or bi[5] != b"MJPG":
                            errs.append("BITMAPINFOHEADER sai %r" % (bi,))
                    if (q2 + 8 + 40) - (s + 8) != sl_size:
                        errs.append("LIST strl size %d != %d" % (sl_size, (q2 + 8 + 40) - (s + 8)))
                p = found[b"hdrl"][0] + 8 + found[b"hdrl"][1]
                continue
            if data[p + 8:p + 12] == b"movi":
                movi_pos = p + 8
                q, got, offs = p + 12, 0, []
                while q < p + 8 + size:
                    if data[q:q + 4] != b"00dc":
                        errs.append("chunk khong phai 00dc @%d" % q); break
                    L = struct.unpack_from("<I", data, q + 4)[0]
                    offs.append((q - movi_pos, L))
                    got += 1
                    q += 8 + L + (L & 1)
                    if q % 2: errs.append("chunk le byte")
                if got != nframes: errs.append("movi co %d khung != %d" % (got, nframes))
                if q != p + 8 + size: errs.append("movi size lech")
                found["_offs"] = offs
        elif tag == b"idx1":
            n = size // 16
            ents = [struct.unpack_from("<4sIII", data, p + 8 + 16 * i) for i in range(n)]
            if n != nframes: errs.append("idx1 co %d muc != %d" % (n, nframes))
            if [(e[2], e[3]) for e in ents] != found.get("_offs"): errs.append("idx1 offset/size khong khop movi")
            if any(e[0] != b"00dc" or e[1] != 0x10 for e in ents): errs.append("idx1 tag/flags sai")
            if p + 8 + size != len(data): errs.append("idx1 khong o cuoi file")
        p += 8 + size
    if b"hdrl" not in found or b"movi" not in found:
        errs.append("thieu hdrl/movi")
    return errs

for lens in ([1000], [101, 100, 4097, 7, 20000], [19001] * 30):
    data, cb = make_avi(lens)
    errs = parse(data, len(lens), 800, 600)
    need(not errs, "AVI %d khung: %s" % (len(lens), "; ".join(errs)))
    need(len(data) == 224 + cb + 8 + 16 * len(lens), "tong kich thuoc file %d khung" % len(lens))

# placeholder luc mo (0 khung) phai dung 224 byte, tag dung
ph = build(800, 600, 5000, 0, 0, 0, 0)
need(len(ph) == 224 and ph[:4] == b"RIFF" and ph[212:216] == b"LIST" and ph[220:224] == b"movi", "header giu cho 224 byte")

# ffmpeg (neu co) doc duoc file mau
import shutil, subprocess, tempfile
ff = shutil.which("ffmpeg")
try:
    from PIL import Image
    import io
except Exception:
    Image = None
if ff and Image is not None:  # file AVI that (JPEG that) phai giai ma duoc bang ffmpeg: 12 khung 320x240
    jp = []
    for i in range(12):
        bio = io.BytesIO()
        Image.new("RGB", (320, 240), (i * 20, 100, 255 - i * 20)).save(bio, "JPEG")
        jp.append(bio.getvalue())
    ch, idx, off, cb = b"", b"", 4, 0
    for j in jp:
        pad = len(j) & 1
        ch += b"00dc" + struct.pack("<I", len(j)) + j + (bytes(1) if pad else b"")
        idx += b"00dc" + struct.pack("<III", 0x10, off, len(j))
        off += 8 + len(j) + pad
        cb += 8 + len(j) + pad
    avi = build(320, 240, 5000, 12, max(len(j) for j in jp), cb, len(idx)) + ch + b"idx1" + struct.pack("<I", len(idx)) + idx
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "t.avi"
        fp.write_bytes(avi)
        r = subprocess.run([ff, "-v", "error", "-i", str(fp), "-f", "null", "-"], capture_output=True, text=True)
        need(r.returncode == 0 and not r.stderr.strip(), "ffmpeg doc AVI mau: " + r.stderr.strip()[:200])
        r2 = subprocess.run([ff, "-i", str(fp), "-f", "null", "-"], capture_output=True, text=True)
        need("frame=   12" in r2.stderr or "frame=12" in r2.stderr.replace(" ", ""), "ffmpeg giai ma du 12 khung")
    print("ffmpeg: doc duoc AVI mau 12 khung")
else:
    print("SKIP ffmpeg/PIL: khong co - chi kiem cau truc bang parser Python")

# kiem doc kich thuoc JPEG (avi_jpeg_dims) bang ban Python tuong ung
def dims(b):
    i = 2
    while i + 4 <= len(b):
        if b[i] != 0xFF: i += 1; continue
        m = b[i + 1]
        if m == 0xFF: i += 1; continue
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7: i += 2; continue
        if m in (0xD9, 0xDA): return None
        seg = (b[i + 2] << 8) | b[i + 3]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            return ((b[i + 7] << 8) | b[i + 8], (b[i + 5] << 8) | b[i + 6])
        i += 2 + seg
    return None
need(dims(jpeg(1024, 768, 10)) == (1024, 768), "doc kich thuoc JPEG (SOF0)")
need("avi_jpeg_dims" in hdr_src and "0xC4" in hdr_src, "avi_jpeg_dims bo qua DHT/DAC/JPG")

if fails:
    print("FAIL check_v04:"); [print(" -", f) for f in fails]; sys.exit(1)
print("PASS check_v04")
