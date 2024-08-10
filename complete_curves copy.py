import numpy as np
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, CubicBezier
import svgwrite
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import unary_union

# Function to extract Bézier curves from SVG
def svg_to_beziers(svg_file):
    paths, _, _ = svg2paths2(svg_file)
    beziers = []
    
    for path in paths:
        for segment in path:
            if isinstance(segment, CubicBezier):
                beziers.append(segment)
    
    return beziers

# Function to convert Bézier curves to line segments
def bezier_to_lines(beziers, num_points=100):
    lines = []
    for bezier in beziers:
        t = np.linspace(0, 1, num_points)
        points = np.array([bezier.point(ti) for ti in t])
        line = LineString([(float(p.real), float(p.imag)) for p in points])
        lines.append(line)
    return lines

# Function to detect gaps between lines
def detect_gaps(lines):
    if not lines:
        return MultiLineString([])

    multi_line = unary_union(lines)
    if isinstance(multi_line, LineString):
        multi_line = MultiLineString([multi_line])
    
    return multi_line

# Function to create a polygon from detected gaps
def create_polygon_from_gaps(detected_gaps):
    if detected_gaps.is_empty:
        return None

    # Convert MultiLineString to a list of coordinates
    coords = []
    if detected_gaps.geom_type == 'MultiLineString':
        for line in detected_gaps.geoms:
            coords.extend(list(line.coords))
        if coords:
            coords.append(coords[0])  # Ensure the polygon is closed

    # Create a polygon from the coordinates
    try:
        polygon = Polygon(coords)
        if polygon.is_valid:
            return polygon
        else:
            return None
    except Exception as e:
        print(f"Error creating polygon: {e}")
        return None

# Function to convert Polygon to Bézier curves (simplified for this example)
def polygon_to_beziers(polygon):
    beziers = []
    exterior_coords = list(polygon.exterior.coords)
    for i in range(len(exterior_coords) - 1):
        start = exterior_coords[i]
        end = exterior_coords[i + 1]
        bezier = CubicBezier(complex(start[0], start[1]), complex(start[0], start[1]), complex(end[0], end[1]), complex(end[0], end[1]))
        beziers.append(bezier)
    return beziers

# Function to complete curves by filling gaps
def complete_curves(beziers):
    lines = bezier_to_lines(beziers)
    detected_gaps = detect_gaps(lines)
    polygon = create_polygon_from_gaps(detected_gaps)
    if polygon:
        completed_beziers = polygon_to_beziers(polygon)
    else:
        completed_beziers = []
    return completed_beziers

# Function to plot Bézier curves
def plot_beziers(beziers):
    fig, ax = plt.subplots()
    
    for bezier in beziers:
        t = np.linspace(0, 1, 100)
        points = np.array([bezier.point(ti) for ti in t])
        ax.plot(points[:, 0], points[:, 1], 'o-', color='black')  # Ensure all lines and dots are black
    
    plt.show()

# Function to save Bézier curves to SVG
def save_beziers_to_svg(beziers, svg_path):
    dwg = svgwrite.Drawing(svg_path, profile='tiny')
    for bezier in beziers:
        path_data = 'M {} {} C {} {}, {} {}, {} {}'.format(
            round(bezier.start.real, 3), round(bezier.start.imag, 3),
            round(bezier.control1.real, 3), round(bezier.control1.imag, 3),
            round(bezier.control2.real, 3), round(bezier.control2.imag, 3),
            round(bezier.end.real, 3), round(bezier.end.imag, 3)
        )
        dwg.add(dwg.path(d=path_data, stroke='black', fill='none'))
    
    dwg.save()

# Example usage with an input SVG file
input_svg = 'data\problems\occlusion2_rec.svg'  # Replace with your SVG file path
output_svg = 'completed_curves_output.svg'  # Path to save the output SVG

# Convert SVG paths to Bézier curves
beziers = svg_to_beziers(input_svg)

# Complete the curves
completed_beziers = complete_curves(beziers)

# Plot the completed Bézier curves
plot_beziers(completed_beziers)

# Save the completed Bézier curves to an SVG file
save_beziers_to_svg(completed_beziers, output_svg)
