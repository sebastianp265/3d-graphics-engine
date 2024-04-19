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
            result.vector_np /= result.get_w()
        return result

    def get_column(self, j: int) -> Vector4:
        return Vector4(self.matrix_np[:, j].reshape(-1, 1))

    def transpose(self) -> 'Matrix4':
        return Matrix4(self.matrix_np.transpose())

    def get_row(self, i: int) -> Vector4:
        return Vector4(self.matrix_np[i, :].reshape(-1, 1))

    def set(self, i, j, value) -> None:
        self.matrix_np[i, j] = value
