from .Vector import vector, vector4, vector2
from quaternion import quaternion as quat
import quaternion as qt
from math import sin, cos, sqrt, acos
import numpy as np
from .utils import vector_norm, _EPS


class quaternion(quat):
    def __init__(self, w=1, x=0, y=0, z=0):
        super(quaternion, self).__init__(w, x, y, z)

    def __len__(self):
        return 4

    def __getitem__(self, i):
        if i == 0:
            return self.w
        elif i == 1:
            return self.x
        elif i == 2:
            return self.y
        elif i == 4:
            return self.z
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __setitem__(self, i, x):
        if i == 0:
            self.w = x
        elif i == 1:
            self.x = x
        elif i == 2:
            self.y = x
        elif i == 3:
            self.z = x
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __iter__(self):
        yield self.w
        yield self.x
        yield self.y
        yield self.z

    def __abs__(self):
        return quaternion(abs(self.w), abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, q):
        return quaternion.fromQuaternion(super(quaternion, self).__add__(q))

    def __sub__(self, q):
        return quaternion.fromQuaternion(super(quaternion, self).__sub__(q))

    def __mul__(self, q):
        return quaternion.fromQuaternion(super(quaternion, self).__mul__(q))

    def __truediv__(self, q):
        return quaternion.fromQuaternion(super(quaternion, self).__truediv__(q))


    def setW(self, x):
        self.w = x

    def setX(self, x):
        self.x = x

    def setY(self, x):
        self.y = x

    def setZ(self, x):
        self.z = x

    def rotateVector(self, vec):
        quat_vector = vector(self.x, self.y, self.z)
        quat_scalar = self.w
        t = 2.0 * quat_vector.cross(vec)
        rotated_vector = vec + (quat_scalar * t) + quat_vector.cross(t)
        return rotated_vector

    def normalized(self):
        return np.normalized(self)

    def normalize(self):
        q = np.normalized(self)
        self.x = q.x
        self.y = q.y
        self.z = q.z
        self.w = q.w

    def conjugate(self):
        return quaternion(self.w, self.x*-1, self.y*-1, self.z*-1)

    def invert(self):
        self = self.inverted()

    def inverted(self):
        return self.conjugate() / np.dot(self, self)

    def toList(self):
        return list(self)

    def toVector4(self):
        return vector4(self.w, self.x, self.y, self.z)

    def toMatrix3x3(self):
        return qt.as_rotation_matrix(self)

    def toMatrix4x4(self):
        return qt.as_matrix4x4(self)

    def to_axi_angle(self):
        scale = sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        axi = vector(self.x / scale, self.y / scale, self.z / scale)
        angle = acos(self.w)*2.0
        return axi, angle

    def to_euler_angles(self):
        return qt.as_euler_angles(self)

    def to_rotation_vector(self):
        return vector.fromList(qt.as_rotation_vector(self))

    def to_spherical_coords(self):
        return vector2.fromList(qt.as_spherical_coords(self))

    def to_np(self):
        return np.array(self)

    def slerp(self, q, fraction, spin=0, shortestpath=True):
        if fraction == 0.0:
            return quaternion.fromQuaternion(self)
        elif fraction == 1.0:
            return quaternion.fromQuaternion(q)
        d = np.dot(self, q)
        if abs(abs(d) - 1.0) < _EPS:
            return quaternion.fromQuaternion(self)
        if shortestpath and d < 0.0:
            # invert rotation
            d = -d
            q *= -1.0
        angle = acos(d) + spin * np.pi
        if abs(angle) < _EPS:
            return quaternion.fromQuaternion(self)
        isin = 1.0 / sin(angle)
        q0 = self * sin((1.0 - fraction) * angle) * isin
        q1 = q * sin(fraction * angle) * isin
        return quaternion.fromQuaternion(q0 + q1)

    @staticmethod
    def from_axi_angle(axi, angle):
        a = axi.normalized()
        sinAng = sin(angle * 0.5)
        q = quaternion(cos(angle * 0.5), a.x() * sinAng, a.y() * sinAng, a.z() * sinAng)
        return q

    @staticmethod
    def from_two_vector(from_vec, to_vec):
        v = from_vec.cross(to_vec)
        v1_len = from_vec.length()
        v2_len = to_vec.length()

        w = sqrt(v1_len * v1_len * v2_len * v2_len) + from_vec.dot(to_vec)
        q = quaternion(w, v.x(), v.y(), v.z())
        q.normalize()
        return q

    @staticmethod
    def from_euler_angles(alpha_beta_gamma, beta=None, gamma=None):
        return quaternion.fromQuaternion(qt.from_euler_angles(alpha_beta_gamma, beta, gamma))

    @staticmethod
    def from_rotation_vector(rot):
        return quaternion.fromQuaternion(qt.from_rotation_vector(rot))

    @staticmethod
    def from_spherical_coords(theta_phi, phi=None):
        return quaternion.fromQuaternion(qt.from_spherical_coords(theta_phi, phi))

    @staticmethod
    def from_rotation_matrix(rot, nonorthogonal=True):
        return quaternion.fromQuaternion(qt.from_rotation_matrix(rot, nonorthogonal))

    @staticmethod
    def fromQuaternion(q):
        return quaternion(q.w, q.x, q.y, q.z)

    @staticmethod
    def fromList(q):
        return quaternion(q[0], q[1], q[2], q[3])

    @staticmethod
    def fromVector4(vec):
        return quaternion(vec.x(), vec.y(), vec.z(), vec.w())

    @staticmethod
    def from_matrix(matrix):
        q = np.empty((4,), dtype=np.float64)
        M = np.array(matrix.data(), dtype=np.float64, copy=False)[:4, :4]
        t = np.trace(M)
        if t > M[3, 3]:
            q[3] = t
            q[2] = M[1, 0] - M[0, 1]
            q[1] = M[0, 2] - M[2, 0]
            q[0] = M[2, 1] - M[1, 2]
        else:
            i, j, k = 0, 1, 2
            if M[1, 1] > M[0, 0]:
                i, j, k = 1, 2, 0
            if M[2, 2] > M[i, i]:
                i, j, k = 2, 0, 1
            t = M[i, i] - (M[j, j] + M[k, k]) + M[3, 3]
            q[i] = t
            q[j] = M[i, j] + M[j, i]
            q[k] = M[k, i] + M[i, k]
            q[3] = M[k, j] - M[j, k]
        q *= 0.5 / sqrt(t * M[3, 3])
        return quaternion.fromList(q)


if __name__ == '__main__':
    a = vector(1, 0, 1)
    #a.normalize()
    #print(a)
    quat = quaternion.from_axi_angle(vector(0,1,0),90)
    b = vector(0,1,0)

    print(b / 5)