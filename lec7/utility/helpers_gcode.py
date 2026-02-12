from __future__ import annotations
from typing import List, Tuple
import numpy as np
import math
from utility.helpers_geom import ensure_closed


def start_gcode_minimal(nozzle_temp: int = 215, bed_temp: int = 60):
    return [
        "; ===== in-class one-layer activity =====",
        "M83 ; relative extrusion",
        "G90 ; absolute positioning",
        f"M104 S{nozzle_temp}",
        f"M140 S{bed_temp}",
        "G28 ; home all",
        f"M109 S{nozzle_temp}",
        f"M190 S{bed_temp}",
        "G92 E0",
    ]


def end_gcode_minimal():
    return [
        "; ===== end =====",
        "M104 S0",
        "M140 S0",
        "M107",
        "G91",
        "G1 Z10 F900",
        "G90",
        "M84",
    ]


def emit_perimeter(
    poly_xy: np.ndarray,
    z: float,
    F_travel: float,
    F_print: float,
    line_width: float,
    layer_h: float,
    filament_d: float,
    flow_mult: float,
    delta_E_for_move,
) -> Tuple[List[str], float]:
    """Emit a closed perimeter using RELATIVE extrusion (M83).

    Returns: (gcode_lines, total_extruded_mm_filament)
    Note: In M83, E in each G1 is a per-move delta (dE), not a running total.
    """
    poly = ensure_closed(poly_xy)
    g: List[str] = []
    E_total = 0.0

    x0, y0 = float(poly[0, 0]), float(poly[0, 1])
    g.append(f"G1 Z{z:.3f} F900")
    g.append(f"G1 X{x0:.3f} Y{y0:.3f} F{F_travel:.0f}")
    g.append("; --- PERIMETER ---")

    for i in range(1, len(poly)):
        x1, y1 = float(poly[i, 0]), float(poly[i, 1])
        L = segment_length(poly[i - 1], poly[i])
        dE = float(delta_E_for_move(L, line_width, layer_h, filament_d, flow_mult))
        if dE <= 0.0:
            continue
        E_total += dE
        g.append(f"G1 X{x1:.3f} Y{y1:.3f} Z{z:.3f} E{dE:.5f} F{F_print:.0f}")

    return g, E_total


def emit_polyline(
    path_xy: np.ndarray,
    z: float,
    E0: float,
    F_travel: float,
    F_print: float,
    line_width: float,
    layer_h: float,
    filament_d: float,
    flow_mult: float,
    delta_E_for_move,
) -> Tuple[List[str], float]:
    """Emit an open polyline using RELATIVE extrusion (M83).

    Parameters:
      - E0 is ignored for relative extrusion (kept only for backward-compatible signature).

    Returns: (gcode_lines, total_extruded_mm_filament)
    """
    g: List[str] = []
    E_total = 0.0

    x0, y0 = float(path_xy[0, 0]), float(path_xy[0, 1])
    g.append(f"G1 X{x0:.3f} Y{y0:.3f} Z{z:.3f} F{F_travel:.0f}")

    for i in range(1, len(path_xy)):
        x1, y1 = float(path_xy[i, 0]), float(path_xy[i, 1])
        dx = x1 - float(path_xy[i - 1, 0])
        dy = y1 - float(path_xy[i - 1, 1])
        L = math.sqrt(dx * dx + dy * dy)
        if L <= 1e-9:
            continue
        dE = float(delta_E_for_move(L, line_width, layer_h, filament_d, flow_mult))
        if dE <= 0.0:
            continue
        E_total += dE
        g.append(f"G1 X{x1:.3f} Y{y1:.3f} Z{z:.3f} E{dE:.5f} F{F_print:.0f}")

    return g, E_total
