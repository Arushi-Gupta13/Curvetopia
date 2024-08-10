import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from svgpathtools import parse_path, Path, Line, CubicBezier, svg2paths2
import svgwrite
import matplotlib.colors as mcolors

from custom_logger import DSLogger


logger = DSLogger(__name__)


# Function to convert a line to a cubic Bézier curve with almost straight control points
def line_to_bezier(line):
    return CubicBezier(
        line.start,
        line.start + (line.end - line.start) * 0.3,
        line.start + (line.end - line.start) * 0.7,
        line.end,
    )


# # Function to fit a cubic Bézier curve to a given set of points
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


def is_mostly_straight(bezier, threshold=0.01):
    t_values = np.linspace(0, 1, 10)
    points = np.array([bezier.point(t) for t in t_values])
    
    # Ensure points are 2D
    if points.ndim == 1:
        points = points.reshape(-1, 2)
    
    start = points[0]
    end = points[-1]
    
    # Calculate vector from start to end
    vector = end - start
    
    # Calculate perpendicular distances
    distances = np.abs(np.cross(vector, start - points)) / np.linalg.norm(vector)
    
    return np.max(distances) < threshold


def has_single_kink(bezier, threshold=0.01):
    t_values = np.linspace(0, 1, 10)
    points = np.array([bezier.point(t) for t in t_values])
    
    # Ensure points are 2D
    if points.ndim == 1:
        points = points.reshape(-1, 2)
    
    start = points[0]
    end = points[-1]
    
    # Calculate vector from start to end
    vector = end - start
    
    # Calculate perpendicular distances
    distances = np.abs(np.cross(vector, start - points)) / np.linalg.norm(vector)
    
    return np.sum(distances > threshold) == 1



def is_almost_right_angle(bezier, angle_threshold=10, straightness_threshold=0.05):
    # Check if the angle between start-control1-end or start-control2-end is close to 90 degrees
    angle1 = calculate_angle(bezier.start, bezier.control1, bezier.end)
    angle2 = calculate_angle(bezier.start, bezier.control2, bezier.end)
    
    is_right_angle = (abs(angle1 - 90) < angle_threshold) or (abs(angle2 - 90) < angle_threshold)
    is_straight = is_mostly_straight(bezier, straightness_threshold)
    
    return is_right_angle and is_straight

def calculate_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    dot_product = np.real(np.dot(v1, v2.conjugate()))
    magnitudes = np.abs(v1) * np.abs(v2)
    cos_angle = dot_product / magnitudes
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    return np.degrees(angle)

def create_right_angle_curve(bezier):
    # Determine which control point is closer to forming a right angle
    angle1 = calculate_angle(bezier.start, bezier.control1, bezier.end)
    angle2 = calculate_angle(bezier.start, bezier.control2, bezier.end)
    
    if abs(angle1 - 90) < abs(angle2 - 90):
        right_angle_point = bezier.control1
    else:
        right_angle_point = bezier.control2

    line1 = Line(bezier.start, right_angle_point)
    line2 = Line(right_angle_point, bezier.end)

    return [line1, line2]

def is_low_curvature(bezier, threshold=0.004):
    t_values = [0.25, 0.5, 0.75]
    curvatures = [abs(bezier.curvature(t)) for t in t_values]
    return max(curvatures) < threshold


def is_right_angle(p1, p2, p3, threshold=5):
    v1 = p1 - p2
    v2 = p3 - p2
    dot_product = np.real(np.dot(v1, v2.conjugate()))
    magnitudes = np.abs(v1) * np.abs(v2)
    cos_angle = dot_product / magnitudes
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    return abs(np.degrees(angle) - 90) < threshold


