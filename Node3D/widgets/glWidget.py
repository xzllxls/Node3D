from PySide2 import QtCore, QtGui, QtWidgets
from OpenGL.GL import *
import OpenGL.GL.framebufferobjects as glfbo
import numpy as np
from ..vendor.pyqtgraph import functions as fn
from ..vendor.pyqtgraph import debug
from ..vendor.pyqtgraph import opengl as gl
from ..opengl import camera
from ..base.data import matrix4x4, AABB_Hit, vector
ShareWidget = None


def showError(item):
    debug.printExc()
    msg = "Error while drawing item %s." % str(item)
    ver = glGetString(GL_VERSION)
    if ver is not None:
        ver = ver.split()[0]
        if int(ver.split(b'.')[0]) < 2:
            print(
                msg + " The original exception is printed above; however, pyqtgraph requires OpenGL version 2.0 or greater for many of its 3D features and your OpenGL version is %s. Installing updated display drivers may resolve this issue." % ver)
        else:
            print(msg)


def checkOpenGLVersion(msg):
    ver = glGetString(GL_VERSION).split()[0]
    if int(ver.split(b'.')[0]) < 2:
        debug.printExc()
        raise Exception(
            msg + " The original exception is printed above; however, pyqtgraph requires OpenGL version 2.0 or greater for many of its 3D features and your OpenGL version is %s. Installing updated display drivers may resolve this issue." % ver)
    else:
        raise


class GLViewWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        # global ShareWidget
        # if ShareWidget is None:
        #     ShareWidget = QtOpenGL.QGLWidget()
        # super(GLViewWidget, self).__init__(self, parent, ShareWidget)
        super(GLViewWidget, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.opts = {
            'viewport': None,
            'drawGrid': True,
            'drawPoints': False,
            'drawFaces': True,
            'drawEdges': False,
            'bgColor': (0.3, 0.3, 0.3, 1),
        }

        self.items = []
        self.meshItems = []
        self.noRepeatKeys = [QtCore.Qt.Key_Right, QtCore.Qt.Key_Left, QtCore.Qt.Key_Up, QtCore.Qt.Key_Down,
                             QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown]
        self.keysPressed = {}

        self.makeCurrent()
        self.cam = camera()

        self._canShowMenu = True
        self.setup_menus()

        viewportFormat = QtGui.QSurfaceFormat()
        # viewportFormat.setSwapInterval(0)  # disable VSync
        viewportFormat.setSamples(2 ** 8)
        self.setFormat(viewportFormat)

    def addCheckedAction(self, name, optName):
        act = QtWidgets.QAction(name, self)
        act.setCheckable(True)
        act.setChecked(self.opts[optName])
        act.triggered.connect(lambda: self.setOpts(optName, act.isChecked()))
        self.menu.addAction(act)

    def setup_menus(self):
        self.menu = QtWidgets.QMenu(self)
        self.addCheckedAction('Show Grid', 'drawGrid')
        self.addCheckedAction('Points', 'drawPoints')
        self.addCheckedAction('Faces', 'drawFaces')
        self.addCheckedAction('Edges', 'drawEdges')

        act = QtWidgets.QAction('Reset Camera', self)
        act.triggered.connect(self.resetCamera)
        self.menu.addAction(act)

    def setOpts(self, name, state):
        self.opts[name] = state

    def addItem(self, item, MeshItem=False):
        if hasattr(item, 'initializeGL'):
            self.makeCurrent()
            try:
                item.initializeGL()
            except:
                checkOpenGLVersion('Error while adding item %s to GLViewWidget.' % str(item))
        if MeshItem:
            self.meshItems.append(item)
        else:
            self.items.append(item)
        item._setView(self)
        self.update()

    def addMeshItem(self, item):
        self.addItem(item, True)

    def removeItem(self, item, meshItem=False):
        if meshItem:
            self.meshItems.remove(item)
        else:
            self.items.remove(item)
        item._setView(None)
        self.update()

    def removeMeshItem(self, item):
        self.removeItem(item, True)

    def initializeGL(self):
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_DST_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_DEPTH_TEST)
        glLineWidth(1.5)
        self.resizeGL(self.width(), self.height())

    def setBackgroundColor(self, *args, **kwds):
        """
        Set the background color of the widget. Accepts the same arguments as
        pg.mkColor() and pg.glColor().
        """
        self.opts['bgColor'] = fn.glColor(*args, **kwds)
        self.update()

    def getViewport(self):
        vp = self.opts['viewport']
        dpr = self.devicePixelRatio()
        if vp is None:
            return 0, 0, int(self.width() * dpr), int(self.height() * dpr)
        else:
            return tuple([int(x * dpr) for x in vp])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def projectionMatrix(self, region=None):
        if region is None:
            dpr = self.devicePixelRatio()
            region = (0, 0, self.width() * dpr, self.height() * dpr)

        x0, y0, w, h = self.getViewport()
        fov = self.getFov()
        nearClip, farClip = self.cam.getClip()

        r = nearClip * np.tan(fov * 0.5 * np.pi / 180.)
        t = r * h / w

        # Note that X0 and width in these equations must be the values used in viewport
        left = r * ((region[0] - x0) * (2.0 / w) - 1)
        right = r * ((region[0] + region[2] - x0) * (2.0 / w) - 1)
        bottom = t * ((region[1] - y0) * (2.0 / h) - 1)
        top = t * ((region[1] + region[3] - y0) * (2.0 / h) - 1)

        return matrix4x4.create_perspective_projection_from_bounds(left, right, bottom, top, nearClip, farClip)

    def setProjection(self, region=None):
        m = self.projectionMatrix(region).data()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(m)

    def viewMatrix(self):
        return self.cam.getViewMatrix()

    def setModelView(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        m = self.viewMatrix().data()
        glMultMatrixf(m.transpose())

    def pixelSize(self, pos):
        """
        Return the approximate size of a screen pixel at the location pos
        Pos may be a Vector or an (N,3) array of locations
        """
        cam = self.cameraPosition()
        if isinstance(pos, np.ndarray):
            cam = np.array(cam).reshape((1,) * (pos.ndim - 1) + (3,))
            dist = ((pos - cam) ** 2).sum(axis=-1) ** 0.5
        else:
            dist = (pos - cam).length()
        xDist = dist * 2. * np.tan(0.5 * self.getFov() * np.pi / 180.)
        return xDist / self.width()

    def keyPressEvent(self, ev):
        if ev.key() in self.noRepeatKeys:
            ev.accept()
            if ev.isAutoRepeat():
                return
            self.keysPressed[ev.key()] = 1
            self.evalKeyState()

    def keyReleaseEvent(self, ev):
        if ev.key() in self.noRepeatKeys:
            ev.accept()
            if ev.isAutoRepeat():
                return
            try:
                del self.keysPressed[ev.key()]
            except:
                self.keysPressed = {}
            self.evalKeyState()

    def evalKeyState(self):
        pass

    def readQImage(self):
        """
        Read the current buffer pixels out as a QImage.
        """
        w = self.width()
        h = self.height()
        self.repaint()
        pixels = np.empty((h, w, 4), dtype=np.ubyte)
        pixels[:] = 128
        pixels[..., 0] = 50
        pixels[..., 3] = 255

        glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, pixels)

        # swap B,R channels for Qt
        tmp = pixels[..., 0].copy()
        pixels[..., 0] = pixels[..., 2]
        pixels[..., 2] = tmp
        pixels = pixels[::-1]  # flip vertical

        img = fn.makeQImage(pixels, transpose=False)
        return img

    def renderToArray(self, size, format=GL_BGRA, type=GL_UNSIGNED_BYTE, textureSize=1024, padding=256):
        w, h = map(int, size)

        self.makeCurrent()
        tex = None
        fb = None
        try:
            output = np.empty((w, h, 4), dtype=np.ubyte)
            fb = glfbo.glGenFramebuffers(1)
            glfbo.glBindFramebuffer(glfbo.GL_FRAMEBUFFER, fb)

            glEnable(GL_TEXTURE_2D)
            tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex)
            texwidth = textureSize
            data = np.zeros((texwidth, texwidth, 4), dtype=np.ubyte)

            ## Test texture dimensions first
            glTexImage2D(GL_PROXY_TEXTURE_2D, 0, GL_RGBA, texwidth, texwidth, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D, 0, GL_TEXTURE_WIDTH) == 0:
                raise Exception("OpenGL failed to create 2D texture ({}x{}); too large for this hardware.".
                                format(texwidth, texwidth))
            ## create teture
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texwidth, texwidth, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                         data.transpose((1, 0, 2)))

            self.opts['viewport'] = (0, 0, w, h)  # viewport is the complete image; this ensures that paintGL(region=...)
            # is interpreted correctly.
            p2 = 2 * padding
            for x in range(-padding, w - padding, texwidth - p2):
                for y in range(-padding, h - padding, texwidth - p2):
                    x2 = min(x + texwidth, w + padding)
                    y2 = min(y + texwidth, h + padding)
                    w2 = x2 - x
                    h2 = y2 - y

                    ## render to texture
                    glfbo.glFramebufferTexture2D(glfbo.GL_FRAMEBUFFER, glfbo.GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex,
                                                 0)

                    self.paintGL(region=(x, h - y - h2, w2, h2), viewport=(0, 0, w2, h2))  # only render sub-region
                    glBindTexture(GL_TEXTURE_2D, tex)  # fixes issue #366

                    ## read texture back to array
                    data = glGetTexImage(GL_TEXTURE_2D, 0, format, type)
                    data = np.fromstring(data, dtype=np.ubyte).reshape(texwidth, texwidth, 4).transpose(1, 0, 2)[:,
                           ::-1]
                    output[x + padding:x2 - padding, y + padding:y2 - padding] = data[padding:w2 - padding,
                                                                                 -(h2 - padding):-padding]

        finally:
            self.opts['viewport'] = None
            glfbo.glBindFramebuffer(glfbo.GL_FRAMEBUFFER, 0)
            glBindTexture(GL_TEXTURE_2D, 0)
            if tex is not None:
                glDeleteTextures([tex])
            if fb is not None:
                glfbo.glDeleteFramebuffers([fb])

        return output

    def paintGL(self, region=None, viewport=None):
        """
        viewport specifies the arguments to glViewport. If None, then we use self.opts['viewport']
        region specifies the sub-region of self.opts['viewport'] that should be rendered.
        Note that we may use viewport != self.opts['viewport'] when exporting.
        """
        if viewport is None:
            glViewport(*self.getViewport())
        else:
            glViewport(*viewport)
        self.setProjection(region=region)
        self.setModelView()
        bgColor = self.opts['bgColor']
        glClearColor(*bgColor)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        self.drawItemTree()

    def drawItemTree(self, item=None):
        if item is None:
            items = self.meshItems + self.items
            # items.sort(key=lambda a: a.depthValue())
            for i in items:
                if not i.visible():
                    continue
                glMatrixMode(GL_MODELVIEW)
                glPushMatrix()
                try:
                    if isinstance(i, gl.GLGraphicsItem.GLGraphicsItem):
                        tr = i.transform()
                        a = np.array(tr.copyDataTo()).reshape((4, 4))
                        glMultMatrixf(a.transpose())
                    self.drawItemTree(i)
                finally:
                    glMatrixMode(GL_MODELVIEW)
                    glPopMatrix()
            return

        # item is not None
        try:
            glPushAttrib(GL_ALL_ATTRIB_BITS)
            item.paint()
        except:
            showError(item)
        finally:
            glPopAttrib()

    def itemsAt(self, x, y):
        # get ray form mouse pos
        ray_ndc = vector(2.0*x/self.width() - 1.0, 2.0*y/self.height() - 1.0, -1)
        ray_eye = self.projectionMatrix().inverted().transformVector(ray_ndc)
        ray_eye.setZ(-1)
        ray_world = self.viewMatrix().inverted().transformVector(ray_eye, fill=0.0).normalized()

        # calculate hit
        meshes = [m for m in self.meshItems if AABB_Hit(m.bbox_min, m.bbox_max, self.cam.getPos(), ray_world)]

        if meshes:
            return meshes[0]
        else:
            return None

    def mousePressEvent(self, ev):
        self.mousePos = ev.pos()
        if ev.button() == QtCore.Qt.LeftButton:
            self.cam.setTarget()
            [item.setSelected(False) for item in self.meshItems]
            y = self.height() - ev.pos().y()
            item = self.itemsAt(x=ev.pos().x(), y=y)
            if item:
                item.setSelected(True)
                self.cam.setTarget(item.bbox_center)
            else:
                self.cam.setTarget()
        elif ev.buttons() == QtCore.Qt.RightButton:
            self._canShowMenu = True
            self.cam.setTarget()

    def mouseMoveEvent(self, ev):
        diff = ev.pos() - self.mousePos
        x = diff.x()
        y = diff.y()
        self.mousePos = ev.pos()

        if ev.buttons() == QtCore.Qt.LeftButton:
            if (ev.modifiers() & QtCore.Qt.ControlModifier):
                self.cam.pan(x, y)
            else:
                self.cam.rotate(x, y)
        elif ev.buttons() == QtCore.Qt.MidButton:
            self.cam.pan(x, y)
        elif ev.buttons() == QtCore.Qt.RightButton:
            delta = (x + y) * 3
            self.cam.zoom(delta)
            self._canShowMenu = False

        self.update()

    def wheelEvent(self, ev):
        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
        if (ev.modifiers() & QtCore.Qt.ControlModifier):
            self.cam.fov *= 0.999 ** delta
        else:
            self.cam.zoom(delta * 3)
        self.update()

    def contextMenuEvent(self, event):
        if not self._canShowMenu:
            return
        self.menu.exec_(QtGui.QCursor.pos())

    def cameraPosition(self):
        return self.cam.getPos()

    def getFov(self):
        return self.cam.fov

    def resetCamera(self):
        self.cam.reset()
        self.update
        self.paintGL()

    def setCameraPosition(self, pos):
        self.cam.reset(pos)

    def clear_meshItems(self):
        self.meshItems.clear()