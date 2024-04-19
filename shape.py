from vector import Vector4


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

