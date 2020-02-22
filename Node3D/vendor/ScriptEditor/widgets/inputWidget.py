from Qt import QtCore, QtGui, QtWidgets
import os
import jedi
from .pythonSyntax import syntaxHighLighter, design

from . import completeWidget
from .. import settingsManager
import re

addEndBracket = True

indentLen = 4
minimumFontSize = 10
escapeButtons = [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Left, QtCore.Qt.Key_Right, QtCore.Qt.Key_Home,
                 QtCore.Qt.Key_End, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown, QtCore.Qt.Key_Delete,
                 QtCore.Qt.Key_Insert, QtCore.Qt.Key_Escape]
font_name = 'Lucida Console'

packageName = __file__.replace("\\", "/").split("/")[-5]
preImport = '''from {}.vendor.NodeGraphQt import NodeGraph\n
gp = NodeGraph()\n
from Framework.widgets.mainWindow import mainWindow\n
wid = mainWindow()\n
from Framework.base.node import GeometryNode\n
node = GeometryNode()\n
import numpy as np\n'''.format(packageName)


class parseText_thread(QtCore.QThread):
    changed = QtCore.Signal(object)

    def __init__(self):
        super(parseText_thread, self).__init__()
        self.textCursor = None
        self.text = ''

    def run(self):
        tc = self.textCursor
        pos = tc.position()
        try:
            if re.match('[a-zA-Z0-9_.]', self.text[pos - 1]):
                self.text = preImport + self.text
                offs = len(preImport.split('\n')) - 1
                bl = tc.blockNumber() + 1 + offs
                col = tc.columnNumber()
                script = jedi.Script(self.text, bl, col, '')
                self.changed.emit(script.completions())
                return
        except:
            pass
        self.changed.emit(None)


