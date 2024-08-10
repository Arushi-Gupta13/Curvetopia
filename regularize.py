import numpy as np
from svgpathtools import svg2paths, Line, CubicBezier, Path
import matplotlib.pyplot as plt

def svg_to_segments(svg_path):
    paths, _ = svg2paths(svg_path)
    segments = []
    for path in paths:
        for segment in path:
            if isinstance(segment, (Line, CubicBezier)):
                segments.append(segment)
    print(f"Total segments extracted: {len(segments)}")
    return segments

def is_straight_line(segment, tolerance=0.01):
    if isinstance(segment, Line):
        return True
    if isinstance(segment, CubicBezier):
        # Check if control points are close to the line between start and end
        line_vector = segment.end - segment.start
        control1_vector = segment.control1 - segment.start
        control2_vector = segment.control2 - segment.start
        
        t1 = np.real(control1_vector * line_vector.conjugate()) / abs(line_vector)**2
        t2 = np.real(control2_vector * line_vector.conjugate()) / abs(line_vector)**2
        
        distance1 = abs(control1_vector - t1 * line_vector)
        distance2 = abs(control2_vector - t2 * line_vector)
        
        return max(distance1, distance2) / abs(line_vector) < tolerance
    return False

def straighten_line(segment):
    if isinstance(segment, Line):
        return segment
    if isinstance(segment, CubicBezier):
        return Line(segment.start, segment.end)

def regularize_segments(segments):
    regularized_segments = []
    for segment in segments:
        if is_straight_line(segment):
            regularized_segments.append(straighten_line(segment))
        else:
            regularized_segments.append(segment)
    
    print(f"Regularized segments: {len(regularized_segments)}")
    return regularized_segments

def plot_segments(segments):
    fig, ax = plt.subplots(figsize=(6, 6))
    for segment in segments:
        if isinstance(segment, Line):
            points = np.array([segment.start, segment.end])
        elif isinstance(segment, CubicBezier):
            t = np.linspace(0, 1, 100)
            points = np.array([segment.point(ti) for ti in t])
        ax.plot(points.real, points.imag, 'k-', linewidth=2)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()

def save_segments_to_svg(segments, svg_path, size):
    import svgwrite
    dwg = svgwrite.Drawing(svg_path, size=(size, size))
    for segment in segments:
        if isinstance(segment, Line):
            dwg.add(dwg.line(start=(segment.start.real, segment.start.imag),
                             end=(segment.end.real, segment.end.imag),
                             stroke='black', stroke_width=2))
        elif isinstance(segment, CubicBezier):
            path = dwg.path(d=f'M {segment.start.real},{segment.start.imag} '
                            f'C {segment.control1.real},{segment.control1.imag} '
                            f'{segment.control2.real},{segment.control2.imag} '
                            f'{segment.end.real},{segment.end.imag}',
                            stroke='black', fill='none', stroke_width=2)
            dwg.add(path)
    dwg.save()

if __name__ == "__main__":
    input_svg = "/Users/arushigarg/Downloads/problems 2/frag0.svg"  // add path to your input svg
    output_svg = "regularized_output.svg"
    
    try:
        segments = svg_to_segments(input_svg)
        regularized_segments = regularize_segments(segments)
        
        if regularized_segments:
            plot_segments(regularized_segments)
            save_segments_to_svg(regularized_segments, output_svg, 100)
            print(f"Regularized SVG saved to {output_svg}")
        else:
            print("No valid segments found in the input SVG.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
