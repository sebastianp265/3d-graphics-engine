import math

from matrix import Matrix4, get_rotation_matrix, get_translation_matrix
from vector import Vector4


class Camera:
    STARTING_POSITION = Vector4.from_cords(0, 0, 0, 1)
    POSITION_DELTA = 0.5
    X_POSITION_DELTA_VECTOR = Vector4.from_cords(POSITION_DELTA, 0, 0, 1)
    Y_POSITION_DELTA_VECTOR = Vector4.from_cords(0, POSITION_DELTA, 0, 1)
    Z_POSITION_DELTA_VECTOR = Vector4.from_cords(0, 0, POSITION_DELTA, 1)

    STARTING_ORIENTATION = Vector4.from_cords(0, 0, 0, 1)
    ORIENTATION_DELTA = 10
    X_ORIENTATION_DELTA = Vector4.from_cords(ORIENTATION_DELTA, 0, 0, 1)
    Y_ORIENTATION_DELTA = Vector4.from_cords(0, ORIENTATION_DELTA, 0, 1)
    Z_ORIENTATION_DELTA = Vector4.from_cords(0, 0, ORIENTATION_DELTA, 1)

    FOV_DELTA = 10
    STARTING_FOV_DEGREES = 90
    MAX_FOV = 170
    MIN_FOV = 10

    Z_FAR = 100
    Z_NEAR = 0.00001

    fov: int
    position: Vector4
    orientation: Vector4

    BASE_VIEW_MATRIX = Matrix4.from_list([[1, 0, 0, 0],
                                          [0, 1, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])
    view_matrix: Matrix4

    screen_width: int
    screen_height: int
    aspect_ratio: float

    delta_time: float

    def __init__(self, screen_width: int, screen_height: int):
        self.position = self.STARTING_POSITION.copy()
        self.orientation = self.STARTING_ORIENTATION.copy()
        self.fov = self.STARTING_FOV_DEGREES
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.aspect_ratio = self.screen_width / self.screen_height
        self.view_matrix = (get_rotation_matrix(self.STARTING_ORIENTATION)
                            .multiply_by_matrix(get_translation_matrix(self.STARTING_POSITION * (-1)))
                            .multiply_by_matrix(self.BASE_VIEW_MATRIX))

        self.delta_time = 1

    def zoom_in(self):
        self.fov -= self.FOV_DELTA * self.delta_time
        self.fov = max(self.fov, self.MIN_FOV)

    def zoom_out(self):
        self.fov += self.FOV_DELTA * self.delta_time
        self.fov = min(self.fov, self.MAX_FOV)

    def rotate_right(self):
        z_orientation_delta = self.Z_ORIENTATION_DELTA * self.delta_time

        self.orientation.set_offset(z_orientation_delta)
        self.update_view_matrix(z_orientation_delta)

    def rotate_left(self):
        z_orientation_delta = self.Z_ORIENTATION_DELTA * self.delta_time * (-1)

        self.orientation.set_offset(z_orientation_delta)
        self.update_view_matrix(z_orientation_delta)

    def look_up(self):
        x_orientation_delta = self.X_ORIENTATION_DELTA * self.delta_time

        self.orientation.set_offset(x_orientation_delta)
        self.update_view_matrix(x_orientation_delta)

    def look_down(self):
        x_orientation_delta = self.X_ORIENTATION_DELTA * self.delta_time * (-1)

        self.orientation.set_offset(x_orientation_delta)
        self.update_view_matrix(x_orientation_delta)

    def look_right(self):
        y_orientation_delta = self.Y_ORIENTATION_DELTA * self.delta_time

        self.orientation.set_offset(y_orientation_delta)
        self.update_view_matrix(y_orientation_delta)

    def look_left(self):
        y_orientation_delta = self.Y_ORIENTATION_DELTA * self.delta_time * (-1)

        self.orientation.set_offset(y_orientation_delta)
        self.update_view_matrix(y_orientation_delta)

    def move_right(self):
        orientation = self.orientation * self.delta_time
        x_orientation_delta = self.X_POSITION_DELTA_VECTOR * self.delta_time

        self.position += get_rotation_matrix(orientation).multiply_by_vector(x_orientation_delta)
        self.update_view_matrix(translation_delta=x_orientation_delta * (-1))

    def move_left(self):
        orientation = self.orientation * self.delta_time
        y_orientation_delta = self.X_POSITION_DELTA_VECTOR * self.delta_time

        self.position -= get_rotation_matrix(orientation).multiply_by_vector(y_orientation_delta)
        self.update_view_matrix(translation_delta=y_orientation_delta)

    def move_front(self):
        orientation = self.orientation * self.delta_time
        z_orientation_delta = self.Z_POSITION_DELTA_VECTOR * self.delta_time

        self.position += get_rotation_matrix(orientation).multiply_by_vector(z_orientation_delta)
        self.update_view_matrix(translation_delta=z_orientation_delta * (-1))

    def move_back(self):
        orientation = self.orientation * self.delta_time
        z_orientation_delta = self.Z_POSITION_DELTA_VECTOR * self.delta_time

        self.position += get_rotation_matrix(orientation).multiply_by_vector(z_orientation_delta)
        self.update_view_matrix(translation_delta=z_orientation_delta)

    def move_up(self):
        orientation = self.orientation * self.delta_time
        y_position_delta = self.Y_POSITION_DELTA_VECTOR * self.delta_time

        self.position -= get_rotation_matrix(orientation).multiply_by_vector(y_position_delta)
        self.update_view_matrix(translation_delta=y_position_delta)

    def move_down(self):
        orientation = self.orientation * self.delta_time
        y_position_delta = self.Y_POSITION_DELTA_VECTOR * self.delta_time

        self.position += get_rotation_matrix(orientation).multiply_by_vector(y_position_delta)
        self.update_view_matrix(translation_delta=y_position_delta * (-1))

    def get_view_matrix(self):
        return self.view_matrix

    def update_view_matrix(self, orientation_delta: Vector4 = None, translation_delta: Vector4 = None):
        if orientation_delta is not None:
            self.view_matrix = get_rotation_matrix(orientation_delta).transpose().multiply_by_matrix(
                self.view_matrix)
        if translation_delta is not None:
            self.view_matrix = get_translation_matrix(translation_delta).multiply_by_matrix(self.view_matrix)

    def get_perspective_projection_matrix(self):
        f = 1 / math.tan(math.radians(self.fov / 2))
        q = self.Z_FAR / (self.Z_FAR - self.Z_NEAR)
        projection_matrix = Matrix4.from_list([[f / self.aspect_ratio, 0, 0, 0],
                                               [0, f, 0, 0],
                                               [0, 0, q, -q * self.Z_NEAR],
                                               [0, 0, 1, 0]])
        return projection_matrix

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
    def set_delta_time(self, delta_time: float):
        self.delta_time = delta_time
