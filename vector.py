import numpy as np

NUMPY_ARRAY_TYPE = float


class Vector4:
    vector_np: np.ndarray

    def __init__(self, vector: np.ndarray):
        if vector.shape[0] != 4 or vector.shape[1] != 1:
            raise ValueError
        self.vector_np = vector

    def __str__(self):
        return str(self.vector_np.flatten())

    @staticmethod
    def from_cords(x: float, y: float, z: float, w: float):
        return Vector4(np.array([[x],
                                 [y],
                                 [z],
                                 [w]], dtype=NUMPY_ARRAY_TYPE))

    def copy(self):
        return Vector4(self.vector_np.copy())

    def get_normalized_xyz(self) -> 'Vector4':
        normalized = self.copy()
        normalized.vector_np[:3] /= self.dot_product_xyz(normalized, normalized)

        return normalized

    @staticmethod
    def dot_product_xyz(a: 'Vector4', b: 'Vector4') -> float:
        return (a.vector_np[:3] * b.vector_np[:3]).sum()

    @staticmethod
    def cross_product_xyz(a: 'Vector4', b: 'Vector4'):
        a1 = a.get_x()
        a2 = a.get_y()
        a3 = a.get_z()

        b1 = b.get_x()
        b2 = b.get_y()
        b3 = b.get_z()

        return Vector4.from_cords(a2 * b3 - a3 * b2,
                                  a3 * b1 - a1 * b3,
                                  a1 * b2 - a2 * b1,
                                  1)

    def __add__(self, other: 'Vector4') -> 'Vector4':
        result = self.copy()
        result.vector_np[:3] += other.vector_np[:3]
        return result

    def __sub__(self, other: 'Vector4') -> 'Vector4':
        result = self.copy()
        result.vector_np[:3] -= other.vector_np[:3]
        return result

    def __mul__(self, other: float) -> 'Vector4':
        result = self.copy()
        result.vector_np[:3] *= other
        return result

    def get_x(self):
        return self.vector_np[0, 0]

    def get_y(self):
        return self.vector_np[1, 0]

    def get_z(self):
        return self.vector_np[2, 0]

    def get_w(self):
        return self.vector_np[3, 0]

    def set_offset(self, offset: 'Vector4') -> None:
        self.vector_np[:3] += offset.vector_np[:3]
