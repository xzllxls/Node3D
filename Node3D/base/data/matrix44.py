from pyrr.matrix44 import *
from pyrr import Matrix44, vector3
import numpy as np


def create_from_compose(scale=None, shear=None, angles=None,
                        translate=None, perspective=None):
    M = np.identity(4)
    if perspective is not None:
        P = np.identity(4)
        P[3, :] = perspective[:4]
        M = np.dot(M, P)
    if scale is not None:
        S = np.identity(4)
        S[0, 0] = scale[0]
        S[1, 1] = scale[1]
        S[2, 2] = scale[2]
        M = np.dot(M, S)
    if angles is not None:
        R = create_from_eulers(np.array(angles, dtype=np.float64))
        M = np.dot(M, R)
    if shear is not None:
        Z = np.identity(4)
        Z[1, 2] = shear[2]
        Z[0, 2] = shear[1]
        Z[0, 1] = shear[0]
        M = np.dot(M, Z)
    if translate is not None:
        M[3, :3] = translate[:3]
    M /= M[3, 3]
    return M


def create_look_at(eye, target, up):
    z = vector3.normalize(eye - target)
    x = vector3.normalize(vector3.cross(up, z))
    y = vector3.normalize(vector3.cross(z, x))
    Minv = np.identity(4, dtype=np.float64)
    Tr = np.identity(4, dtype=np.float64)
    for i in range(3):
        Minv[0][i] = x[i]
        Minv[1][i] = y[i]
        Minv[2][i] = z[i]
        Tr[i][3] = -target[i]
    return np.dot(Minv, Tr)