"""Loc anh truoc khi chinh mau: mat nhoe, mat nham, anh chup lien tiep trung nhau.

Chi DOC anh nguon. Ket qua ghi vao --out:
  <nhom>/                       anh xem truoc (2048 px, khong EXIF) theo nhom: dat / xem-lai / loai / trung-lap.
                                Tuan duyet bang cach keo anh giua cac thu muc; develop.py xuat nhung anh trong dat/.
  tong-quan-<nhom>.jpg          bang anh kem ly do (khung mat: xanh = dat, vang = nghi ngo, do = loi)
  bao-cao.csv / bao-cao.json    moi anh: nhom, ly do, diem tung khuon mat

Chay:  uv run scripts/cull.py <thu-muc-anh> --out <thu-muc-ket-qua>
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import cv2
import imagehash
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image, ImageDraw, ImageOps

MODELS = Path(__file__).resolve().parent.parent / "models"
EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
GROUPS = ("dat", "xem-lai", "loai", "trung-lap")


@dataclass
class Face:
    box: list[int]  # x, y, w, h tren anh da giam (WORK_EDGE)
    det: float  # do tin cay YuNet
    sharp: float  # phuong sai Laplacian vung mat (chuan hoa 160 px)
    blink_l: float | None = None  # 0 = mo, 1 = nham (None: khong doc duoc)
    blink_r: float | None = None
    main: bool = True  # mat chinh (khong phai nguoi phia sau)
    verdict: str = "ok"  # ok / nghi / loi


@dataclass
class Photo:
    file: str
    taken: str | None
    faces: list[Face] = field(default_factory=list)
    hash: str = ""
    burst: int = -1
    group: str = "dat"
    reasons: list[str] = field(default_factory=list)


def load(path: Path, edge: int) -> tuple[np.ndarray, str | None]:
    """Doc anh (giai ma JPEG o do phan giai giam cho nhanh), xoay theo EXIF, tra BGR + thoi diem chup."""
    im = Image.open(path)
    taken = im.getexif().get_ifd(0x8769).get(36867) or im.getexif().get(306)
    im.draft("RGB", (edge, edge))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((edge, edge))
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR), taken


def sharpness(gray: np.ndarray) -> float:
    # Chi thu nho ve 160 px (khong phong to: phong to lam mo -> diem thap gia)
    g = cv2.resize(gray, (160, 160), interpolation=cv2.INTER_AREA)
    return float(cv2.Laplacian(g, cv2.CV_64F).var())


def analyse(path: Path, det, lmk, edge: int, min_face: int) -> Photo:
    img, taken = load(path, edge)
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, found = det.detect(img)
    photo = Photo(file=path.name, taken=taken)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for row in [] if found is None else found:
        x, y, fw, fh = (int(v) for v in row[:4])
        if min(fw, fh) < min_face:
            continue
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + fw, w), min(y + fh, h)
        face = Face(box=[x, y, fw, fh], det=round(float(row[14]), 3), sharp=0.0)
        # Do net: phan giua mat (bo toc/nen o vien)
        ix, iy = int(fw * 0.15), int(fh * 0.15)
        face.sharp = round(sharpness(gray[y0 + iy : y1 - iy, x0 + ix : x1 - ix]), 1)
        # Mat nham: cat mat + le 40% roi chay Face Landmarker
        m = int(max(fw, fh) * 0.4)
        crop = img[max(y - m, 0) : min(y + fh + m, h), max(x - m, 0) : min(x + fw + m, w)]
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(crop[:, :, ::-1]))
        res = lmk.detect(mp_img)
        if res.face_blendshapes:
            bs = {c.category_name: c.score for c in res.face_blendshapes[0]}
            face.blink_l = round(bs.get("eyeBlinkLeft", 0.0), 3)
            face.blink_r = round(bs.get("eyeBlinkRight", 0.0), 3)
        photo.faces.append(face)
    # Mat chinh: >= 45% canh mat lon nhat (bo nguoi nho phia sau)
    if photo.faces:
        big = max(f.box[2] for f in photo.faces)
        for f in photo.faces:
            f.main = f.box[2] >= 0.45 * big
    small = cv2.resize(img, (512, int(512 * h / w)), interpolation=cv2.INTER_AREA)
    photo.hash = str(imagehash.phash(Image.fromarray(small[:, :, ::-1])))
    return photo


def parse_time(s: str | None) -> datetime | None:
    try:
        return datetime.strptime(s.strip("\x00 "), "%Y:%m:%d %H:%M:%S") if s else None
    except ValueError:
        return None


def classify(photos: list[Photo], a: argparse.Namespace) -> None:
    mains = [f.sharp for p in photos for f in p.faces if f.main]
    median = statistics.median(mains) if mains else 0.0
    for p in photos:
        main = [f for f in p.faces if f.main]
        if not main:
            p.group, p.reasons = "xem-lai", ["khong thay mat (anh canh / mat nghieng / qua nho)"]
            continue
        bad, doubt = [], []
        for i, f in enumerate(main, 1):
            rel = f.sharp / median if median else 1.0
            if rel < a.blur_bad:
                f.verdict = "loi"
                bad.append(f"mat {i} nhoe ({rel:.0%} trung vi)")
            elif rel < a.blur_doubt:
                f.verdict = "nghi"
                doubt.append(f"mat {i} hoi nhoe ({rel:.0%} trung vi)")
            if f.blink_l is None:
                f.verdict = "nghi" if f.verdict == "ok" else f.verdict
                doubt.append(f"mat {i}: khong doc duoc mat")
                continue
            blink = max(f.blink_l, f.blink_r)
            if blink >= a.blink_bad:
                f.verdict = "loi"
                bad.append(f"mat {i} nham mat ({blink:.2f})")
            elif blink >= a.blink_doubt:
                f.verdict = "nghi" if f.verdict == "ok" else f.verdict
                doubt.append(f"mat {i} mat hip ({blink:.2f})")
        p.group = "loai" if bad else "xem-lai" if doubt else "dat"
        p.reasons = bad + doubt


def mark_bursts(photos: list[Photo], a: argparse.Namespace) -> None:
    """Gom anh lien tiep giong nhau; trong moi loat chi giu anh tot nhat, con lai -> trung-lap."""
    burst, prev = 0, None
    for p in photos:
        t = parse_time(p.taken)
        if prev is not None:
            same = imagehash.hex_to_hash(p.hash) - imagehash.hex_to_hash(prev[0].hash) <= a.hash_dist
            close = t and prev[1] and abs((t - prev[1]).total_seconds()) <= a.burst_sec
            if not (same and close):
                burst += 1
        p.burst, prev = burst, (p, t)

    def score(p: Photo) -> tuple:
        main = [f for f in p.faces if f.main]
        worst_blink = max((max(f.blink_l, f.blink_r) for f in main if f.blink_l is not None), default=1.0)
        return (GROUPS.index(p.group), worst_blink, -min((f.sharp for f in main), default=0.0))

    for b in {p.burst for p in photos}:
        members = [p for p in photos if p.burst == b]
        if len(members) < 2:
            continue
        best = min(members, key=score)
        for p in members:
            if p is not best and p.group != "loai":
                p.reasons.insert(0, f"cung loat voi {best.file} (anh do tot hon)")
                p.group = "trung-lap"


def sheet(src: Path, photos: list[Photo], out: Path, edge: int) -> None:
    if not photos:
        return
    tw, th, cols = 420, 300, 5
    rows = (len(photos) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw, rows * (th + 34)), "white")
    d = ImageDraw.Draw(canvas)
    color = {"ok": (0, 170, 0), "nghi": (230, 170, 0), "loi": (220, 0, 0)}
    for i, p in enumerate(photos):
        im = Image.open(src / p.file)
        im.draft("RGB", (edge, edge))
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((edge, edge))
        dr = ImageDraw.Draw(im)
        for f in p.faces:
            x, y, w, h = f.box
            dr.rectangle([x, y, x + w, y + h], outline=color[f.verdict] if f.main else (150, 150, 150), width=6)
        im.thumbnail((tw, th))
        x0, y0 = (i % cols) * tw, (i // cols) * (th + 34)
        canvas.paste(im, (x0, y0))
        d.text((x0 + 3, y0 + th + 2), p.file, fill="black")
        d.text((x0 + 3, y0 + th + 16), "; ".join(p.reasons)[:70], fill=(120, 0, 0))
    canvas.save(out, quality=85)


def preview(src: Path, dst: Path, edge: int = 2048) -> None:
    """Anh xem truoc de duyet: xoay dung, thu nho, KHONG mang EXIF (GPS) theo."""
    im = Image.open(src)
    icc = im.info.get("icc_profile")
    im.draft("RGB", (edge, edge))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((edge, edge))
    im.save(dst, quality=88, icc_profile=icc)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--edge", type=int, default=3000, help="canh dai khi phan tich (px)")
    ap.add_argument("--min-face", type=int, default=60, help="bo mat nho hon (px, tren anh --edge)")
    ap.add_argument("--blur-bad", type=float, default=0.30, help="do net < x * trung vi -> loai")
    ap.add_argument("--blur-doubt", type=float, default=0.55, help="do net < x * trung vi -> xem lai")
    ap.add_argument("--blink-bad", type=float, default=0.80, help="eyeBlink >= x -> loai")
    ap.add_argument("--blink-doubt", type=float, default=0.45, help="eyeBlink >= x -> xem lai")
    ap.add_argument("--hash-dist", type=int, default=12, help="pHash cach nhau <= x -> cung loat")
    ap.add_argument("--burst-sec", type=float, default=4.0, help="chup cach nhau <= x giay -> cung loat")
    ap.add_argument("--no-sheet", action="store_true")
    ap.add_argument("--force", action="store_true", help="xoa thu muc nhom cu (ke ca anh Tuan da keo) roi tao lai")
    a = ap.parse_args()

    files = sorted(p for p in a.src.iterdir() if p.suffix.lower() in EXTS)
    if a.out.resolve() == a.src.resolve() or a.src.resolve() in a.out.resolve().parents:
        ap.error("--out phai nam ngoai thu muc anh goc")
    used = [g for g in GROUPS if (a.out / g).is_dir() and any((a.out / g).iterdir())]
    if used and not a.force:
        ap.error(f"thu muc nhom {used} da co anh (co the Tuan dang duyet) -> them --force de tao lai")
    a.out.mkdir(parents=True, exist_ok=True)
    det = cv2.FaceDetectorYN.create(str(MODELS / "face_detection_yunet_2023mar.onnx"), "", (320, 320), 0.7)
    opts = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODELS / "face_landmarker.task")),
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        output_face_blendshapes=True,
    )
    t0 = time.time()
    photos = []
    with vision.FaceLandmarker.create_from_options(opts) as lmk:
        for i, f in enumerate(files, 1):
            photos.append(analyse(f, det, lmk, a.edge, a.min_face))
            if i % 50 == 0:
                print(f"{i}/{len(files)} anh, {time.time() - t0:.0f} s", flush=True)
    classify(photos, a)
    mark_bursts(photos, a)

    with open(a.out / "bao-cao.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "nhom", "ly_do", "so_mat", "loat", "mat_chinh: do_net / nham_trai / nham_phai"])
        for p in photos:
            faces = " | ".join(f"{f.sharp:.0f}/{f.blink_l}/{f.blink_r}" for f in p.faces if f.main)
            w.writerow([p.file, p.group, "; ".join(p.reasons), len(p.faces), p.burst, faces])
    (a.out / "bao-cao.json").write_text(
        json.dumps([asdict(p) for p in photos], ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for g in GROUPS:
        members = [p for p in photos if p.group == g]
        folder = a.out / g
        if folder.is_dir():
            for old in folder.iterdir():
                if old.suffix.lower() in EXTS:
                    old.unlink()
        folder.mkdir(exist_ok=True)
        for p in members:
            preview(a.src / p.file, folder / (Path(p.file).stem + ".jpg"))
        if not a.no_sheet:
            sheet(a.src, members, a.out / f"tong-quan-{g}.jpg", a.edge)
        print(f"{g:10s} {len(members):4d}")
    print(f"Xong {len(photos)} anh trong {time.time() - t0:.0f} s -> {a.out}")


if __name__ == "__main__":
    main()
