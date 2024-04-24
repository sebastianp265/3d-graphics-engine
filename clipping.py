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
