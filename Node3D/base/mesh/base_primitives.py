import math
import numpy as np
from numpy.linalg import norm
from ..data import quaternion, vector
from math import sin, cos


def generate_tube(p0, p1, r0_out, r1_out, r0_in, r1_in, num_segments=16,
                  with_quad=True):
    """ Generate generalized tube (i.e. cylinder with an axial hole).
    Args:
        p0 (``np.ndarray``): Bottom center.
        p1 (``np.ndarray``): Top center.
        r0_out (``float``): Bottom outer radius.
        r1_out (``float``): Top outer radius.
        r0_in (``float``): Bottom inner radius.
        r1_in (``float``): Top inner radius.
        num_segments (``int``): Number of segments to a discrete circle consists.
        with_quad (``bool``): Output a quad mesh instead.

    """

    assert (len(p0) == 3)
    assert (len(p1) == 3)
    Z = np.array([0, 0, 1], dtype=float)
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    axis = p1 - p0
    l = norm(axis)
    if l <= 1e-12:
        axis = Z
    N = num_segments

    angles = [2 * math.pi * i / float(N) for i in range(N)]
    rim = np.array([[math.cos(theta), math.sin(theta), 0.0]
                    for theta in angles])
    rot = quaternion.from_two_vector(vector.fromList(Z), vector.fromList(axis)).toMatrix3x3()

    bottom_outer_rim = np.dot(rot, rim.T).T * r0_out + p0
    bottom_inner_rim = np.dot(rot, rim.T).T * r0_in + p0
    top_outer_rim = np.dot(rot, rim.T).T * r1_out + p1
    top_inner_rim = np.dot(rot, rim.T).T * r1_in + p1

    vertices = np.vstack([
        bottom_outer_rim,
        bottom_inner_rim,
        top_outer_rim,
        top_inner_rim])

    if with_quad:
        top = np.array([
            [2 * N + i, 2 * N + (i + 1) % N, 3 * N + (i + 1) % N, 3 * N + i]
            for i in range(N)])
        bottom = np.array([
            [(i + 1) % N, i, N + i, N + (i + 1) % N]
            for i in range(N)])
        inner = np.array([
            [3 * N + i, 3 * N + (i + 1) % N, N + (i + 1) % N, N + i]
            for i in range(N)])
        outer = np.array([
            [i, (i + 1) % N, 2 * N + (i + 1) % N, 2 * N + i]
            for i in range(N)])
        faces = np.vstack([top, bottom, inner, outer])
    else:
        top = np.array([
            [[2 * N + i, 2 * N + (i + 1) % N, 3 * N + i],
             [3 * N + i, 2 * N + (i + 1) % N, 3 * N + (i + 1) % N]
             ] for i in range(N)])
        bottom = np.array([
            [[(i + 1) % N, i, N + i],
             [(i + 1) % N, N + i, N + (i + 1) % N]
             ] for i in range(N)])
        inner = np.array([
            [[3 * N + i, 3 * N + (i + 1) % N, N + i],
             [N + i, 3 * N + (i + 1) % N, N + (i + 1) % N]
             ] for i in range(N)])
        outer = np.array([
            [[i, (i + 1) % N, 2 * N + i],
             [2 * N + i, (i + 1) % N, 2 * N + (i + 1) % N]
             ] for i in range(N)])

        faces = np.vstack([
            top.reshape((-1, 3)),
            bottom.reshape((-1, 3)),
            inner.reshape((-1, 3)),
            outer.reshape((-1, 3))])
    return vertices, faces


