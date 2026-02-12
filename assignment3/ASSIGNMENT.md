# Assignment 3: Parametric Lamp Shade 3D Printing Slicer

## Overview

In this assignment, you will build a complete 3D printing slicer that generates parametric lamp shades. Your slicer will implement geometric algorithms, validate printability constraints, and produce production-ready G-code for a Prusa MK4S printer.

**Learning Objectives:**
- Implement parametric geometry functions for design flexibility
- Apply computational geometry algorithms
- Generate manufacturing-compatible G-code with validation
- Analyze and compare design trade-offs quantitatively
- Understand physical manufacturing constraints

**Key Features:**
- 4 parametric profile types (linear, concave, convex, sinusoidal)
- Twist rotation and wave texture support for organic designs
- Printability validation (overhang angle checking)
- Spiral lamp shade mode G-code generation
- Performance analysis and profile comparison

---

## Getting Started

### Prerequisites
- Python 3.8+
- NumPy, Matplotlib
- PrusaSlicer (for G-code preview)

### File Structure

Your working files are organized by assignment part:

```
student_files/
  config.py               <- Shared configuration (PrinterSpecs, LampShadeParams) [provided]
  part1_geometry.py        <- Part 1: Profile functions, validation, layer generation (TODOs)
  part2_scanline.py        <- Part 2: Scanline algorithm  (TODOs)
  part3_gcode.py           <- Part 3: Extrusion math, toolpath, G-code writer  (TODOs)
  part4_analysis.py        <- Part 4: Performance analysis   (TODOs)
  main.py                  <- Main pipelin
  test_functions.py        <- Unit tests for Parts 1-3
  test_all_profiles.py     <- Generate all 4 required profiles
  utility/
    helpers_geom.py        <- Geometry utilities (do not modify)
    helpers_gcode.py       <- G-code utilities (do not modify)
    helpers_viz.py         <- Visualization utilities (do not modify)
  output/                  <- Generated G-code files go here
```

### Provided (Pre-Implemented) Functions

The following functions are already implemented for you:
- **`config.py`** - `LampShadeParams` class with `validate()` method, `PrinterSpecs` class
- **`part1_geometry.py`** -  `lamp_shade_radius_at_height()`, `calculate_radial_wave()` (wave texture formula), `generate_lamp_shade_layers()` (layer collection loop)
- **`part4_analysis.py`** - `compare_profiles()` (runs all profiles and prints comparison table)
- **`main.py`** - Full pipeline entry point

### Deliverables
1. All source files with TODOs completed (no `NotImplementedError` remaining)
2. `output/*.gcode` - All 4 profile G-code files
3.  Technical report with analysis and screenshots

---

## Part 1: Parametric Lamp Shade Geometry 

### Overview
Implement functions to generate parametric lamp shade profiles with different aesthetic and functional characteristics, such as twist rotation and wave textures.

**File:** `part1_geometry.py`

- [ ] `validate_printability()` checks overhang angles
- [ ] `calculate_twist_angle()` supports 3 twist types
- [ ] `generate_lamp_shade_layer()` creates circles with twist/wave
- [ ] Visualization works (`python main.py`)


### Profile Functions 

`lamp_shade_radius_at_height()` has been implemented for you. It calculates the lamp shade radius at any height using four different profile types. Even though it has been implemented for you, please take the time to understand each profile. It will help with the rest of the assignment.

**Profiles:**

1. **Linear** - Straight taper
   ```python
   r(t) = base_radius + t * (top_radius - base_radius)
   ```

2. **Concave** - Curves inward
   ```python
   r(t) = base_radius + t^2 * (top_radius - base_radius)
   ```

3. **Convex** - Curves outward
   ```python
   r(t) = base_radius + t^0.5 * (top_radius - base_radius)
   ```

4. **Sinusoidal** - Gentle decorative waves
   ```python
   amplitude = 0.05 * average_radius
   r(t) = linear_radius + amplitude * sin(4*pi * t)
   ```

**Where:** `t = z / total_height` (normalized height from 0 to 1)


### Task 1.1: Printability Validation

