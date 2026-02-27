from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QTextFormat, QFont
from PyQt6.QtCore import QRect, Qt, QSize
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit

from .syntax_highlighter import SyntaxHighlighter


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_area_size()

    def paintEvent(self, event):
        self.editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width()
        self.highlight_current_line()

    def line_number_area_size(self):
        digits = len(str(max(1, self.blockCount())))
        space = 8 + self.fontMetrics().horizontalAdvance("9") * digits
        return QSize(space, 0)

    def update_line_number_area_width(self):
        margins = self.line_number_area_size().width()
        self.setViewportMargins(margins, 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_size().width(), cr.height())
        )

    def paint_line_numbers(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(40, 40, 40))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(140, 140, 140))
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 5,
                    self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor(48, 48, 48))
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = 1 if event.angleDelta().y() > 0 else -1
            font = self.font()
            new_size = max(8, min(48, font.pointSize() + delta))
            font.setPointSize(new_size)
            self.setFont(font)
            self.update_line_number_area_width()
            event.accept()
        else:
            super().wheelEvent(event)


class EditorTab(QWidget):
    def __init__(self, filename=None, content="", parent=None):
        super().__init__(parent)
        self.filename = filename
        self.modified = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.editor = CodeEditor()
        self.highlighter = SyntaxHighlighter(self.editor.document())
        self.editor.setPlainText(content)

        layout.addWidget(self.editor)

        self.editor.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        self.modified = True

    @property
    def is_modified(self):
        return self.modified

    def get_text(self):
        return self.editor.toPlainText()

    def set_text(self, text):
        self.editor.setPlainText(text)
        self.modified = False

    def scale_font(self, delta):
        font = self.editor.font()
        new_size = max(8, min(48, font.pointSize() + delta))
        font.setPointSize(new_size)
        self.editor.setFont(font)
        self.editor.update_line_number_area_width()