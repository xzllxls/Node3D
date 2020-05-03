from Qt import QtGui, QtCore, QtWidgets, QtOpenGL
from PIL import Image
import numpy as np
ZOOM_MIN = -0.95
ZOOM_MAX = 2.0


class ImageGraphicsView(QtWidgets.QGraphicsView):
    position_changed = QtCore.Signal(object, object)
    color_changed = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(ImageGraphicsView, self).__init__(parent)

        self.setScene(ImageGraphicsScene(self))
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setOptimizationFlag(QtWidgets.QGraphicsView.DontAdjustForAntialiasing)

        self.setAcceptDrops(True)
        self.resize(850, 800)

        self._scene_range = QtCore.QRectF(
            0, 0, self.size().width(), self.size().height())
        self._update_scene()
        self._last_size = self.size()

        self._image_item = ImageItem()
        self.image_data = None
        self.scene().addItem(self._image_item)
        self._image_item.mouse_moved.connect(self.update_info)

        self._origin_pos = None
        self._previous_pos = QtCore.QPoint(self.width(), self.height())

        self.LMB_state = False
        self.RMB_state = False
        self.MMB_state = False
        self.ALT_state = False
        self.CTRL_state = False
        self.SHIFT_state = False
        self.COLLIDING_state = False

    def __repr__(self):
        return '{}.{}()'.format(
            self.__module__, self.__class__.__name__)

    def update_info(self, x, y):
        if self.image_data is not None:
            self.position_changed.emit(x, y)
            self.color_changed.emit(self.image_data[x, y])

    def set_image(self, data, update=True):
        if update:
            self.image_data = data
        data = data.copy()
        try:
            data = np.clip(data*255, 0, 255).astype(np.uint8)
        except:
            data = (data*255, 0, 255).astype(np.uint8)
        dim = data.shape[-1]
        if dim == 4 or dim == 3:
            if dim == 3:
                _d = np.empty((data.shape[0], data.shape[1], 4), dtype=np.uint8)
                _d[..., [0, 1, 2]] = data
                _d[..., 3] = 255
                data = _d
            data = data
            pil_img = Image.fromarray(data.transpose((1, 0, 2)), "RGBA")
        else:
            if len(data.shape) == 3:
                data = data.reshape((data.shape[0], data.shape[1]))
            pil_img = Image.fromarray(data.transpose((1, 0)), "L")

        self._image_item.setPixmap(QtGui.QPixmap.fromImage(pil_img.toqimage()))

    # --- private ---

    def _set_viewer_zoom(self, value, sensitivity=None, pos=None):
        if pos:
            pos = self.mapToScene(pos)
        if sensitivity is None:
            scale = 1.001 ** value
            self.scale(scale, scale, pos)
            return

        if value == 0.0:
            return
        scale = (0.9 + sensitivity) if value < 0.0 else (1.1 - sensitivity)
        zoom = self.get_zoom()
        if ZOOM_MIN >= zoom:
            if scale == 0.9:
                return
        if ZOOM_MAX <= zoom:
            if scale == 1.1:
                return
        self.scale(scale, scale, pos)

    def _set_viewer_pan(self, pos_x, pos_y):
        speed = self._scene_range.width() * 0.0012
        x = -pos_x * speed
        y = -pos_y * speed
        self._scene_range.adjust(x, y, x, y)
        self._update_scene()

    def scale(self, sx, sy, pos=None):
        scale = [sx, sx]
        center = pos or self._scene_range.center()
        w = self._scene_range.width() / scale[0]
        h = self._scene_range.height() / scale[1]
        self._scene_range = QtCore.QRectF(
            center.x() - (center.x() - self._scene_range.left()) / scale[0],
            center.y() - (center.y() - self._scene_range.top()) / scale[1],
            w, h
        )
        self._update_scene()

    def _update_scene(self):
        self.setSceneRect(self._scene_range)
        self.fitInView(self._scene_range, QtCore.Qt.KeepAspectRatio)

    # --- reimplemented events ---

    def resizeEvent(self, event):
        delta = max(self.size().width() / self._last_size.width(),
                    self.size().height() / self._last_size.height())
        self._set_viewer_zoom(delta)
        self._last_size = self.size()
        super(ImageGraphicsView, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        pass

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = True
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = True
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = True

        self._origin_pos = event.pos()
        self._previous_pos = event.pos()

        super(ImageGraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = False
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = False
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = False

        super(ImageGraphicsView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        super(ImageGraphicsView, self).mouseMoveEvent(event)

        if self.MMB_state and self.ALT_state:
            pos_x = (event.x() - self._previous_pos.x())
            zoom = 0.1 if pos_x > 0 else -0.1
            self._set_viewer_zoom(zoom, 0.05, pos=event.pos())
        elif self.MMB_state or (self.LMB_state and self.ALT_state):
            pos_x = (event.x() - self._previous_pos.x())
            pos_y = (event.y() - self._previous_pos.y())
            self._set_viewer_pan(pos_x, pos_y)

        self._previous_pos = event.pos()
        super(ImageGraphicsView, self).mouseMoveEvent(event)

    def wheelEvent(self, event):
        try:
            delta = event.delta()
        except AttributeError:
            # For PyQt5
            delta = event.angleDelta().y()
            if delta == 0:
                delta = event.angleDelta().x()
        self._set_viewer_zoom(delta, pos=event.pos())

    def keyPressEvent(self, event):
        self.ALT_state = event.modifiers() == QtCore.Qt.AltModifier
        self.CTRL_state = event.modifiers() == QtCore.Qt.ControlModifier
        self.SHIFT_state = event.modifiers() == QtCore.Qt.ShiftModifier

        if event.modifiers() == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier):
            self.ALT_state = True
            self.SHIFT_state = True

        if event.key() == QtCore.Qt.Key_F:
            self.fit_to_image()
        elif event.key() == QtCore.Qt.Key_R:
            self.show_channel(0)
        elif event.key() == QtCore.Qt.Key_G:
            self.show_channel(1)
        elif event.key() == QtCore.Qt.Key_B:
            self.show_channel(2)
        elif event.key() == QtCore.Qt.Key_A:
            self.show_channel(3)
        elif event.key() == QtCore.Qt.Key_Q:
            self.show_channel(None)

        super(ImageGraphicsView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.ALT_state = event.modifiers() == QtCore.Qt.AltModifier
        self.CTRL_state = event.modifiers() == QtCore.Qt.ControlModifier
        self.SHIFT_state = event.modifiers() == QtCore.Qt.ShiftModifier
        super(ImageGraphicsView, self).keyReleaseEvent(event)

    def show_channel(self, channel):
        if self.image_data is None:
            return
        if channel is None:
            self.set_image(self.image_data, False)
            return

        dim = self.image_data.shape[-1]
        if len(self.image_data.shape) == 2:
            dim = 1
        if channel == 3 and channel >= dim:
            self.set_image(np.ones((self.image_data.shape[0],
                                    self.image_data.shape[1]),
                                   dtype=self.image_data.dtype), False)
            return
        if channel >= dim:
            self.set_image(np.zeros((self.image_data.shape[0],
                                    self.image_data.shape[1]),
                                    dtype=self.image_data.dtype), False)
            return
        if dim == 1:
            self.set_image(self.image_data, False)
            return
        self.set_image(self.image_data[..., channel], False)

    def center_selection(self,):
        rect = self._combined_rect(None)
        self.centerOn(rect.center().x(), rect.center().y())

    def reset_zoom(self, cent=None):
        self._scene_range = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        if cent:
            self._scene_range.translate(cent - self._scene_range.center())
        self._update_scene()

    def get_zoom(self):
        transform = self.transform()
        cur_scale = (transform.m11(), transform.m22())
        return float('{:0.2f}'.format(cur_scale[0] - 1.0))

    def set_zoom(self, value=0.0):
        if value == 0.0:
            self.reset_zoom()
            return
        zoom = self.get_zoom()
        if zoom < 0.0:
            if not (ZOOM_MIN <= zoom <= ZOOM_MAX):
                return
        else:
            if not (ZOOM_MIN <= value <= ZOOM_MAX):
                return
        value = value - zoom
        self._set_viewer_zoom(value, 0.0)

    def fit_to_image(self):
        self._scene_range = self._image_item.boundingRect()
        self._update_scene()

    def force_update(self):
        self._update_scene()

    def scene_rect(self):
        return [self._scene_range.x(), self._scene_range.y(),
                self._scene_range.width(), self._scene_range.height()]

    def scene_center(self):
        cent = self._scene_range.center()
        return [cent.x(), cent.y()]

    def set_scene_rect(self, rect):
        self._scene_range = QtCore.QRectF(*rect)
        self._update_scene()

    def clear_key_state(self):
        self.CTRL_state = False
        self.SHIFT_state = False
        self.ALT_state = False

    def use_OpenGL(self):
        format = QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)
        format.setSamples(4)
        self.setViewport(QtOpenGL.QGLWidget(format))


class ImageGraphicsScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent=None):
        super(ImageGraphicsScene, self).__init__(parent)
        self.setBackgroundBrush(QtGui.QColor(0, 0, 0))
        self.editable = True

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(self.__module__,
                                      self.__class__.__name__,
                                      self.viewer())

    def _draw_text(self, painter, pen):
        font = QtGui.QFont()
        font.setPixelSize(48)
        painter.setFont(font)
        parent = self.viewer()
        pos = QtCore.QPoint(20, parent.height()-20)
        painter.setPen(pen)
        painter.drawText(parent.mapToScene(pos), 'Not Editable')

    def drawBackground(self, painter, rect):
        super(ImageGraphicsScene, self).drawBackground(painter, rect)

    def mousePressEvent(self, event):
        super(ImageGraphicsScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(ImageGraphicsScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super(ImageGraphicsScene, self).mouseReleaseEvent(event)

    def viewer(self):
        return self.views()[0] if self.views() else None


class ImageItem(QtWidgets.QGraphicsPixmapItem, QtCore.QObject):
    mouse_moved = QtCore.Signal(object, object)

    def __init__(self):
        super(ImageItem, self).__init__()
        QtCore.QObject.__init__(self)
        self.setShapeMode(QtWidgets.QGraphicsPixmapItem.BoundingRectShape)
        self.setAcceptHoverEvents(True)

    def hoverMoveEvent(self, event):
        super(ImageItem, self).hoverMoveEvent(event)
        self.mouse_moved.emit(int(event.pos().x()), int(event.pos().y()))

    # def mousePressEvent(self, event):
    #     super(ImageItem, self).mousePressEvent(event)
    #     self.mouse_moved.emit(int(event.pos().x()), int(event.pos().y()))