Implement `validate_printability()` to check that profiles respect 3D printing constraints.

**Physical Constraint:** FDM printers can only print overhangs up to 45 degrees without support structures (for PLA).

**Algorithm:**
1. Sample profile at each layer height
2. Calculate dr/dz between consecutive layers
3. Convert slope to angle: `angle = arctan(|dr| / dz)`
4. Return `(False, error_message)` if angle > 45 degrees
5. Return `(True, "Valid")` if all checks pass


### Task 1.2: Twist Angle Calculation

Implement `calculate_twist_angle()` to compute how much each layer rotates around the center.

**Twist Types:**
- `'linear'`: Constant rate. `twist = t * total_twist_rad`
- `'accelerating'`: More twist near top. `twist = t^2 * total_twist_rad`
- `'decelerating'`: More twist near bottom. `twist = (1 - (1-t)^2) * total_twist_rad`

Where `t = z / total_height` and `total_twist_rad = radians(twist_degrees)`.

Return `0.0` if `twist_enabled` is False.


### Task 1.3: Layer Generation

Implement `generate_lamp_shade_layer()` to create a single cross-section polygon at height z, incorporating twist rotation and wave texture.

**Algorithm:**
1. Compute base radius via `lamp_shade_radius_at_height()`
2. Compute twist angle via `calculate_twist_angle()`
3. Generate evenly-spaced angles: `linspace(0, 2*pi, num_points, endpoint=False)`
4. For each angle:
   - Apply twist: `twisted_angle = angle + twist`
   - Compute wave offset: `calculate_radial_wave(angle, z, params)` (provided)
   - Final radius = base_radius + wave_offset
   - Convert to (x, y) using cos/sin with `PrinterSpecs.BED_CENTER`
5. Close polygon with `ensure_closed()`


**Note:** `calculate_radial_wave()` is already implemented for you. When `twist_enabled` and `wave_enabled` are both `False`, this should produce a simple parametric circle.

---

## Part 2: Scanline Infill Algorithm 
### Overview
Implement the scanline algorithm from Lecture 6 to find interior regions of polygons.

**File:** `part2_scanline.py`

- [ ] `scanline_x_intersections()` finds all crossings
- [ ] `even_odd_segments()` pairs correctly
- [ ] Works with both convex and concave shapes


### Task 2.1: Scanline Intersections

*In-class activity from Lecture 6*

Implement `scanline_x_intersections()` to find where a horizontal line intersects a polygon.

**Algorithm:**
1. For each edge of polygon:
   - Check if scanline crosses edge
   - Skip horizontal edges
   - Calculate x-coordinate of intersection using linear interpolation
2. Sort x-coordinates left to right
3. Return sorted list

**Edge Cases:**
- Horizontal edges: Skip (parallel to scanline)
- Vertices: Ensure not double-counted
- Numerical stability: Use epsilon tolerance

### Task 2.2: Even-Odd Segments 

*In-class activity from Lecture 6*

Implement `even_odd_segments()` to pair intersections into inside/outside segments.

**Algorithm:**
- Pair sorted intersections: (x[0], x[1]), (x[2], x[3]), ...
- Return list of 2x2 arrays: `[[x0, y], [x1, y]]`

---

## Part 3: G-code Generation 
### Overview
Generate Prusa MK4S-compatible G-code for spiral lamp shade printing.

**File:** `part3_gcode.py`

- [ ] `extruded_area()` uses capsule model
- [ ] `delta_E_for_move()` calculates correctly
- [ ] `generate_spiral_lamp_shade_toolpath()` creates spiral
- [ ] `write_lamp_shade_gcode()` produces valid G-code with Z monotonicity

### Task 3.1: Extrusion Mathematics (10 points)

*In-class activity from Lecture 7*

**Capsule Model Cross-Section:**

Implement `extruded_area()`:
```
Area = width * height + pi * (height/2)^2
```

Implement `delta_E_for_move()`:
```
Volume = Area * length
E = Volume / (pi * (filament_diameter/2)^2) * flow_multiplier
```

### Task 3.2: Spiral Toolpath

