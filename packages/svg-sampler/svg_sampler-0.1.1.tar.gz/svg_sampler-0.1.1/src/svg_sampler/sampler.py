import sys
import math
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon
from shapely.ops import triangulate, unary_union
from svgpathtools import parse_path
import numpy as np
import matplotlib.pyplot as plt


def parse_float(value, default=0.0):
    """Convert a string to float, returning a default value on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def create_rect(elem):
    """Create a rectangle Polygon from an SVG rect element."""
    x = parse_float(elem.get("x", "0"))
    y = parse_float(elem.get("y", "0"))
    width = parse_float(elem.get("width"))
    height = parse_float(elem.get("height"))
    return Polygon([(x, y), (x + width, y), (x + width, y + height), (x, y + height)])


def create_circle(elem, num_points=100):
    """Create a circular Polygon approximated by num_points from an SVG circle element."""
    cx = parse_float(elem.get("cx"))
    cy = parse_float(elem.get("cy"))
    r = parse_float(elem.get("r"))
    points = [
        (cx + r * math.cos(2 * math.pi * i / num_points),
         cy + r * math.sin(2 * math.pi * i / num_points))
        for i in range(num_points)
    ]
    return Polygon(points)


def create_ellipse(elem, num_points=100):
    """Create an elliptical Polygon approximated by num_points from an SVG ellipse element."""
    cx = parse_float(elem.get("cx"))
    cy = parse_float(elem.get("cy"))
    rx = parse_float(elem.get("rx"))
    ry = parse_float(elem.get("ry"))
    points = [
        (cx + rx * math.cos(2 * math.pi * i / num_points),
         cy + ry * math.sin(2 * math.pi * i / num_points))
        for i in range(num_points)
    ]
    return Polygon(points)


def create_polygon(elem):
    """Create a Polygon from an SVG polygon element."""
    points_str = elem.get("points")
    points = []
    for pair in points_str.strip().split():
        coords = pair.split(',') if ',' in pair else pair.split()
        if len(coords) >= 2:
            x, y = map(float, coords[:2])
            points.append((x, y))
    return Polygon(points)


def create_path(elem, num_points=100):
    """Create a Polygon from an SVG path element.
    
    Returns None if the path is not continuous or not closed.
    """
    d = elem.get("d")
    path = parse_path(d)
    if not path.iscontinuous():
        return None
    if not path.isclosed():
        if abs(path.start - path.end) > 1e-6:
            return None
    points = [complex(path.point(t)) for t in np.linspace(0, 1, num_points + 1)]
    pts = [(pt.real, pt.imag) for pt in points]
    return Polygon(pts)


def parse_style(style_str):
    """Parse a style string into a dictionary of properties."""
    styles = {}
    for part in style_str.split(';'):
        if ':' in part:
            key, value = part.split(':', 1)
            styles[key.strip()] = value.strip()
    return styles


def extract_geometry(elem):
    """Extract the geometry and fill color from an SVG element.
    
    Returns a tuple (geometry, fill) or (None, None) if no valid fill is found.
    """
    tag = elem.tag.split('}')[-1]
    fill = elem.get("fill")
    if fill is None:
        style = elem.get("style")
        if style:
            style_dict = parse_style(style)
            fill = style_dict.get("fill")
    if fill is None or fill.lower() == "none":
        return None, None
    geometry = None
    if tag == "rect":
        geometry = create_rect(elem)
    elif tag == "circle":
        geometry = create_circle(elem)
    elif tag == "ellipse":
        geometry = create_ellipse(elem)
    elif tag == "polygon":
        geometry = create_polygon(elem)
    elif tag == "path":
        geometry = create_path(elem)
    return geometry, fill


def traverse_svg(elem):
    """Recursively traverse the SVG XML and extract geometries and fill colors."""
    shapes = []
    geometry, fill = extract_geometry(elem)
    if geometry is not None:
        shapes.append((geometry, fill))
    for child in elem:
        shapes.extend(traverse_svg(child))
    return shapes


def get_shapes_from_svg(path):
    """Parse an SVG file and return a list of (geometry, fill) tuples."""
    tree = ET.parse(path)
    root = tree.getroot()
    shapes = traverse_svg(root)
    return shapes


def interior_triangles(polygon, tol=1e-10):
    """Return triangles (as Polygons) that are completely inside the given polygon."""
    all_triangles = triangulate(polygon)
    interior = []
    for tri in all_triangles:
        clipped = tri.intersection(polygon)
        if clipped.is_empty:
            continue
        if clipped.geom_type == 'Polygon':
            coords = list(clipped.exterior.coords)
            if len(coords) - 1 == 3:
                if abs(clipped.area - tri.area) < tol:
                    interior.append(clipped)
    return interior


def triangulation_sampling(polygon, num_samples, *, rng):
    """
    Sample points uniformly from within a polygon using its triangulation.
    
    Parameters:
        polygon (Polygon): The polygon to sample from.
        num_samples (int): The total number of sample points.
        rng (np.random.Generator): A NumPy random Generator instance.
        
    Returns:
        pts (ndarray): An array of shape (num_samples, 2) with sampled (x, y) points.
    """
    triangles = interior_triangles(polygon)
    n_tri = len(triangles)
    if n_tri == 0:
        raise ValueError("No interior triangles found; check the polygon geometry.")
    triangle_vertices = []
    areas = []
    for tri in triangles:
        coords = list(tri.exterior.coords)[:3]
        triangle_vertices.append(coords)
        areas.append(tri.area)
    triangle_vertices = np.array(triangle_vertices)
    areas = np.array(areas)
    cum_areas = np.cumsum(areas)
    total_area = cum_areas[-1]
    r = rng.uniform(0, total_area, num_samples)
    indices = np.searchsorted(cum_areas, r)
    u = rng.random(num_samples)
    v = rng.random(num_samples)
    mask = u + v > 1
    u[mask] = 1 - u[mask]
    v[mask] = 1 - v[mask]
    A = triangle_vertices[indices, 0, :]
    B = triangle_vertices[indices, 1, :]
    C = triangle_vertices[indices, 2, :]
    pts = A + np.expand_dims(u, axis=1) * (B - A) + np.expand_dims(v, axis=1) * (C - A)
    return pts


def resolve_overlaps_upper_only(shapes):
    """
    Resolve overlapping shapes such that for any overlapping region only the top (layerwise upper)
    shape is retained.
    
    Parameters:
        shapes: List of (geometry, fill) tuples in drawing order (first = bottom, last = top).
    
    Returns:
        A new list of (geometry, fill) tuples where overlapping parts have been removed from lower layers.
    """
    resolved = []
    union_upper = None
    for geometry, fill in reversed(shapes):

        if not geometry.is_valid:
            geometry = geometry.buffer(0)

        if union_upper is not None:
            
            if not union_upper.is_valid:
                union_upper = union_upper.buffer(0)
            try:
                geometry = geometry.difference(union_upper)
            except Exception as e:
                # Attempt to clean both geometries and try again
                geometry = geometry.buffer(0).difference(union_upper.buffer(0))

        if not geometry.is_empty:
            resolved.append((geometry, fill))
            # Update union_upper with the current geometry
            if union_upper is None:
                union_upper = geometry
            else:
                union_upper = unary_union([union_upper, geometry])
                if not union_upper.is_valid:
                    union_upper = union_upper.buffer(0)

    resolved.reverse()
    return resolved


def sample_from_svg(path, total_samples, sample_setting="equal_over_classes",
                    overlap_mode="all", normalize=False, *, seed):
    """
    Sample points from an SVG file's filled shapes.
    
    Parameters:
      path (str): Path to the SVG file.
      total_samples (int): Total number of points to sample.
      sample_setting (str): One of:
         - "equal_over_classes": Union shapes of the same fill and sample equally per color.
         - "equal_over_shapes": Sample equally from each individual shape.
         - "based_on_area": Allocate samples proportionally to the area of the union of shapes per color.
      overlap_mode (str): One of:
         - "all": Sample from all classes even if they overlap.
         - "upper_only": In overlapping regions, only sample from the layerwise upper (top) shape.
      normalize (bool): If True, normalize the X coordinates per axis to [0, 1].
      seed (int): Seed for random number generation.
    
    Returns:
      X (ndarray): Sampled points of shape (N, 2).
      y (ndarray): Numeric class labels corresponding to each point.
    """
    rng = np.random.default_rng(seed)
    s = get_shapes_from_svg(path)
    if overlap_mode == "upper_only":
        s = resolve_overlaps_upper_only(s)
    shape_groups = {}
    for shape, color in s:
        shape_groups.setdefault(color, []).append(shape)
    if sample_setting == "equal_over_classes":
        union_groups = {color: unary_union(shapes) for color, shapes in shape_groups.items()}
        n_classes = len(union_groups)
        samples_per_class = int(total_samples / n_classes)
        X_list, y_list = [], []
        label_dict = {color: i for i, color in enumerate(union_groups.keys())}
        for color, union in union_groups.items():
            pts = triangulation_sampling(union, samples_per_class, rng=rng)
            X_list.append(pts)
            y_list.append(np.full(pts.shape[0], label_dict[color]))
        X, y = np.concatenate(X_list, axis=0), np.concatenate(y_list, axis=0)
    elif sample_setting == "equal_over_shapes":
        n_shapes = len(s)
        samples_per_shape = int(total_samples / n_shapes)
        X_list, y_list = [], []
        label_dict = {}
        for shape, color in s:
            if color not in label_dict:
                label_dict[color] = len(label_dict)
        for shape, color in s:
            pts = triangulation_sampling(shape, samples_per_shape, rng=rng)
            X_list.append(pts)
            y_list.append(np.full(pts.shape[0], label_dict[color]))
        X, y = np.concatenate(X_list, axis=0), np.concatenate(y_list, axis=0)
    elif sample_setting == "based_on_area":
        union_groups = {color: unary_union(shapes) for color, shapes in shape_groups.items()}
        total_area = sum(union.area for union in union_groups.values())
        X_list, y_list = [], []
        label_dict = {color: i for i, color in enumerate(union_groups.keys())}
        for color, union in union_groups.items():
            n_samples = int(round(total_samples * union.area / total_area))
            pts = triangulation_sampling(union, n_samples, rng=rng)
            X_list.append(pts)
            y_list.append(np.full(pts.shape[0], label_dict[color]))
        X, y = np.concatenate(X_list, axis=0), np.concatenate(y_list, axis=0)
    else:
        raise ValueError(f"Chosen sampling setting '{sample_setting}' does not exist.")
    
    if normalize:
        min_x, max_x = X[:, 0].min(), X[:, 0].max()
        min_y, max_y = X[:, 1].min(), X[:, 1].max()
        if max_x - min_x > 0:
            X[:, 0] = (X[:, 0] - min_x) / (max_x - min_x)
        if max_y - min_y > 0:
            X[:, 1] = (X[:, 1] - min_y) / (max_y - min_y)
    
    return X, y


if __name__ == '__main__':
    # Example usage:
    # Provide a seed to ensure reproducibility.
    X, y = sample_from_svg("your_svg_file.svg", total_samples=1000, seed=42)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap="viridis")
    plt.show()
