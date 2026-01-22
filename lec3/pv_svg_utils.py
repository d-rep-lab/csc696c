from __future__ import annotations

"""PyVista -> SVG utilities 

- Internal coordinates are in mm.
- SVG export can be in px (96 PPI) or mm.

- Export CLOSED loops as <path ... Z> so Carbide Create (CNC Machine) treats them as closed vectors.
- Open geometry remains exported as <polyline>.
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pyvista as pv

MM_PER_INCH = 25.4
PX_PER_INCH = 96.0
PX_PER_MM = PX_PER_INCH / MM_PER_INCH  # ~3.7795


@dataclass
class SvgExportOptions:
    export_units: str = "px"  # "px" or "mm"
    stroke_width: float = 0.2
    margin_mm: float = 2.0


def _as_xyz(points: np.ndarray) -> np.ndarray:
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] not in (2, 3):
        raise ValueError("points must be Nx2 or Nx3")
    if pts.shape[1] == 2:
        pts = np.c_[pts[:, 0], pts[:, 1], np.zeros(len(pts))]
    return pts


def polyline_from_points(
    points_xyz: np.ndarray, close: bool = True, tol: float = 1e-3
) -> pv.PolyData:
    """
    Build a PyVista polyline from points and ensure numeric closure for CAM.

    tol is in mm. We "snap" the last point to the first if already close enough,
    otherwise we append the first point.
    """
    pts = _as_xyz(points_xyz)

    if close:
        d = np.linalg.norm(pts[0, :2] - pts[-1, :2])
        if d <= tol:
            pts[-1] = pts[0]  # snap closed
        else:
            pts = np.vstack([pts, pts[0]])  # append closure

    return pv.lines_from_points(pts, close=False)


def bounds_xy(poly: pv.PolyData) -> Tuple[float, float, float, float]:
    xmin, xmax, ymin, ymax, *_ = poly.bounds
    return xmin, xmax, ymin, ymax


def recenter_and_scale_to_width(
    poly: pv.PolyData, target_width_mm: float
) -> pv.PolyData:
    xmin, xmax, ymin, ymax = bounds_xy(poly)
    w = xmax - xmin
    if w <= 0:
        raise ValueError("Non-positive width")
    cx, cy = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0

    out = poly.copy(deep=True)
    out.points[:, 0] -= cx
    out.points[:, 1] -= cy
    s = target_width_mm / w
    out.points *= s
    return out


def edges_from_tube_slice(
    line: pv.PolyData, radius_mm: float, n_sides: int = 96, z0: float = 0.0
) -> pv.PolyData:
    """
    Offset helper: tube(radius) -> slice -> boundary edges.
    Robust fallback: if edges are empty but sliced has line cells, return sliced.
    """
    tube = line.tube(radius=radius_mm, n_sides=n_sides)
    sliced = tube.slice(normal=(0, 0, 1), origin=(0, 0, z0))

    edges = sliced.extract_feature_edges(
        boundary_edges=True,
        feature_edges=False,
        manifold_edges=False,
        non_manifold_edges=False,
    )

    if edges.n_cells == 0 and sliced.n_cells > 0:
        return sliced
    return edges


def rect_polyline(
    w_mm: float, h_mm: float, cx_mm: float = 0.0, cy_mm: float = 0.0
) -> pv.PolyData:
    hw, hh = w_mm / 2.0, h_mm / 2.0
    pts = np.array(
        [
            [cx_mm - hw, cy_mm - hh, 0.0],
            [cx_mm + hw, cy_mm - hh, 0.0],
            [cx_mm + hw, cy_mm + hh, 0.0],
            [cx_mm - hw, cy_mm + hh, 0.0],
            [cx_mm - hw, cy_mm - hh, 0.0],
        ],
        dtype=float,
    )
    return polyline_from_points(pts, close=True)


def circle_polyline(
    r_mm: float, cx_mm: float, cy_mm: float, n: int = 128
) -> pv.PolyData:
    t = np.linspace(0, 2 * np.pi, n, endpoint=True)
    pts = np.c_[cx_mm + r_mm * np.cos(t), cy_mm + r_mm * np.sin(t), np.zeros_like(t)]
    return polyline_from_points(pts, close=True)


def _mm_to_units(
    x_mm: float, y_mm: float, opts: SvgExportOptions
) -> Tuple[float, float]:
    if opts.export_units == "mm":
        return x_mm, y_mm
    return x_mm * PX_PER_MM, y_mm * PX_PER_MM


def export_single_closed_loop_to_svg(
    poly: pv.PolyData, filename: str, opts: SvgExportOptions = SvgExportOptions()
) -> None:
    """
    Export ONE closed loop as a single <path ... Z> regardless of cell structure.
    Avoids Carbide Create complaining about any open vectors in the file.
    """
    if poly.n_points < 3:
        raise ValueError("Need at least 3 points for a closed loop.")

    # Use point order directly
    pts = poly.points.copy()

    # Snap-close numerically (mm)
    if np.linalg.norm(pts[0, :2] - pts[-1, :2]) <= 1e-3:
        pts[-1] = pts[0]
    else:
        pts = np.vstack([pts, pts[0]])

    # Compute bounds from points (not cells)
    xmin, xmax = float(pts[:, 0].min()), float(pts[:, 0].max())
    ymin, ymax = float(pts[:, 1].min()), float(pts[:, 1].max())

    xmin -= opts.margin_mm
    xmax += opts.margin_mm
    ymin -= opts.margin_mm
    ymax += opts.margin_mm

    x0, y0 = _mm_to_units(xmin, ymin, opts)
    x1, y1 = _mm_to_units(xmax, ymax, opts)
    w = x1 - x0
    h = y1 - y0

    def xy_to_svg(x_mm: float, y_mm: float) -> Tuple[float, float]:
        x_u, y_u = _mm_to_units(x_mm, y_mm, opts)
        sx = x_u - x0
        sy = y1 - y_u  # flip y
        return sx, sy

    coords = [xy_to_svg(p[0], p[1]) for p in pts]

    # Drop duplicate last point before writing path (Z will close)
    if len(coords) > 2:
        xF, yF = coords[0]
        xL, yL = coords[-1]
        if abs(xF - xL) < 1e-6 and abs(yF - yL) < 1e-6:
            coords = coords[:-1]

    d = "M " + " ".join([f"{x:.3f} {y:.3f}" for x, y in coords]) + " Z"
    units = "mm" if opts.export_units == "mm" else "px"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="{w:.3f}{units}" height="{h:.3f}{units}" viewBox="0 0 {w:.3f} {h:.3f}">
  <path d="{d}" fill="none" stroke="black" stroke-width="{opts.stroke_width}"/>
</svg>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg)