Implement `generate_spiral_lamp_shade_toolpath()` to create a continuous spiral.

**Key idea:** Instead of printing each layer as a closed loop (which leaves a visible seam), spiral mode gradually increases Z within each revolution so the nozzle traces one continuous helix from bottom to top.

**Algorithm (detailed in docstring):**
1. Calculate `z_increment = layer_height / num_points`
2. For each layer, for each perimeter point:
   - `z_current = z_base + i * z_increment`
   - Append `(x, y, z_current)`
3. Remove duplicate closing points if present
4. Return `(M, 3)` numpy array

**Requirements:**
- Z must be monotonically increasing (never decrease)
- Returns `(N, 3)` array of `[x, y, z]` coordinates


### Task 3.3: G-code Writer 

Implement the G-code generation loop inside `write_lamp_shade_gcode()`.

The function scaffolding (header, footer, stats calculation) is provided. You need to implement the main loop that:

1. Iterates through `spiral_path` points (starting from index 1)
2. Enforces Z monotonicity: if `z < prev_z`, clamp to `prev_z`
3. Calculates move distance and extrusion amount (`delta_E_for_move`)
4. Accumulates `total_distance`
5. Emits G1 commands in the format:
   ```
   G1 X{x:.3f} Y{y:.3f} Z{z:.3f} E{dE:.5f} F{speed:.0f}
   ```

**Must Return Stats Dict:**
```python
{
    'generation_time': float,  # seconds
    'file_size': int,          # bytes
    'line_count': int,
    'toolpath_points': int,
    'total_distance': float    # mm
}
```

---

## Part 4: Analysis & Testing 

### Overview
Analyze your lamp shade designs quantitatively and generate all required output files.

**File:** `part4_analysis.py`

- [ ] `analyze_lamp_shade_performance()` returns all 4 metrics
- [ ] All 4 profile G-code files generated
- [ ] All files preview correctly in PrusaSlicer
- [ ] Report completed

### Task 4.1: Performance Analysis 

Implement `analyze_lamp_shade_performance()` to calculate design metrics.

**Required Metrics:**

1. **Max Overhang Angle** 
   - Scan through layers calculating dr/dz between consecutive layers
   - Find maximum angle using `arctan(|dr| / dz)`

2. **Volume Estimate** 
   - Approximate each layer as cylindrical shell
   - `Volume_layer = 2*pi * radius * wall_thickness * layer_height`
   - Sum all layers

3. **Print Time Estimate** 
   - `time = total_distance / print_speed`
   - Add 10% overhead for accelerations
   - Convert to minutes

4. **Material Usage** 
   - `material_grams = volume_mm3 / 1000 * 1.24`
   - (PLA density = 1.24 g/cm^3)

**Must Return:**
```python
{
    'max_overhang_angle': float,    # degrees
    'volume_estimate': float,       # mm^3
    'print_time_estimate': float,   # minutes
    'material_usage': float         # grams
}
```

**Note:** `compare_profiles()` is already implemented for you. It calls your `analyze_lamp_shade_performance()` for each profile type and prints a formatted comparison table.

### Task 4.2: Generate All 4 Profile Types  (REQUIRED)

Generate G-code for **all 4 profile types** with the same base parameters for fair comparison.

**Required Base Parameters (identical for all):**
- Base radius: 30mm
- Top radius: 25mm
- Height: 50mm
- Layer height: 0.20mm
- Line width: 0.48mm

**Required Output Files:**
1. `output/lamp_shade_linear.gcode`
2. `output/lamp_shade_concave.gcode`
3. `output/lamp_shade_convex.gcode`
4. `output/lamp_shade_sinusoidal.gcode`

**How to generate:** Run `python test_all_profiles.py` after implementing all functions.

**Validation:**
- All 4 files open in PrusaSlicer without errors
- Show continuous spiral in preview
- Pass printability validation (no overhang errors)

---

## Report Requirements

### REPORT Must Include:

4. **Performance Analysis**
   - Profile comparison table (from `compare_profiles()`)
   - Discussion of trade-offs:
     - Which profile uses least material?
     - Which prints fastest?
     - Which has highest overhang risk?
   - Recommendation: Best profile for production and why

