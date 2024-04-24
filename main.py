import pygame

pygame.init()

import sys
from itertools import chain

import numpy as np

from camera import Camera
from clipping import triangle_clip_against_plane
from drawing import draw_camera_info, draw_shape, SCREEN_WIDTH, SCREEN_HEIGHT, DEPTH_BUFFER
from shape import Shape
from vector import Vector4


def update_shape(camera: Camera, shape: Shape) -> Shape:
    view_matrix = camera.get_view_matrix()
    perspective_projection_matrix = camera.get_perspective_projection_matrix()

    triangles_after_view_matrix: list[tuple[Vector4, Vector4, Vector4]] = []
    for triangle in shape.triangles:
        updated_triangle: tuple[Vector4, Vector4, Vector4] = (view_matrix.multiply_by_vector(triangle[0]),
                                                              view_matrix.multiply_by_vector(triangle[1]),
                                                              view_matrix.multiply_by_vector(triangle[2]))
        triangles_after_view_matrix.append(updated_triangle)

    visible_triangles = []

    for triangle_after_view_matrix in triangles_after_view_matrix:
        edge1 = triangle_after_view_matrix[1] - triangle_after_view_matrix[0]
        edge2 = triangle_after_view_matrix[2] - triangle_after_view_matrix[0]
        normal = Vector4.cross_product_xyz(edge1, edge2)
        normal = normal.get_normalized_xyz()

        dot_product = Vector4.dot_product_xyz(normal, triangle_after_view_matrix[0])
        if dot_product > 0:
            visible_triangles.append(triangle_after_view_matrix)

    clipped_triangles_z = clip_triangles_against_plane(visible_triangles,
                                                       Vector4.from_cords(0, 0, camera.Z_NEAR, 1),
                                                       Vector4.from_cords(0, 0, 1, 1))

    triangles_after_perspective_projection = []
    for clipped_triangle_z in clipped_triangles_z:
        perspective_projected_triangle = (
            perspective_projection_matrix.multiply_by_vector(clipped_triangle_z[0]),
            perspective_projection_matrix.multiply_by_vector(clipped_triangle_z[1]),
            perspective_projection_matrix.multiply_by_vector(clipped_triangle_z[2])
        )
        triangles_after_perspective_projection.append(perspective_projected_triangle)

    clipped_triangles = triangles_after_perspective_projection
    clipped_triangles = clip_triangles_against_plane(clipped_triangles,
                                                     Vector4.from_cords(-1, 0, 0, 1),
                                                     Vector4.from_cords(1, 0, 0, 1))
    clipped_triangles = clip_triangles_against_plane(clipped_triangles,
                                                     Vector4.from_cords(1, 0, 0, 1),
                                                     Vector4.from_cords(-1, 0, 0, 1))
    clipped_triangles = clip_triangles_against_plane(clipped_triangles,
                                                     Vector4.from_cords(0, -1, 0, 1),
                                                     Vector4.from_cords(0, 1, 0, 1))
    clipped_triangles = clip_triangles_against_plane(clipped_triangles,
                                                     Vector4.from_cords(0, 1, 0, 1),
                                                     Vector4.from_cords(0, -1, 0, 1))

    return Shape(clipped_triangles, shape.color)


def clip_triangles_against_plane(triangles: list[tuple[Vector4, Vector4, Vector4]],
                                 plane_p: Vector4,
                                 plane_n: Vector4) -> list[tuple[Vector4, Vector4, Vector4]]:
    clipped_triangles = chain.from_iterable(triangle_clip_against_plane(plane_p, plane_n, triangle)
                                            for triangle in triangles)
    return list(clipped_triangles)


def draw(camera: Camera, screen: pygame.Surface, shapes: list[Shape]):
    screen.fill((255, 255, 255))
    DEPTH_BUFFER.fill(np.inf)

    for shape in shapes:
        shape = update_shape(camera, shape)
        draw_shape(screen, shape)
    draw_camera_info(camera, screen)
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

    colors = [(127, 0, 127),
              (0, 255, 0),
              (0, 0, 255),
              (127, 127, 0)]
    for i, color in enumerate(colors):
        shapes[i].set_color(color)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hello world")

    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    if is_continous:
        continous_program_loop(camera, screen, shapes)
    else:
        event_based_program_loop(camera, screen, shapes)


if __name__ == "__main__":
    main(False)
