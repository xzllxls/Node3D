from PySide2 import QtGui, QtCore, QtWidgets
from PIL import Image, ImageQt
from ctypes import byref, c_float, c_uint
from typing import Tuple, Any
from plotoptix._load_lib import PLATFORM
from plotoptix.npoptix import NpOptiX

from Node3D.opengl.Camera import camera
import sys
import numpy as np


def set_mesh(self, name: str, pos: Any, pidx=None, normals=None, nidx=None,
             c: Any = np.ascontiguousarray([0.94, 0.94, 0.94], dtype=np.float32),
             mat: str = "diffuse", make_normals: bool = False) -> None:
    pidx_ptr = pidx.ctypes.data
    if pos.dtype != np.float32: pos = np.ascontiguousarray(pos, dtype=np.float32)
    if not pos.flags['C_CONTIGUOUS']: pos = np.ascontiguousarray(pos, dtype=np.float32)
    pos_ptr = pos.ctypes.data

    if normals.dtype != np.float32: normals = np.ascontiguousarray(normals, dtype=np.float32)
    if not normals.flags['C_CONTIGUOUS']: normals = np.ascontiguousarray(normals, dtype=np.float32)
    normals_ptr = normals.ctypes.data

    if type(c) is float:
        t = c
        c = pos.copy()
        c[...] = [t, t, t]
    elif type(c) is list:
        t = c
        c = pos.copy()
        c[...] = t
    if c.dtype != np.float32: c = np.ascontiguousarray(c, dtype=np.float32)
    if not c.flags['C_CONTIGUOUS']: c = np.ascontiguousarray(c, dtype=np.float32)
    col_ptr = c.ctypes.data

    if name in self.geometry_handles:
        msg = "Geometry %s already exists, use update_mesh() instead." % name
        self._logger.error(msg)
        if self._raise_on_error: raise ValueError(msg)
        return

    try:
        self._padlock.acquire()
        n = pos.shape[0]
        s = self._optix.setup_mesh(name, mat, n, pidx.shape[0], n, pos_ptr, col_ptr, pidx_ptr, normals_ptr, pidx_ptr)

        self.geometry_handles[name] = s
        self.geometry_names[s] = name
        self.geometry_sizes[name] = self._optix.get_geometry_size(name)

    except Exception as e:
        self._logger.error(str(e))
        if self._raise_on_error: raise
    finally:
        self._padlock.release()


NpOptiX.set_mesh = set_mesh


