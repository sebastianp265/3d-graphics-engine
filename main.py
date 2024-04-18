import math
from math import tan, sin, cos
import sys

import numpy as np
import pygame

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

Z_FAR = 100
Z_NEAR = 0.1

ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

NUMPY_ARRAY_TYPE = float

vector3 = np.ndarray
vector4 = np.ndarray


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

    FOV_DELTA = 10
    STARTING_FOV_DEGREES = 90

    fov: int
    position: vector4
    orientation: list[float]

    def __init__(self):
        self.position = self.STARTING_POSITION
        self.orientation = self.STARTING_ORIENTATION
        self.fov = self.STARTING_FOV_DEGREES

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
        cx = cos(o_x)
        sx = sin(o_x)

        cy = cos(o_y)
        sy = sin(o_y)

        cz = cos(o_z)
        sz = sin(o_z)

        u = np.array([cy * cz + sy * sx * sz, cx * sz, cy * sx * sz - cz * sy, 0], dtype=NUMPY_ARRAY_TYPE)
        v = np.array([cz * sy * sx - cy * sz, cx * cz, cy * cz * sx + sy * sz, 0], dtype=NUMPY_ARRAY_TYPE)
        w = np.array([cx * sy, -sx, cy * cx, 0], dtype=NUMPY_ARRAY_TYPE)

        rotation_matrix = np.array([u, v, w, [0, 0, 0, 1]], dtype=NUMPY_ARRAY_TYPE).transpose()

        return rotation_matrix


class Shape:
    lines: list[tuple[vector4, vector4]]

    def __init__(self, lines):
        self.lines = lines

    def copy(self):
        return Shape([(point1.copy(), point2.copy()) for point1, point2 in self.lines])

    def set_offset(self, offset: np.ndarray):
        for p1, p2 in self.lines:
            p1 += offset
            p2 += offset


def read_object_from_file(filename: str):
    with open(filename, "r") as f:
        num_of_points = int(f.readline())
        points = {}

        for _ in range(num_of_points):
            args = f.readline().strip().split()
            points[args[0]] = np.array([[float(x)] for x in args[1:4] + [1]], dtype=NUMPY_ARRAY_TYPE)

        num_of_lines = int(f.readline())
        lines = []
        for _ in range(num_of_lines):
            args = f.readline().strip().split()
            lines.append((points[args[0]].copy(), points[args[1]].copy()))

        return Shape(lines)


def get_perspective_projection_matrix(camera: Camera):
    f = 1 / tan(math.radians(camera.fov / 2))
    q = Z_FAR / (Z_FAR - Z_NEAR)
    projection_matrix = np.array([[f / ASPECT_RATIO, 0, 0, 0],
                                  [0, f, 0, 0],
                                  [0, 0, q, -q * Z_NEAR],
                                  [0, 0, 1, 0]], dtype=NUMPY_ARRAY_TYPE)
    return projection_matrix


def on_update_shape(camera: Camera,
                    shape: Shape) -> Shape:
    shape.copy()
    view_matrix = camera.get_view_matrix()
    perspective_projection_matrix = get_perspective_projection_matrix(camera)

    updated_lines = []
    for line in shape.lines:
        updated_line = tuple(view_matrix @ point for point in line)
        updated_line = line_clip_against_plane(np.array([0, 0, Z_NEAR]),
                                               np.array([0, 0, 1]),
                                               updated_line[0].flatten()[:3],
                                               updated_line[1].flatten()[:3])
        if updated_line is None:
            continue
        updated_line = tuple(np.array([[point[0]],
                                       [point[1]],
                                       [point[2]],
                                       [1]]) for point in updated_line)

        updated_line = tuple(perspective_projection_matrix @ point for point in updated_line)
        updated_line = tuple(point / point[3][0] if point[3][0] != 0 else point
                             for point in updated_line)

        updated_lines.append(updated_line)

    return Shape(updated_lines)


def normalize(v: np.ndarray):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def get_intersection_point_of_line_with_a_plane(plane_p: np.ndarray,
                                                plane_n: np.ndarray,
                                                line_start: np.ndarray,
                                                line_end: np.ndarray):
    plane_n = normalize(plane_n)
    plane_d = -np.dot(plane_n, plane_p)
    ad = np.dot(line_start, plane_n)
    bd = np.dot(line_end, plane_n)
    t = (-plane_d - ad) / (bd - ad)
    return line_start + (line_end - line_start) * t


def line_clip_against_plane(plane_p: vector3,
                            plane_n: vector3,
                            line_start: vector3,
                            line_end: vector3):
    # plane_n = normalize(plane_n)

    def get_signed_distance(point: vector3):
        return np.dot(plane_n, point) - np.dot(plane_n, plane_p)

    start_dist = get_signed_distance(line_start)
    end_dist = get_signed_distance(line_end)

    if start_dist < 0 and end_dist < 0:  # both are outside
        return None
    elif start_dist * end_dist > 0:  # both are inside
        return line_start, line_end
    else:
        intersection_point = get_intersection_point_of_line_with_a_plane(
            plane_p,
            plane_n,
            line_start,
            line_end
        )
        if start_dist < 0:
            return intersection_point, line_end
        else:
            return line_start, intersection_point


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

    for edge in shape.lines:
        point1, point2 = edge

        x1 = (point1[0, 0] + 1) * SCREEN_WIDTH / 2
        y1 = (point1[1, 0] + 1) * SCREEN_HEIGHT / 2

        x2 = (point2[0, 0] + 1) * SCREEN_WIDTH / 2
        y2 = (point2[1, 0] + 1) * SCREEN_HEIGHT / 2

        pygame.draw.line(screen, [0, 0, 0], (x1, y1), (x2, y2))


def main() -> None:
    pygame.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 12)

    cuboid = read_object_from_file("cuboid.txt")

    offsets = [
        np.array([[1],
                  [0],
                  [1],
                  [0]]),
        np.array([[-4],
                  [0],
                  [1],
                  [0]]),
        np.array([[1],
                  [0],
                  [5],
                  [0]]),
        np.array([[-4],
                  [0],
                  [5],
                  [0]]),
    ]

    shapes = []
    for os in offsets:
        shape = cuboid.copy()
        shape.set_offset(os)
        shapes.append(shape)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hello world")

    camera = Camera()

    def draw():
        screen.fill((255, 255, 255))

        for shape in shapes:
            shape = on_update_shape(camera, shape)
            draw_shape(camera, screen, shape, font)
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

                case pygame.K_z:
                    camera.zoom_in()
                case pygame.K_c:
                    camera.zoom_out()

                case _:
                    continue
            draw()


if __name__ == "__main__":
    main()
