import numpy as np
from typing import List, Sequence
from utility.helpers_geom import (
    ensure_closed,
    make_rectangle,
    make_concave,
    bbox_xy,
    scale_polygon,
)
from utility.helpers_viz import visualize_scanline_segments


def scanline_x_intersections(
    rect: np.ndarray, y: float, eps: float = 1e-9
) -> List[float]:
    """
    Return all x-coordinates where a horizontal scanline at height y intersects the polygon boundary.

    You will use this for scanline infill and the even–odd rule.

    Hints:
    -Eps is a tiny tolerance. Use eps to help avoid double counting edges / when we have an edge that is horizontal
    -Use linear interpolation to find where the edge hits horizontal scanline: "what fraction f of the edge is already at y pos?", then use the same f to compute x pos.
    -Return sorted x-coordinates left-to-right
    """

    raise NotImplementedError


def even_odd_segments(
    x_pos: Sequence[float], y: float, min_seg_len: float = 1e-3
) -> List[np.ndarray]:
    """Convert sorted x-intersections into inside segments using the even–odd rule.

    Hints:
    -Remember: we toggle "inside" and "outside" segments each time we cross a boundary
    -Use min_seg_len to filter any tiny fragments (if any)
    """

    raise NotImplementedError


def sweep_scanlines(
    rect: np.ndarray, vert_scan_dist: float, offset_scale: float, min_seg_len: float
):

    # offset (i.e., shrink) rect to account for line-width of the nozzle + make sure we don't spill beyond the absolute perimeters
    offset_rect = scale_polygon(rect, offset_scale)

    xmin, xmax, ymin, ymax = bbox_xy(offset_rect)
    scanned_y, segs = [], []
    y = ymin + 0.5 * vert_scan_dist  # pick the first scanline y at midpoint
    while y <= ymax - 0.25 * vert_scan_dist:  # sweep upwards

        # TODO #1 : return a sorted list of x-coordinates where the horizontal line at height y crosses polygon edges
        x_pos = scanline_x_intersections(offset_rect, y)

        # TODO #2 : Apply even-odd rule
        segs.extend(even_odd_segments(x_pos, y, min_seg_len))

        scanned_y.append(float(y))
        y += vert_scan_dist

    return offset_rect, scanned_y, segs


def main():
    """
    Implement the two TODO's using a rectangle polygon.
    Test the robustness of your solution using a concave polygon afterward
    """

    perimeter_coordinates = make_rectangle(
        cx=105.0, cy=105.0, w=70.0, h=70.0
    )  # returns xy coordinates of rectangle

    # perimeter_coordinates = make_concave(cx=105.0, cy=105.0, s=12.0)

    offset_poly, scanned_y, segs = sweep_scanlines(
        perimeter_coordinates, vert_scan_dist=6.0, offset_scale=0.96, min_seg_len=0.3
    )

    visualize_scanline_segments(offset_poly, scanned_y, segs)


if __name__ == "__main__":
    main()
