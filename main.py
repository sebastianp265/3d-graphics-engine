import sys

import pygame

from camera import Camera
from clipping import line_clip_against_plane
from drawing import draw_camera_info, draw_shape
from shape import Shape
from vector import Vector4

pygame.init()

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

FONT = pygame.font.Font(pygame.font.get_default_font(), 12)


def update_shape(camera: Camera, shape: Shape) -> Shape:
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


def draw(camera: Camera, screen: pygame.Surface, shapes: list[Shape]):
    screen.fill((255, 255, 255))

    draw_camera_info(camera, screen, FONT)
    for shape in shapes:
        shape = update_shape(camera, shape)
        draw_shape(screen, shape)
    pygame.display.update()


def continous_program_loop(camera: Camera, screen: pygame.Surface, shapes: list[Shape]):
    clock = pygame.time.Clock()
    fps = 60
    delta_time = 0

    running = True
    draw(camera, screen, shapes)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        camera.set_delta_time(delta_time)
        if keys[pygame.K_UP]:
            camera.look_up()
        if keys[pygame.K_DOWN]:
            camera.look_down()
        if keys[pygame.K_RIGHT]:
            camera.look_right()
        if keys[pygame.K_LEFT]:
            camera.look_left()
        if keys[pygame.K_e]:
            camera.rotate_right()
        if keys[pygame.K_q]:
            camera.rotate_left()

        if keys[pygame.K_w]:
            camera.move_front()
        if keys[pygame.K_s]:
            camera.move_back()
        if keys[pygame.K_a]:
            camera.move_left()
        if keys[pygame.K_d]:
            camera.move_right()
        if keys[pygame.K_SPACE]:
            camera.move_up()
        if keys[pygame.K_LSHIFT]:
            camera.move_down()

        if keys[pygame.K_z]:
            camera.zoom_in()
        if keys[pygame.K_c]:
            camera.zoom_out()

        draw(camera, screen, shapes)

        delta_time = clock.tick(fps) / 100

    pygame.quit()
    sys.exit()


def event_based_program_loop(camera: Camera, screen: pygame.Surface, shapes: list[Shape]):
    draw(camera, screen, shapes)
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                match event.key:
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


def main(is_continous: bool = False) -> None:
    cuboid = Shape.read_shape_from_file("cuboid.txt")

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

    if is_continous:
        continous_program_loop(camera, screen, shapes)
    else:
        event_based_program_loop(camera, screen, shapes)


if __name__ == "__main__":
    main(True)
