from ..base.data import vector, quaternion, matrix4x4

CAMERA_TRANSLATION_FACTOR = 0.01


class camera(object):
    def __init__(self):
        self.pos = vector(0, 0, 0)
        self.forwardPos = vector(0, 0, 1)
        self.upPos = vector(0, 1, 0)
        self.target = vector(0, 0, 0)
        self.zero = vector(0, 0, 0)
        self.fov = 70.0
        self.reset()

    def getFarClip(self):
        return self.getDistance()*0.001

    def getNearClip(self):
        return self.getDistance()*1000

    def getClip(self):
        d = self.getDistance()
        return d*0.001, d*1000

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
        up = self.getUp()
        side = self.getSide()
        target = self.getTarget()

        # axi1 = abs(dx) * up
        # axi2 = abs(dy) * side
        # axi = axi1 + axi2
        # axi.normalize()

        axi = up if abs(dx) > abs(dy) else side
        ang = -(dx + dy) * 0.5

        self.move(-target)

        quat = quaternion.from_axi_angle(axi, ang*0.01)
        self.rot(quat)
        self.move(target)

        fw = self.getForward()
        sd = fw.cross(self.getUp())
        sd.setY(0)
        up = sd.cross(fw).normalized()
        self.upPos = self.pos + up

    def zoom(self, delta):
        dis = self.getDistance()
        if dis == 0.0:
            dis = 0.01
        delta *= dis * CAMERA_TRANSLATION_FACTOR
        self.move((self.target-self.pos).normalized() * delta * 0.05)

    def move(self, delta):
        self.pos += delta
        self.forwardPos += delta
        self.upPos += delta

    def rot(self, quat):
        self.pos = quat.rotateVector(self.pos)
        self.forwardPos = quat.rotateVector(self.forwardPos)
        self.upPos = quat.rotateVector(self.upPos)

    def getViewMatrix(self):
        return matrix4x4.from_lookAt(self.pos, self.forwardPos, self.getUp())

    def getTarget(self):
        return self.target

    def setTarget(self, target=None):
        if target is None:
            dis = self.pos.distanceToPoint(self.zero)
            self.target = self.pos + self.getForward() * dis
        else:
            self.target = vector.fromList(target)

    def getSide(self):
        return self.getForward().cross(self.getUp())

    def getForward(self):
        return (self.forwardPos - self.pos).normalized()

    def getUp(self):
        return (self.upPos - self.pos).normalized()

    def reset(self, pos=vector(-10, 10, 10)):
        self.pos = pos
        dir = (self.zero - self.pos).normalized()
        self.forwardPos = self.pos + dir
        up = vector(0, 1, 0)
        side = dir.cross(up)
        self.upPos = self.pos + side.cross(dir)
        self.target = vector(0, 0, 0)

    def getPos(self):
        return [self.pos.x(), self.pos.y(), self.pos.z()]

    def getDistance(self):
        return self.pos.distanceToPoint(self.target)
