import math
from math import sin, cos

import numpy as np

from vector import Vector4, NUMPY_ARRAY_TYPE


class Matrix4:
    matrix_np: np.ndarray

    def __init__(self, matrix_np: np.ndarray):
        self.matrix_np = matrix_np

    def __str__(self):
        return str(self.matrix_np)

    @staticmethod
    def from_list(matrix_list: list[list[float]]):
        return Matrix4(np.array(matrix_list, dtype=NUMPY_ARRAY_TYPE))

    def copy(self) -> 'Matrix4':
        return Matrix4(self.matrix_np.copy())

    def multiply_by_matrix(self, matrix: 'Matrix4'):
        return Matrix4(self.matrix_np @ matrix.matrix_np)

    def multiply_by_vector(self, vector: Vector4) -> Vector4:
        result = Vector4(self.matrix_np @ vector.vector_np)
        if result.get_w() != 0:
            result.vector_np[:3] /= result.get_w()
        return result

    def get_column(self, j: int) -> Vector4:
        return Vector4(self.matrix_np[:, j].reshape(-1, 1))

    def transpose(self) -> 'Matrix4':
        return Matrix4(self.matrix_np.transpose())

    def get_row(self, i: int) -> Vector4:
        return Vector4(self.matrix_np[i, :].reshape(-1, 1))

    def set(self, i, j, value) -> None:
        self.matrix_np[i, j] = value


def get_rotation_matrix_over_x(orientation_x_angle: int):
    o_x = math.radians(orientation_x_angle)
    s_x = sin(o_x)
    c_x = cos(o_x)
    return Matrix4.from_list([[1, 0, 0, 0],
                              [0, c_x, -s_x, 0],
                              [0, s_x, c_x, 0],
                              [0, 0, 0, 1]])


def get_rotation_matrix_over_y(orientation_y_angle: int):
    o_y = math.radians(orientation_y_angle)
    s_y = sin(o_y)
    c_y = cos(o_y)
    return Matrix4.from_list([[c_y, 0, s_y, 0],
                              [0, 1, 0, 0],
                              [-s_y, 0, c_y, 0],
                              [0, 0, 0, 1]])


def get_rotation_matrix_over_z(orientation_z_angle: int):
    o_z = math.radians(orientation_z_angle)
    s_z = sin(o_z)
    c_z = cos(o_z)
    return Matrix4.from_list([[c_z, -s_z, 0, 0],
                              [s_z, c_z, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])


def get_rotation_matrix(orientation: Vector4) -> Matrix4:
    r_x = get_rotation_matrix_over_x(orientation.get_x())
    r_y = get_rotation_matrix_over_y(orientation.get_y())
    r_z = get_rotation_matrix_over_z(orientation.get_z())

    return r_x.multiply_by_matrix(r_y).multiply_by_matrix(r_z)


def get_translation_matrix(translation: Vector4):
    return Matrix4.from_list([[1, 0, 0, translation.get_x()],
                              [0, 1, 0, translation.get_y()],
                              [0, 0, 1, translation.get_z()],
                              [0, 0, 0, 1]])
