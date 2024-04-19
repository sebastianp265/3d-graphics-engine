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

    STARTING_ORIENTATION = Vector4.from_cords(0, 0, 0, 1)
    ORIENTATION_DELTA = 5
    X_ORIENTATION_DELTA = Vector4.from_cords(ORIENTATION_DELTA, 0, 0, 1)
    Y_ORIENTATION_DELTA = Vector4.from_cords(0, ORIENTATION_DELTA, 0, 1)
    Z_ORIENTATION_DELTA = Vector4.from_cords(0, 0, ORIENTATION_DELTA, 1)

    FOV_DELTA = 10
    STARTING_FOV_DEGREES = 90

    Z_FAR = 100
    Z_NEAR = 0.1

    fov: int
    position: Vector4
    orientation: Vector4

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
        self.orientation.set_offset(self.Z_ORIENTATION_DELTA)

    def rotate_left(self):
        self.orientation.set_offset(self.Z_ORIENTATION_DELTA * (-1))

    def look_up(self):
        self.orientation.set_offset(self.X_ORIENTATION_DELTA)

    def look_down(self):
        self.orientation.set_offset(self.X_ORIENTATION_DELTA * (-1))

    def look_right(self):
        self.orientation.set_offset(self.Y_ORIENTATION_DELTA)

    def look_left(self):
        self.orientation.set_offset(self.Y_ORIENTATION_DELTA * (-1))

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

    # def get_view_matrix(self):
    #     v = self.v
    #     w = self.w
    #
    #     u = Vector4.cross_product_xyz(w, v)
    #     self.u = u
    #
    #     view_matrix = Matrix4.from_list([[u.get_x(), u.get_y(), u.get_z(), -Vector4.dot_product_xyz(u, self.position)],
    #                                      [v.get_x(), v.get_y(), v.get_z(), -Vector4.dot_product_xyz(v, self.position)],
    #                                      [w.get_x(), w.get_y(), w.get_z(), -Vector4.dot_product_xyz(w, self.position)],
    #                                      [0, 0, 0, 1]])
    #
    #     return view_matrix
    #

    # def get_view_matrix_from_direction(self):
    #     front = self.get_rotation_matrix().multiply_by_vector(self.front)
    #     front = self.get_translation_matrix().multiply_by_vector(front)
    #     front = front.get_normalized_xyz()
    #
    #     up = self.get_rotation_matrix().multiply_by_vector(self.up)
    #     up = self.get_translation_matrix().multiply_by_vector(up)
    #     up = up.get_normalized_xyz()
    #
    #     right = Vector4.cross_product_xyz(up, front)  # u
    #
    #     return Matrix4.from_list(
    #         [[right.get_x(), right.get_y(), right.get_z(),
    #           -Vector4.dot_product_xyz(right, self.position)],
    #          [up.get_x(), up.get_y(), up.get_z(),
    #           -Vector4.dot_product_xyz(up, self.position)],
    #          [front.get_x(), front.get_y(), front.get_z(),
    #           -Vector4.dot_product_xyz(front, self.position)],
    #          [0, 0, 0, 1]])

    def get_view_matrix(self):
        view_matrix = self.get_rotation_matrix().transpose()

        u = view_matrix.get_row(0)
        v = view_matrix.get_row(1)
        w = view_matrix.get_row(2)

        view_matrix.set(0, 3, -Vector4.dot_product_xyz(u, self.position))
        view_matrix.set(1, 3, -Vector4.dot_product_xyz(v, self.position))
        view_matrix.set(2, 3, -Vector4.dot_product_xyz(w, self.position))

        return view_matrix

    def get_rotation_matrix_over_x(self):
        o_x = math.radians(self.orientation.get_x())
        s_x = sin(o_x)
        c_x = cos(o_x)
        return Matrix4.from_list([[1, 0, 0, 0],
                                  [0, c_x, -s_x, 0],
                                  [0, s_x, c_x, 0],
                                  [0, 0, 0, 1]])

    def get_rotation_matrix_over_y(self):
        o_y = math.radians(self.orientation.get_y())
        s_y = sin(o_y)
        c_y = cos(o_y)
        return Matrix4.from_list([[c_y, 0, s_y, 0],
                                  [0, 1, 0, 0],
                                  [-s_y, 0, c_y, 0],
                                  [0, 0, 0, 1]])

    def get_rotation_matrix_over_z(self):
        o_z = math.radians(self.orientation.get_z())
        s_z = sin(o_z)
        c_z = cos(o_z)
        return Matrix4.from_list([[c_z, -s_z, 0, 0],
                                  [s_z, c_z, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])

    def get_rotation_matrix(self) -> Matrix4:
        r_x = self.get_rotation_matrix_over_x()
        r_y = self.get_rotation_matrix_over_y()
        r_z = self.get_rotation_matrix_over_z()

        return r_x.multiply_by_matrix(r_y).multiply_by_matrix(r_z)

    def get_translation_matrix(self):
        return Matrix4.from_list([[1, 0, 0, -self.position.get_x()],
                                  [0, 1, 0, -self.position.get_y()],
                                  [0, 0, 1, -self.position.get_z()],
                                  [0, 0, 0, 1]])

    # https://en.wikipedia.org/wiki/Euler_angles#Conversion_to_other_orientation_representations
    # def get_rotation_matrix(self) -> Matrix4:
    #     o_x, o_y, o_z = list(map(math.radians, [self.orientation.get_x(),
    #                                             self.orientation.get_y(),
    #                                             self.orientation.get_z()]))
    #     c1 = cos(o_x)
    #     s1 = sin(o_x)
    #
    #     c2 = cos(o_y)
    #     s2 = sin(o_y)
    #
    #     c3 = cos(o_z)
    #     s3 = sin(o_z)
    #
    #     # u = [c2 * c3 + s2 * s1 * s3, c1 * s3, c2 * s1 * s3 - c3 * s2, 0]
    #     # v = [c3 * s2 * s1 - c2 * s3, c1 * c3, c2 * c3 * s1 + s2 * s3, 0]
    #     # w = [c1 * s2, -s1, c2 * c1, 0]
    #
    #     u = [c2 * c3, c1 * s3 + c3 * s1 * s2, s1 * s3 - c1 * c3 * s2, 0]
    #     v = [-c2 * s3, c1 * c3 - s1 * s2 * s3, c3 * s1 + c1 * s2 * s3, 0]
    #     w = [s2, -c2 * s1, c1 * c2, 0]
    #
    #     d = [0, 0, 0, 1]
    #
    #     rotation_matrix = Matrix4.from_list([u, v, w, d]).transpose()
    #     # Desired output:
    #     # [[u_x, v_x, w_x, 0],
    #     #  [u_y, v_y, w_y, 0],
    #     #  [u_z, v_z, w_z, 0],
    #     #  [0  ,   0,   0, 1]]
    #     print(rotation_matrix)
    #     return rotation_matrix

    def get_perspective_projection_matrix(self):
        f = 1 / math.tan(math.radians(self.fov / 2))
        q = self.Z_FAR / (self.Z_FAR - self.Z_NEAR)
        projection_matrix = Matrix4.from_list([[f / self.aspect_ratio, 0, 0, 0],
                                               [0, f, 0, 0],
                                               [0, 0, q, -q * self.Z_NEAR],
                                               [0, 0, 1, 0]])
        return projection_matrix
