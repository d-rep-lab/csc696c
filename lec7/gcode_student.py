import numpy as np
import math
from typing import List, Sequence

from utility.helpers_geom import (
    ensure_closed,
    make_rectangle,
    make_concave,
    build_serpentine_infill,
)
from utility.helpers_gcode import (
    start_gcode_minimal,
    end_gcode_minimal,
)
from utility.helpers_viz import visualize_serpentine_toolpath


class Params:
    z: float = 0.28
    layer_h: float = 0.28
    line_w: float = 0.48
    filament_d: float = 1.75
    flow: float = 1.0
    F_travel: float = 6000.0
    F_print: float = 1500.0
    spacing: float = 6.0
    offset_scale: float = 0.96
    min_seg_len: float = 0.30
    cx: float = 105.0
    cy: float = 105.0


# ------------------------------------------------------------
# Part 1: EX1 functions (copy/paste or import)
# ------------------------------------------------------------
def scanline_intersections(poly_xy: np.ndarray, y: float, eps: float = 1e-9):
    raise NotImplementedError


def even_odd_segments(xs: Sequence[float], y: float, min_seg_len: float = 1e-3):
    raise NotImplementedError


# ------------------------------------------------------------
# Part 2: Slicer Flow math
# ------------------------------------------------------------
def extruded_area(width_mm: float, height_mm: float) -> float:
    """Approximate cross-sectional area (mm^2) of an extruded line.

    Hints:
    - Use the 'capsule' model from lecture: rectangle + circle. (Slide 122)
    - width_mm ~= nozzle/line width, height_mm ~= layer height.
    """
    raise NotImplementedError


def delta_E_for_G1(
    L_mm: float,
    width_mm: float,
    height_mm: float,
    filament_d_mm: float,  # filament diameter
):
    """Return E (mm of filament) to extrude for a move of length L_mm.

    Recall:
        -volume_out = extruded_area * L_mm
        - volume_in  = (pi * (filament_d/2)^2) * ΔE
          => ΔE = volume_out / filament_area
    Refer to slide 102, slide 139

    """
    raise NotImplementedError


# ------------------------------------------------------------
# Part 2.5: Writing G-Code
# ------------------------------------------------------------


def polyline_extrude(
    path_xy: np.ndarray,
    z: float,
    F_travel: float,
    F_print: float,
    line_width: float,
    layer_h: float,
    filament_d: float,
    flow_mult: float,
    delta_E_for_move,
    eps: float = 1e-9,
):
    """Emit G-code lines for one polyline at fixed Z using RELATIVE extrusion (M83).

    Must-do behavior:
    1) TRAVEL to the first point (no E).
    2) For each segment:
        - compute segment length L
        - compute dE = delta_E_for_move(L, ...)
        - emit a PRINT move with E=dE (per-move extrusion)

    Output: list_of_lines
    """
    g_code = []

    # Guard rail
    if path_xy is None or len(path_xy) < 2:
        return g_code
    assert path_xy.ndim == 2 and path_xy.shape[1] == 2, "path_xy must be Nx2"

    # Travel to first point
    x0, y0 = path_xy[0, 0], path_xy[0, 1]
    # call G1 Code (using 4 parameter; no E!) and then append to g_code
    # Remember, if we're traveling we use F_travel (speed)

    # Print segments with RELATIVE extrusion (E=dE for each move)
    for i in range(1, len(path_xy)):
        x_prev, y_prev = path_xy[i - 1, 0], path_xy[i - 1, 1]
        x, y = path_xy[i, 0], path_xy[i, 1]
        dx = x - x_prev
        dy = y - y_prev
        L = math.sqrt(dx * dx + dy * dy)
        if L <= eps:
            continue

        # TODO #1 : Finish delta_E_for_move () to compute dE for this segment(a positive number)
        # dE = delta_E_for_move(...)

        if dE <= 0.0:  # check dE is positive
            continue

        # TODO #2 : Send the printing move for this segment.
        # Travel moves: no E. Print moves: include E
        # call G1 Code (using all 5 parameter) and then append to g
        # Remember to use F_print

        raise NotImplementedError("Not implemented yet")

    return g_code


def write_gcode(layers: List[dict], P: "Params", delta_E_for_move):
    """Complete G-code program using RELATIVE extrusion (M83)

    Each layer dict provides:
      - z
      - perimeter_xy
      - infill_xy (serpentine-infill pattern)

    You will:
      - write header
      - per layer: move to Z, then perimeter, then infill
      - write footer

    Notes:
      - Travel moves should NOT include any E term.
      - Extrusion moves should include E=dE for that move.
    """
    g = []
    g.extend(start_gcode_minimal())  # pre-amble starter code
    g.append("M83 ; relative extrusion")

    # Layer loop
    # Note: currently unnecessary bc we're focusing on one layer but is needed for Assignment 3
    for layer_idx, layer in enumerate(layers):
        z = layer["z"]
        perim = layer["perimeter_xy"]
        infill = layer["infill_xy"]

        g.append(f"; ===== LAYER {layer_idx} Z={z:.3f} =====")

        # TODO: Travel to Z using P.F_travel (no E)
        # g.append(...)

        g.append("; --- PERIMETER ---")
        perim = ensure_closed(perim)  # need to ensure it is closed
        # g.extend(polyline_extrude(...)) => call on polyline_extrude using PERIM geometry

        # TODO: infill
        g.append("; --- SERPENTINE INFILL ---")
        # g.extend(polyline_extrude(...)) => call on polyline_extrude using INFILL geometry

        raise NotImplementedError("Finish function")

    g.extend(end_gcode_minimal())
    return g


def main():
    # One-layer geometry
    P = Params()

    # Outer boundary (perimeter)
    perimeter_coordinates = make_rectangle(P.cx, P.cy, w=70.0, h=70.0)
    # perimeter_coordinates = make_concave(cx=105.0, cy=105.0, s=12.0)

    # Infill path (serpentine)
    offset, scanned_y, serp_path = build_serpentine_infill(
        perimeter_coordinates,
        spacing=P.spacing,
        offset_scale=P.offset_scale,
        min_seg_len=P.min_seg_len,
        scanline_intersections=scanline_intersections,
        even_odd_segments=even_odd_segments,
    )

    visualize_serpentine_toolpath(offset, scanned_y, serp_path)

    # G-code output
    layers = [
        {
            "z": P.z,
            "perimeter_xy": perimeter_coordinates,
            "infill_xy": serp_path,
        }
    ]

    gcode_lines = write_gcode(layers, P, delta_E_for_G1)

    out_path = "out/out_one_layer.gcode"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(gcode_lines) + "\n")
    print("Wrote:", out_path)


if __name__ == "__main__":
    main()
