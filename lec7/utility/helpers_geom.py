import numpy as np
import math
from typing import Tuple, List


def ensure_closed(poly_xy: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    poly_xy = np.asarray(poly_xy, dtype=float)
    if poly_xy.ndim != 2 or poly_xy.shape[1] != 2:
        raise ValueError("poly_xy must be (N,2)")
    if len(poly_xy) < 3:
        raise ValueError("Need >= 3 vertices")
    if np.linalg.norm(poly_xy[0] - poly_xy[-1]) <= eps:
        return poly_xy.copy()
    return np.vstack([poly_xy, poly_xy[0]])


def bbox_xy(poly_xy: np.ndarray) -> Tuple[float, float, float, float]:
    p = np.asarray(poly_xy, dtype=float)
    return (
        float(p[:, 0].min()),
        float(p[:, 0].max()),
        float(p[:, 1].min()),
        float(p[:, 1].max()),
    )


def poly_centroid(poly_xy: np.ndarray) -> Tuple[float, float]:
    p = np.asarray(poly_xy, dtype=float)
    return float(p[:, 0].mean()), float(p[:, 1].mean())


def scale_polygon(poly_xy: np.ndarray, scale: float) -> np.ndarray:
    p = ensure_closed(poly_xy)[:-1]
    c = np.array(poly_centroid(p), dtype=float)  # center (cx,cy)
    q = c + scale * (p - c)  # scale from center
    return ensure_closed(q)


def make_rectangle(cx: float, cy: float, w: float, h: float) -> np.ndarray:
    """
    Makes a rectangle of width w and height h centered at (cx, cy)
    """
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = cy - h / 2.0, cy + h / 2.0
    pts = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=float)
    return pts


def make_concave(cx: float, cy: float, s: float = 10.0) -> np.ndarray:
    pts = np.array(
        [
            [cx - 2 * s, cy - 2 * s],
            [cx + 0 * s, cy - 2 * s],
            [cx + 0 * s, cy - 1 * s],
            [cx + 2 * s, cy + 0 * s],
            [cx + 0 * s, cy + 1 * s],
            [cx + 0 * s, cy + 2 * s],
            [cx - 2 * s, cy + 2 * s],
            [cx - 1 * s, cy + 0 * s],
        ],
        dtype=float,
    )
    return ensure_closed(pts)


def segments_to_serpentine(rows: List[List[np.ndarray]]) -> np.ndarray:
    pts: List[np.ndarray] = []
    for row_idx, row in enumerate(rows):
        if not row:
            continue

        row_sorted = sorted(row, key=lambda s: float(min(s[0, 0], s[1, 0])))
        row_pts: List[np.ndarray] = []

        if row_idx % 2 == 0:
            for s in row_sorted:
                a, b = s[0], s[1]
                row_pts.extend([a, b] if a[0] <= b[0] else [b, a])
        else:
            for s in reversed(row_sorted):
                a, b = s[0], s[1]
                row_pts.extend([a, b] if a[0] >= b[0] else [b, a])

        if not pts:
            pts.extend([np.array(p, dtype=float) for p in row_pts])
        else:
            prev = pts[-1]
            nxt = np.array(row_pts[0], dtype=float)
            if float(((prev - nxt) ** 2).sum()) > 1e-12:
                pts.append(nxt)
            for p in row_pts[1:]:
                pts.append(np.array(p, dtype=float))

    return np.vstack(pts)


def build_serpentine_infill(
    perimeter_xy: np.ndarray,
    spacing: float,
    offset_scale: float,
    min_seg_len: float,
    scanline_intersections,
    even_odd_segments,
) -> Tuple[np.ndarray, List[float], np.ndarray]:
    """Return (offset_polygon, scan_ys, serpentine_path_xy)."""

    offset = scale_polygon(perimeter_xy, offset_scale)
    xmin, xmax, ymin, ymax = bbox_xy(offset)

    rows: List[List[np.ndarray]] = []
    scan_ys: List[float] = []

    y = ymin + 0.5 * spacing
    while y <= ymax - 0.25 * spacing:
        xs = scanline_intersections(offset, y)
        rows.append(even_odd_segments(xs, y, min_seg_len=min_seg_len))
        scan_ys.append(float(y))
        y += spacing

    return offset, scan_ys, segments_to_serpentine(rows)
