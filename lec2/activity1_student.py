from __future__ import annotations

"""
Activity 1 (Student Template)

-Convert the given image to a binary silhouette, 
-Extract the outline as an ordered list of points
-Use PyVista to visualize/debug it before converting it into a manufacturable SVG later.

You will implement:
  - TODO 1: binarize_silhouette(img)  -> mask (bool)
  - TODO 2: extract_largest_contour(mask) -> contour_xy in (x,y) pixel coords
  
"""

import os
import numpy as np
import pyvista as pv

from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.measure import find_contours


# -----------------------------
# SETTINGS
# -----------------------------
INPUT_PATH = os.path.join("inputs", "square.png")  # switch to bird.png later


def load_grayscale(path: str) -> np.ndarray:
    # Load image into grayscale float array
    img = imread(path)
    if img.ndim == 3:
        img = img[..., :3].astype(float)
        img = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]
    return img.astype(float)


def binarize_silhouette(img: np.ndarray) -> np.ndarray:
    """
    TODO 1:
    Return a boolean mask where the silhouette region is True.

    Assumption: black shape on white background.

    REQUIRED TO DEBUG PRINTS:
      - img.min(), img.max()
      - otsu threshold
      - mask.mean()  (fraction of True pixels)

    Hint: Understand the return value of threshold_otsu
    """
    thr = threshold_otsu(
        img
    )  # https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_otsu

    # TODO 1A: Implement robust mask rule.
    # if thr ....
    # mask = ...
    # else
    # mask = ...

    raise NotImplementedError("TODO 1A: implement binarize_silhouette()")

    # print("img min/max:", float(img.min()), float(img.max()))
    # print("otsu thr:", float(thr))
    # print("mask.mean:", float(mask.mean()))
    # return mask


def extract_largest_contour(mask: np.ndarray) -> np.ndarray:
    """
    TODO 2:
    Use skimage.find_contours to extract all contours, then choose the largest (longest) one.

    find_contours returns arrays of shape (N,2) in (row, col).
    Return Nx2 in (x, y) pixel coordinates:
      x = col
      y = row

    REQUIRED TO DEBUG PRINTS:
      - number of contours found
      - length (N) of the chosen contour

    Hint: Longest contour is usually the outer boundary
    """
    contours = find_contours(
        mask.astype(float), level=0.5
    )  # https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.find_contours

    # TODO 2A: if no contours, raise ValueError("No contours found ...")
    # TODO 2B: choose longest contour
    # TODO 2C: convert (row,col)->(x,y)

    raise NotImplementedError("TODO 2A–2C: implement extract_largest_contour()")


def contour_to_pv_polyline_xy(contour_xy: np.ndarray, h_px: int) -> pv.PolyData:
    # Convert Nx2 contour into pixel coords to a PyVista polyline for visual overlay.
    # Flip Y so it overlays correctly on a texture plane.

    xy = np.asarray(contour_xy, float).copy()
    xy[:, 1] = (h_px - 1) - xy[:, 1]  # flip y for plotting

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


def main():
    img = load_grayscale(INPUT_PATH)
    h, w = img.shape[:2]

    # Step 1 needed for the pipeline
    mask = binarize_silhouette(img)  # TODO 1
    contour_xy = extract_largest_contour(mask)  # TODO 2

    # --- Save outputs for next class (Part B: SVG export) ---
    os.makedirs("outputs", exist_ok=True)
    stem = os.path.splitext(os.path.basename(INPUT_PATH))[0]  # e.g., "square"
    out_npy = os.path.join("outputs", f"outline_{stem}_px.npy")
    np.save(out_npy, contour_xy)
    print("Saved contour:", out_npy)

    # Visual debugging using Pyvista
    texture = image_to_texture(img)

    plane = pv.Plane(
        center=(w / 2, h / 2, 0),
        i_size=w,
        j_size=h,
        i_resolution=1,
        j_resolution=1,
    )

    contour_poly = contour_to_pv_polyline_xy(contour_xy, h_px=h)

    p = pv.Plotter(title="Activity 1 Part A: image + extracted contour")
    p.add_mesh(plane, texture=texture)  # serving as a reference
    p.add_mesh(contour_poly, color="orange", line_width=4, label="largest contour")
    p.add_legend()
    p.show()

    print("Image shape (HxW):", img.shape)
    print("Contour points:", contour_xy.shape[0])


if __name__ == "__main__":
    main()
