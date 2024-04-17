import math
from math import tan, sin, cos, pi
import sys
from dataclasses import dataclass

import numpy as np
import pygame

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

Z_FAR = 10
Z_NEAR = 0.1

ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
FOV_DEGREES = 90

NUMPY_ARRAY_TYPE = float


class Camera:
    STARTING_POSITION = np.array([[0], [0], [-2], [0]], dtype=NUMPY_ARRAY_TYPE)
    POSITION_DELTA = 0.5
    X_POSITION_DELTA_VECTOR = np.array([[POSITION_DELTA],
                                        [0],
                                        [0],
                                        [0]], dtype=NUMPY_ARRAY_TYPE)
    Y_POSITION_DELTA_VECTOR = np.array([[0],
                                        [POSITION_DELTA],
                                        [0],
                                        [0]], dtype=NUMPY_ARRAY_TYPE)
    Z_POSITION_DELTA_VECTOR = np.array([[0],
                                        [0],
                                        [POSITION_DELTA],
                                        [0]], dtype=NUMPY_ARRAY_TYPE)

    STARTING_ORIENTATION = [0, 0, 0]
    ORIENTATION_DELTA = 5

    position: np.ndarray
    orientation: list[float]

    def __init__(self):
        self.position = self.STARTING_POSITION
        self.orientation = self.STARTING_ORIENTATION

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
        self.position += self.get_rotation_matrix() @ self.X_POSITION_DELTA_VECTOR

    def move_left(self):
        self.position -= self.get_rotation_matrix() @ self.X_POSITION_DELTA_VECTOR

    def move_front(self):
        self.position += self.get_rotation_matrix() @ self.Z_POSITION_DELTA_VECTOR

    def move_back(self):
        self.position -= self.get_rotation_matrix() @ self.Z_POSITION_DELTA_VECTOR

    def move_up(self):
        self.position -= self.get_rotation_matrix() @ self.Y_POSITION_DELTA_VECTOR

    def move_down(self):
        self.position += self.get_rotation_matrix() @ self.Y_POSITION_DELTA_VECTOR

    def get_view_matrix(self):
        view_matrix = self.get_rotation_matrix().transpose()

        u = view_matrix[0, :]
        v = view_matrix[1, :]
        w = view_matrix[2, :]

        view_matrix[0, 3] = -np.dot(u, self.position.flatten())
        view_matrix[1, 3] = -np.dot(v, self.position.flatten())
        view_matrix[2, 3] = -np.dot(w, self.position.flatten())

        return view_matrix

    def get_rotation_matrix(self):
        o_x, o_y, o_z = list(map(math.radians, self.orientation))
        c3 = cos(o_z)
        s3 = sin(o_z)
        c2 = cos(o_x)
        s2 = sin(o_x)
        c1 = cos(o_y)
        s1 = sin(o_y)
        u = np.array([c1 * c3 + s1 * s2 * s3, c2 * s3, c1 * s2 * s3 - c3 * s1, 0], dtype=NUMPY_ARRAY_TYPE)
        v = np.array([c3 * s1 * s2 - c1 * s3, c2 * c3, c1 * c3 * s2 + s1 * s3, 0], dtype=NUMPY_ARRAY_TYPE)
        w = np.array([c2 * s1, -s2, c1 * c2, 0], dtype=NUMPY_ARRAY_TYPE)

        rotation_matrix = np.array([u, v, w, [0, 0, 0, 1]], dtype=NUMPY_ARRAY_TYPE).transpose()

        return rotation_matrix.copy()


@dataclass
class Shape:
    points: dict[str, np.ndarray]
    edges: list[tuple[str, str]]


def read_object_from_file(filename: str):
    with open(filename, "r") as f:
        num_of_points = int(f.readline())
        points = {}

        for _ in range(num_of_points):
            args = f.readline().strip().split()
            points[args[0]] = np.array([[float(x)] for x in args[1:4] + [1]], dtype=NUMPY_ARRAY_TYPE)

        num_of_edges = int(f.readline())
        edges = []
        for _ in range(num_of_edges):
            args = f.readline().strip().split()
            edges.append((args[0], args[1]))

        return Shape(points, edges)


