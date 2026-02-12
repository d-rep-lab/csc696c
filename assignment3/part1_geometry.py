"""
Part 1: Parametric Lamp Shade Geometry

TODOs in this file: 7
  - TODO 1-4: Four profile types in lamp_shade_radius_at_height()
  - TODO 5:   validate_printability()
  - TODO 5b:  calculate_twist_angle()
  - TODO 6:   generate_lamp_shade_layer()
"""

import numpy as np
import math
from typing import List, Tuple, Optional

from config import PrinterSpecs, LampShadeParams
from utility.helpers_geom import ensure_closed


# ============================================================================
# PROFILE FUNCTIONS
# ============================================================================


def lamp_shade_radius_at_height(
    z: float,
    base_radius: float,
    top_radius: float,
    total_height: float,
    profile_type: str = "linear",
) -> float:
    """
    Calculate the lamp shade radius at a given height z using different profile functions.
    This function has been implemented for you, but take the time to understand the difference.

    PROFILE TYPES:
        1. 'linear' - Straight taper
        2. 'concave' - Curves inward
        3. 'convex' - Curves outward
        4. 'sinusoidal' - Gentle waves

    PARAMETERS:
        z: The layer height above bed (0 to total_height)
        base_radius: Radius at z=0 (bottom of lamp shade)
        top_radius: Radius at z=total_height (top of lamp shade)
        total_height : Total height of the lamp shade
        profile_type : Type of profile function (linear, concave, etc.)

    RETURNS:
        radius: Radius at height z
    """

    # Normalize height to [0, 1]
    t = z / total_height
    t = max(0.0, min(1.0, t))  # Guard rail for a valid range

    if profile_type == "linear":
        radius = base_radius + t * (top_radius - base_radius)
    elif profile_type == "concave":
        t_modified = t**2.0
        radius = base_radius + t_modified * (top_radius - base_radius)
    elif profile_type == "convex":
        t_modified = t**0.5
        radius = base_radius + t_modified * (top_radius - base_radius)
    elif profile_type == "sinusoidal":
        amplitude = 0.05 * (base_radius + top_radius) / 2
        wave = amplitude * math.sin(4 * math.pi * t)
        radius = base_radius + t * (top_radius - base_radius) + wave
    else:
        radius = base_radius + t * (top_radius - base_radius)

    return float(radius)


# ============================================================================
# PRINTABILITY VALIDATION
# ============================================================================


def validate_printability(
    profile_func,
    total_height: float,
    layer_height: float,
    max_overhang_angle: float = 45.0,
) -> Tuple[bool, str]:
    """
    Validate that the lamp shade profile is printable (overhang constraints).

    Remember 3D printers can only print overhangs up to ~45 degrees without support structures.
    This function checks that the lamp shade profile respects this physical constraint.

    PARAMETER:
        profile_func: Function that takes z and returns radius: profile_func(z) -> r
        total_height: Total lamp shade height
        layer_height: Layer height for sampling
        max_overhang_angle: Maximum printable overhang angle (degrees), typically 45 degrees for PLA

    Returns:
        valid: True if printable, False otherwise

    Algorithm:
        1. Sample the profile at each layer height (z = layer_height, 2*layer_height, ...)
        2. For each consecutive pair of layers:
            - Calculate change in radius: dr = r[i] - r[i-1]
            - Calculate change in height: dz = z[i] - z[i-1] = layer_height
            - Calculate slope angle: angle = arctan(|dr| / dz)
            - If angle > max_overhang_angle, return False
        3. If all layers pass, return True

    Physical Interpretation:
        - If radius increases going up (dr > 0), creates overhang
        - angle = arctan(dr/dz) gives overhang angle from vertical
        - 45 deg is typical limit for PLA without supports
        - Steeper angles require support structures

    Examples:
        ###GOOD CASE
        def profile(z): return 30.0 - z * 0.3  # Gradual taper inward
        valid, msg = validate_printability(profile, 50.0, 0.2, 45.0)
        print(valid, msg)
        True "Valid"

        ###BAD CASE
        def bad_profile(z): return 20.0 + z * 0.8  # Too steep outward
        valid, msg = validate_printability(bad_profile, 50.0, 0.2, 45.0)
        print(valid, msg)
        False "Overhang angle 68.2 deg exceeds maximum 45.0 deg at z=20.0mm"

    """
    # TODO #5
    raise NotImplementedError("TODO: Implement validate_printability")


# ============================================================================
# TWIST AND WAVE
# ============================================================================


