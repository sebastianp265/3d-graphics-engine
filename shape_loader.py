import numpy as np

from shape import Shape
from vector import Vector4


def read_object_from_file(filename: str):
    with open(filename, "r") as f:
        num_of_points = int(f.readline())
        points = {}

        for _ in range(num_of_points):
            args = f.readline().strip().split()
            points[args[0]] = np.array([[float(x)] for x in args[1:4] + [1]])

        num_of_lines = int(f.readline())
        lines = []
        for _ in range(num_of_lines):
            args = f.readline().strip().split()
            lines.append((Vector4(points[args[0]].copy()),
                          Vector4(points[args[1]].copy())))

        return Shape(lines)