def get_perspective_projection_matrix():
    f = 1 / tan(math.radians(FOV_DEGREES / 2))
    q = Z_FAR / (Z_FAR - Z_NEAR)
    projection_matrix = np.array([[f / ASPECT_RATIO, 0, 0, 0],
                                  [0, f, 0, 0],
                                  [0, 0, q, -q * Z_NEAR],
                                  [0, 0, 1, 0]], dtype=NUMPY_ARRAY_TYPE)
    return projection_matrix


def project_shape(camera: Camera,
                  shape: Shape) -> Shape:
    def _project_point(point: np.ndarray) -> np.ndarray:
        result = point.copy()

        view_matrix = camera.get_view_matrix()
        result = view_matrix @ result

        perspective_projection_matrix = get_perspective_projection_matrix()
        result = perspective_projection_matrix @ result

        if result[3, 0] != 0:
            result /= result[3, 0]

        return result

    return Shape(
        {name: _project_point(point) for name, point in shape.points.items()},
        shape.edges
    )


X_MIN = -1
X_MAX = 1

Y_MIN = -1
Y_MAX = 1

Z_MIN = 0
Z_MAX = 1


# reference: https://www.mdpi.com/1999-4893/16/4/201
def clip_edge(p0: np.ndarray, p1: np.ndarray):
    p0 = p0.copy()
    p1 = p1.copy()

    def recover_real_z(z_out):
        q = Z_FAR / (Z_FAR - Z_NEAR)
        z_in = (q * Z_NEAR) / (q - z_out)
        return z_in

    x0 = p0[0, 0]
    y0 = p0[1, 0]
    # z0 = p0[2, 0]
    z0 = recover_real_z(p0[2, 0])

    x1 = p1[0, 0]
    y1 = p1[1, 0]
    # z1 = p0[2, 0]
    z1 = recover_real_z(p1[2, 0])

    print(f'z0={z0}, z1={z1}')

    if not ((x0 < X_MIN and x1 < X_MIN) or (x0 > X_MAX and x1 > X_MAX) or
            (y0 < Y_MIN and y1 < Y_MIN) or (y0 > Y_MAX and y1 > Y_MAX) or
            (z0 < Z_MIN and z1 < Z_MIN) or (z0 > Z_MAX and z1 > Z_MAX)):

        a = x1 - x0
        b = y1 - y0
        c = z1 - z0

        if x0 < X_MIN:
            y0 = b / a * (X_MIN - x0) + y0
            z0 = c / a * (X_MIN - x0) + z0
            x0 = X_MIN
        elif x0 > X_MAX:
            y0 = b / a * (X_MAX - x0) + y0
            z0 = c / a * (X_MAX - x0) + z0
            x0 = X_MAX

        if y0 < Y_MIN:
            x0 = a / b * (Y_MIN - y0) + x0
            z0 = c / b * (Y_MIN - y0) + z0
            y0 = Y_MIN
        elif y0 > Y_MAX:
            x0 = a / b * (Y_MAX - y0) + x0
            z0 = c / b * (Y_MAX - y0) + z0
            y0 = Y_MAX
        if z0 < Z_MIN:
            x0 = a / c * (Z_MIN - z0) + x0
            y0 = b / c * (Z_MIN - z0) + y0
            z0 = Z_MIN
        elif z0 > Z_MAX:
            x0 = a / c * (Z_MAX - z0) + x0
            y0 = b / c * (Z_MAX - z0) + y0
            z0 = Z_MAX

        p0[0][0] = x0
        p0[1][0] = y0
        p0[2][0] = z0

        if x1 < X_MIN:
            y1 = b / a * (X_MIN - x0) + y0
            z1 = c / a * (X_MIN - x0) + z0
            x1 = X_MIN
        elif x1 > X_MAX:
            y1 = b / a * (X_MAX - x0) + y0
            z1 = c / a * (X_MAX - x0) + z0
            x1 = X_MAX

        if y1 < Y_MIN:
            x1 = a / b * (Y_MIN - y0) + x0
            z1 = c / b * (Y_MIN - y0) + z0
            y1 = Y_MIN
        elif y1 > Y_MAX:
            x1 = a / b * (Y_MAX - y0) + x0
            z1 = c / b * (Y_MAX - y0) + z0
            y1 = Y_MAX

        if z1 < Z_MIN:
            x1 = a / c * (Z_MIN - z0) + x0
            y1 = b / c * (Z_MIN - z0) + y0
            z1 = Z_MIN
        elif z1 > Z_MAX:
            x1 = a / c * (Z_MAX - z0) + x0
            y1 = b / c * (Z_MAX - z0) + y0
            z1 = Z_MAX

        p1[0][0] = x1
        p1[1][0] = y1
        p1[2][0] = z1
    else:
        return None

    return p0, p1


