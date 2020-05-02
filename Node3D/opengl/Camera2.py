from ..base.data import vector3, matrix44, Vector3, quaternion
import numpy as np
CAMERA_TRANSLATION_FACTOR = 0.01


class camera(object):
    def __init__(self):
        self.transform = matrix44.create_identity(np.float64)
        self._rotTheta = 0
        self._rotPhi = 15
        self._rotPsi = 0
        self.dist = 30

        self.zero = Vector3([0, 0, 0], np.float64)
        self.pos = Vector3([0, 10, 10], np.float64)
        self._center = Vector3([0, 0, 0], np.float64)

        self.fov = 70.0
        self._pushToCameraTransform()

    def getFarClip(self):
        return 1000 # self.dist * 0.001

    def getNearClip(self):
        return 0.01 #self.dist * 1000

    def getClip(self):
        d = 1
        return d * 0.001, d * 10000

    def rotate(self, dx, dy):
        self._rotTheta += dx*0.25
        self._rotPhi += dy*0.25
        self._pushToCameraTransform()

    def zoom(self, delta):
        delta = -0.001 * delta + 1
        if delta > 1 and self.dist < 2:
            self.dist += min(10.0 / 25.0, delta)
        else:
            self.dist *= delta
        if self.dist < 0.01:
            self.dist = 0.01

        self._pushToCameraTransform()

    def pan(self, dx, dy):
        q = quaternion.create_from_matrix(self.transform)
        up = quaternion.apply_to_vector(q, Vector3([0, 1, 0], np.float64))
        right = quaternion.apply_to_vector(q, Vector3([1, 0, 0], np.float64))
        self._center += -dx * right * 0.1 + dy * up * 0.1
        self._pushToCameraTransform()

    def getViewMatrix(self):
        return self.transform

    def getTarget(self):
        return self.target

    def setTarget(self, target=None):
        return
        if target is None:
            self.dist = vector3.length(self.pos - self.zero)
            self._center = self.pos
        else:
            self._center = Vector3(target, np.float64)
            self.dist = self.pos.distanceToPoint(self._center)

    def reset(self, pos=Vector3([-10, 10, 10], np.float64)):
        pass
        # self.pos = pos
        # dir = vector3.normalize(self.zero - self.pos)
        # self.forwardPos = self.pos + dir
        # up = Vector3([0, 1, 0], np.float64)
        # side = vector3.cross(dir, up)
        # self.upPos = self.pos + vector3.cross(side, dir)
        # self.target = Vector3([0, 0, 0], np.float64)

    def getPos(self):
        return self.pos

    @staticmethod
    def RotMatrix(vec, angle):
        return matrix44.create_from_axis_rotation(vec, np.deg2rad(angle))

    def _pushToCameraTransform(self):
        # self._center = vector(0,0,0)
        self.transform = (
            matrix44.create_from_translation(Vector3([0, 0, -self.dist], np.float64)) *
            self.RotMatrix(Vector3([0, 0, ]), self._rotPsi) *
            self.RotMatrix(Vector3([1, 0, 0]), self._rotPhi) *
            self.RotMatrix(Vector3([0, 1, 0]), self._rotTheta) *
            matrix44.create_from_translation(self._center))