class inputClass(QtWidgets.QTextEdit):
    executeSignal = QtCore.Signal()
    saveSignal = QtCore.Signal()
    inputSignal = QtCore.Signal()

    def __init__(self, parent, desk=None):

        # https://github.com/davidhalter/jedi
        # http://jedi.jedidjah.ch/en/latest/
        super(inputClass, self).__init__(parent)
        self.p = parent
        self.desk = desk
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.document().setDefaultFont(QtGui.QFont(font_name, minimumFontSize, QtGui.QFont.Normal))
        metrics = QtGui.QFontMetrics(self.document().defaultFont())
        self.setTabStopWidth(4 * metrics.width(' '))
        self.setAcceptDrops(True)
        self.fs = 12
        self.completer = completeWidget.completeMenuClass(parent, self)
        self.thread = parseText_thread()
        self.thread.changed.connect(self.completer.updateCompleteList)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.openMenu)
        data = settingsManager.scriptEditor().readSettings()
        self.applyHightLighter(data.get('theme'))
        # self.changeFontSize(False)
        self.changeFontSize(True)

    def focusOutEvent(self, event):
        self.saveSignal.emit()
        self.completer.hideMe()
        QtWidgets.QTextEdit.focusOutEvent(self, event)

    def hideEvent(self, event):
        self.completer.updateCompleteList()
        try:
            QtWidgets.QTextEdit.hideEvent(self, event)
        except:
            pass

    def applyHightLighter(self, theme=None, qss=None):
        self.blockSignals(True)
        colors = None
        if theme or not theme == 'default':
            colors = design.getColors(theme)
            if self.completer:
                self.completer.updateStyle(colors)
        self.hgl = syntaxHighLighter.PythonHighlighterClass(self, colors)
        st = design.editorStyle(theme)
        self.setStyleSheet(st)
        self.blockSignals(False)

    def applyPreviewStyle(self, colors):
        self.blockSignals(True)
        self.hgl = syntaxHighLighter.PythonHighlighterClass(self, colors)
        qss = design.applyColorToEditorStyle(colors)
        self.setStyleSheet(qss)
        self.completer.setStyleSheet(qss)
        self.blockSignals(False)

    def parseText(self):
        if self.completer:
            text = self.toPlainText()
            self.moveCompleter()
            if text:
                self.thread.text = text
                self.thread.textCursor = self.textCursor()
                self.thread.start()
            else:
                self.completer.updateCompleteList()

    def moveCompleter(self):
        # self.p.out.showMessage('move')
        rec = self.cursorRect()
        # pt = self.mapToGlobal(QPoint(rec.bottomRight().x(), rec.y()+self.completer.lineHeight))
        pt = self.mapToGlobal(rec.bottomRight())
        y = x = 0
        if self.completer.isVisible() and self.desk:
            currentScreen = self.desk.screenGeometry(self.mapToGlobal(rec.bottomRight()))
            futureCompGeo = self.completer.geometry()
            futureCompGeo.moveTo(pt)
            if not currentScreen.contains(futureCompGeo):
                try:
                    i = currentScreen.intersect(futureCompGeo)
                except:
                    i = currentScreen.intersected(futureCompGeo)
                x = futureCompGeo.width() - i.width()
                y = futureCompGeo.height() + self.completer.lineHeight if (futureCompGeo.height() - i.height()) > 0 else 0

        pt = self.mapToGlobal(rec.bottomRight()) + QtCore.QPoint(10 - x, -y)
        self.completer.move(pt)

    def charBeforeCursor(self, cursor):
        pos = cursor.position()
        if pos:
            text = self.toPlainText()
            return text[pos - 1]

    def getCurrentIndent(self):
        cursor = self.textCursor()
        auto = self.charBeforeCursor(cursor) == ':'
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        result = ''
        if line.strip():
            p = r"(^\s*)"
            m = re.search(p, line)
            if m:
                result = m.group(0)
            if auto:
                result += '    '
        return result

    def keyPressEvent(self, event):
        self.inputSignal.emit()
        parse = 0
        # apply complete
        if event.modifiers() == QtCore.Qt.NoModifier and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            if self.completer and self.completer.isVisible():
                self.completer.applyCurrentComplete()
                return
            # auto indent
            else:
                add = self.getCurrentIndent()
                if add:
                    QtWidgets.QTextEdit.keyPressEvent(self, event)
                    cursor = self.textCursor()
                    cursor.insertText(add)
                    self.setTextCursor(cursor)
                    return
        # remove 4 spaces
        elif event.modifiers() == QtCore.Qt.NoModifier and event.key() == QtCore.Qt.Key_Backspace:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine, QtGui.QTextCursor.KeepAnchor)
            line = cursor.selectedText()
            if line:
                p = r"    $"
                m = re.search(p, line)
                if m:
                    cursor.removeSelectedText()
                    line = line[:-3]
                    cursor.insertText(line)
                    self.setTextCursor(cursor)
            parse = 1
        # comment
        elif event.modifiers() == QtCore.Qt.AltModifier and event.key() == QtCore.Qt.Key_Q:
            self.p.tab.comment()
            return
        # execute selected
        elif event.modifiers() == QtCore.Qt.ControlModifier and event.key() in [QtCore.Qt.Key_Return,
                                                                                QtCore.Qt.Key_Enter]:
            if self.completer:
                self.completer.updateCompleteList()
            self.executeSignal.emit()
            return
        # ignore Shift + Enter
        elif event.modifiers() == QtCore.Qt.ShiftModifier and event.key() in [QtCore.Qt.Key_Return,
                                                                              QtCore.Qt.Key_Enter]:
            return
        # duplicate
        elif event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_D:
            self.duplicate()
            self.update()
            return
        elif event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Slash:
            self.commentSelected()
            self.update()
            return
        # increase indent
        elif event.key() == QtCore.Qt.Key_Tab:
            if self.completer:
                if self.completer.isVisible():
                    self.completer.applyCurrentComplete()
                    return
            if self.textCursor().selection().toPlainText():
                self.selectBlocks()
                self.moveSelected(True)
                return
            else:
                self.insertPlainText(' ' * indentLen)
                return
        # decrease indent
        elif event.key() == QtCore.Qt.Key_Backtab:
            self.selectBlocks()
            self.moveSelected(False)
            if self.completer:
                self.completer.updateCompleteList()
            return
        # close completer
        elif event.key() in escapeButtons:
            if self.completer:
                self.completer.updateCompleteList()
            self.setFocus()
        # go to completer
        elif event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_Up:
            if self.completer.isVisible():
                self.completer.setFocus()
                if self.completer.activeState():
                    self.completer.keyPressEvent(event)
                else:
                    self.completer.activateCompleter(event.key())
                return
        # just close completer
        elif not event.modifiers() == QtCore.Qt.NoModifier and not event.modifiers() == QtCore.Qt.ShiftModifier:
            self.completer.updateCompleteList()
        else:
            parse = 1

        QtWidgets.QTextEdit.keyPressEvent(self, event)
        # start parse text
        if (parse and event.text()) or event.text() == '.':
            self.parseText()

    def moveSelected(self, inc):
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.document().documentLayout().blockSignals(True)
            self.selectBlocks()
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            text = cursor.selection().toPlainText()
            cursor.removeSelectedText()
            if inc:
                newText = self.addTabs(text)
            else:
                newText = self.removeTabs(text)
            cursor.beginEditBlock()
            cursor.insertText(newText)
            cursor.endEditBlock()
            newEnd = cursor.position()
            cursor.setPosition(start)
            cursor.setPosition(newEnd, QtGui.QTextCursor.KeepAnchor)
            self.document().documentLayout().blockSignals(False)
            self.setTextCursor(cursor)
            self.update()

    def commentSelected(self):
        cursor = self.textCursor()
        self.document().documentLayout().blockSignals(True)
        self.selectBlocks()
        pos = cursor.position()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
        cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        text = cursor.selection().toPlainText()
        self.document().documentLayout().blockSignals(False)
        # cursor.removeSelectedText()
        text, offset = self.addRemoveComments(text)
        cursor.insertText(text)
        cursor.setPosition(min(pos + offset, len(self.toPlainText())))
        self.setTextCursor(cursor)
        self.update()

    def addRemoveComments(self, text):
        result = text
        ofs = 0
        if text.strip():
            lines = text.split('\n')
            ind = 0
            while not lines[ind].strip():
                ind += 1
            if lines[ind].strip()[0] == '#':  # remove comment
                result = '\n'.join([x.replace('#', '', 1) for x in lines])
                ofs = -1
            else:  # add comment
                result = '\n'.join(['#' + x for x in lines])
                ofs = 1
        return result, ofs

    def insertText(self, comp):
        cursor = self.textCursor()
        self.document().documentLayout().blockSignals(True)
        cursor.insertText(comp.complete)
        cursor = self.fixLine(cursor, comp)
        self.document().documentLayout().blockSignals(False)
        self.setTextCursor(cursor)
        self.update()

    def fixLine(self, cursor, comp):
        # self.document().documentLayout().blockSignals(True)
        pos = cursor.position()
        linePos = cursor.positionInBlock()

        cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        cursor.removeSelectedText()

        start = line[:linePos]
        end = line[linePos:]
        before = start[:-len(comp.name)]
        br = ''
        ofs = 0
        if hasattr(comp, 'end_char'):
            if addEndBracket and before and comp.end_char:
                brackets = {'"': '"', "'": "'"}  # , '(':')', '[':']'}
                if before[-1] in brackets:
                    ofs = 1
                    br = brackets[before[-1]]
                    if end and end[0] == brackets[before[-1]]:
                        br = ''

        res = before + comp.name + br + end

        # self.document().documentLayout().blockSignals(False)
        cursor.beginEditBlock()
        cursor.insertText(res)
        cursor.endEditBlock()
        cursor.clearSelection()
        cursor.setPosition(pos + ofs, QtGui.QTextCursor.MoveAnchor)
        return cursor

    def duplicate(self):
        self.document().documentLayout().blockSignals(True)
        cursor = self.textCursor()
        if cursor.hasSelection():  # duplicate selected
            sel = cursor.selectedText()
            end = cursor.selectionEnd()
            cursor.setPosition(end)
            cursor.insertText(sel)
            cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        else:  # duplicate line
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.EndOfLine, QtGui.QTextCursor.KeepAnchor)
            line = cursor.selectedText()
            cursor.clearSelection()
            cursor.insertText('\n' + line)
            self.setTextCursor(cursor)
        self.document().documentLayout().blockSignals(False)

    def removeTabs(self, text):
        lines = text.split('\n')
        new = []
        pat = re.compile("^ .*")
        for line in lines:
            line = line.replace('\t', ' ' * indentLen)
            for _ in range(4):
                if pat.match(line):
                    line = line[1:]
            new.append(line)
        return '\n'.join(new)

    def addTabs(self, text):
        lines = [(' ' * indentLen) + x for x in text.split('\n')]
        return '\n'.join(lines)

    def selectBlocks(self):
        self.document().documentLayout().blockSignals(True)
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        self.document().documentLayout().blockSignals(False)

    def getSelection(self):
        cursor = self.textCursor()
        text = cursor.selection().toPlainText()
        return text

    def addText(self, text):
        if self.completer:
            self.completer.updateCompleteList()
        self.blockSignals(True)
        self.append(text)
        self.blockSignals(False)

    ########################### DROP
    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        QtWidgets.QTextEdit.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        QtWidgets.QTextEdit.dragMoveEvent(self, event)

    def dragLeaveEvent(self, event):
        event.accept()
        QtWidgets.QTextEdit.dragLeaveEvent(self, event)

    def dropEvent(self, event):
        event.acceptProposedAction()
        QtWidgets.QTextEdit.dropEvent(self, event)

    ################################################################

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if self.completer:
                self.completer.updateCompleteList()
            if event.delta() > 0:
                self.changeFontSize(True)
                # self.zoomIn(1)
            else:
                self.changeFontSize(False)
                # self.zoomOut(1)
        # super(inputClass, self).wheelEvent(event)
        else:
            QtWidgets.QTextEdit.wheelEvent(self, event)

    def changeFontSize(self, up):
        f = self.font()
        size = f.pointSize()
        if up:
            size = min(30, size + 1)
        else:
            size = max(8, size - 1)
        f.setPointSize(size)
        f.setFamily(font_name)
        self.setFont(f)

    def setTextEditFontSize(self, size):
        style = self.styleSheet() + '''QTextEdit
    {
        font-size: %spx;
        font-family: %s;
    }''' % (size, font_name)
        self.setStyleSheet(style)

    def insertFromMimeData(self, source):
        text = source.text()
        # text = re.sub(r'[^\x00-\x7F]','?', text)
        self.insertPlainText(text)

    def getFontSize(self):
        s = self.font().pointSize()
        return s

    def setFontSize(self, size):
        if size > minimumFontSize:
            f = self.font()
            f.setPointSize(size)
            self.setFont(f)

    def mousePressEvent(self, event):
        self.completer.updateCompleteList()
        QtWidgets.QTextEdit.mousePressEvent(self, event)

    def selectWord(self, pattern, number, replace=None):
        text = self.toPlainText()
        if not pattern in text:
            return number
        cursor = self.textCursor()
        indexis = [(m.start(0), m.end(0)) for m in re.finditer(self.fixRegextSymbols(pattern), text)]
        if number > len(indexis) - 1:
            number = 0
        cursor.setPosition(indexis[number][0])
        cursor.setPosition(indexis[number][1], QtGui.QTextCursor.KeepAnchor)
        if replace:
            cursor.removeSelectedText()
            cursor.insertText(replace)
        self.setTextCursor(cursor)
        self.setFocus()
        return number

    def fixRegextSymbols(self, pattern):
        for s in ['[', ']', '(', ')', '*', '^', '.', ',', '{', '}', '$']:
            pattern = pattern.replace(s, '\\' + s)
        return pattern

    def replaceAll(selfold, new):
        pass
