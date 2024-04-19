from math import sin, cos
import math

from matrix import Matrix4
from vector import Vector4


class Camera:
    STARTING_POSITION = Vector4.from_cords(0, 0, -2, 0)
    POSITION_DELTA = 0.5
    X_POSITION_DELTA_VECTOR = Vector4.from_cords(POSITION_DELTA, 0, 0, 1)
    Y_POSITION_DELTA_VECTOR = Vector4.from_cords(0, POSITION_DELTA, 0, 1)
    Z_POSITION_DELTA_VECTOR = Vector4.from_cords(0, 0, POSITION_DELTA, 1)

    STARTING_ORIENTATION = [0, 0, 0]
    ORIENTATION_DELTA = 5

    FOV_DELTA = 10
    STARTING_FOV_DEGREES = 90

    Z_FAR = 100
    Z_NEAR = 0.1

    fov: int
    position: Vector4
    orientation: list[float]

    screen_width: int
    screen_height: int
    aspect_ratio: float

    def __init__(self, screen_width: int, screen_height: int):
        self.position = self.STARTING_POSITION
        self.orientation = self.STARTING_ORIENTATION
        self.fov = self.STARTING_FOV_DEGREES
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.aspect_ratio = self.screen_width / self.screen_height

    def zoom_in(self):
        self.fov -= self.FOV_DELTA
        self.fov = max(self.fov, 10)

    def zoom_out(self):
        self.fov += self.FOV_DELTA
        self.fov = min(self.fov, 170)

    def rotate_right(self):
        self.orientation[2] += self.ORIENTATION_DELTA

    def rotate_left(self):
        self.orientation[2] -= self.ORIENTATION_DELTA

    def look_up(self):
        self.orientation[0] += self.ORIENTATION_DELTA

    def look_down(self):
        self.orientation[0] -= self.ORIENTATION_DELTA

    def look_right(self):
        self.orientation[1] += self.ORIENTATION_DELTA

    def look_left(self):
        self.orientation[1] -= self.ORIENTATION_DELTA

    def move_right(self):
        self.position += self.get_rotation_matrix().multiply_by_vector(self.X_POSITION_DELTA_VECTOR)

    def move_left(self):
        self.position -= self.get_rotation_matrix().multiply_by_vector(self.X_POSITION_DELTA_VECTOR)

    def move_front(self):
        self.position += self.get_rotation_matrix().multiply_by_vector(self.Z_POSITION_DELTA_VECTOR)

    def move_back(self):
        self.position -= self.get_rotation_matrix().multiply_by_vector(self.Z_POSITION_DELTA_VECTOR)

    def move_up(self):
        self.position -= self.get_rotation_matrix().multiply_by_vector(self.Y_POSITION_DELTA_VECTOR)

    def move_down(self):
        self.position += self.get_rotation_matrix().multiply_by_vector(self.Y_POSITION_DELTA_VECTOR)

    def get_view_matrix(self):
        view_matrix = self.get_rotation_matrix().transpose()

        u = view_matrix.get_row(0)
        v = view_matrix.get_row(1)
        w = view_matrix.get_row(2)

        view_matrix.set(0, 3, -Vector4.dot_product_xyz(u, self.position))
        view_matrix.set(1, 3, -Vector4.dot_product_xyz(v, self.position))
        view_matrix.set(2, 3, -Vector4.dot_product_xyz(w, self.position))

        return view_matrix

    # https://en.wikipedia.org/wiki/Euler_angles#Conversion_to_other_orientation_representations
    def get_rotation_matrix(self) -> Matrix4:
        o_x, o_y, o_z = list(map(math.radians, self.orientation))
        c1 = cos(o_x)
        s1 = sin(o_x)

        c2 = cos(o_y)
        s2 = sin(o_y)

        c3 = cos(o_z)
        s3 = sin(o_z)

        # u = [c2 * c3 + s2 * s1 * s3, c1 * s3, c2 * s1 * s3 - c3 * s2, 0]
        # v = [c3 * s2 * s1 - c2 * s3, c1 * c3, c2 * c3 * s1 + s2 * s3, 0]
        # w = [c1 * s2, -s1, c2 * c1, 0]

        u = [c2 * c3, c1 * s3 + c3 * s1 * s2, s1 * s3 - c1 * c3 * s2, 0]
        v = [-c2 * s3, c1 * c3 - s1 * s2 * s3, c3 * s1 + c1 * s2 * s3, 0]
        w = [s2, -c2 * s1, c1 * c2, 0]

        d = [0, 0, 0, 1]

        rotation_matrix = Matrix4.from_list([u, v, w, d]).transpose()
        # Desired output:
        # [[u_x, v_x, w_x, 0],
        #  [u_y, v_y, w_y, 0],
        #  [u_z, v_z, w_z, 0],
        #  [0  ,   0,   0, 1]]
        print(rotation_matrix)
        return rotation_matrix

    def get_perspective_projection_matrix(self):
        f = 1 / math.tan(math.radians(self.fov / 2))
        q = self.Z_FAR / (self.Z_FAR - self.Z_NEAR)
        projection_matrix = Matrix4.from_list([[f / self.aspect_ratio, 0, 0, 0],
                                               [0, f, 0, 0],
                                               [0, 0, q, -q * self.Z_NEAR],
                                               [0, 0, 1, 0]])
        return projection_matrix
