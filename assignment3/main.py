import numpy as np

from config import LampShadeParams
from part1_geometry import (
    generate_lamp_shade_layers,
    generate_lamp_shade_layer,
    lamp_shade_radius_at_height,
)
from part3_gcode import generate_spiral_lamp_shade_toolpath, write_lamp_shade_gcode
from part4_analysis import analyze_lamp_shade_performance, compare_profiles
from utility.helpers_viz import visualize_lamp_shade_preview


def preview_lamp_shade_geometry(params: LampShadeParams, num_preview_layers: int = 20):
    """
    Visualize lamp shade geometry before generating G-code.
    """

    print(f"\nGenerating lamp shade preview with {num_preview_layers} layers...")

    preview_heights = np.linspace(
        params.layer_height, params.total_height, num_preview_layers
    )

    preview_layers = []
    for z in preview_heights:
        perimeter = generate_lamp_shade_layer(z, params)
        preview_layers.append(
            {
                "z": z,
                "perimeter_xy": perimeter,
                "radius": lamp_shade_radius_at_height(
                    z,
                    params.base_radius,
                    params.top_radius,
                    params.total_height,
                    params.profile_type,
                ),
            }
        )

    visualize_lamp_shade_preview(preview_layers, params.profile_type)


def main():

    # Create lamp shade parameters
    params = LampShadeParams()
    params.base_radius = 30.0
    params.top_radius = 25.0
    params.total_height = 50.0
    params.profile_type = "linear"
    params.num_points = 64
    params.layer_height = 0.20

    # Validate parameters (includes printability check)
    try:
        params.validate()
        print("Parameters validated (including printability)")
    except ValueError as e:
        print(f"Validation failed: {e}")
        return

    print("\n[1/5] Generating lamp shade geometry...")
    layers = generate_lamp_shade_layers(params)
    print(f"  Generated {len(layers)} layers")

    print("\n[2/5] Generating spiral toolpath...")
    spiral_path = generate_spiral_lamp_shade_toolpath(layers, params)
    print(f"  Generated {len(spiral_path)} toolpath points")

    print("\n[3/5] Writing G-code...")
    output_file = f"output/lamp_shade_{params.profile_type}.gcode"
    gcode_stats = write_lamp_shade_gcode(spiral_path, params, output_file)

    print("\n[4/5] Analyzing performance...")
    analysis = analyze_lamp_shade_performance(layers, spiral_path, gcode_stats, params)
    print(f"  Max overhang: {analysis.get('max_overhang_angle', 'N/A'):.1f} deg")
    print(f"  Volume: {analysis.get('volume_estimate', 'N/A'):.0f} mm3")
    print(f"  Print time: {analysis.get('print_time_estimate', 'N/A'):.1f} min")
    print(f"  Material: {analysis.get('material_usage', 'N/A'):.1f} g")

    print("\n[5/5] Comparing profiles...")
    compare_profiles(["linear", "concave", "convex", "sinusoidal"], params)

    print("\nDONE!")
    print("\nNext steps:")
    print("  1. Review generated G-code in PrusaSlicer")
    print("  2. Include profile comparison table in report")
    print("  3. Discuss printability constraints encountered")
    print("  4. Analyze performance trade-offs between profiles")
    print()


if __name__ == "__main__":
    main()
