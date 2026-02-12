"""
Part 2: Scanline Algorithm

TODOs in this file: 2
  - TODO: scanline_x_intersections()   (In-class activity from Lec 6)
  - TODO: even_odd_segments()          (In-class activity from Lec 6)
"""

import numpy as np
from typing import List

from utility.helpers_geom import ensure_closed


def scanline_x_intersections(
    poly_xy: np.ndarray, y: float, eps: float = 1e-9
) -> List[float]:
    """
    Find all x-coordinates where horizontal line at height y intersects polygon.

    (In-class activity from Lec 6)
    """

    raise NotImplementedError("TODO: Implement scanline_x_intersections")


def even_odd_segments(
    x_positions: List[float], y: float, min_seg_len: float = 1e-3
) -> List[np.ndarray]:
    """
    Convert sorted x-intersections into inside segments using even-odd rule.

    (In-class activity from Lec 6)
    """

    raise NotImplementedError("TODO: Implement even_odd_segments")
