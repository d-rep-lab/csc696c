"""
Part 4: Validation, Testing & Analysis

TODOs in this file: 1
  - TODO: analyze_lamp_shade_performance()

compare_profiles() is provided for you.
"""

import copy
import numpy as np
from typing import List, Dict

from config import LampShadeParams


# ============================================================================
# PERFORMANCE ANALYSIS
# ============================================================================


def analyze_lamp_shade_performance(
    layers: List[dict],
    spiral_path: np.ndarray,
    gcode_stats: Dict,
    params: LampShadeParams,
) -> Dict:
    """
    Analyze lamp shade design and generation performance.

    Parameters:
        layers: Generated layer data
        spiral_path: Toolpath array
        gcode_stats: Stats from write_lamp_shade_gcode()
        params: Lamp Shade parameters

    Returns:
        A Dict. Must include:
            - max_overhang_angle: float (degrees) - maximum slope in profile
            - volume_estimate: float (mm^3) - approximate lamp shade volume
            - print_time_estimate: float (minutes) - estimated print time
            - material_usage: float (grams) - material needed (PLA density 1.24 g/cm^3)

    Algorithm Hints:

    Max Overhang:
    - Scan through layers calculating dr/dz between consecutive layers
    - Find maximum angle using arctan(dr/dz)

    Volume Estimate:
    - Approximate each layer as cylindrical shell
    - Volume per layer = 2*pi * radius * wall_thickness * dz
    - Sum all layers

    Print Time:
    - Use total_distance from gcode_stats
    - Time = distance / speed (convert print_speed from mm/min to mm/s)
    - Add ~10% overhead for accelerations

    Material Usage:
    - Convert volume from mm^3 to cm^3
    - Multiply by PLA density: 1.24 g/cm^3
    """

    # TODO: Implement comprehensive lamp shade analysis
    raise NotImplementedError("TODO: Implement analyze_lamp_shade_performance")


# ============================================================================
# PROFILE COMPARISON (provided)
# ============================================================================


def compare_profiles(
    profile_types: List[str], params_template: LampShadeParams
) -> None:
    """
    Generate comparison of different profile types.

    Runs each profile through the full pipeline (layers -> toolpath -> gcode -> analysis)
    and prints a side-by-side comparison table.

    Parameters:
        profile_types : List of profiles to compare (e.g., ['linear', 'concave', 'convex', 'sinusoidal'])
        params_template : Template parameters (same for all except profile_type)
    """
    from part1_geometry import generate_lamp_shade_layers
    from part3_gcode import generate_spiral_lamp_shade_toolpath, write_lamp_shade_gcode

    results = []

    for profile_type in profile_types:
        params = copy.copy(params_template)
        params.profile_type = profile_type
        params.z_increment_per_point = None  # Reset for recalculation

        try:
            layers = generate_lamp_shade_layers(params)
            spiral_path = generate_spiral_lamp_shade_toolpath(layers, params)
            output_file = f"output/lamp_shade_{profile_type}_comparison.gcode"
            gcode_stats = write_lamp_shade_gcode(spiral_path, params, output_file)
            analysis = analyze_lamp_shade_performance(
                layers, spiral_path, gcode_stats, params
            )
            results.append((profile_type, analysis))
        except Exception as e:
            print(f"  Failed for {profile_type}: {e}")

    # Format comparison table
    print("\nProfile Comparison:")
    header = f"| {'Profile':12s} | {'Max Overhang':12s} | {'Volume':10s} | {'Print Time':10s} | {'Material':10s} |"
    separator = f"|{'-' * 14}|{'-' * 14}|{'-' * 12}|{'-' * 12}|{'-' * 12}|"
    print(header)
    print(separator)
    for profile_type, analysis in results:
        overhang = f"{analysis.get('max_overhang_angle', 0):.1f} deg"
        volume = f"{analysis.get('volume_estimate', 0):.0f} mm3"
        time_est = f"{analysis.get('print_time_estimate', 0):.1f} min"
        material = f"{analysis.get('material_usage', 0):.1f} g"
        print(
            f"| {profile_type.capitalize():12s} | {overhang:12s} | {volume:10s} | {time_est:10s} | {material:10s} |"
        )