5. **Screenshots**
   - PrusaSlicer previews of **all 4 profile types**
   - Side-by-side comparison showing visual differences

---

## Submission Instructions

### What to Submit

**D2L**

1. **Code Files**:
   ```
   assignment4_yourname.zip
   +-- config.py
   +-- part1_geometry.py
   +-- part2_scanline.py
   +-- part3_gcode.py
   +-- part4_analysis.py
   +-- main.py
   +-- test_functions.py
   +-- test_all_profiles.py
   +-- utility/
   |   +-- helpers_geom.py (provided, no changes)
   |   +-- helpers_gcode.py (provided, no changes)
   |   +-- helpers_viz.py (provided, no changes)
   +-- output/
       +-- lamp_shade_linear.gcode
       +-- lamp_shade_concave.gcode
       +-- lamp_shade_convex.gcode
       +-- lamp_shade_sinusoidal.gcode
   ```

2. **Report** (`REPORT.md` or `REPORT.pdf`):
   - Report with analysis
   - Screenshots from PrusaSlicer
   - Profile comparison table

### Submission Checklist

Before submitting, verify:
- [ ] All TODO functions implemented (no `NotImplementedError`)
- [ ] Code runs without errors: `python main.py`
- [ ] All 4 profile types generated: `python test_all_profiles.py`
- [ ] All 4 use identical base parameters (30mm base, 25mm top, 50mm height)
- [ ] G-code previews correctly in PrusaSlicer
- [ ] `validate_printability()` catches overhang violations
- [ ] Performance analysis produces reasonable numbers
- [ ] Profile comparison table included in report
- [ ] Screenshots included
- [ ] Report addresses all required sections
- [ ] Files properly named and organized

---

## Resources
- Lecture 6 slides: Scanline algorithms
- Lecture 7 slides: G-code generation
- Lecture 7 supplement: Printability constraints
- Prusa MK4S specifications: https://www.prusa3d.com/mk4s


---

## FAQ

**Q: What if my profile fails printability validation?**
A: Adjust your parameters! Try smaller amplitude for sinusoidal, or less aggressive taper for concave/convex.

**Q: How do I know if my G-code is correct?**
A: Load it in PrusaSlicer (File > Import > Import G-code). It should show a continuous spiral with no errors.

**Q: Why do I need to generate all 4 profiles?**
A: Your performance analysis (Task 4.1) and profile comparison table must be based on actual generated G-code, not theoretical calculations. Generating all 4 with identical parameters ensures a fair comparison.

**Q: My validation test says "Overhang 68 deg at z=15.0mm" - what do I do?**
A: Your profile is too steep! Either reduce the radius change rate, increase height, or choose a gentler profile type.

**Q: What's the difference between `analyze_lamp_shade_performance()` and `compare_profiles()`?**
A: `analyze_lamp_shade_performance()` calculates metrics for one design (you implement this). `compare_profiles()` runs your analysis on multiple profiles and prints a comparison table (provided for you).

---

## Tips for Success

### Test Incrementally
- Use provided `test_functions.py` after each function
   Test As You Go

After implementing each function, test it:
```bash
# Test Part 1 (geometry)
python test_functions.py 1

# Test Part 2 (scanline)
python test_functions.py 2

# Test Part 3 (g-code)
python test_functions.py 3

# Test everything
python test_functions.py all
```

- Test each profile type individually
- Verify G-code in PrusaSlicer frequently
- Run `python main.py` to test the full pipeline
   Once all tests pass:
```bash
# Run the full pipeline for one profile
python main.py

# Generate all 4 required profiles
python test_all_profiles.py
```

### Debug Systematically
- Print intermediate values
- Visualize geometry before G-code generation
- Check one layer at a time
- Use PrusaSlicer preview to spot issues

### Common Pitfalls
- Forgetting to close polygons (first = last point) - use `ensure_closed()`
- Radians vs degrees in angle calculations
- Division by zero in dr/dz
- Z decreasing (violates monotonicity)
- Redundant G-code commands (already in provided header)

