import numpy as np

from OpenGL.GL import *
from ..GLGraphicsItem import GLGraphicsItem
from ... import QtGui
from ... import functions as fn

__all__ = ['GLGridItem']


def _draw_axis():
    glColor4f(1, 0.35, 0.35, 0.8)
    glVertex3f(10000, 0, 0)
    glVertex3f(-10000, 0, 0)

    glColor4f(0.35, 1, 0.35, 0.8)
    glVertex3f(0, 10000, 0)
    glVertex3f(0, -10000, 0)

    glColor4f(0.35, 0.35, 1, 0.8)
    glVertex3f(0, 0, 10000)
    glVertex3f(0, 0, -10000)


class GLGridItem(GLGraphicsItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem>`
    
    Displays a wire-frame grid. 
    """

    def __init__(self, size=None, color=(1, 1, 1, 0.1), antialias=True, glOptions='translucent'):
        GLGraphicsItem.__init__(self)
        self.setGLOptions(glOptions)
        self.antialias = antialias
        if size is None:
            size = QtGui.QVector3D(20, 20, 20)
        self.setSize(size=size)
        self.setSpacing(1, 1, 1)
        self._color = (1, 1, 1, 0.5)
        self.setColor(color)
        self.draw_axis = False

    def setSize(self, x=None, y=None, z=None, size=None):
        """
        Set the size of the axes (in its local coordinate system; this does not affect the transform)
        Arguments can be x,y,z or size=QVector3D().
        """
        if size is not None:
            x = size.x()
            y = size.y()
            z = size.z()
        self.__size = [x, y, z]
        self.update()

    def size(self):
        return self.__size[:]

    def setSpacing(self, x=None, y=None, z=None, spacing=None):
        """
        Set the spacing between grid lines.
        Arguments can be x,y,z or spacing=QVector3D().
        """
        if spacing is not None:
            x = spacing.x()
            y = spacing.y()
            z = spacing.z()
        self.__spacing = [x, y, z]
        self.update()

    def spacing(self):
        return self.__spacing[:]

    def setColor(self, color):
        self._color = color
        self.update()

    def color(self):
        return self.__color

    def paint(self):
        if not self.view().opts['drawGrid']:
            return

        glBegin(GL_LINES)

        if self.draw_axis:
            _draw_axis()

        x, y, z = self.size()
        xs, ys, zs = self.spacing()

        xvals = np.arange(-x / 2., x / 2. + xs * 0.001, xs)
        yvals = np.arange(-y / 2., y / 2. + ys * 0.001, ys)

        glColor4f(*self._color)
        for x in xvals:
            if x == 0:
                continue
            glVertex3f(x, 0, yvals[0])
            glVertex3f(x, 0, yvals[-1])
        for y in yvals:
            if y == 0:
                continue
            glVertex3f(xvals[0], 0, y)
            glVertex3f(xvals[-1], 0, y)
        glEnd()
