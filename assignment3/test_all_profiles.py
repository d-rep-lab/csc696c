"""
Test script to generate all 4 required profile types.

This script demonstrates how to generate G-code for all 4 profile types
using identical base parameters for fair comparison.

Run this after implementing your lamp_shade_slicer.py to verify it works correctly.
"""

from config import LampShadeParams
from part1_geometry import generate_lamp_shade_layers
from part3_gcode import generate_spiral_lamp_shade_toolpath, write_lamp_shade_gcode
from part4_analysis import analyze_lamp_shade_performance, compare_profiles


def generate_all_profiles():
    """Generate all 4 required profile types for the assignment."""

    print("=" * 60)
    print("GENERATING ALL 4 REQUIRED PROFILE TYPES")
    print("=" * 60)

    # Base parameters - SAME for all profiles for fair comparison
    base_params = {
        "base_radius": 30.0,
        "top_radius": 25.0,
        "total_height": 50.0,
        "layer_height": 0.20,
        "line_width": 0.48,
        "num_points": 64,
        "nozzle_temp": 215,
        "bed_temp": 60,
    }

    # Profile types to generate
    profile_types = ["linear", "concave", "convex", "sinusoidal"]

    results = {}

    for profile_type in profile_types:
        print(f"\n{'='*60}")
        print(f"GENERATING: {profile_type.upper()} PROFILE")
        print(f"{'='*60}")

        # Create parameters
        params = LampShadeParams()
        params.base_radius = base_params["base_radius"]
        params.top_radius = base_params["top_radius"]
        params.total_height = base_params["total_height"]
        params.layer_height = base_params["layer_height"]
        params.line_width = base_params["line_width"]
        params.num_points = base_params["num_points"]
        params.nozzle_temp = base_params["nozzle_temp"]
        params.bed_temp = base_params["bed_temp"]
        params.profile_type = profile_type

        try:
            # Validate parameters (includes printability check)
            params.validate()
            print(f"✓ Parameters validated (including printability)")

            # Generate geometry
            print(f"[1/4] Generating lamp shade geometry...")
            layers = generate_lamp_shade_layers(params)
            print(f"✓ Generated {len(layers)} layers")

            # Generate toolpath
            print(f"[2/4] Generating spiral toolpath...")
            spiral_path = generate_spiral_lamp_shade_toolpath(layers, params)
            print(f"✓ Generated {len(spiral_path)} toolpath points")

            # Write G-code
            print(f"[3/4] Writing G-code...")
            output_file = f"output/lamp_shade_{profile_type}.gcode"
            gcode_stats = write_lamp_shade_gcode(spiral_path, params, output_file)

            # Analyze performance
            print(f"[4/4] Analyzing performance...")
            analysis = analyze_lamp_shade_performance(
                layers, spiral_path, gcode_stats, params
            )

            # Store results
            results[profile_type] = {
                "params": params,
                "stats": gcode_stats,
                "analysis": analysis,
                "output_file": output_file,
            }

            # Print summary
            print(f"\n✓ {profile_type.upper()} COMPLETE:")
            print(f"  File: {output_file}")
            print(f"  Size: {gcode_stats['file_size']/1024:.1f} KB")
            print(f"  Generation time: {gcode_stats['generation_time']:.2f}s")
            print(
                f"  Max overhang: {analysis.get('max_overhang_angle', 'N/A'):.1f} degrees"
            )
            print(f"  Volume: {analysis.get('volume_estimate', 'N/A'):.0f} mm^3")
            print(f"  Print time: {analysis.get('print_time_estimate', 'N/A'):.1f} min")
            print(f"  Material: {analysis.get('material_usage', 'N/A'):.1f} g")

        except Exception as e:
            print(f"\n❌ ERROR generating {profile_type}: {e}")
            import traceback

            traceback.print_exc()
            continue

    # Final summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully generated {len(results)}/4 profiles")

    if len(results) == 4:
        print("\n✅ ALL 4 REQUIRED PROFILES GENERATED!")
        print("\nNext steps:")
        print("  1. Open each .gcode file in PrusaSlicer to verify")
        print("  2. Take screenshots for your report")
        print("  3. Include profile comparison table in report")
        print("  4. Analyze trade-offs (volume, time, material)")
    else:
        print(f"\n⚠️  Only {len(results)}/4 profiles generated successfully")
        print("Fix errors above before submitting")

    # Generate comparison table for report
    if len(results) >= 2:
        print(f"\n{'='*60}")
        print("PROFILE COMPARISON TABLE (copy to report):")
        print(f"{'='*60}\n")
        compare_profiles(profile_types[: len(results)], LampShadeParams())

    return results


def test_single_profile(profile_type="linear"):
    """
    Test a single profile type for debugging.

    Usage:
        test_single_profile('linear')
        test_single_profile('concave')
    """

    print(f"\nTesting {profile_type} profile...")

    params = LampShadeParams()
    params.base_radius = 30.0
    params.top_radius = 25.0
    params.total_height = 50.0
    params.profile_type = profile_type

    try:
        params.validate()
        layers = generate_lamp_shade_layers(params)
        spiral_path = generate_spiral_lamp_shade_toolpath(layers, params)
        gcode_stats = write_lamp_shade_gcode(
            spiral_path, params, f"output/test_{profile_type}.gcode"
        )
        analysis = analyze_lamp_shade_performance(
            layers, spiral_path, gcode_stats, params
        )

        print(f"✓ {profile_type} test passed")
        return True
    except Exception as e:
        print(f"❌ {profile_type} test failed: {e}")
        return False


if __name__ == "__main__":
    # Generate all 4 required profiles
    results = generate_all_profiles()

    # Optionally, test individual profiles for debugging
    # test_single_profile('linear')
