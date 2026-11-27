"""meshhash.py - ma bam HINH HOC chuan hoa cua STL (2026-11-28, toi uu chuoi CAD).
Boolean Blender (MANIFOLD) moi lan dung lai cho cung hinh nhung THU TU tam giac khac -> md5 byte doi -> cache khong bao gio trung.
canon_hash(): lam tron dinh 1e-3 mm, sap dinh trong tam giac + sap danh sach tam giac -> cung hinh = cung ma (bo qua huong mat).
    python meshhash.py a.stl [b.stl ...]
"""
import hashlib
import sys
from pathlib import Path

import numpy as np

_DT = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])


def load_tris(path):
    b = open(path, "rb").read()
    n = int.from_bytes(b[80:84], "little") if len(b) >= 84 else 0
    if len(b) == 84 + 50 * n:
        return np.frombuffer(b, dtype=_DT, count=n, offset=84)["v"].astype(np.float64)
    v = [list(map(float, ln.split()[1:4])) for ln in b.decode("ascii", "replace").splitlines() if ln.strip().startswith("vertex")]
    return np.array(v, dtype=np.float64).reshape(-1, 3, 3)


def canon_hash(path, q=1e-3):
    t = load_tris(path)
    if not len(t):
        return "empty"
    k = np.round(t / q).astype(np.int64) + (1 << 20)            # +-1 m o buoc 1e-3 -> 21 bit/truc
    key = (k[:, :, 0] << 42) | (k[:, :, 1] << 21) | k[:, :, 2]   # 1 so nguyen / dinh
    key = np.sort(key, axis=1)
    key = key[np.lexsort((key[:, 2], key[:, 1], key[:, 0]))]
    return hashlib.md5(key.tobytes()).hexdigest()


def _canon_array(t, q):
    k = np.round(t / q).astype(np.int64) + (1 << 20)
    key = (k[:, :, 0] << 42) | (k[:, :, 1] << 21) | k[:, :, 2]
    o = np.argsort(key, axis=1)
    ts = np.take_along_axis(t, o[:, :, None], axis=1)
    ks = np.take_along_axis(key, o, axis=1)
    return ts[np.lexsort((ks[:, 2], ks[:, 1], ks[:, 0]))]


def signature(path):
    """Chu ky hinh hoc KHONG phu thuoc cach chia tam giac: dien tich, the tich, mo-men mat bac 1 (3) + bac 2 (6), hop bao (6).
    Do 2026-11-28: boolean MANIFOLD dung lai cung hinh doi so tam giac (+-4) va thu tu, chu ky chi lech ~1e-11 tuong doi."""
    t = load_tris(path)
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    ar = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    ce = (a + b + c) / 3
    vol = np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6
    m1 = (ar[:, None] * ce).sum(0)
    m2 = (ar[:, None, None] * ce[:, :, None] * ce[:, None, :]).sum(0)[np.triu_indices(3)]
    p = t.reshape(-1, 3)
    return [float(x) for x in np.r_[ar.sum(), vol, m1, m2, p.min(0), p.max(0)]]


def sig_equal(s1, s2, rtol=1e-8):
    """Nguong 1e-8: nhieu dung lai ~1e-11; doi that (doi lo 0,01 mm) ~1e-6 tro len."""
    if s1 is None or s2 is None or len(s1) != len(s2):
        return False
    a, b = np.asarray(s1), np.asarray(s2)
    return bool(np.all(np.abs(a - b) <= rtol * np.maximum(np.abs(a), 1.0)))


def same_geom(a, b):
    """2 STL cung hinh (theo chu ky, bo qua cach chia tam giac)? File thieu -> False."""
    if not (Path(a).exists() and Path(b).exists()):
        return False
    return sig_equal(signature(a), signature(b))


def hash_many(paths, extra=""):
    h = hashlib.md5(extra.encode("utf-8"))
    for p in sorted(map(str, paths)):
        h.update(p.replace("\\", "/").rsplit("/", 1)[-1].encode()); h.update(canon_hash(p).encode())
    return h.hexdigest()


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(canon_hash(p), p)
