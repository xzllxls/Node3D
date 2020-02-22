from PySide2.QtGui import QMatrix3x3, QMatrix4x4
from .Quaternion import quaternion
from .Vector import vector, vector4
import numpy as np
import quaternion as qt
from math import *
from .utils import _EPS, _AXES2TUPLE, _NEXT_AXIS, _TUPLE2AXES, vector_norm


class matrix3x3(object):
    def __init__(self, _data=None):
        if _data is not None and _data.shape == (3, 3):
            self._data = _data
        else:
            self.setToIdentity()

    def __getitem__(self, i):
        return self._data[i]

    def __setitem__(self, i, j, x):
        self._data[i, j] = x

    def __iter__(self):
        for i in self._data.flatten():
            yield i

    def __add__(self, v):
        return matrix3x3(self._data + v)

    def __sub__(self, v):
        return matrix3x3(self._data - v)

    def __mul__(self, v):
        if type(v) is matrix3x3:
            return matrix3x3(np.dot(self._data, v.data()))
        else:
            return matrix3x3(self._data * v)

    def __truediv__(self, v):
        return matrix3x3(self._data / v)

    def __repr__(self):
        return str(self._data)

    def setToIdentity(self):
        self._data = np.identity(3, dtype=np.float64)

    def data(self):
        return self._data

    def scale(self, scale):
        self._data[0][0] *= scale[0]
        self._data[1][1] *= scale[1]
        self._data[2][2] *= scale[2]

    def setScale(self, scale):
        self._data[0][0] = scale[0]
        self._data[1][1] = scale[1]
        self._data[2][2] = scale[2]

    def rotate(self, angle, direction, point=None):
        m = matrix3x3.from_rotate(angle, direction, point)
        self._data = np.dot(self._data, m._data)

    def dirScale(self, dir, scale):
        m = matrix3x3.from_dir_scale(dir, scale)
        self._data = np.dot(self._data, m.data())

    def invert(self):
        self._data = self.inverted()

    def inverted(self):
        try:
            return np.linalg.inv(self._data)
        except:
            return np.zeros((3,3))

    def rotateVector(self, vec):
        return vector.fromList(np.dot(self._data, vec))

    def toMatrix4x4(self):
        mat = np.c_[self._data, np.zeros(3)]
        mat = np.r_[mat, np.zeros((1, 4))]
        mat[3][3] = 1.0
        return matrix4x4(mat)

    @staticmethod
    def from_quaternion(q):
        return matrix3x3(qt.as_rotation_matrix(q))

    @staticmethod
    def zeros():
        return matrix3x3(np.zeros((3, 3)))

    @staticmethod
    def ones():
        return matrix3x3(np.ones((3, 3)))

    @staticmethod
    def reflection(point, normal):
        point = np.array(point)
        normal = np.array(normal.normalized())
        M = np.identity(3)
        M[:3, :3] -= 2.0 * np.outer(normal, normal)
        M[:3, 3] = (2.0 * np.dot(point[:3], normal)) * normal
        return matrix3x3(M)

    @staticmethod
    def from_rotate(angle, direction, point=None):
        sina = sin(angle)
        cosa = cos(angle)
        direction = np.array(direction.normalized())
        # rotation matrix around unit vector
        R = np.array(((cosa, 0.0, 0.0),
                      (0.0, cosa, 0.0),
                      (0.0, 0.0, cosa)), dtype=np.float64)
        R += np.outer(direction, direction) * (1.0 - cosa)
        direction *= sina
        R += np.array(((0.0, -direction[2], direction[1]),
                       (direction[2], 0.0, -direction[0]),
                       (-direction[1], direction[0], 0.0)),
                      dtype=np.float64)
        M = np.identity(3)
        M[:3, :3] = R
        if point is not None:
            # rotation not around origin
            point = np.array(point[:3], dtype=np.float64, copy=False)
            M[:3, 3] = point - np.dot(R, point)
        return matrix3x3(M)

    @staticmethod
    def from_eulers(eulers):
        pitch = eulers[0]
        roll = eulers[1]
        yaw = eulers[2]

        sP = sin(pitch)
        cP = cos(pitch)
        sR = sin(roll)
        cR = cos(roll)
        sY = sin(yaw)
        cY = cos(yaw)

        data = np.array(
            [[cY * cP, -cY * sP * cR + sY * sR, cY * sP * sR + sY * cR, ],
             [sP, cP * cR, -cP * sR, ],
             [-sY * cP, sY * sP * cR + cY * sR, -sY * sP * sR + cY * cR, ],
             ], dtype=np.float64)

        return matrix3x3(data)

    @staticmethod
    def from_x_rotation(theta):
        cosT = cos(theta)
        sinT = sin(theta)

        data = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, cosT, -sinT],
                [0.0, sinT, cosT]
            ],
            dtype=np.float64)
        return matrix3x3(data)

    @staticmethod
    def from_y_rotation(theta):
        cosT = cos(theta)
        sinT = sin(theta)

        data = np.array(
            [
                [cosT, 0.0, sinT],
                [0.0, 1.0, 0.0],
                [-sinT, 0.0, cosT]
            ],
            dtype=np.float64
        )

        return matrix3x3(data)

    @staticmethod
    def from_z_rotation(theta):
        cosT = cos(theta)
        sinT = sin(theta)

        data = np.array(
            [
                [cosT, -sinT, 0.0],
                [sinT, cosT, 0.0],
                [0.0, 0.0, 1.0]
            ],
            dtype=np.float64
        )
        return matrix3x3(data)

    @staticmethod
    def from_dir_scale(dir, scale):
        dir = dir.normalized()
        scale -= 1.0
        m = np.zeros((3, 3), dtype=np.float64)
        m[0][0] = 1 + scale * dir.x() * dir.x()
        m[0][1] = scale * dir.x() * dir.y()
        m[0][2] = scale * dir.x() * dir.z()
        m[1][0] = scale * dir.x() * dir.y()
        m[1][1] = 1 + scale * dir.y() * dir.y()
        m[1][2] = scale * dir.y() * dir.z()
        m[2][0] = scale * dir.x() * dir.z()
        m[2][1] = scale * dir.y() * dir.z()
        m[2][2] = 1 + scale * dir.z() * dir.z()
        return matrix3x3(m)