class OptixWindow(QtWidgets.QWidget):
    camera_changed = QtCore.Signal()
    closed = QtCore.Signal()
    resized = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.opts = {
            'viewport': None,
            'drawGrid': True,
            'drawPoints': False,
            'drawFaces': True,
            'drawEdges': False
        }

        self.cam = camera()
        self._canShowMenu = True
        self.setup_menus()
        self.mousePos = None
        self.pixel_map = None

    def addCheckedAction(self, name, optName):
        act = QtWidgets.QAction(name, self)
        act.setCheckable(True)
        act.setChecked(self.opts[optName])
        act.triggered.connect(lambda: self.setOpts(optName, act.isChecked()))
        self.menu.addAction(act)

    def setup_menus(self):
        self.menu = QtWidgets.QMenu(self)
        # self.addCheckedAction('Show Grid', 'drawGrid')
        # self.addCheckedAction('Points', 'drawPoints')
        # self.addCheckedAction('Faces', 'drawFaces')
        # self.addCheckedAction('Edges', 'drawEdges')

        act = QtWidgets.QAction('Reset Camera', self)
        act.triggered.connect(self.resetCamera)
        self.menu.addAction(act)

        act = QtWidgets.QAction('Start', self)
        act.triggered.connect(self.start)
        self.menu.addAction(act)

        act = QtWidgets.QAction('Stop', self)
        act.triggered.connect(self.stop)
        self.menu.addAction(act)

        act = QtWidgets.QAction('Pause', self)
        act.triggered.connect(self.pause)
        self.menu.addAction(act)

        act = QtWidgets.QAction('Resume', self)
        act.triggered.connect(self.resume)
        self.menu.addAction(act)

        act = QtWidgets.QAction('Refresh', self)
        act.triggered.connect(self.refresh)
        self.menu.addAction(act)

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def refresh(self):
        pass

    def setOpts(self, name, state):
        pass

    def keyPressEvent(self, ev):
        pass

    def keyReleaseEvent(self, ev):
        pass

    def mousePressEvent(self, ev):
        self.mousePos = ev.pos()
        if ev.button() == QtCore.Qt.LeftButton:
            self.cam.setTarget()
            # y = self.height() - ev.pos().y()
            # item = self.itemsAt(x=ev.pos().x(), y=y)

        elif ev.buttons() == QtCore.Qt.RightButton:
            self._canShowMenu = True
            self.cam.setTarget()

    def mouseMoveEvent(self, ev):
        diff = ev.pos() - self.mousePos
        x = diff.x()
        y = diff.y()
        self.mousePos = ev.pos()

        if ev.buttons() == QtCore.Qt.LeftButton:
            if ev.modifiers() & QtCore.Qt.ControlModifier:
                self.cam.pan(x, y)
            else:
                self.cam.rotate(x, y)
        elif ev.buttons() == QtCore.Qt.MidButton:
            self.cam.pan(x, y)
        elif ev.buttons() == QtCore.Qt.RightButton:
            delta = (x + y) * 3
            self.cam.zoom(delta)
            self._canShowMenu = False
        else:
            return

        self.camera_changed.emit()

    def wheelEvent(self, ev):
        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
        if ev.modifiers() & QtCore.Qt.ControlModifier:
            self.cam.fov *= 0.999 ** delta
        else:
            self.cam.zoom(delta * 3)
        self.camera_changed.emit()

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
        self.camera_changed.emit()

    def setCameraPosition(self, pos):
        self.cam.reset(pos)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

    def set_map(self, img_array):
        height, width = img_array.shape
        bytesPerLine, _ = img_array.strides
        image = QtGui.QImage(
            img_array.data.tobytes(),
            width,
            height,
            bytesPerLine,
            QtGui.QImage.Format_Indexed8,
        )
        # image.setColorTable(GRAY_COLORTABLE)
        self.pixel_map = QtGui.QPixmap.fromImage(image.copy())
        self.update()

    def set_map_pil(self, img):
        self.pixel_map = QtGui.QPixmap.fromImage(ImageQt.ImageQt(img))
        self.update()

    def paintEvent(self, event):
        if self.pixel_map is None:
            return
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), self.pixel_map)


