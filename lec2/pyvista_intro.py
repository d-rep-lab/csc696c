from __future__ import annotations

import numpy as np
import pyvista as pv

TARGET_WIDTH_MM = 60.0


def make_square_xy() -> np.ndarray:
    # Simple outline points (Nx2). Intentionally NOT closed.
    return np.array(
        [
            [0.0, 0.0],
            [20.0, 0.0],
            [20.0, 20.0],
            [0.0, 20.0],
        ],
        dtype=float,
    )


def convert_2d_to_3d(pts_xy: np.ndarray) -> np.ndarray:
    # Convert Nx2 to Nx3 by adding a flat z = 0 layer
    pts_xy = np.asarray(pts_xy, dtype=float)
    if pts_xy.ndim != 2 or pts_xy.shape[1] != 2:
        raise ValueError("Expected Nx2 array.")
    return np.c_[pts_xy[:, 0], pts_xy[:, 1], np.zeros(len(pts_xy))]


def ensure_closed(pts_xyz: np.ndarray, tol: float = 1e-6) -> np.ndarray:
    # Ensure the polyline is closed by appending the first point (if needed)

    pts = np.asarray(pts_xyz, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 3:
        raise ValueError("Expected Nx3 array.")

    d = np.linalg.norm(pts[0, :2] - pts[-1, :2])
    if d <= tol:
        pts[-1] = pts[0]  # snap -- to make sure it's exact
        return pts
    return np.vstack([pts, pts[0]])


def resize_outline(poly: pv.PolyData, target_width_mm: float) -> pv.PolyData:
    # Rescale the outline to match a specific width in mm
    xmin, xmax, ymin, ymax, zmin, zmax = poly.bounds
    w = xmax - xmin
    if w <= 0:
        raise ValueError("Invalid geometry: width must be positive.")

    cx = (xmin + xmax) / 2.0
    cy = (ymin + ymax) / 2.0
    s = target_width_mm / w

    out = poly.copy(deep=True)
    out.points[:, 0] = (out.points[:, 0] - cx) * s
    out.points[:, 1] = (out.points[:, 1] - cy) * s
    # Z is untouched, assuming it's already flat
    return out


def main():
    pts_xy = make_square_xy()
    pts_xyz = convert_2d_to_3d(pts_xy)
    pts_xyz = ensure_closed(pts_xyz)

    poly = pv.lines_from_points(pts_xyz, close=False)
    print("n_points:", poly.n_points, "n_cells:", poly.n_cells)
    print("bounds:", poly.bounds)

    poly_scaled = resize_outline(poly, TARGET_WIDTH_MM)
    print("scaled bounds:", poly_scaled.bounds)

    p = pv.Plotter(title="PyVista Intro")
    p.add_mesh(poly_scaled, color="navy", line_width=6, label="Scaled Outline")
    p.add_legend()
    p.show()


if __name__ == "__main__":
    main()
