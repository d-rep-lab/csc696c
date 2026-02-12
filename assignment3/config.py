from typing import Optional


class PrinterSpecs:
    """Prusa MK4S printer specifications"""

    BED_SIZE = (250, 210)  # mm (X, Y)
    BED_CENTER = (105, 105)  # mm (X, Y)
    MAX_Z = 220  # mm
    NOZZLE_DIAMETER = 0.4  # mm
    FILAMENT_DIAMETER = 1.75  # mm
    MAX_TEMP_NOZZLE = 300  # Celcius
    MAX_TEMP_BED = 120  # Celcius
    MAX_OVERHANG_ANGLE = 45.0  # degrees (printability limit)


class LampShadeParams:
    """Parameters for lamp shade generation and printing"""

    def __init__(self):
        # Geometry parameters
        self.base_radius: float = 30.0  # mm
        self.top_radius: float = 25.0  # mm
        self.total_height: float = 50.0  # mm
        self.num_points: int = 64  # points per layer
        self.profile_type: str = "linear"  # 'linear', 'concave', 'convex', 'sinusoidal'

        # Printing parameters
        self.layer_height: float = 0.20  # mm
        self.line_width: float = 0.48  # mm (slightly wider than nozzle)
        self.print_speed: float = 1500.0  # mm/min
        self.travel_speed: float = 6000.0  # mm/min
        self.flow_multiplier: float = 1.0  # extrusion multiplier

        # Temperature settings (PLA)
        self.nozzle_temp: int = 215  # Celcius
        self.bed_temp: int = 60  # Celcius

        # Twist parameters
        self.twist_enabled: bool = False
        self.twist_degrees: float = 0.0  # Total twist in degrees over full height
        self.twist_type: str = "linear"  # 'linear', 'accelerating', 'decelerating'

        # Wave/texture parameters
        self.wave_enabled: bool = False
        self.wave_amplitude: float = 0.0  # mm radial displacement
        self.wave_frequency: int = 6  # number of waves around perimeter
        self.wave_vertical_freq: float = 3.0  # vertical wave frequency

        # Advanced parameters
        self.z_increment_per_point: Optional[float] = None  # auto-calculated if None

    def validate(self) -> None:
        """
        Validate parameter constraints.

        REQUIREMENTS:
        - Must check basic constraints (positive values, ranges)
        - Must validate bed boundaries
        - Must call validate_printability() to check overhang constraints
        """
        from part1_geometry import lamp_shade_radius_at_height, validate_printability

        # Basic validation
        if self.base_radius <= 0 or self.top_radius <= 0:
            raise ValueError("Radii must be positive")
        if self.total_height <= 0:
            raise ValueError("Height must be positive")
        if self.layer_height <= 0 or self.layer_height > 0.3:
            raise ValueError("Layer height must be in range (0, 0.3]")
        if self.num_points < 12:
            raise ValueError("Need at least 12 points for smooth circle")

        # Check bed limits
        max_radius = max(self.base_radius, self.top_radius)
        cx, cy = PrinterSpecs.BED_CENTER
        if (
            cx - max_radius < 0
            or cx + max_radius > PrinterSpecs.BED_SIZE[0]
            or cy - max_radius < 0
            or cy + max_radius > PrinterSpecs.BED_SIZE[1]
        ):
            raise ValueError("Lamp Shade extends beyond bed boundaries")

        if self.total_height > PrinterSpecs.MAX_Z:
            raise ValueError(f"Height exceeds printer maximum ({PrinterSpecs.MAX_Z}mm)")

        # Minimum radius check (structural stability)
        min_radius = min(self.base_radius, self.top_radius)
        if min_radius < 10.0:
            raise ValueError(
                f"Minimum radius must be >=10mm for stability (got {min_radius:.1f}mm)"
            )

        # Check printability (overhang constraints)
        profile_func = lambda z: lamp_shade_radius_at_height(
            z, self.base_radius, self.top_radius, self.total_height, self.profile_type
        )

        valid, message = validate_printability(
            profile_func,
            self.total_height,
            self.layer_height,
            PrinterSpecs.MAX_OVERHANG_ANGLE,
        )

        if not valid:
            raise ValueError(f"Printability check failed: {message}")
