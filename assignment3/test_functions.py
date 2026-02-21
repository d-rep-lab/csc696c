"""
Unit Testing Helper - Test individual functions as you implement them

This script helps you validate each part of your implementation incrementally.
Run this after implementing each function to ensure it works correctly.

Usage:
    python test_functions.py [part_number]

    part_number: 1 (geometry), 2 (scanline), 3 (gcode), or 'all'
"""

import sys
import numpy as np
import math

# Import from your implementation
try:
    from config import LampShadeParams, PrinterSpecs
    from part1_geometry import (
        lamp_shade_radius_at_height,
        generate_lamp_shade_layer,
        generate_lamp_shade_layers,
    )
    from part2_scanline import scanline_x_intersections, even_odd_segments
    from part3_gcode import extruded_area, delta_E_for_move

    IMPLEMENTATION_AVAILABLE = True
except (ImportError, NotImplementedError) as e:
    print(f"Could not import implementation: {e}")
    print("   Some tests will be skipped.")
    IMPLEMENTATION_AVAILABLE = False


def test_part1_geometry():
    """Test Part 1: Parametric Lamp Shade Geometry"""
    print("\n" + "=" * 60)
    print("TESTING PART 1: PARAMETRIC LAMP SHADE GEOMETRY")
    print("=" * 60)

    if not IMPLEMENTATION_AVAILABLE:
        print("❌ Implementation not available")
        return False

    all_passed = True

    # Test 1.1: lamp_shade_radius_at_height - Linear
    print("\n[1.1] Testing lamp_shade_radius_at_height - Linear profile")
    try:
        # At z=0, should return base_radius
        r0 = lamp_shade_radius_at_height(0, 30, 20, 50, "linear")
        assert abs(r0 - 30.0) < 0.01, f"Expected 30.0 at z=0, got {r0}"
        print(f"  ✓ z=0: radius = {r0:.2f}mm (expected 30.00mm)")

        # At z=25 (midpoint), should return average
        r_mid = lamp_shade_radius_at_height(25, 30, 20, 50, "linear")
        assert abs(r_mid - 25.0) < 0.01, f"Expected 25.0 at z=25, got {r_mid}"
        print(f"  ✓ z=25: radius = {r_mid:.2f}mm (expected 25.00mm)")

        # At z=50, should return top_radius
        r_top = lamp_shade_radius_at_height(50, 30, 20, 50, "linear")
        assert abs(r_top - 20.0) < 0.01, f"Expected 20.0 at z=50, got {r_top}"
        print(f"  ✓ z=50: radius = {r_top:.2f}mm (expected 20.00mm)")

        print("  ✅ Linear profile tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Linear profile tests FAILED: {e}")
        all_passed = False

    # Test 1.2: lamp_shade_radius_at_height - Other profiles
    print("\n[1.2] Testing other profile types")
    try:
        for profile in ["concave", "convex", "sinusoidal"]:
            r = lamp_shade_radius_at_height(25, 30, 20, 50, profile)
            assert 15 < r < 35, f"Radius {r} out of reasonable range for {profile}"
            print(f"  ✓ {profile}: radius = {r:.2f}mm at z=25")
        print("  ✅ Profile variety tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Profile variety tests FAILED: {e}")
        all_passed = False

    # Test 1.3: generate_lamp_shade_layer
    print("\n[1.3] Testing generate_lamp_shade_layer")
    try:
        params = LampShadeParams()
        params.base_radius = 30.0
        params.top_radius = 30.0
        params.total_height = 50.0
        params.num_points = 64

        layer = generate_lamp_shade_layer(25.0, params)

        # Check shape
        assert layer.shape[1] == 2, f"Expected Nx2 array, got {layer.shape}"
        print(f"  ✓ Layer shape: {layer.shape}")

        # Check it's closed
        assert np.allclose(layer[0], layer[-1]), "Polygon not closed"
        print(f"  ✓ Polygon is closed")

        # Check points are on circle (within tolerance)
        cx, cy = PrinterSpecs.BED_CENTER
        for x, y in layer[:-1]:  # Exclude duplicate closing point
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            assert abs(dist - 30.0) < 0.01, f"Point ({x},{y}) not on circle"
        print(f"  ✓ All points lie on correct circle")

        print("  ✅ Layer generation tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Layer generation tests FAILED: {e}")
        all_passed = False

    # Test 1.4: generate_lamp_shade_layers
    print("\n[1.4] Testing generate_lamp_shade_layers")
    try:
        params = LampShadeParams()
        params.total_height = 10.0  # Small for testing
        params.layer_height = 2.0
        params.base_radius = 20.0
        params.top_radius = 20.0

        layers = generate_lamp_shade_layers(params)

        expected_layers = int(10.0 / 2.0)
        assert (
            len(layers) == expected_layers
        ), f"Expected {expected_layers} layers, got {len(layers)}"
        print(f"  ✓ Generated {len(layers)} layers (expected {expected_layers})")

        # Check layer structure
        for i, layer in enumerate(layers):
            assert "z" in layer, f"Layer {i} missing 'z'"
            assert "perimeter_xy" in layer, f"Layer {i} missing 'perimeter_xy'"
            assert "radius" in layer, f"Layer {i} missing 'radius'"
        print(f"  ✓ All layers have required keys")

        print("  ✅ Multi-layer generation tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Multi-layer generation tests FAILED: {e}")
        all_passed = False

    return all_passed


