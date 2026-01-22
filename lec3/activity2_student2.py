from __future__ import annotations

"""
Activity 2 

Prereq from Acitivty 1:
- You already generated and saved an outline as:
  outputs/outline_<name>_px.npy
-If you didn't, use the provided contour file /output/outline_square_mm.npy

What you will implement:
  - TODO 1: smooth_polyline_xy (closed loop smoothing)
  - TODO 2: resample_closed_polyline_xy (uniform arc-length resampling)
  - TODO 3: pixels_to_mm (rough conversion; final scaling is enforced later)
  - TODO 4: Convery Nx2 => Nx3


Helper functions:
- pv_svg_utils.py (do-not-edit)
"""

import os
import numpy as np
import pyvista as pv

from pv_svg_utils import (
    polyline_from_points,
    recenter_and_scale_to_width,
    export_single_closed_loop_to_svg,
    SvgExportOptions,
)

# -----------------------------
# SETTINGS
# -----------------------------
OUTLINE_NPY = os.path.join(
    "inputs", "outline_square_px.npy"
)  # use the output from Activity 1 (.npy) otherwise use the provided .npy
OUT_DIR = "outputs"

TARGET_WIDTH_MM = 60.0
EXPORT_UNITS = "px"
N_RESAMPLE = 400  # number of points on the exported outline
SMOOTH_PASSES = 2  # small smoothing; low to preserve shape
PX_PER_MM_GUESS = 10.0  # rough guess; final scaling is enforced later anyway


# -----------------------------
# TODO FUNCTIONS
# -----------------------------
def smooth_polyline_xy(xy: np.ndarray, passes: int = 1) -> np.ndarray:
    """
    TODO 1: Closed-loop smoothing

    Hint:
    - Use local neighbors (each point and its neighbors) to help you find the average
    - Treat the polyline as a loop (neighbors wrap around).
    - For each pass, move each point slightly toward its neighbors.
    - np.roll can help access previous/next points.

    Helpful debug prints:
    - print("shape:", xy.shape, "dtype:", xy.dtype)
    - print("bbox before:", xy.min(axis=0), xy.max(axis=0))
    - print("bbox after :", out.min(axis=0), out.max(axis=0))

    Return: Nx2 array
    """

    raise NotImplementedError("TODO 1: implement smooth_polyline_xy()")


def resample_closed_polyline_xy(xy: np.ndarray, n: int) -> np.ndarray:
    """
    TODO 2:
    Resample a CLOSED polyline to exactly n points (uniform in arc-length)

    Hints:
    -Ensure closure: last point equals first point. [Done for you]
    -Compute cumulative distance s along the loop (arc-length parameterization).
    -Choose n equally spaced s-values.
    -Interpolate x(s), y(s) at those s-values.

    Requirements (important for fabrication):
    - Output MUST be shape (n, 2)
    - Do NOT repeat the first point at the end (no duplicate endpoint)

    Helpful Debug prints:
    - print("N_in:", len(xy), "N_out:", len(out))
    - print("total length:", total)
    - After resampling: report step length stats (min/mean/max)
        (if max is way larger than mean, your sampling isn't uniform)

    Return: Nx2 array with exactly n points (do NOT repeat the first point at the end)
    """
    xy = np.asarray(xy, dtype=float)

    # Ensure closures in xy for resampling
    xy_closed = ensure_closed_xy(xy)  # shape (m+1, 2)

    # TODO implement steps 2-4

    raise NotImplementedError("TODO 2: implement resample_closed_polyline_xy()")


def pixels_to_mm(xy_px: np.ndarray, px_per_mm_guess: float = 10.0) -> np.ndarray:
    """
    TODO 3: Convert pixel coordinates => mm-ish coordinates and flip y for CAD-style coordinates.

    Why flip y?
        - Image coordinates usually have +y going DOWN, but geometry/CAD is the opposite (i.e., +y going UP).

    Hints:
    - output is float
    -to scale: divide by px_per_mm_guess
    - to flip: y *= -1

    Debug/visual check:
    - If your exported outline looks upside-down in the plot/SVG (e.g., Illustrator/Carbide Create), your y-direction is wrong.

    """

    # return Nx2 array

    raise NotImplementedError("TODO 3: implement pixels_to_mm()")


def convert_to_xyz(xy: np.ndarray) -> np.ndarray:
    """
    TODO 4: Convert Nx2 -> Nx3 by adding a z=0 column for PyVista.
    PyVista expects [x,y, z]. Contour is currently 2D [x,y]

    Hint:
      - x = xy[:, 0]
      - y = xy[:, 1]
      - z = np.zeros(N)
      - Combine into (N,3) using np.c_ or np.column_stack
    """
    raise NotImplementedError("TODO 4: implement convert_to_xyz()")


# -----------------------------
# Helper Function
# -----------------------------
def ensure_closed_xy(xy: np.ndarray) -> np.ndarray:
    # ensure closure in xy for resampling
    xy = np.asarray(xy, dtype=float)

    if len(xy) < 3:
        raise ValueError("Need at least 3 points.")

    if np.linalg.norm(xy[0] - xy[-1]) <= 1e-9:
        xy = xy.copy()
        xy[-1] = xy[0]
        return xy

    return np.vstack([xy, xy[0]])


def main():
    contour_xy_px = np.load(OUTLINE_NPY)  # Nx2 in (x,y) pixel coords
    if contour_xy_px.ndim != 2 or contour_xy_px.shape[1] != 2:
        raise ValueError("Expected Nx2 contour in pixel coords.")

    # -----------------------------
    # PIPELINE
    # -----------------------------

    # Will fail at TODO 1 by design

    # TODO 1: Smooth the contour (closed-loop smoothing)
    contour_xy = smooth_polyline_xy(contour_xy_px, passes=SMOOTH_PASSES)

    # TODO 2: Resample to N_RESAMPLE points
    contour_xy = resample_closed_polyline_xy(contour_xy, n=N_RESAMPLE)

    # TODO 3: Convert pixels -> mm-ish coords (and flip y)
    contour_xy_mm = pixels_to_mm(contour_xy, px_per_mm_guess=PX_PER_MM_GUESS)

    # TODO 4: Convert Nx2 -> Nx3 for PyVista
    pts_xyz = convert_to_xyz(contour_xy_mm)

    # Build a closed polyline in PyVista (snaps/appends closure for CAM)
    outline = polyline_from_points(pts_xyz, close=True, tol=1e-3)

    # Scale + recenter so final width is exactly TARGET_WIDTH_MM
    outline = recenter_and_scale_to_width(outline, TARGET_WIDTH_MM)

    # Hard assert closure before export (sanity check)
    pts = outline.points
    if np.linalg.norm(pts[0, :2] - pts[-1, :2]) > 1e-3:
        raise ValueError("Outline is not closed after processing (should not happen).")

    # -----------------------------
    # EXPORT
    # -----------------------------
    os.makedirs(OUT_DIR, exist_ok=True)

    name = (
        os.path.splitext(os.path.basename(OUTLINE_NPY))[0]
        .replace("outline_", "")
        .replace("_px", "")
    )
    svg_path = os.path.join(OUT_DIR, f"outline_{name}.svg")
    opts = SvgExportOptions(export_units=EXPORT_UNITS, stroke_width=0.2, margin_mm=3.0)
    export_single_closed_loop_to_svg(outline, svg_path, opts)

    print("wrote:", svg_path)

    p = pv.Plotter(title=f"Activity 2")
    p.add_mesh(outline, color="navy", line_width=5, label="outline (closed)")
    p.add_legend()
    p.show()


if __name__ == "__main__":
    main()
