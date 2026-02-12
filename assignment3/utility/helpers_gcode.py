from __future__ import annotations
from typing import List, Tuple
import numpy as np
import math
from utility.helpers_geom import ensure_closed


def start_gcode_minimal(nozzle_temp: int = 215, bed_temp: int = 60):
    return [
        "; ===== Parametric Lamp Shade Slicer - Prusa MK4S =====",
        "; Generated with custom lamp shade slicer",
        "; printer_model = Prusa MK4S",
        "; nozzle_diameter = 0.4",
        "; filament_diameter = 1.75",
        "",
        "G21 ; set units to millimeters",
        "G90 ; use absolute coordinates for positioning",
        "M83 ; use relative distances for extrusion",
        "",
        "; Set acceleration limits for Prusa MK4S",
        "M201 X2500 Y2500 Z200 E2500 ; sets maximum accelerations, mm/sec^2",
        "M203 X200 Y200 Z12 E120 ; sets maximum feedrates, mm/sec",
        "M204 P1250 R1250 T1250 ; sets acceleration (P, T) and retract acceleration (R), mm/sec^2",
        "",
        "; Set temperatures",
        f"M104 S{nozzle_temp} ; set hotend temp",
        f"M140 S{bed_temp} ; set bed temp",
        f"M190 S{bed_temp} ; wait for bed temp",
        "M109 S170 ; wait for hotend temp (partial)",
        "",
        "; Home all axes",
        "G28 ; home all without mesh bed level",
        "",
        "; Heat to printing temperature",
        f"M109 S{nozzle_temp} ; wait for hotend temp",
        "",
        "; Reset extruder",
        "G92 E0 ; reset extruder position",
    ]


def end_gcode_minimal():
    return [
        "",
        "; ===== End of print =====",
        "G92 E0 ; reset extruder",
        "",
        "; Turn off hotend and bed",
        "M104 S0 ; turn off hotend temperature",
        "M140 S0 ; turn off heated bed temperature",
        "",
        "; Disable fan",
        "M107 ; turn off fan",
        "",
        "; Retract and raise Z",
        "G91 ; relative positioning",
        "G1 E-2 F2700 ; retract filament",
        "G1 Z10 F900 ; raise Z",
        "",
        "; Return to absolute positioning",
        "G90 ; absolute positioning",
        "",
        "; Disable motors",
        "M84 ; disable motors",
    ]


def write_perimeter(
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
    """Write a closed perimeter using RELATIVE extrusion (M83).

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
        dx = x1 - float(poly[i - 1, 0])
        dy = y1 - float(poly[i - 1, 1])
        L = math.sqrt(dx * dx + dy * dy)
        dE = float(delta_E_for_move(L, line_width, layer_h, filament_d, flow_mult))
        if dE <= 0.0:
            continue
        E_total += dE
        g.append(f"G1 X{x1:.3f} Y{y1:.3f} Z{z:.3f} E{dE:.5f} F{F_print:.0f}")

    return g, E_total


def write_polyline(
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
    """Write an open polyline using RELATIVE extrusion (M83).

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
