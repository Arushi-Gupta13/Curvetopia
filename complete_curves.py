import numpy as np
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, CubicBezier, Line, QuadraticBezier
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, nearest_points
from scipy.spatial import cKDTree

def svg_to_segments(svg_file):
    paths, _, _ = svg2paths2(svg_file)
    segments = []
    for path in paths:
        for segment in path:
            if isinstance(segment, (CubicBezier, Line, QuadraticBezier)):
                segments.append(segment)
    return segments

def segments_to_lines(segments, num_points=100):
    lines = []
    for segment in segments:
        t = np.linspace(0, 1, num_points)
        points = np.array([segment.point(ti) for ti in t])
        line = LineString([(float(p.real), float(p.imag)) for p in points])
        lines.append(line)
    return lines

def connect_nearby_endpoints(lines, max_distance=10):
    merged = linemerge(lines)
    if isinstance(merged, LineString):
        return [merged]
    
    endpoints = []
    for line in merged.geoms:
        endpoints.extend([Point(line.coords[0]), Point(line.coords[-1])])
    
    tree = cKDTree([(p.x, p.y) for p in endpoints])
    
    connections = []
    for i, p in enumerate(endpoints):
        distances, indices = tree.query((p.x, p.y), k=2)
        if distances[1] <= max_distance and indices[1] != i:
            connections.append(LineString([p, endpoints[indices[1]]]))
    
    return list(linemerge(list(merged.geoms) + connections).geoms)

def complete_curves(lines, max_distance=10):
    connected_lines = connect_nearby_endpoints(lines, max_distance)
    return connected_lines

svg_file_path = "data/problems/occlusion2_rec.svg"
segments = svg_to_segments(svg_file_path)
lines = segments_to_lines(segments)

completed_curves = complete_curves(lines)

plt.figure(figsize=(10, 10))

for curve in completed_curves:
    x, y = curve.xy
    plt.plot(x, y, color='blue')

plt.axis('equal')
plt.title("Completed Curves")
plt.savefig("completed_curves.png")
plt.show()