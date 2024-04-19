import sys

import pygame

import shape_loader as loader

from camera import Camera
from shape import Shape
from vector import Vector4

pygame.init()

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

FONT = pygame.font.Font(pygame.font.get_default_font(), 12)


def on_update_shape(camera: Camera,
                    shape: Shape) -> Shape:
    view_matrix = camera.get_view_matrix()
    perspective_projection_matrix = camera.get_perspective_projection_matrix()

    updated_lines: list[tuple[Vector4, Vector4]] = []
    for line in shape.lines:
        updated_line: tuple[Vector4, Vector4] = (view_matrix.multiply_by_vector(line[0]),
                                                 view_matrix.multiply_by_vector(line[1]))
        updated_line = line_clip_against_plane(Vector4.from_cords(0, 0, camera.Z_NEAR, 0),
                                               Vector4.from_cords(0, 0, 1, 0),
                                               updated_line[0],
                                               updated_line[1])
        if updated_line is None:
            continue

        updated_line = (perspective_projection_matrix.multiply_by_vector(updated_line[0]),
                        perspective_projection_matrix.multiply_by_vector(updated_line[1]))

        updated_lines.append(updated_line)

    return Shape(updated_lines)


def get_intersection_point_of_line_with_a_plane(plane_p: Vector4,
                                                plane_n: Vector4,
                                                line_start: Vector4,
                                                line_end: Vector4):
    plane_n = plane_n.get_normalized_xyz()

    plane_d = -Vector4.dot_product_xyz(plane_n, plane_p)
    ad = Vector4.dot_product_xyz(line_start, plane_n)
    bd = Vector4.dot_product_xyz(line_end, plane_n)
    t = (-plane_d - ad) / (bd - ad)
    return line_start + (line_end - line_start) * t


def line_clip_against_plane(plane_p: Vector4,
                            plane_n: Vector4,
                            line_start: Vector4,
                            line_end: Vector4):
    plane_n = plane_n.get_normalized_xyz()

    def get_signed_distance(point: Vector4):
        return Vector4.dot_product_xyz(plane_n, point) - Vector4.dot_product_xyz(plane_n, plane_p)

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


def draw_camera_info(camera: Camera,
                     screen: pygame.Surface):
    cx, cy, cz = camera.position.get_x(), camera.position.get_y(), camera.position.get_z()
    text_surface_camera_position = FONT.render(f'x={cx} y={cy} z={cz}', True, [0, 0, 0])
    coord_text_width = text_surface_camera_position.get_width()
    coord_text_height = text_surface_camera_position.get_height()
    screen.blit(text_surface_camera_position, dest=[SCREEN_WIDTH - coord_text_width, 0])

    o_x, o_y, o_z = camera.orientation.get_x(), camera.orientation.get_y(), camera.orientation.get_z()
    text_surface_camera_orientation = FONT.render(f'o_x={o_x} o_y={o_y} o_z={o_z}', True,
                                                  [0, 0, 0])
    orientation_text_width = text_surface_camera_orientation.get_width()
    screen.blit(text_surface_camera_orientation, dest=[SCREEN_WIDTH - orientation_text_width, coord_text_height])


def draw_shape(camera: Camera,
               screen: pygame.Surface,
               shape: Shape):
    draw_camera_info(camera, screen)

    for edge in shape.lines:
        point1, point2 = edge

        x1 = (point1.get_x() + 1) * SCREEN_WIDTH / 2
        y1 = (point1.get_y() + 1) * SCREEN_HEIGHT / 2

        x2 = (point2.get_x() + 1) * SCREEN_WIDTH / 2
        y2 = (point2.get_y() + 1) * SCREEN_HEIGHT / 2

        pygame.draw.line(screen, [0, 0, 0], (x1, y1), (x2, y2))


def draw(camera: Camera, screen: pygame.Surface, shapes: list[Shape]):
    screen.fill((255, 255, 255))

    for shape in shapes:
        shape = on_update_shape(camera, shape)
        draw_shape(camera, screen, shape)
    pygame.display.update()


def main() -> None:
    cuboid = loader.read_object_from_file("cuboid.txt")

    offsets = [Vector4.from_cords(1, 0, 1, 1),
               Vector4.from_cords(-4, 0, 1, 1),
               Vector4.from_cords(1, 0, 5, 1),
               Vector4.from_cords(-4, 0, 5, 1)]

    shapes = []
    for os in offsets:
        shape = cuboid.copy()
        shape.set_offset(os)
        shapes.append(shape)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hello world")

    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    draw(camera, screen, shapes)
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
            draw(camera, screen, shapes)


if __name__ == "__main__":
    main()
