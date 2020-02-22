from Qt import QtGui, QtCore, QtWidgets
from scipy.interpolate import interp1d


def build_curve_ramp(values, kind):
    sorted_points = sorted(values, key=lambda v: v[0])
    x = [-0.1]
    y = [sorted_points[0][1]]
    [[x.append(i[0]), y.append(i[1])] for i in sorted_points]
    x.append(1.1)
    y.append(sorted_points[-1][1])
    try:
        return interp1d(x, y, kind=kind)
    except:
        return None


class Curve(object):
    """ Interface to a curve which also manages connecting the end of the
    curve with the beginning. """

    def __init__(self):
        self._curve = None
        self._modified = False
        self._border_points = 1
        self._color = (170, 170, 170)
        self._cv_points = [(0, 0), (1.0, 1.0)]
        #
        self.kind = "quadratic"
        self.build_curve()

    def set_interp_kind(self, kind):
        if kind in ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']:
            self.kind = kind
            self.build_curve()

    @property
    def modified(self):
        """ Returns whether the curve was modified since the creation """
        return self._modified

    @property
    def control_points(self):
        """ Returns a list of all controll points """
        return self._cv_points

    @control_points.setter
    def control_points(self, points):
        """ Sets the cv points to the given list of points """
        self._cv_points = points
        self._modified = True
        self.build_curve()

    @property
    def color(self):
        """ Returns the display color of the curve """
        return self._color

    @color.setter
    def color(self, rgb):
        """ Sets the display color of the curve """
        self._color = rgb

    def set_single_value(self, val):
        """ Sets the curve to be linear, and only use a single value """
        self._cv_points = [[0.5, val]]
        self._modified = False
        self.build_curve()

    def append_cv(self, x, y):
        """ Appends a new cv and returns the index of the attached cv """
        self._cv_points.append([x, y])
        self.build_curve()
        self._modified = True
        return len(self._cv_points) - 1

    def remove_cv(self, index):
        """ Attempts to remove the cv at the given index, does nothing if only
        one control point is left """
        if len(self._cv_points) > 1:
            del self._cv_points[index]
        self._modified = True
        self.build_curve()

    def build_curve(self):
        """ Rebuilds the curve based on the controll point values """
        sorted_points = sorted(self._cv_points, key=lambda v: v[0])
        x = [-0.1]
        y = [sorted_points[0][1]]
        [[x.append(i[0]), y.append(i[1])] for i in sorted_points]
        x.append(1.1)
        y.append(sorted_points[-1][1])
        try:
            self._curve = interp1d(x, y, kind=self.kind)
        except:
            pass

    def setValue(self, value):
        self._cv_points = value[0]
        self.kind = value[1]
        self.build_curve()

    def set_cv_value(self, index, x_value, y_value):
        """ Updates the cv point at the given index """
        self._cv_points[index] = [x_value, y_value]
        self._modified = True

    def get_value(self, offset):
        return self._curve(offset)

    def value(self):
        sorted_points = sorted(self._cv_points, key=lambda v: v[0])
        return [sorted_points, self.kind]

    def serialize(self):
        """ Returns the value of the curve as yaml list """
        points = ["[{:5.10f},{:5.10f}]".format(float(a), float(b)) for a, b in self._cv_points]
        return "[" + ','.join(points) + "]"


