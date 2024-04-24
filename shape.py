from vector import Vector4
import numpy as np


class Shape:
    lines: list[tuple[Vector4, Vector4]]

    def __init__(self, lines: list[tuple[Vector4, Vector4]]):
        self.lines = lines

    def copy(self):
        return Shape([(point1.copy(), point2.copy()) for point1, point2 in self.lines])

    def set_offset(self, offset: Vector4):
        for p1, p2 in self.lines:
            p1.set_offset(offset)
            p2.set_offset(offset)

    @staticmethod
    def read_shape_from_file(filename: str) -> 'Shape':
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