def calculate_twist_angle(z: float, params: LampShadeParams) -> float:
    """
    Calculate the twist rotation angle (in radians) at height z.

    The twist rotates each layer's points around the center, creating a
    spiral/helical appearance when viewed from the side.

    Parameters:
        z: Height above bed
        params: LampShadeParams (uses twist_enabled, twist_degrees, twist_type, total_height)

    Returns:
        Twist angle in radians at height z. Returns 0.0 if twist_enabled is False.

    Twist Types:
        - 'linear': Constant twist rate.  twist = t * total_twist_rad
        - 'accelerating': More twist at the top.  twist = t^2 * total_twist_rad
        - 'decelerating': More twist at the bottom.  twist = (1 - (1-t)^2) * total_twist_rad

    Where t = z / total_height (normalized 0..1) and total_twist_rad = radians(twist_degrees).
    """

    # TODO #5b: Implement twist angle calculation
    raise NotImplementedError("TODO: Implement calculate_twist_angle")


def calculate_radial_wave(angle: float, z: float, params: LampShadeParams) -> float:
    """
    Calculate radial displacement at a point due to wave/texture pattern.

    Produces an organic, bumpy surface by combining horizontal waves (around the
    perimeter) with vertical waves (along the height). The product of sin and cos
    creates a helical interference pattern.

    Parameters:
        angle: Angular position around the circle (0 to 2*pi)
        z: Height above bed
        params: LampShadeParams (uses wave_enabled, wave_amplitude, wave_frequency, wave_vertical_freq)

    Returns:
        Radial offset in mm to add to the base radius. Returns 0.0 if wave_enabled is False.
    """
    if not params.wave_enabled:
        return 0.0

    horizontal_wave = math.sin(params.wave_frequency * angle)
    vertical_wave = math.cos(params.wave_vertical_freq * z)
    combined = horizontal_wave * vertical_wave

    return float(params.wave_amplitude * combined)


# ============================================================================
# LAYER GENERATION
# ============================================================================


def generate_lamp_shade_layer(
    z: float, params: LampShadeParams, num_points: Optional[int] = None
) -> np.ndarray:
    """
    Generate a cross-section at height z, with optional twist and wave texture.

    Parameters:
        z: Height of this layer above the bed (mm)
        params : LampShadeParams
            Contains geometry, twist, and wave settings.
        num_points : Number of points in circle (uses params.num_points if None)

    Returns:
        layer_xy : (N+1, 2) array of (x, y) coordinates forming a closed polygon.
                   The last point duplicates the first (closed via ensure_closed).

    Algorithm:
        1. Compute the base radius at this height:
               r = lamp_shade_radius_at_height(z, base_radius, top_radius, total_height, profile_type)
        2. Compute twist angle (if twist_enabled):
               twist = calculate_twist_angle(z, params)
        3. Generate evenly-spaced angles:  theta = linspace(0, 2*pi, num_points, endpoint=False)
        4. For each angle theta_i:
               a. twisted_angle = theta_i + twist       (rotates the whole layer)
               b. wave_offset   = calculate_radial_wave(theta_i, z, params)   (adds bumps)
               c. final_radius  = r + wave_offset
               d. x_i = cx + final_radius * cos(twisted_angle)
               e. y_i = cy + final_radius * sin(twisted_angle)
        5. Stack into (N, 2) array and call ensure_closed() to close the polygon.

    Notes:
        - Center at PrinterSpecs.BED_CENTER (cx, cy)
        - When twist_enabled is False, twist angle is 0 (no rotation)
        - When wave_enabled is False, wave_offset is 0 (plain circle)
        - With both disabled, this produces a simple parametric circle
    """

    if num_points is None:
        num_points = params.num_points

    # TODO #6: Implement cross-section generation with twist and wave support
    raise NotImplementedError("TODO: Implement generate_lamp_shade_layer")


def generate_lamp_shade_layers(params: LampShadeParams) -> List[dict]:
    """
    Generate all layer geometries for the lamp shade from bottom to top.

    Iterates from z=layer_height to z=total_height in steps of layer_height.
    Each layer dict contains 'z', 'perimeter_xy', and 'radius'.
    """

    layers = []

    z = params.layer_height
    while z <= params.total_height:
        perimeter = generate_lamp_shade_layer(z, params)
        radius = lamp_shade_radius_at_height(
            z,
            params.base_radius,
            params.top_radius,
            params.total_height,
            params.profile_type,
        )

        layers.append(
            {"z": float(z), "perimeter_xy": perimeter, "radius": float(radius)}
        )

        z += params.layer_height

    return layers