class QtOptiX(OptixWindow):
    def __init__(self):
        super().__init__()

        self.optix = NpOptiX(on_rt_accum_done=self.on_render_finished,
                             on_launch_finished=self.update_content)
        self.inited = False

        # save initial values to set size of Qt window on startup
        if PLATFORM == "Windows":
            dpi_scale = self.optix._optix.get_display_scaling()
            self.optix._logger.info("DPI scaling: %d", dpi_scale)
            if dpi_scale != 1:
                self.optix._logger.warn("DPI setting may cause blurred raytracing output, see this answer")
                self.optix._logger.warn("for the solution https://stackoverflow.com/a/52599951/10037996:")
                self.optix._logger.warn("set python.exe and pythonw.exe files Properties -> Compatibility")
                self.optix._logger.warn("-> Change high DPI settings -> check Override high DPI scaling")
                self.optix._logger.warn("behaviour, select Application in the drop-down menu.")

    def show(self) -> None:
        if not self.optix._is_started:
            self.optix.start()
        super().show()
        self._run_event_loop()

    def start(self):
        if not self.optix._is_started:
            self.optix.start()
        self._run_event_loop()

    def _run_event_loop(self):
        if self.inited:
            return

        self.optix.resize(self.width(), self.height())

        self.optix._fixed_size = None
        self.optix._image_scale = 1.0
        self.optix._image_at = (0, 0)

        self.closed.connect(lambda: self.optix.close())
        self.resized.connect(lambda: self.on_resized())
        self.camera_changed.connect(lambda: self.update_cam())

        self.optix.setup_camera("camera")
        self.update_cam()

        with self.optix._padlock:
            pil_img = Image.fromarray(self.optix._img_rgba, mode="RGBA")
            self.set_map_pil(pil_img)

        self.optix._is_started = True
        self.optix._update_req = False
        self.inited = True

    def update_cam(self):
        cam = self.cam
        self.optix.update_camera("camera", cam.pos, cam.forwardPos, cam.getUp(), fov=cam.fov)
        self.internal_image_update()

    def get_image_xy(self, wnd_x, wnd_y):
        if self.optix._fixed_size is None:
            return wnd_x, wnd_y
        else:
            x = int((wnd_x - self._image_at[0]) / self._image_scale)
            y = int((wnd_y - self._image_at[1]) / self._image_scale)
            return x, y

    def get_hit_at(self, x, y):
        c_x = c_float()
        c_y = c_float()
        c_z = c_float()
        c_d = c_float()
        if self.optix._optix.get_hit_at(x, y, byref(c_x), byref(c_y), byref(c_z), byref(c_d)):
            return c_x.value, c_y.value, c_z.value, c_d.value
        else:
            return 0, 0, 0, 0

    def get_object_at(self, x, y):
        c_handle = c_uint()
        c_index = c_uint()
        if self.optix._optix.get_object_at(x, y, byref(c_handle), byref(c_index)):
            handle = c_handle.value
            index = c_index.value
            return handle, index
        else:
            return None, None

    def get_rt_size(self) -> Tuple[int, int]:
        return self.optix._fixed_size

    def set_rt_size(self, size: Tuple[int, int]) -> None:
        assert self.optix._is_started, "Raytracing thread not running."

        if self.optix._fixed_size == size: return

        self.optix._fixed_size = size
        with self.optix._padlock:
            if self.optix._fixed_size is None:
                w, h = self.width(), self.height()
            else:
                w, h = self.optix._fixed_size
            self.optix.resize(width=w, height=h)

    def on_resized(self):
        self.optix.resize(self.width(), self.height())
        self.update_cam()

    def internal_image_update(self):
        pil_img = Image.fromarray(self.optix._img_rgba, mode="RGBA")

        self._image_scale = 1.0
        if self.optix._fixed_size is not None:
            wc, hc = self.width(), self.height()
            if self.optix._width / wc > self.optix._height / hc:
                self._image_scale = wc / self._width
                hnew = int(self.optix._height * self._image_scale)
                pil_img = pil_img.resize((wc, hnew), Image.ANTIALIAS)
            else:
                self._image_scale = hc / self.optix._height
                wnew = int(self.optix._width * self._image_scale)
                pil_img = pil_img.resize((wnew, hc), Image.ANTIALIAS)

        # update image on canvas
        self.set_map_pil(pil_img)
        # no redraws until the next launch
        self.optix._update_req = False

    def update_content(self, *args):
        assert self.optix._is_started, "Raytracing thread not running."
        if self.optix._is_started:
            self.optix._update_req = True
            # self._statusBar.setText("FPS: %.3f" % self.optix._optix.get_fps())
            with self.optix._padlock:
                self.internal_image_update()

    def on_render_finished(self, result):
        print('finished')

    def pasue(self):
        self.optix.pause_compute()

    def resume(self):
        self.optix.resume_compute()

    def stop(self):
        self.optix.close()

    def refresh(self):
        self.optix.refresh_scene()

if __name__ == '__main__':
    import openmesh
    import os

    p = os.getcwd().replace("\\", "/")
    mesh = "/".join(p.split("/")[:-3]) + "/test_geos/Toy.obj"

    app = QtWidgets.QApplication([])
    wid = QtOptiX()
    wid.optix.set_background(0)

    m = openmesh.read_trimesh(mesh)
    # m = openmesh.PolyMesh()
    # m.triangulate()
    m.update_vertex_normals()
    # color = np.random.random((m.n_vertices(), 3))

    wid.optix.set_mesh("surd", pos=m.points(), pidx=m.face_vertex_indices(), normals=m.vertex_normals(),
                       c=m.points())
    wid.optix.set_param(min_accumulation_step=1, max_accumulation_frames=1000)
    wid.show()
    # d = np.linalg.norm(optix.optix.get_camera_target() - optix.optix.get_camera_eye())
    wid.optix.setup_light("light1", color=10, radius=0.3 * 10)
    wid.update_cam()
    sys.exit(app.exec_())
