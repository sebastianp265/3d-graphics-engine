from vector import Vector4
import numpy as np


class Shape:
    triangles: list[tuple[Vector4, Vector4, Vector4]]

    def __init__(self, triangles: list[tuple[Vector4, Vector4, Vector4]]):
        self.triangles = triangles

    def copy(self):
        return Shape([(point1.copy(), point2.copy(), point3.copy()) for point1, point2, point3 in self.triangles])

    def set_offset(self, offset: Vector4):
        for p0, p1, p2 in self.triangles:
            p0.set_offset(offset)
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
            triangles = []
            for _ in range(num_of_lines):
                args = f.readline().strip().split()
                triangles.append((Vector4(points[args[0]].copy()),
                                  Vector4(points[args[1]].copy()),
                                  Vector4(points[args[2]].copy())))

            return Shape(triangles)