class CurveWidget(QtWidgets.QWidget):
    valueChangeFinished = QtCore.Signal(object)
    valueChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        """ Constructs the CurveWidget, we start with an initial curve """
        super(CurveWidget, self).__init__(parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.curve = Curve()

        # Widget render constants
        self._cv_point_size = 5

        # Currently dragged control point, format is:
        # (CurveIndex, PointIndex, Drag-Offset (x,y))
        self._drag_point = None
        self._drag_value = 0.0
        self._height = 0.0

        # Currently selected control point, format is:
        # (CurveIndex, PointIndex)
        self._selected_point = None
        self.show_unit = True

    def set_interp_kind(self, kind):
        self.curve.set_interp_kind(kind)
        self.update()

    def setValue(self, value):
        self.curve.setValue(value)
        self.update()

    def value(self):
        return self.curve.value()

    def paintEvent(self, e):
        """ Internal QT paint event, draws the entire widget """
        qp = QtGui.QPainter()
        qp.begin(self)
        self._draw(qp)
        qp.end()

    def mousePressEvent(self, QMouseEvent):
        """ Internal mouse-press handler """
        self._drag_point = None
        self._selected_point = None
        mouse_pos = QMouseEvent.pos()
        mouse_x = mouse_pos.x()
        mouse_y = mouse_pos.y()

        curve = self.curve
        width = self.width()
        height = self.height()

        # Check for clicks on control points
        for cv_index, (x, y) in enumerate(curve.control_points):
            point_x = self._get_x_value_for(x)
            point_y = self._get_y_value_for(y)
            if abs(point_x - mouse_x) < self._cv_point_size + 6:
                if (abs(point_y - mouse_y)) < self._cv_point_size + 6:
                    drag_x_offset = mouse_x - point_x
                    drag_y_offset = mouse_y - point_y
                    mpos_relx = float(mouse_x) / width
                    self._drag_point = (cv_index, (drag_x_offset, drag_y_offset))
                    self._drag_value = mpos_relx
                    self._height = float(mouse_y) / height
                    self._selected_point = cv_index

        # If still no intersection, check if we clicked a curve
        if 0 < mouse_x < width:
            if 0 < mouse_y < height:
                mpos_relx = float(mouse_x) / width
                curve_py = curve.get_value(mpos_relx)
                curve_offy = self._get_y_value_for(curve_py)

                if abs(curve_offy - mouse_y) < 8 and self._selected_point is None:
                    # Clicked on curve, spawn new point
                    cv_index = curve.append_cv(mpos_relx, curve_py)

                    self._selected_point = cv_index
                    self._drag_point = (cv_index, (0, 0))
                    self._drag_value = mpos_relx
                    self._height = float(mouse_y) / height
        self.update()

    def mouseReleaseEvent(self, event):
        """ Internal mouse-release handler """
        self._drag_point = None
        self._drag_value = -1
        self.update()
        self.valueChangeFinished.emit(self.value())

    def mouseMoveEvent(self, event):
        """ Internal mouse-move handler """

        if self._drag_point is not None:
            mouse_x = event.pos().x() - self._drag_point[1][0]
            mouse_y = event.pos().y() - self._drag_point[1][1]

            # Convert to local coordinate
            local_x = max(0, min(1, mouse_x / float(self.width())))
            local_y = mouse_y / float(self.height())
            local_y = 1 - max(0, min(1, local_y))

            self._drag_value = local_x
            self._height = local_y

            # Set new point data
            self.curve.set_cv_value(self._drag_point[0], local_x, local_y)

            # Redraw curve
            self.curve.build_curve()
            self.update()
            self.valueChanged.emit(self.value())

    def keyPressEvent(self, event):
        """ Internal keypress handler """
        # Delete anchor point
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_current_point()

    def delete_current_point(self):
        """ Deletes the currently selected point """
        if self._selected_point is not None:
            self.curve.remove_cv(self._selected_point)
            self._selected_point = None
            self._drag_point = None
            self.update()

    def set_curve(self, curve):
        """ Sets the list of displayed curves """
        self._selected_point = None
        self._drag_point = None
        self.curve = curve
        self.update()

    def _get_y_value_for(self, local_value):
        """ Converts a value from 0 to 1 to a value from 0 .. canvas height """
        local_value = max(0, min(1.0, 1.0 - local_value))
        local_value *= self.height()
        return local_value

    def _get_x_value_for(self, local_value):
        """ Converts a value from 0 to 1 to a value from 0 .. canvas width """
        local_value = max(0, min(1.0, local_value))
        local_value *= self.width()
        return local_value

    def _draw(self, painter):
        """ Internal method to draw the widget """

        width = self.width()
        height = self.height()

        # Draw field background
        painter.setPen(QtGui.QColor(70, 70, 70))
        painter.setBrush(QtGui.QColor(40, 40, 40))
        painter.drawRect(0, 0, width - 1, height - 1)

        if self.show_unit:
            # Compute amount of horizontal / vertical lines
            num_vert_lines = 10
            line_spacing_x = width / num_vert_lines
            num_horiz_lines = 5
            line_spacing_y = height / num_horiz_lines

            # Draw vertical lines
            painter.setPen(QtGui.QColor(50, 50, 50))
            for i in range(num_vert_lines + 1):
                line_pos = i * line_spacing_x - 1
                painter.drawLine(line_pos, 0, line_pos, height)

            # Draw horizontal lines
            # painter.setPen(QtGui.QColor(200, 200, 200))
            for i in range(num_horiz_lines):
                line_pos = height - i * line_spacing_y
                painter.drawLine(0, line_pos, width, line_pos)

            # Draw vetical legend labels
            painter.setPen(QtGui.QColor(70, 70, 70))
            for i in range(num_horiz_lines):
                if i > 0:
                    line_pos = height - i * line_spacing_y
                    painter.drawText(6, line_pos + 3, "{:.1f}".format(i * 0.2))

            # # Draw horizontal legend labels
            for i in range(num_vert_lines + 1):
                if i == 0 or i == num_vert_lines:
                    continue
                line_pos = i * line_spacing_x
                painter.drawText(line_pos - 14, height - 10, "{:.1f}".format(i * 0.1))

        # Draw curve
        painter.setPen(QtGui.QColor(*self.curve.color))
        last_value = 0
        for i in range(width):
            rel_offset = i / (width - 1.0)
            curve_height = self._get_y_value_for(self.curve.get_value(rel_offset))
            if i == 0:
                last_value = curve_height

            painter.drawLine(i - 1, last_value, i, curve_height)
            last_value = curve_height

        # Draw the CV points of the curve
        painter.setBrush(QtGui.QColor(240, 240, 240))

        for cv_index, (x, y) in enumerate(self.curve.control_points):
            offs_x = x * width
            offs_y = (1 - y) * height

            if self._selected_point and self._selected_point == cv_index:
                painter.setPen(QtGui.QColor(255, 0, 0))
            else:
                painter.setPen(QtGui.QColor(100, 100, 100))
            painter.drawRect(
                offs_x - self._cv_point_size, offs_y - self._cv_point_size,
                2 * self._cv_point_size, 2 * self._cv_point_size)

        # Draw selected value
        if self._drag_point:
            painter.setBrush(QtGui.QColor(200, 200, 200))
            painter.setPen(QtGui.QColor(200, 200, 200))
            offs_x = max(0, min(width + 10, self._drag_value * width - 19))
            painter.drawText(offs_x + 7, height - 20, "{:.2f} , {:.2f}".format(self._drag_value, self._height))
            painter.setPen(QtGui.QColor(150, 150, 150))
            painter.drawLine(offs_x + 19, 0, offs_x + 19, height + 5)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    editor = CurveWidget()

    editor.show()
    print(editor.value())
    app.exec_()
