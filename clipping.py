from vector import Vector4


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


def triangle_clip_against_plane(plane_p: Vector4,
                                plane_n: Vector4,
                                triangle: tuple[Vector4, Vector4, Vector4]
                                ) -> list[tuple[Vector4, Vector4, Vector4]] | None:
    def get_signed_distance(point: Vector4):
        return Vector4.dot_product_xyz(plane_n, point) - Vector4.dot_product_xyz(plane_n, plane_p)

    p0_dist = get_signed_distance(triangle[0])
    p1_dist = get_signed_distance(triangle[1])
    p2_dist = get_signed_distance(triangle[2])

    inside_points = []
    outside_points = []
    if p0_dist >= 0:
        inside_points.append(triangle[0])
    else:
        outside_points.append(triangle[0])

    if p1_dist >= 0:
        inside_points.append(triangle[1])
    else:
        outside_points.append(triangle[1])

    if p2_dist >= 0:
        inside_points.append(triangle[2])
    else:
        outside_points.append(triangle[2])

    if len(inside_points) == 0:
        return None
    if len(inside_points) == 3:
        return [triangle]

    if len(inside_points) == 1 and len(outside_points) == 2:
        p0 = inside_points[0]
        p1 = get_intersection_point_of_line_with_a_plane(plane_p,
                                                         plane_n,
                                                         p0,
                                                         outside_points[0])
        p2 = get_intersection_point_of_line_with_a_plane(plane_p,
                                                         plane_n,
                                                         p0,
                                                         outside_points[1])
        return [(p0, p1, p2)]

    if len(inside_points) == 2 and len(outside_points) == 1:
        p00 = inside_points[0]
        p10 = inside_points[1]
        p20 = get_intersection_point_of_line_with_a_plane(plane_p,
                                                          plane_n,
                                                          p00,
                                                          outside_points[0])
        p01 = inside_points[1]
        p11 = get_intersection_point_of_line_with_a_plane(plane_p,
                                                          plane_n,
                                                          p01,
                                                          outside_points[0])
        p21 = p20.copy()

        return [(p00, p10, p20), (p01, p11, p21)]

    raise Exception("Not expected to end up here")


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
