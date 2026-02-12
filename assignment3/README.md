# Parametric Lamp Shade 3D Printing Slicer - Student Files

## Quick Start

1. **Review the assignment:**
   ```
   Read ASSIGNMENT.md for complete instructions
   ```

2. **Implement the TODOs in each file:**
   ```bash
   # Edit part1_geometry.py  (profiles, validation, twist, layer generation)
   # Edit part2_scanline.py  (scanline intersections, even-odd segments)
   # Edit part3_gcode.py     (extrusion math, spiral toolpath, G-code writer)
   # Edit part4_analysis.py  (performance analysis)
   ```

3. **Test your implementation:**
   ```
   # Run unit tests
   python test_functions.py

   # Generate all 4 required profiles
   python test_all_profiles.py

   # Run the full pipeline
   python main.py
   ```

4. **Verify in PrusaSlicer:**
   - Open each generated .gcode file
   - Check for continuous spiral
   - Take screenshots for report

## Required Deliverables

You must generate **ALL 4 profile types** with identical base parameters:

1. `output/lamp_shade_linear.gcode`
2. `output/lamp_shade_concave.gcode`
3. `output/lamp_shade_convex.gcode`
4. `output/lamp_shade_sinusoidal.gcode`

**Base Parameters (use for all):**
- Base radius: 30mm
- Top radius: 25mm
- Height: 50mm
- Layer height: 0.20mm

## File Structure

```
student_files/
  config.py               <- Shared configuration [provided, do not modify]
  part1_geometry.py        <- Part 1: Geometry TODOs
  part2_scanline.py        <- Part 2: Scanline TODOs
  part3_gcode.py           <- Part 3: G-code TODOs
  part4_analysis.py        <- Part 4: Analysis TODO
  main.py                  <- Main pipeline
  test_functions.py        <- Unit tests for Parts 1-3
  test_all_profiles.py     <- Generate all 4 required profiles
  utility/                 <- Helper functions [do not modify]
    helpers_gcode.py
    helpers_geom.py
    helpers_viz.py
```

**Pre-implemented for you:** `calculate_radial_wave()`, `generate_lamp_shade_layers()`, `compare_profiles()`

## Assignment Structure

**Part 1: Parametric Geometry**
- Implement 4 profile types
- Implement printability validation
- Implement twist angle calculation
- Implement layer generation (with twist/wave support)

**Part 2: Scanline Algorithm**
- Implement intersection finding (Lec 6)
- Implement even-odd fill (Lec 6)

**Part 3: G-code Generation**
- Implement extrusion math (Lec 7)
- Implement spiral toolpath
- Implement G-code writer loop

**Part 4: Analysis & Testing**
- Implement performance analysis
- Generate all 4 profiles
- G-code validation


## Important Notes

**All 4 profiles are required** - Your performance analysis must be based on actual generated G-code, not theoretical calculations.

**Use identical parameters** - All 4 lamp shades should use the same base parameters for fair comparison.