def clip_shape(shape: Shape):
    clipped_edges: list[tuple[str, str]] = []
    points: dict[str, np.ndarray] = {}

    i = 0
    for edge in shape.edges:
        clipped_edge = clip_edge(shape.points[edge[0]], shape.points[edge[1]])
        if clipped_edge is None:
            continue
        p0, p1 = clipped_edge

        p0_name = str(i)
        same_point_found = False

        for point_name, point in points.items():
            if np.array_equal(point, p0):
                same_point_found = True
                p0_name = point_name
                break

        points[p0_name] = p0
        if not same_point_found:
            i += 1

        p1_name = str(i)
        same_point_found = False

        for point_name, point in points.items():
            if np.array_equal(point, p1):
                same_point_found = True
                p1_name = point_name
                break

        points[p1_name] = p1
        if not same_point_found:
            i += 1

        clipped_edges.append((p0_name, p1_name))

    return Shape(points, clipped_edges)


def draw_shape(camera: Camera,
               screen: pygame.Surface,
               shape: Shape,
               point_description_font: pygame.font.Font):
    x, y, z = camera.position[0][0], camera.position[1][0], camera.position[2][0]
    text_surface_camera_position = point_description_font.render(f'x={x} y={y} z={z}', True, [0, 0, 0])
    coord_text_width = text_surface_camera_position.get_width()
    coord_text_height = text_surface_camera_position.get_height()
    screen.blit(text_surface_camera_position, dest=[SCREEN_WIDTH - coord_text_width, 0])

    o_x, o_y, o_z = camera.orientation
    text_surface_camera_orientation = point_description_font.render(f'o_x={o_x} o_y={o_y} o_z={o_z}', True,
                                                                    [0, 0, 0])
    orientation_text_width = text_surface_camera_orientation.get_width()
    screen.blit(text_surface_camera_orientation, dest=[SCREEN_WIDTH - orientation_text_width, coord_text_height])

    for edge in shape.edges:
        point1_name, point2_name = edge

        point1 = shape.points[point1_name]
        point2 = shape.points[point2_name]

        x1 = (point1[0, 0] + 1) * SCREEN_WIDTH / 2
        y1 = (point1[1, 0] + 1) * SCREEN_HEIGHT / 2

        x2 = (point2[0, 0] + 1) * SCREEN_WIDTH / 2
        y2 = (point2[1, 0] + 1) * SCREEN_HEIGHT / 2

        pygame.draw.line(screen, [0, 0, 0], (x1, y1), (x2, y2))

        text_surface_point1 = point_description_font.render(point1_name, True, [0, 0, 0])
        screen.blit(text_surface_point1, dest=(x1, y1))

        text_surface_point2 = point_description_font.render(point2_name, True, [0, 0, 0])
        screen.blit(text_surface_point2, dest=(x2, y2))


def main() -> None:
    pygame.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 12)

    axis = read_object_from_file("axis.txt")
    cuboid = read_object_from_file("cuboid.txt")
    cuboid_larger = read_object_from_file("cuboid_larger.txt")
    shapes = [cuboid]

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hello world")

    camera = Camera()

    def draw():
        screen.fill((255, 255, 255))

        for shape in shapes:
            projected_shape = project_shape(camera, shape)
            clipped_shape = clip_shape(projected_shape)
            draw_shape(camera, screen, clipped_shape, font)
        pygame.display.update()

    draw()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_a:
                    camera.move_left()
                case pygame.K_d:
                    camera.move_right()
                case pygame.K_UP:
                    camera.look_up()
                case pygame.K_DOWN:
                    camera.look_down()
                case pygame.K_RIGHT:
                    camera.look_right()
                case pygame.K_LEFT:
                    camera.look_left()
                case pygame.K_e:
                    camera.rotate_right()
                case pygame.K_q:
                    camera.rotate_left()

                case pygame.K_w:
                    camera.move_front()
                case pygame.K_s:
                    camera.move_back()
                case pygame.K_a:
                    camera.move_left()
                case pygame.K_d:
                    camera.move_right()

                case pygame.K_SPACE:
                    camera.move_up()
                case pygame.K_LSHIFT:
                    camera.move_down()

                case _:
                    continue
            draw()


if __name__ == "__main__":
    main()
