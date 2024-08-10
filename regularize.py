import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from svgpathtools import parse_path, Path, Line, CubicBezier, svg2paths2
import svgwrite

# Function to convert a line to a cubic Bézier curve with almost straight control points
def line_to_bezier(line):
    return CubicBezier(line.start, line.start + (line.end - line.start) * 0.3,
                       line.start + (line.end - line.start) * 0.7, line.end)

# Function to fit a cubic Bézier curve to a given set of points
def fit_cubic_bezier(points):
    points = np.array(points)
    if points.ndim == 1:
        points = points.reshape(-1, 2)
    
    tck, u = splprep([points[:, 0], points[:, 1]], k=3, s=0)
    u_new = np.linspace(u.min(), u.max(), len(points))
    x_new, y_new = splev(u_new, tck)
    bezier_points = np.column_stack([x_new, y_new])
    return bezier_points

# Function to convert SVG paths to Bézier curves
def svg_to_beziers(svg_file):
    paths, attributes, _ = svg2paths2(svg_file)
    beziers = []
    
    for path in paths:
        for segment in path:
            if isinstance(segment, Line):
                # Convert line segment to Bézier curve
                bezier = line_to_bezier(segment)
            elif isinstance(segment, CubicBezier):
                bezier = segment
            else:
                continue
            
            beziers.append(bezier)
    
    return beziers

# Function to regularize a curve by fitting cubic Bézier curves
def regularize_curve(beziers):
    regularized_beziers = []
    
    for bezier in beziers:
        points = [bezier.start, bezier.control1, bezier.control2, bezier.end]
        points = [(p.real, p.imag) for p in points]  # Ensure points are 2D
        fitted_points = fit_cubic_bezier(points)
        new_bezier = CubicBezier(complex(*fitted_points[0]), complex(*fitted_points[1]),
                                 complex(*fitted_points[2]), complex(*fitted_points[3]))
        regularized_beziers.append(new_bezier)
    
    return regularized_beziers

# Function to plot Bézier curves
def plot_beziers(beziers):
    fig, ax = plt.subplots()
    
    for bezier in beziers:
        points = [bezier.start, bezier.control1, bezier.control2, bezier.end]
        points = np.array([[p.real, p.imag] for p in points])
        ax.plot(points[:, 0], points[:, 1], 'o-', color='black')  # Ensure all lines and dots are black
    
    plt.show()

# Function to save Bézier curves to SVG
def save_beziers_to_svg(beziers, svg_path):
    dwg = svgwrite.Drawing(svg_path, profile='tiny')
    for bezier in beziers:
        # Construct the path data string for SVG
        path_data = 'M {} {} C {} {}, {} {}, {} {}'.format(
            round(bezier.start.real, 3), round(bezier.start.imag, 3),
            round(bezier.control1.real, 3), round(bezier.control1.imag, 3),
            round(bezier.control2.real, 3), round(bezier.control2.imag, 3),
            round(bezier.end.real, 3), round(bezier.end.imag, 3)
        )
        # Add the path to the SVG drawing
        dwg.add(dwg.path(d=path_data, stroke='black', fill='none'))
    
    dwg.save()

# Example usage with an input SVG file
input_svg = 'data/problems/frag0.svg'  # Replace with your SVG file path
output_svg = 'regularized_output.svg'  # Path to save the output SVG

beziers = svg_to_beziers(input_svg)
regularized_beziers = regularize_curve(beziers)

# Plot the regularized Bézier curves
plot_beziers(regularized_beziers)

# Save the regularized Bézier curves to an SVG file
save_beziers_to_svg(regularized_beziers, output_svg)