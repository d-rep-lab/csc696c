import numpy as np
from typing import Sequence


def _polyline_pv(points_xy: np.ndarray, z: float = 0.0):
    pts = np.asarray(points_xy, dtype=float)
    pts3D = np.c_[pts[:, 0], pts[:, 1], np.full(len(pts), float(z))]  # turning in (N,3)
    lines = np.hstack([[len(pts3D)], np.arange(len(pts3D))]).astype(np.int64)
    return pts3D, lines


def visualize_scanline_segments(
    poly_xy: np.ndarray,
    scan_ys: Sequence[float],
    segments: Sequence[np.ndarray],
    title: str = "Scanline + Even-Odd",
) -> None:
    import pyvista as pv

    pv.set_plot_theme("document")
    pl = pv.Plotter(window_size=(1200, 900))
    pl.add_text(title, font_size=12)

    pts3D, lines = _polyline_pv(poly_xy, z=0.0)
    outline = pv.PolyData(pts3D)
    outline.lines = lines
    pl.add_mesh(outline, line_width=5, opacity=0.95)

    xmin, xmax = float(poly_xy[:, 0].min()), float(poly_xy[:, 0].max())
    for y in scan_ys:
        ln = np.array([[xmin, y], [xmax, y]], dtype=float)
        pts3D, lines = _polyline_pv(ln, z=0.0)
        lnd = pv.PolyData(pts3D)
        lnd.lines = lines
        pl.add_mesh(lnd, line_width=2, opacity=0.18)

    for s in segments:
        pts3D, lines = _polyline_pv(s, z=0.0)
        sd = pv.PolyData(pts3D)
        sd.lines = lines
        pl.add_mesh(sd, line_width=8, opacity=0.95, color="orange")

    pl.view_xy()
    pl.show()


def visualize_serpentine_toolpath(
    poly_xy: np.ndarray,
    scan_ys: Sequence[float],
    path_xy: np.ndarray,
    title: str = "Serpentine Infill",
) -> None:
    import pyvista as pv  # type: ignore

    pv.set_plot_theme("document")
    pl = pv.Plotter(window_size=(1200, 900))
    pl.add_text(title, font_size=12)

    pts3D, lines = _polyline_pv(poly_xy, z=0.0)
    outline = pv.PolyData(pts3D)
    outline.lines = lines
    pl.add_mesh(outline, line_width=5, opacity=0.95)

    xmin, xmax = float(poly_xy[:, 0].min()), float(poly_xy[:, 0].max())
    for y in scan_ys:
        ln = np.array([[xmin, y], [xmax, y]], dtype=float)
        pts3D, lines = _polyline_pv(ln, z=0.0)
        lnd = pv.PolyData(pts3D)
        lnd.lines = lines
        pl.add_mesh(lnd, line_width=2, opacity=0.15)

    pts3D, lines = _polyline_pv(path_xy, z=0.0)
    path = pv.PolyData(pts3D)
    path.lines = lines
    pl.add_mesh(path, line_width=9, opacity=0.95, color="orange")

    pl.view_xy()
    pl.show()


def visualize_lamp_shade_preview(layers: list, profile_type: str = ""):
    """
    Visualize lamp shade geometry in 3D using PyVista.
    
    Parameters:
    -----------
    layers : list of dict
        Each dict contains 'z', 'perimeter_xy', 'radius'
    profile_type : str
        Profile type for title
    """
    try:
        import pyvista as pv
    except ImportError:
        print("⚠️  PyVista not installed. Skipping 3D visualization.")
        return
    
    pv.set_plot_theme("document")
    pl = pv.Plotter(window_size=(1200, 900))
    
    title = f"Lamp Shade Preview - {profile_type.capitalize()} Profile"
    pl.add_text(title, font_size=14)
    
    # Draw each layer as a circle
    for layer in layers:
        z = layer['z']
        perimeter = layer['perimeter_xy']
        
        # Create 3D points
        pts3D = np.c_[perimeter[:, 0], perimeter[:, 1], np.full(len(perimeter), z)]
        lines = np.hstack([[len(pts3D)], np.arange(len(pts3D))]).astype(np.int64)
        
        poly = pv.PolyData(pts3D)
        poly.lines = lines
        pl.add_mesh(poly, line_width=3, opacity=0.7, color='steelblue')
    
    # Add vertical lines to show structure
    num_vertical = 8
    for i in range(num_vertical):
        angle = 2 * np.pi * i / num_vertical
        points = []
        for layer in layers:
            r = layer['radius']
            cx, cy = 105.0, 105.0
            x = cx + r * np.cos(angle)
            y = cy + r * np.sin(angle)
            points.append([x, y, layer['z']])
        
        points = np.array(points)
        lines = np.hstack([[len(points)], np.arange(len(points))]).astype(np.int64)
        vert_line = pv.PolyData(points)
        vert_line.lines = lines
        pl.add_mesh(vert_line, line_width=1, opacity=0.3, color='gray')
    
    pl.show()