def test_part2_scanline():
    """Test Part 2: Scanline Algorithms"""
    print("\n" + "=" * 60)
    print("TESTING PART 2: SCANLINE ALGORITHMS")
    print("=" * 60)

    if not IMPLEMENTATION_AVAILABLE:
        print("❌ Implementation not available")
        return False

    all_passed = True

    # Test 2.1: scanline_x_intersections - Rectangle
    print("\n[2.1] Testing scanline_x_intersections - Rectangle")
    try:
        # Simple rectangle
        rect = np.array([[70, 70], [140, 70], [140, 140], [70, 140], [70, 70]])

        # Scanline through middle
        x_intersections = scanline_x_intersections(rect, 105)
        assert (
            len(x_intersections) == 2
        ), f"Expected 2 intersections, got {len(x_intersections)}"
        assert (
            abs(x_intersections[0] - 70) < 0.01
        ), f"Expected x=70, got {x_intersections[0]}"
        assert (
            abs(x_intersections[1] - 140) < 0.01
        ), f"Expected x=140, got {x_intersections[1]}"
        print(f"  ✓ Rectangle intersections: {x_intersections}")

        # Scanline at edge
        x_edge = scanline_x_intersections(rect, 70)
        print(f"  ✓ Edge intersections: {len(x_edge)} found")

        print("  ✅ Rectangle scanline tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Rectangle scanline tests FAILED: {e}")
        all_passed = False

    # Test 2.2: even_odd_segments
    print("\n[2.2] Testing even_odd_segments")
    try:
        # Two pairs of intersections
        x_positions = [70.0, 90.0, 110.0, 130.0]
        segments = even_odd_segments(x_positions, 100.0)

        assert len(segments) == 2, f"Expected 2 segments, got {len(segments)}"

        # Check first segment
        seg1 = segments[0]
        assert np.allclose(seg1[0], [70.0, 100.0]), f"Segment 1 start wrong: {seg1[0]}"
        assert np.allclose(seg1[1], [90.0, 100.0]), f"Segment 1 end wrong: {seg1[1]}"

        # Check second segment
        seg2 = segments[1]
        assert np.allclose(seg2[0], [110.0, 100.0]), f"Segment 2 start wrong: {seg2[0]}"
        assert np.allclose(seg2[1], [130.0, 100.0]), f"Segment 2 end wrong: {seg2[1]}"

        print(
            f"  ✓ Generated {len(segments)} segments from {len(x_positions)} intersections"
        )
        print("  ✅ Even-odd segment tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Even-odd segment tests FAILED: {e}")
        all_passed = False

    return all_passed


def test_part3_gcode():
    """Test Part 3: G-code Generation"""
    print("\n" + "=" * 60)
    print("TESTING PART 3: G-CODE GENERATION")
    print("=" * 60)

    if not IMPLEMENTATION_AVAILABLE:
        print("❌ Implementation not available")
        return False

    all_passed = True

    # Test 3.1: extruded_area
    print("\n[3.1] Testing extruded_area")
    try:
        # Standard PLA parameters
        area = extruded_area(0.4, 0.2)

        # Expected: 0.4 * 0.2 + pi * (0.2/2)^2 = 0.08 + 0.0314... ≈ 0.1114
        expected = 0.4 * 0.2 + math.pi * (0.2 / 2) ** 2
        assert abs(area - expected) < 0.001, f"Expected {expected:.4f}, got {area:.4f}"
        print(
            f"  ✓ Capsule area (0.4mm × 0.2mm): {area:.4f}mm² (expected {expected:.4f}mm²)"
        )

        print("  ✅ Extruded area tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Extruded area tests FAILED: {e}")
        all_passed = False

    # Test 3.2: delta_E_for_move
    print("\n[3.2] Testing delta_E_for_move")
    try:
        # Standard move: 10mm at 0.4mm width, 0.2mm height, 1.75mm filament
        dE = delta_E_for_move(10.0, 0.4, 0.2, 1.75)

        # Rough calculation: area ≈ 0.1114, volume = 1.114mm^3
        # filament_area = pi * (1.75/2)^2 ≈ 2.405mm^2
        # dE ≈ 1.114 / 2.405 ~= 0.463mm

        # Should be in reasonable range
        assert 0.3 < dE < 0.6, f"dE = {dE:.3f} seems unreasonable"
        print(f"  ✓ Extrusion for 10mm move: {dE:.3f}mm filament")

        # Test with flow multiplier
        dE_flow = delta_E_for_move(10.0, 0.4, 0.2, 1.75, flow_mult=1.1)
        assert abs(dE_flow - dE * 1.1) < 0.01, "Flow multiplier not applied correctly"
        print(f"  ✓ With 110% flow: {dE_flow:.3f}mm filament")

        print("  ✅ Delta E calculation tests PASSED")
    except (NotImplementedError, AssertionError) as e:
        print(f"  ❌ Delta E calculation tests FAILED: {e}")
        all_passed = False

    return all_passed


def run_all_tests():
    """Run all test suites"""
    print("\n" + "=" * 70)
    print("RUNNING ALL UNIT TESTS")
    print("=" * 70)

    results = {}

    results["Part 1: Geometry"] = test_part1_geometry()
    results["Part 2: Scanline"] = test_part2_scanline()
    results["Part 3: G-code"] = test_part3_gcode()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for part, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{part:30s} {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Your implementation looks good.")
        print("   Next: Generate test lamp shades and validate G-code in PrusaSlicer.")
    else:
        print("\n⚠️  SOME TESTS FAILED. Review the errors above.")
        print("   Fix the failing functions and run tests again.")

    return all_passed


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        part = sys.argv[1].lower()

        if part == "1":
            test_part1_geometry()
        elif part == "2":
            test_part2_scanline()
        elif part == "3":
            test_part3_gcode()
        elif part == "all":
            run_all_tests()
        else:
            print("Usage: python test_functions.py [1|2|3|all]")
    else:
        run_all_tests()


if __name__ == "__main__":
    main()