def regularize_curve(
    beziers, angle_threshold=40, curvature_threshold=0.004, straightness_threshold=0.05
):
    regularized_beziers = []

    for bezier in beziers:
        logger.print_bhagwa(f"Bezier: {bezier} \n\n")

        if isinstance(bezier, Line):
            logger.print_red(f"Line: ETHE \n\n")
            regularized_beziers.append(bezier)
        elif isinstance(bezier, CubicBezier):
            logger.print_pink(f"Line: ETHE \n\n")
            is_ra = is_almost_right_angle(bezier, angle_threshold, straightness_threshold)
            logger.print_bhagwa(f"is_ra: {is_ra} \n\n")
            if is_ra:
                right_angle_lines = create_right_angle_curve(bezier)
                regularized_beziers.extend(right_angle_lines)
            elif is_low_curvature(bezier, curvature_threshold):
                regularized_beziers.append(Line(bezier.start, bezier.end))
            else:
                subdivided = subdivide_bezier(bezier)
                regularized_beziers.extend(subdivided)

    return regularized_beziers


def subdivide_bezier(bezier, num_subdivisions=2):
    subdivided = []
    for i in range(num_subdivisions):
        t = (i + 1) / (num_subdivisions + 1)
        left, right = bezier.split(t)
        subdivided.append(left)
    subdivided.append(right)
    return subdivided


def plot_beziers(beziers):
    fig, ax = plt.subplots(figsize=(6, 6))
    color = 'black'
    linewidth = 8  # Increased linewidth for thicker strokes

    for bezier in beziers:
        if isinstance(bezier, list):
            for line in bezier:
                points = [line.start, line.end]
                points = np.array([[p.real, p.imag] for p in points])
                ax.plot(points[:, 0], points[:, 1], '-', color=color, linewidth=linewidth)
        elif isinstance(bezier, CubicBezier):
            points = [bezier.start, bezier.control1, bezier.control2, bezier.end]
            points = np.array([[p.real, p.imag] for p in points])
            ax.plot(points[:, 0], points[:, 1], '-', color=color, linewidth=linewidth)
        else:  # Line
            points = [bezier.start, bezier.end]
            points = np.array([[p.real, p.imag] for p in points])
            ax.plot(points[:, 0], points[:, 1], '-', color=color, linewidth=linewidth)

    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()


def save_beziers_to_svg(beziers, svg_path):
    dwg = svgwrite.Drawing(svg_path, profile="tiny")
    colors = list(mcolors.TABLEAU_COLORS.values())

    for i, bezier in enumerate(beziers):
        color = colors[i % len(colors)]
        if isinstance(bezier, list):  # Handle right angle case
            for line in bezier:
                dwg.add(
                    dwg.line(
                        start=(line.start.real, line.start.imag),
                        end=(line.end.real, line.end.imag),
                        stroke=color,
                        fill="none",
                        stroke_width=2,
                    )
                )
        elif isinstance(bezier, CubicBezier):
            path_data = "M {} {} C {} {}, {} {}, {} {}".format(
                round(bezier.start.real, 3),
                round(bezier.start.imag, 3),
                round(bezier.control1.real, 3),
                round(bezier.control1.imag, 3),
                round(bezier.control2.real, 3),
                round(bezier.control2.imag, 3),
                round(bezier.end.real, 3),
                round(bezier.end.imag, 3),
            )
            dwg.add(dwg.path(d=path_data, stroke=color, fill="none", stroke_width=2))
        else:  # Line
            dwg.add(
                dwg.line(
                    start=(bezier.start.real, bezier.start.imag),
                    end=(bezier.end.real, bezier.end.imag),
                    stroke=color,
                    fill="none",
                    stroke_width=2,
                )
            )

    dwg.save()


if __name__ == "__main__":
    # Example usage with an input SVG file
    input_svg = "data/problems/isolated.svg"
    output_svg = "regularized_output.svg"

    beziers = svg_to_beziers(input_svg)
    regularized_beziers = regularize_curve(beziers)

    plot_beziers(regularized_beziers)
    save_beziers_to_svg(regularized_beziers, output_svg)