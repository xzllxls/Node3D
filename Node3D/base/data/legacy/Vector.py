from Qt.QtGui import QVector3D, QVector2D, QVector4D
import numpy as np


class vector(QVector3D):
    def __init__(self, *args):
        if len(args) == 1:
            super(vector, self).__init__(*args[0])
        elif len(args) == 3:
            super(vector, self).__init__(*args)
        else:
            super(vector, self).__init__()

    def __len__(self):
        return 3

    def __getitem__(self, i):
        if i == 0:
            return self.x()
        elif i == 1:
            return self.y()
        elif i == 2:
            return self.z()
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __setitem__(self, i, x):
        if i == 0:
            self.setX(x)
        elif i == 1:
            self.setY(x)
        elif i == 2:
            self.setZ(x)
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __iter__(self):
        yield self.x()
        yield self.y()
        yield self.z()

    def __abs__(self):
        return vector(abs(self.x()), abs(self.y()), abs(self.z()))

    def __add__(self, vec):
        if type(vec) in [float, int]:
            return vector(self.x()+vec, self.y()+vec, self.z()+vec)
        return vector.fromVector(super(vector, self).__add__(vec))

    def __sub__(self, vec):
        if type(vec) in [float, int]:
            return vector(self.x()-vec, self.y()-vec, self.z()-vec)
        return vector.fromVector(super(vector, self).__sub__(vec))

    def __mul__(self, vec):
        return vector.fromVector(super(vector, self).__mul__(vec))

    def __truediv__(self, vec):
        return vector.fromVector(super(vector, self).__truediv__(vec))

    def cross(self, vec):
        return vector.fromVector(QVector3D.crossProduct(self, vec))

    def dot(self, vec):
        return QVector3D.dotProduct(self, vec)

    def normalized(self):
        return vector.fromVector(super(vector, self).normalized())

    def angle(self, vec):
        n1 = self.length()
        n2 = vec.length()
        if n1 == 0. or n2 == 0.:
            return None
        ang = np.arccos(np.clip(QVector3D.dotProduct(self, vec) / (n1 * n2), -1.0, 1.0))
        return ang * 180. / np.pi

    def normal(self, vec1, vec2=None):
        if vec2 is None:
            return vector.fromVector(QVector3D.normal(self, vec1))
        else:
            return vector.fromVector(QVector3D.normal(self, vec1, vec2))

    def toVector2(self):
        return vector2(self.x(), self.y())

    def toVector4(self):
        return vector4(self.x(), self.y(), self.z(), 0)

    def to_np(self):
        return np.array(self)

    @staticmethod
    def fromList(data):
        return vector(data[0], data[1], data[2])

    @staticmethod
    def fromVector(vec):
        return vector(vec.x(), vec.y(), vec.z())


class vector2(QVector2D):
    def __init__(self, *args):
        if len(args) == 1:
            super(vector2, self).__init__(*args[0])
        elif len(args) == 2:
            super(vector2, self).__init__(*args)
        else:
            super(vector2, self).__init__()

    def __len__(self):
        return 2

    def __getitem__(self, i):
        if i == 0:
            return self.x()
        elif i == 1:
            return self.y()
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __setitem__(self, i, x):
        if i == 0:
            self.setX(x)
        elif i == 1:
            self.setY(x)
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __iter__(self):
        yield self.x()
        yield self.y()

    def __abs__(self):
        return vector2(abs(self.x()), abs(self.y()))

    def __add__(self, vec):
        if type(vec) in [float, int]:
            return vector2(self.x()+vec, self.y()+vec)
        return vector2.fromVector(super(vector2, self).__add__(vec))

    def __sub__(self, vec):
        if type(vec) in [float, int]:
            return vector2(self.x()-vec, self.y()-vec)
        return vector2.fromVector(super(vector2, self).__sub__(vec))

    def __mul__(self, vec):
        return vector2.fromVector(super(vector2, self).__mul__(vec))

    def __truediv__(self, vec):
        return vector2.fromVector(super(vector2, self).__truediv__(vec))

    def dot(self, vec):
        return QVector2D.dotProduct(self, vec)

    def normalized(self):
        return vector2.fromVector(super(vector2, self).normalized())

    def angle(self, vec):
        n1 = self.length()
        n2 = vec.length()
        if n1 == 0. or n2 == 0.:
            return None
        ang = np.arccos(np.clip(QVector3D.dotProduct(self.toVector3(), vec.toVector3()) / (n1 * n2), -1.0, 1.0))
        return ang * 180. / np.pi

    def toVector3(self):
        return vector(self.x(), self.y(), 0)

    def toVector4(self):
        return vector4(self.x(), self.y(), 0, 0)

    def to_np(self):
        return np.array(self)

    @staticmethod
    def fromList(data):
        return vector2(data[0], data[1])

    @staticmethod
    def fromVector(vec):
        return vector2(vec.x(), vec.y())


class vector4(QVector4D):
    def __init__(self, *args):
        if len(args) == 1:
            super(vector4, self).__init__(*args[0])
        elif len(args) == 4:
            super(vector4, self).__init__(*args)
        else:
            super(vector4, self).__init__()

    def __len__(self):
        return 4

    def __getitem__(self, i):
        if i == 0:
            return self.x()
        elif i == 1:
            return self.y()
        elif i == 2:
            return self.z()
        elif i == 3:
            return self.w()
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __setitem__(self, i, x):
        if i == 0:
            self.setX(x)
        elif i == 1:
            self.setY(x)
        elif i == 2:
            self.setZ(x)
        elif i == 3:
            self.setW(x)
        else:
            raise IndexError("Point has no index %s" % str(i))

    def __iter__(self):
        yield self.x()
        yield self.y()
        yield self.z()
        yield self.w()

    def __abs__(self):
        return vector4(abs(self.x()), abs(self.y()),abs(self.z()), abs(self.w()))

    def __add__(self, vec):
        if type(vec) in [float, int]:
            return vector4(self.x()+vec, self.y()+vec, self.z()+vec, self.w()+vec)
        return vector4.fromVector(super(vector4, self).__add__(vec))

    def __sub__(self, vec):
        if type(vec) in [float, int]:
            return vector4(self.x()-vec, self.y()-vec, self.z()-vec, self.w()-vec)
        return vector4.fromVector(super(vector4, self).__sub__(vec))

    def __mul__(self, vec):
        return vector4.fromVector(super(vector4, self).__mul__(vec))

    def __truediv__(self, vec):
        return vector4.fromVector(super(vector4, self).__truediv__(vec))

    def dot(self, vec):
        return QVector4D.dotProduct(self, vec)

    def normalized(self):
        return vector4.fromVector(super(vector4, self).normalized())

    def toVector3(self):
        return vector(self.x(), self.y(), self.z())

    def toVector2(self):
        return vector4(self.x(), self.y())

    def to_np(self):
        return np.array(self)

    @staticmethod
    def fromList(data):
        return vector4(data[0], data[1], data[2], data[3])

    @staticmethod
    def fromVector(vec):
        return vector4(vec.x(), vec.y(), vec.z(), vec.w())


if __name__ == '__main__':
    a = vector(1, -1, 0)
    b = vector(0, 1, 0)
    a[0] = 10
    print(np.asarray(a))