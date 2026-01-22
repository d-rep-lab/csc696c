from __future__ import annotations

"""
Assignment 2: Image -> Contour -> Millable SVG

Goal:
1) Load a black-shape-on-white image.
2) Binarize to a silhouette mask.
3) Extract the largest contour as Nx2 points in (x,y) pixel coords.
4) Clean it (smooth + resample), convert to mm-ish coordinates, flip y.
5) Export a CLOSED SVG outline that can be milled.

You will implement:
  - TODO 1: binarize_silhouette(img) -> mask (bool)
  - TODO 2: extract_largest_contour(mask) -> contour_xy_px (Nx2, x=col, y=row)
  - TODO 3: smooth_polyline_xy(xy, passes)
  - TODO 4: resample_closed_polyline_xy(xy, n)
  - TODO 5: pixels_to_mm(xy_px, px_per_mm_guess)
  - TODO 6: convert_to_xyz(xy)

! Note: you're not being graded on using specific NumPy operations
You will be graded on meeting the specs and passing sanity checks. Look at the print statements.

Provided helper functions(do-not-edit):
  - pv_svg_utils.py: 
"""

import os
import numpy as np
import pyvista as pv

from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.measure import find_contours

from pv_svg_utils import (
    polyline_from_points,
    recenter_and_scale_to_width,
    export_single_closed_loop_to_svg,
    SvgExportOptions,
)

# -----------------------------
# SETTINGS
# -----------------------------
INPUT_PATH = os.path.join("input", "bird.jpeg")
OUT_DIR = "outputs"

TARGET_WIDTH_MM = 60.0
EXPORT_UNITS = "px"

N_RESAMPLE = 400
SMOOTH_PASSES = 2
PX_PER_MM_GUESS = 10.0


# -----------------------------
# PART 1: IMAGE -> CONTOUR
# -----------------------------
def load_grayscale(path: str) -> np.ndarray:
    img = imread(path)
    if img.ndim == 3:
        img = img[..., :3].astype(float)
        img = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]
    return img.astype(float)


# Activity 1
def binarize_silhouette(img: np.ndarray) -> np.ndarray:

    raise NotImplementedError("TODO A: implement binarize_silhouette()")


# Activity 1
def extract_largest_contour(mask: np.ndarray) -> np.ndarray:

    raise NotImplementedError("TODO B: implement extract_largest_contour()")


def contour_to_pv_polyline_xy(contour_xy: np.ndarray, h_px: int) -> pv.PolyData:
    # Convert Nx2 contour into pixel coords to a PyVista polyline for visual overlay.
    # Flip Y so it overlays correctly on a texture plane.
    xy = np.asarray(contour_xy, float).copy()
    xy[:, 1] = (h_px - 1) - xy[:, 1]
    pts = np.c_[xy[:, 0], xy[:, 1], np.zeros(len(xy))]
    return pv.lines_from_points(pts, close=False)


def image_to_texture(img_gray: np.ndarray) -> pv.Texture:
    # Make a PyVista texture from a grayscale image.
    # Needed for purely visual debugging
    g = img_gray.copy()
    g = g - g.min()
    if g.max() > 0:
        g = g / g.max()
    g8 = (255 * g).astype(np.uint8)
    rgb = np.stack([g8, g8, g8], axis=-1)
    return pv.Texture(rgb)


# -----------------------------
# PART 2: CONTOUR -> SVG
# -----------------------------
def ensure_closed_xy(xy: np.ndarray) -> np.ndarray:
    xy = np.asarray(xy, dtype=float)
    if len(xy) < 3:
        raise ValueError("Need at least 3 points.")
    if np.linalg.norm(xy[0] - xy[-1]) <= 1e-9:
        out = xy.copy()
        out[-1] = out[0]
        return out
    return np.vstack([xy, xy[0]])


# Activity 2
def smooth_polyline_xy(xy: np.ndarray, passes: int = 1) -> np.ndarray:

    raise NotImplementedError("TODO C: implement smooth_polyline_xy()")


# Activity 2
def resample_closed_polyline_xy(xy: np.ndarray, n: int) -> np.ndarray:

    raise NotImplementedError("TODO D: implement resample_closed_polyline_xy()")


# Activity 2
def pixels_to_mm(
    xy_px: np.ndarray, px_per_mm_guess: float = PX_PER_MM_GUESS
) -> np.ndarray:

    raise NotImplementedError("TODO E: implement pixels_to_mm()")


# Activity 2
def convert_to_xyz(xy: np.ndarray) -> np.ndarray:

    raise NotImplementedError("TODO F: implement convert_to_xyz()")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # -------- Part 1: image -> contour --------
    img = load_grayscale(INPUT_PATH)
    h, w = img.shape[:2]

    mask = binarize_silhouette(img)  # TODO A
    print(f"TODO 1: MASK_MEAN: {float(np.mean(mask)):.6f}")

    contour_xy_px = extract_largest_contour(mask)  # TODO B
    if contour_xy_px.ndim != 2 or contour_xy_px.shape[1] != 2:
        raise ValueError("extract_largest_contour must return Nx2.")
    print(f"TODO 2: CONTOUR_NUM_POINTS: {int(len(contour_xy_px))}")

    stem = os.path.splitext(os.path.basename(INPUT_PATH))[0]
    out_npy = os.path.join(OUT_DIR, f"outline_{stem}_px.npy")
    np.save(out_npy, contour_xy_px)
    print("Activity 1 Saved contour:", out_npy)

    # Visual output for Part 1
    texture = image_to_texture(img)
    plane = pv.Plane(
        center=(w / 2, h / 2, 0), i_size=w, j_size=h, i_resolution=1, j_resolution=1
    )
    contour_poly = contour_to_pv_polyline_xy(contour_xy_px, h_px=h)

    p = pv.Plotter(title="Assignment 2: Part 1 (Contour)")
    p.add_mesh(plane, texture=texture)
    p.add_mesh(contour_poly, color="orange", line_width=4, label="largest contour")
    p.add_legend()
    p.show()

    # -------- Part 2: contour -> svg --------
    contour_xy = smooth_polyline_xy(contour_xy_px, passes=SMOOTH_PASSES)  # TODO C
    contour_xy = resample_closed_polyline_xy(contour_xy, n=N_RESAMPLE)  # TODO D
    contour_xy_mm = pixels_to_mm(contour_xy, px_per_mm_guess=PX_PER_MM_GUESS)  # TODO E

    pts_xyz = convert_to_xyz(contour_xy_mm)  # TODO F

    outline = polyline_from_points(pts_xyz, close=True, tol=1e-3)
    outline = recenter_and_scale_to_width(outline, TARGET_WIDTH_MM)

    # Export SVG
    svg_path = os.path.join(OUT_DIR, f"outline_{stem}.svg")
    opts = SvgExportOptions(export_units=EXPORT_UNITS, stroke_width=0.2, margin_mm=3.0)
    export_single_closed_loop_to_svg(outline, svg_path, opts)
    print(f"Activity 2 SVG Output: {svg_path}")

    # Visual output for Part 2
    p2 = pv.Plotter(title="Assignment 2: Part 2 (SVG)")
    p2.add_mesh(outline, color="navy", line_width=5, label="outline (closed)")
    p2.add_legend()
    p2.show()


if __name__ == "__main__":
    main()
