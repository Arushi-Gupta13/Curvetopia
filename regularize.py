import svgpathtools as svg
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, leastsq

def line_to_bezier(start, end):
    # Convert a line to a simple cubic Bézier
    control1 = start + (end - start) / 3
    control2 = start + 2 * (end - start) / 3
    return svg.CubicBezier(start, control1, control2, end)

def fit_line(points):
    def line(x, a, b):
        return a * x + b
    
    x = np.array([p.real for p in points])
    y = np.array([p.imag for p in points])
    
    # Initial guess for line parameters
    a_guess = (y[-1] - y[0]) / (x[-1] - x[0])
    b_guess = y[0] - a_guess * x[0]
    
    try:
        params, _ = curve_fit(line, x, y, p0=[a_guess, b_guess])
    except Exception as e:
        print(f"Error fitting line: {e}")
        return svg.Line(start=complex(x[0], y[0]), end=complex(x[-1], y[-1]))
    
    a, b = params
    return svg.Line(start=complex(x[0], line(x[0], a, b)),
                    end=complex(x[-1], line(x[-1], a, b)))

def fit_square(points):
    # Calculate the centroid of the points
    x = np.array([p.real for p in points])
    y = np.array([p.imag for p in points])
    cx, cy = np.mean(x), np.mean(y)
    
    # Calculate the distances from the centroid to all points
    distances = np.sqrt((x - cx)**2 + (y - cy)**2)
    
    # Estimate the square side length as the average distance multiplied by sqrt(2)
    side_length = 2 * np.mean(distances) / np.sqrt(2)
    
    # Define the corners of the square
    half_side = side_length / 2
    square_points = [
        complex(cx - half_side, cy - half_side),
        complex(cx + half_side, cy - half_side),
        complex(cx + half_side, cy + half_side),
        complex(cx - half_side, cy + half_side),
        complex(cx - half_side, cy - half_side)
    ]
    
    # Create a new path for the square
    return svg.Path(*[svg.Line(start=square_points[i], end=square_points[i+1]) for i in range(4)])

def plot_combined_path(beziers, title):
    plt.figure()
    for bezier in beziers:
        x = [np.real(bezier.start), np.real(bezier.control1), np.real(bezier.control2), np.real(bezier.end)]
        y = [np.imag(bezier.start), np.imag(bezier.control1), np.imag(bezier.control2), np.imag(bezier.end)]
        plt.plot(x, y, 'k-', lw=2)
    plt.title(title)
    plt.axis('equal')
    plt.show()

def process_and_regularize_curves(input_svg, output_svg):
    paths, attributes, svg_attributes = svg.svg2paths2(input_svg)
    
    combined_beziers_before = []
    
    for path in paths:
        beziers = []
        
        for segment in path:
            if isinstance(segment, svg.Line):
                line = fit_line([segment.start, segment.end])
                bezier = line_to_bezier(line.start, line.end)
                beziers.append(bezier)
            elif isinstance(segment, svg.CubicBezier):
                beziers.append(segment)
            elif isinstance(segment, svg.QuadraticBezier):
                beziers.append(segment.to_cubic())
            elif isinstance(segment, svg.Arc):
                # Fit circles to arcs or convert arcs to circles
                circle = fit_circle([p for p in segment.approximate_bezier_path()])
                beziers.append(circle)
            else:
                beziers.append(segment)
                
        # Detect and fit squares (replace with your own detection logic if needed)
        combined_beziers_before.extend(beziers)
        
        # Check for square-like shapes
        for shape in beziers:
            if isinstance(shape, svg.Path):
                points = [seg.start for seg in shape if isinstance(seg, svg.Line)]
                if len(points) == 4:
                    # Assuming a potential square if there are 4 lines
                    square = fit_square(points)
                    combined_beziers_before.append(square)
    
    # Visualize the combined paths without regularization (original structure)
    plot_combined_path(combined_beziers_before, 'Original Path')

    # Apply minimal adjustment if needed
    combined_beziers_after = combined_beziers_before
    
    # Visualize the combined paths after minimal adjustment
    plot_combined_path(combined_beziers_after, 'After Minimal Adjustment')

    # Save the output SVG file with minimal adjustment
    regularized_paths = [svg.Path(*combined_beziers_after)]
    svg.wsvg(regularized_paths, attributes=attributes, svg_attributes=svg_attributes, filename=output_svg)

# Example usage
input_svg_file = 'data/problems/frag1.svg'  # Replace with your actual input file
output_svg_file = 'output_regularized.svg'  # Output file
process_and_regularize_curves(input_svg_file, output_svg_file)