def generate_sphere(radius, resolution):
    faces = []
    tri_faces = []
    size = 2 * resolution * (resolution - 1) + 2
    verts = np.empty((size, 3), dtype=np.float64)
    verts[0] = [0.0, radius, 0.0]
    verts[1] = [0.0, -radius, 0.0]

    step = np.pi / float(resolution)
    for i in range(1, resolution):
        alpha = step * i
        base = 2 + 2 * resolution * (i - 1)
        for j in range(2 * resolution):
            theta = step * j
            verts[base + j] = np.array([sin(alpha) * cos(theta), cos(alpha), sin(alpha) * sin(theta)]) * radius

    for j in range(2 * resolution):
        j1 = (j + 1) % (2 * resolution)
        base = 2
        tri_faces.append([0, base + j, base + j1])
        base = 2 + 2 * resolution * (resolution - 2)
        tri_faces.append([1, base + j1, base + j])

    for i in range(1, resolution - 1):
        base1 = 2 + 2 * resolution * (i - 1)
        base2 = base1 + 2 * resolution
        for j in range(2 * resolution):
            j1 = (j + 1) % (2 * resolution)
            faces.append([base2 + j, base2 + j1, base1 + j1, base1 + j])

    return tri_faces, faces, verts


def generate_cylinder(radius, height, resolution, split):
    faces = []
    tri_faces = []

    verts = np.empty((resolution * (split + 1) + 2, 3), dtype=np.float64)
    verts[0] = [0.0, height * 0.5, 0.0]
    verts[1] = [0.0, -height * 0.5, 0.0]

    step = np.pi * 2.0 / float(resolution)
    h_step = height / float(split)
    for i in range(split + 1):
        for j in range(resolution):
            theta = step * j
            verts[2 + resolution * i + j] = [cos(theta) * radius, height * 0.5 - h_step * i, sin(theta) * radius]

    for j in range(resolution):
        j1 = (j + 1) % resolution
        base = 2
        tri_faces.append([0, base + j, base + j1])
        base = 2 + resolution * split
        tri_faces.append([1, base + j1, base + j])

    for i in range(split):
        base1 = 2 + resolution * i
        base2 = base1 + resolution
        for j in range(resolution):
            j1 = (j + 1) % resolution
            faces.append([base2 + j, base2 + j1, base1 + j1, base1 + j])

    return tri_faces, faces, verts


def generate_cone(radius, height, resolution, split):
    faces = []
    tri_faces = []

    verts = np.empty((resolution * split + 2, 3), dtype=np.float64)
    verts[0] = [0.0, 0.0, 0.0]
    verts[1] = [0.0, height, 0.0]

    step = np.pi * 2.0 / float(resolution)
    h_step = height / float(split)
    r_step = radius / float(split)
    for i in range(split):
        base = 2 + resolution * i
        r = r_step * (split - i)
        for j in range(resolution):
            theta = step * j
            verts[base + j] = [cos(theta) * r, h_step * i, sin(theta) * r]

    for j in range(resolution):
        j1 = (j + 1) % resolution
        base = 2
        tri_faces.append([0, base + j, base + j1])
        base = 2 + resolution * (split - 1)
        tri_faces.append([1, base + j1, base + j])

    for i in range(split - 1):
        base1 = 2 + resolution * i
        base2 = base1 + resolution
        for j in range(resolution):
            j1 = (j + 1) % resolution
            faces.append([base2 + j1, base2 + j, base1 + j, base1 + j1])

    return tri_faces, faces, verts


def generate_torus(torus_radius, tube_radius, radial_resolution, tubular_resolution):
    verts = np.empty((radial_resolution * tubular_resolution, 3), dtype=np.float64)
    faces = np.empty((radial_resolution * tubular_resolution, 4), dtype=np.uint)

    def vert_idx(uidx, vidx):
        return uidx * tubular_resolution + vidx

    u_step = 2 * np.pi / float(radial_resolution)
    v_step = 2 * np.pi / float(tubular_resolution)

    for uidx in range(radial_resolution):
        u = uidx * u_step
        w = np.array([cos(u), 0, sin(u)])

        for vidx in range(tubular_resolution):
            v = vidx * v_step
            verts[vert_idx(uidx, vidx)] = torus_radius * w + tube_radius * cos(v) * w + \
                                          np.array([0, tube_radius * sin(v), 0])

            face_idx = uidx * tubular_resolution + vidx

            faces[face_idx] = [
                    vert_idx((uidx + 1) % radial_resolution, vidx),
                    vert_idx((uidx + 1) % radial_resolution, (vidx + 1) % tubular_resolution),
                    vert_idx(uidx, (vidx + 1) % tubular_resolution),
                    vert_idx(uidx, vidx)]

    return faces, verts
