import numpy as np


def render_iso(tri, size_px=360):
    """Render a triangle mesh from an isometric view using a software z-buffer."""
    tri = np.asarray(tri, dtype=np.float64)
    if tri.ndim != 3 or tri.shape[1:] != (3, 3):
        raise ValueError("tri must have shape (n, 3, 3)")
    size_px = int(size_px)
    if size_px < 1:
        raise ValueError("size_px must be positive")
    image = np.full((size_px, size_px, 3), 255, dtype=np.uint8)
    if len(tri) == 0:
        return image

    az, el = np.deg2rad(-60.0), np.deg2rad(30.0)
    view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    right = np.array([-np.sin(az), np.cos(az), 0.0])
    up = np.cross(view, right)
    center = (tri.min(axis=(0, 1)) + tri.max(axis=(0, 1))) * 0.5
    centered = tri - center
    px, py, pz = centered @ right, centered @ up, centered @ view
    extent = max(float(np.ptp(px)), float(np.ptp(py)))
    scale = (0.85 * max(0, size_px - 1)) / extent if extent > 0 else 1.0
    sx = px * scale + (size_px - 1) * 0.5
    sy = (size_px - 1) * 0.5 - py * scale

    zbuf = np.full((size_px, size_px), -np.inf, dtype=np.float64)
    light = np.array([0.35, -0.45, 0.82], dtype=np.float64)
    light /= np.linalg.norm(light)
    base = np.array([0.30, 0.58, 0.78])
    for i in range(len(tri)):
        x, y = sx[i], sy[i]
        x0, x1 = max(0, int(np.ceil(x.min() - 0.5))), min(size_px - 1, int(np.floor(x.max() - 0.5)))
        y0, y1 = max(0, int(np.ceil(y.min() - 0.5))), min(size_px - 1, int(np.floor(y.max() - 0.5)))
        a, b, c = np.array([x[0], y[0]]), np.array([x[1], y[1]]), np.array([x[2], y[2]])
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        cr = np.cross(tri[i, 1] - tri[i, 0], tri[i, 2] - tri[i, 0])
        norm = np.linalg.norm(cr)
        if norm <= 1e-15:
            continue
        shade = np.clip(0.35 + 0.65 * abs(float((cr / norm) @ light)), 0.25, 1.0)
        color = np.rint(base * shade * 255).astype(np.uint8)
        painted = False
        if x0 <= x1 and y0 <= y1 and abs(den) > 1e-14 and (x1 - x0 + 1) * (y1 - y0 + 1) > 1:
            xs, ys = np.arange(x0, x1 + 1, dtype=np.float64) + 0.5, np.arange(y0, y1 + 1, dtype=np.float64) + 0.5
            xx, yy = np.meshgrid(xs, ys)
            w0 = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / den
            w1 = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / den
            w2 = 1.0 - w0 - w1
            inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
            if inside.any():
                depth = w0 * pz[i, 0] + w1 * pz[i, 1] + w2 * pz[i, 2]
                region = zbuf[y0:y1 + 1, x0:x1 + 1]
                mask = inside & (depth > region)
                region[mask] = depth[mask]
                image[y0:y1 + 1, x0:x1 + 1][mask] = color
                painted = True
        if not painted:
            ix, iy = int(np.floor(x.mean())), int(np.floor(y.mean()))
            if 0 <= ix < size_px and 0 <= iy < size_px:
                depth = float(pz[i].mean())
                if depth > zbuf[iy, ix]:
                    zbuf[iy, ix] = depth
                    image[iy, ix] = color
    return image
