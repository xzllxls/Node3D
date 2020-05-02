from ..base.data import vector3, Vector3, quaternion, Quaternion, matrix44
import numpy as np
CAMERA_TRANSLATION_FACTOR = 0.01


class camera(object):
    def __init__(self):
        self.pos = Vector3([0, 0, 0], dtype=np.float64)
        self.forwardPos = Vector3([0, 0, 1], dtype=np.float64)
        self.upPos = Vector3([0, 1, 0], dtype=np.float64)
        self.target = Vector3([0, 0, 0], dtype=np.float64)
        self.zero = Vector3([0, 0, 0], dtype=np.float64)
        self.fov = 70.0
        self.reset()

    def getFarClip(self):
        return self.getDistance() * 1000

    def getNearClip(self):
        return self.getDistance() * 0.001

    def getClip(self):
        d = self.getDistance()
        return d * 0.001, d * 1000

    def pan(self, dx, dy):
        dis = self.getDistance()
        if dis == 0.0:
            dis = 0.01
        dx *= dis * CAMERA_TRANSLATION_FACTOR
        dy *= dis * CAMERA_TRANSLATION_FACTOR
        side = self.getSide()
        up = self.getUp()
        self.move((side * -dx + up * dy) * 0.1)

    def rotate(self, dx, dy):
        up = Vector3([0, 1, 0], dtype=np.float64)
        side = self.getSide()
        target = self.getTarget()

        # axi1 = abs(dx) * up
        # axi2 = abs(dy) * side
        # axi = axi1 + axi2
        # axi.normalize()

        axi = up if abs(dx) > abs(dy) else side
        ang = -(dx + dy) * 0.5

        self.move(-target)

        quat = Quaternion.from_axis_rotation(axi, ang * 0.01)
        self.rot(quat)
        self.move(target)

    def zoom(self, delta):
        dis = self.getDistance()
        if dis == 0.0:
            dis = 0.01
        delta *= dis * CAMERA_TRANSLATION_FACTOR
        self.move(vector3.normalize(self.target - self.pos) * delta * 0.05)

    def move(self, delta):
        self.pos += delta
        self.forwardPos += delta
        self.upPos += delta

    def rot(self, quat):
        self.pos = quaternion.apply_to_vector(quat, self.pos)
        self.forwardPos = quaternion.apply_to_vector(quat, self.forwardPos)
        self.upPos = quaternion.apply_to_vector(quat, self.upPos)

    def getViewMatrix(self):
        return matrix44.create_look_at(self.pos, self.forwardPos, self.getUp())

    def getTarget(self):
        return self.target

    def setTarget(self, target=None):
        if target is None:
            dis = vector3.length(self.pos - self.zero)
            self.target = self.pos + self.getForward() * dis
        else:
            self.target = Vector3(target)

    def getSide(self):
        return vector3.cross(self.getForward(), self.getUp())

    def getForward(self):
        return vector3.normalize(self.forwardPos - self.pos)

    def getUp(self):
        return vector3.normalize(self.upPos - self.pos)

    def reset(self, pos=Vector3([-10, 10, 10], dtype=np.float64)):
        self.pos = pos
        dir = vector3.normalize(self.zero - self.pos)
        self.forwardPos = self.pos + dir
        up = Vector3([0, 1, 0], dtype=np.float64)
        side = vector3.cross(dir, up)
        self.upPos = self.pos + vector3.cross(side, dir)
        self.target = Vector3([0, 0, 0], dtype=np.float64)

    def getPos(self):
        return self.pos

    def getDistance(self):
        return vector3.length(self.pos - self.target)
