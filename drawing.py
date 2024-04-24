import pygame

from camera import Camera
from shape import Shape


def draw_camera_info(camera: Camera,
                     screen: pygame.Surface,
                     font: pygame.font.Font):
    cx, cy, cz = camera.position.get_x(), camera.position.get_y(), camera.position.get_z()
    text_surface_camera_position = font.render(f'x={cx:.2f} y={cy:.2f} z={cz:.2f}', True, [0, 0, 0])
    coord_text_width = text_surface_camera_position.get_width()
    coord_text_height = text_surface_camera_position.get_height()
    screen.blit(text_surface_camera_position, dest=[screen.get_width() - coord_text_width, 0])

    o_x, o_y, o_z = camera.orientation.get_x(), camera.orientation.get_y(), camera.orientation.get_z()
    text_surface_camera_orientation = font.render(f'o_x={o_x:.2f} o_y={o_y:.2f} o_z={o_z:.2f}', True,
                                                  [0, 0, 0])
    orientation_text_width = text_surface_camera_orientation.get_width()
    screen.blit(text_surface_camera_orientation, dest=[screen.get_width() - orientation_text_width, coord_text_height])


def draw_shape(screen: pygame.Surface, shape: Shape):
    for edge in shape.lines:
        point1, point2 = edge

        x1 = (point1.get_x() + 1) * screen.get_width() / 2
        y1 = (point1.get_y() + 1) * screen.get_height() / 2

        x2 = (point2.get_x() + 1) * screen.get_width() / 2
        y2 = (point2.get_y() + 1) * screen.get_height() / 2

        pygame.draw.line(screen, [0, 0, 0], (x1, y1), (x2, y2))
