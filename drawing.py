import numpy as np
import pygame

from camera import Camera
from shape import Shape

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

FONT = pygame.font.Font(pygame.font.get_default_font(), 12)


def draw_camera_info(camera: Camera,
                     screen: pygame.Surface):
    cx, cy, cz = camera.position.get_x(), camera.position.get_y(), camera.position.get_z()
    text_surface_camera_position = FONT.render(f'x={cx:.2f} y={cy:.2f} z={cz:.2f}', True, [0, 0, 0])
    coord_text_width = text_surface_camera_position.get_width()
    coord_text_height = text_surface_camera_position.get_height()
    screen.blit(text_surface_camera_position, dest=[screen.get_width() - coord_text_width, 0])

    o_x, o_y, o_z = camera.orientation.get_x(), camera.orientation.get_y(), camera.orientation.get_z()
    text_surface_camera_orientation = FONT.render(f'o_x={o_x:.2f} o_y={o_y:.2f} o_z={o_z:.2f}', True,
                                                  [0, 0, 0])
    orientation_text_width = text_surface_camera_orientation.get_width()
    screen.blit(text_surface_camera_orientation, dest=[screen.get_width() - orientation_text_width, coord_text_height])


DEPTH_BUFFER = np.empty((SCREEN_WIDTH + 1, SCREEN_HEIGHT + 1), dtype=float)


def draw_shape(screen: pygame.Surface, shape: Shape):
    for triangle in shape.triangles:
        point0, point1, point2 = triangle

        x1 = (point0.get_x() + 1) * screen.get_width() / 2
        y1 = (point0.get_y() + 1) * screen.get_height() / 2
        z1 = point0.get_w()

        x2 = (point1.get_x() + 1) * screen.get_width() / 2
        y2 = (point1.get_y() + 1) * screen.get_height() / 2
        z2 = point1.get_w()

        x3 = (point2.get_x() + 1) * screen.get_width() / 2
        y3 = (point2.get_y() + 1) * screen.get_height() / 2
        z3 = point2.get_w()

        draw_triangle(screen, x1, y1, z1, x2, y2, z2, x3, y3, z3, shape.color)
        #
        # pygame.draw.line(screen, [255, 0, 0], (x1, y1), (x2, y2))
        #
        # pygame.draw.line(screen, [255, 0, 0], (x2, y2), (x3, y3))
        #
        # pygame.draw.line(screen, [255, 0, 0], (x3, y3), (x1, y1))
        #


def draw_triangle(screen: pygame.Surface, x1, y1, z1, x2, y2, z2, x3, y3, z3, color: tuple[int, int, int]):
    x1, y1, z1, x2, y2, z2, x3, y3, z3 = map(int, [x1, y1, z1, x2, y2, z2, x3, y3, z3])

    if y2 < y1:
        y1, y2 = y2, y1
        x1, x2 = x2, x1
        z1, z2 = z2, z1
    if y3 < y1:
        y1, y3 = y3, y1
        x1, x3 = x3, x1
        z1, z3 = z3, z1
    if y3 < y2:
        y2, y3 = y3, y2
        x2, x3 = x3, x2
        z2, z3 = z3, z2

    def draw_horizontal_line(y, x_start, x_end, z_start, z_end):
        if x_start > x_end:
            x_start, x_end = x_end, x_start
            z_start, z_end = z_end, z_start
        t_step = 1 / (x_end - x_start) if x_end != x_start else -1000
        t = 0
        for x in range(x_start, x_end + 1):
            z = (1 - t) * z_start + t * z_end
            if z < DEPTH_BUFFER[x, y]:
                screen.set_at((x, y), color)
                DEPTH_BUFFER[x, y] = z
            t += t_step

    # Calculate steps for the first part of the triangle
    dy1 = y2 - y1
    dx1 = x2 - x1
    dz1 = z2 - z1

    dy2 = y3 - y1
    dx2 = x3 - x1
    dz2 = z3 - z1

    dax_step = dx1 / abs(dy1) if dy1 != 0 else 0
    dbx_step = dx2 / abs(dy2) if dy2 != 0 else 0

    dz1_step = dz1 / abs(dy1) if dy1 != 0 else 0
    dz2_step = dz2 / abs(dy2) if dy2 != 0 else 0

    for i in range(y1, y2 + 1):
        ax = int(x1 + (i - y1) * dax_step)
        bx = int(x1 + (i - y1) * dbx_step)

        zs = z1 + (i - y1) * dz1_step
        ze = z1 + (i - y1) * dz2_step

        draw_horizontal_line(i, ax, bx, zs, ze)

    dy1 = y3 - y2
    dx1 = x3 - x2
    dz1 = z3 - z2

    dax_step = dx1 / abs(dy1) if dy1 != 0 else 0

    dz1_step = dz1 / abs(dy1) if dy1 != 0 else 0

    for i in range(y2, y3 + 1):
        ax = int(x2 + (i - y2) * dax_step)
        bx = int(x1 + (i - y1) * dbx_step)

        zs = z2 + (i - y2) * dz1_step
        ze = z1 + (i - y1) * dz2_step

        draw_horizontal_line(i, ax, bx, zs, ze)