class matrix4x4(object):
    def __init__(self, _data=None):
        if _data is not None and _data.shape == (4, 4):
            self._data = _data
        else:
            self.setToIdentity()

    def __getitem__(self, i, j):
        return self._data[i, j]

    def __setitem__(self, i, j, x):
        self._data[i, j] = x

    def __iter__(self):
        for i in self._data.flatten():
            yield i

    def __add__(self, v):
        return matrix4x4(self._data + v)

    def __sub__(self, v):
        return matrix4x4(self._data - v)

    def __mul__(self, v):
        if type(v) is matrix4x4:
            return matrix4x4(np.dot(self._data, v.data()))
        else:
            return matrix4x4(self._data * v)

    def __truediv__(self, v):
        return matrix4x4(self._data / v)

    def __repr__(self):
        return str(self._data)

    def setToIdentity(self):
        self._data = np.identity(4, dtype=np.float64)

    def data(self):
        return self._data

    def translate(self, trans):
        self._data[3][0] += trans[0]
        self._data[3][1] += trans[1]
        self._data[3][2] += trans[2]

    def scale(self, scale):
        self._data[0][0] *= scale[0]
        self._data[1][1] *= scale[1]
        self._data[2][2] *= scale[2]

    def setTranslate(self, trans):
        self._data[3][:3] = trans

    def setScale(self, scale):
        self._data[0][0] = scale[0]
        self._data[1][1] = scale[1]
        self._data[2][2] = scale[2]

    def dirScale(self, dir, scale):
        m = matrix4x4.from_dir_scale(dir, scale)
        self._data = np.dot(self._data, m.data())

    def getTranslate(self):
        return self._data[3][:3].copy()

    def invert(self):
        self._data = self.inverted()

    def inverted(self):
        try:
            return np.linalg.inv(self._data)
        except:
            return matrix4x4.from_scale([0, 0, 0])

    def transformVector(self, vec):
        v = vector4(vec.x(), vec.y(), vec.z(), 1)
        return vector.fromList(np.dot(self._data, v))

    def toMatrix3x3(self):
        return matrix3x3(self._data[:3][..., [0, 1, 2]].copy())

    def decompose(self):
        M = np.array(self._data, dtype=np.float64, copy=True).T
        if abs(M[3, 3]) < _EPS:
            raise ValueError("M[3, 3] is zero")
        M /= M[3, 3]
        P = M.copy()
        P[:, 3] = 0, 0, 0, 1
        if not np.linalg.det(P):
            raise ValueError("Matrix is singular")

        scale = np.zeros((3,), dtype=np.float64)
        shear = [0, 0, 0]
        angles = [0, 0, 0]

        if any(abs(M[:3, 3]) > _EPS):
            perspective = np.dot(M[:, 3], np.linalg.inv(P.T))
            M[:, 3] = 0, 0, 0, 1
        else:
            perspective = np.array((0, 0, 0, 1), dtype=np.float64)

        translate = M[3, :3].copy()
        M[3, :3] = 0

        row = M[:3, :3].copy()
        scale[0] = vector_norm(row[0])
        row[0] /= scale[0]
        shear[0] = np.dot(row[0], row[1])
        row[1] -= row[0] * shear[0]
        scale[1] = vector_norm(row[1])
        row[1] /= scale[1]
        shear[0] /= scale[1]
        shear[1] = np.dot(row[0], row[2])
        row[2] -= row[0] * shear[1]
        shear[2] = np.dot(row[1], row[2])
        row[2] -= row[1] * shear[2]
        scale[2] = vector_norm(row[2])
        row[2] /= scale[2]
        shear[1:] /= scale[2]

        if np.dot(row[0], np.cross(row[1], row[2])) < 0:
            scale *= -1
            row *= -1

        angles[1] = asin(-row[0, 2])
        if cos(angles[1]):
            angles[0] = atan2(row[1, 2], row[2, 2])
            angles[2] = atan2(row[0, 1], row[0, 0])
        else:
            # angles[0] = math.atan2(row[1, 0], row[1, 1])
            angles[0] = atan2(-row[2, 1], row[1, 1])
            angles[2] = 0.0

        return vector.fromList(scale), vector.fromList(shear), \
               vector.fromList(angles), vector.fromList(translate), \
               perspective

    def to_translation(self):
        return vector.fromList(self._data[:3, 3].copy())

    @staticmethod
    def from_quaternion(q):
        return matrix4x4(qt.as_matrix4x4(q))

    @staticmethod
    def zeros():
        return matrix4x4(np.zeros((4, 4)))

    @staticmethod
    def ones():
        return matrix4x4(np.ones((4, 4)))

    @staticmethod
    def reflection(point, normal):
        point = np.array(point)
        normal = np.array(normal.normalized())
        M = np.identity(4)
        M[:3, :3] -= 2.0 * np.outer(normal, normal)
        M[:3, 3] = (2.0 * np.dot(point[:3], normal)) * normal
        return matrix4x4(M)

    @staticmethod
    def from_projection(point, normal, direction=None,
                          perspective=None, pseudo=False):
        M = np.identity(4)
        point = np.array(point[:3], dtype=np.float64, copy=False)
        normal = np.array(normal.normalized())
        if perspective is not None:
            # perspective projection
            perspective = np.array(perspective[:3], dtype=np.float64,
                                      copy=False)
            M[0, 0] = M[1, 1] = M[2, 2] = np.dot(perspective-point, normal)
            M[:3, :3] -= np.outer(perspective, normal)
            if pseudo:
                # preserve relative depth
                M[:3, :3] -= np.outer(normal, normal)
                M[:3, 3] = np.dot(point, normal) * (perspective+normal)
            else:
                M[:3, 3] = np.dot(point, normal) * perspective
            M[3, :3] = -normal
            M[3, 3] = np.dot(perspective, normal)
        elif direction is not None:
            # parallel projection
            direction = np.array(direction, dtype=np.float64, copy=False)
            scale = np.dot(direction, normal)
            M[:3, :3] -= np.outer(direction, normal) / scale
            M[:3, 3] = direction * (np.dot(point, normal) / scale)
        else:
            # orthogonal projection
            M[:3, :3] -= np.outer(normal, normal)
            M[:3, 3] = np.dot(point, normal) * normal
        return matrix4x4(M)
    
    @staticmethod
    def from_scale(factor, origin=None, direction=None):
        '''Return matrix to scale by factor around origin in direction.'''

        if direction is None:
            # uniform scaling
            M = np.array(((factor, 0.0, 0.0, 0.0),
                             (0.0, factor, 0.0, 0.0),
                             (0.0, 0.0, factor, 0.0),
                             (0.0, 0.0, 0.0, 1.0)), dtype=np.float64)
            if origin is not None:
                M[:3, 3] = origin[:3]
                M[:3, 3] *= 1.0 - factor
        else:
            # nonuniform scaling
            direction = np.array(direction)
            factor = 1.0 - factor
            M = np.identity(4)
            M[:3, :3] -= factor * np.outer(direction, direction)
            if origin is not None:
                M[:3, 3] = (factor * np.dot(origin[:3], direction)) * direction
        return matrix4x4(M)

    @staticmethod
    def from_shear(angle, direction, point, normal):
        normal = np.array(normal.normalized())
        direction = np.array(direction.normalized())
        if abs(np.dot(normal, direction)) > 1e-6:
            raise ValueError("direction and normal vectors are not orthogonal")
        angle = tan(angle)
        M = np.identity(4)
        M[:3, :3] += angle * np.outer(direction, normal)
        M[:3, 3] = -angle * np.dot(point[:3], normal) * direction
        return matrix4x4(M)

    @staticmethod
    def from_euler_angles(ai, aj, ak, axes='sxyz'):
        try:
            firstaxis, parity, repetition, frame = _AXES2TUPLE[axes]
        except (AttributeError, KeyError):
            _ = _TUPLE2AXES[axes]
            firstaxis, parity, repetition, frame = axes

        i = firstaxis
        j = _NEXT_AXIS[i + parity]
        k = _NEXT_AXIS[i - parity + 1]

        if frame:
            ai, ak = ak, ai
        if parity:
            ai, aj, ak = -ai, -aj, -ak

        si, sj, sk = sin(ai), sin(aj), sin(ak)
        ci, cj, ck = cos(ai), cos(aj), cos(ak)
        cc, cs = ci * ck, ci * sk
        sc, ss = si * ck, si * sk

        M = np.identity(4)
        if repetition:
            M[i, i] = cj
            M[i, j] = sj * si
            M[i, k] = sj * ci
            M[j, i] = sj * sk
            M[j, j] = -cj * ss + cc
            M[j, k] = -cj * cs - sc
            M[k, i] = -sj * ck
            M[k, j] = cj * sc + cs
            M[k, k] = cj * cc - ss
        else:
            M[i, i] = cj * ck
            M[i, j] = sj * sc - cs
            M[i, k] = sj * cc + ss
            M[j, i] = cj * sk
            M[j, j] = sj * ss + cc
            M[j, k] = sj * cs - sc
            M[k, i] = -sj
            M[k, j] = cj * si
            M[k, k] = cj * ci
        return matrix4x4(M)

    @staticmethod
    def from_compose(scale=None, shear=None, angles=None, translate=None,
                       perspective=None):
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
            R = matrix4x4.from_euler_angles(angles[0], angles[1], angles[2], 'sxyz')
            M = np.dot(M, R.data())
        if shear is not None:
            Z = np.identity(4)
            Z[1, 2] = shear[2]
            Z[0, 2] = shear[1]
            Z[0, 1] = shear[0]
            M = np.dot(M, Z)
        if translate is not None:
            M[3, :3] = translate[:3]
        M /= M[3, 3]
        return matrix4x4(M)

    @staticmethod
    def from_lookAt(eye, target, up):
        z = (eye - target).normalized()
        x = up.cross(z).normalized()
        y = z.cross(x).normalized()
        Minv = np.identity(4, dtype=np.float64)
        Tr = np.identity(4, dtype=np.float64)
        for i in range(3):
            Minv[0][i] = x[i]
            Minv[1][i] = y[i]
            Minv[2][i] = z[i]
            Tr[i][3] = -target[i]
        return matrix4x4(np.dot(Minv, Tr))

    @staticmethod
    def from_translation(trans):
        M = np.identity(4)
        M[:3, 3] = np.array(trans)
        return matrix4x4(M)

    @staticmethod
    def from_eulers(eulers):
        return matrix3x3.from_eulers(eulers).toMatrix4x4()

    @staticmethod
    def from_dir_scale(dir, scale):
        return matrix3x3.from_dir_scale(dir, scale).toMatrix4x4()

    @staticmethod
    def from_x_rotation(theta):
        return matrix3x3.from_x_rotation(theta).toMatrix4x4()

    @staticmethod
    def from_y_rotation(theta):
        return matrix3x3.from_y_rotation(theta).toMatrix4x4()

    @staticmethod
    def from_z_rotation(theta):
        return matrix3x3.from_z_rotation(theta).toMatrix4x4()

    @staticmethod
    def create_perspective_projection_from_bounds(
            left,
            right,
            bottom,
            top,
            near,
            far):

        A = (right + left) / (right - left)
        B = (top + bottom) / (top - bottom)
        C = -(far + near) / (far - near)
        D = -2. * far * near / (far - near)
        E = 2. * near / (right - left)
        F = 2. * near / (top - bottom)

        data = np.array((
            (E, 0., 0., 0.),
            (0., F, 0., 0.),
            (A, B, C, -1.),
            (0., 0., D, 0.),
        ), dtype=np.float64)

        return matrix4x4(data)

    @staticmethod
    def create_perspective_projection(fovy, aspect, near, far):
        ymax = near * np.tan(fovy * np.pi / 360.0)
        xmax = ymax * aspect
        return matrix4x4.create_perspective_projection_from_bounds(-xmax, xmax, -ymax, ymax, near, far)



if __name__ == "__main__":
    a = matrix3x3()
    a *= 10
    print(a)
