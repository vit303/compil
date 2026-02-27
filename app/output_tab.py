from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView


class OutputTab(QWidget):
    def __init__(self, title="Результаты", table=False, tr=lambda x: x):
        super().__init__()
        self.tr = tr
        self.is_table = table

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if table:
            self.table = QTableWidget()
            self.table.setColumnCount(3)
            
            headers = [self.tr("Строка"), self.tr("Позиция"), self.tr("Сообщение")]
            self.table.setHorizontalHeaderLabels(headers)
            
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            layout.addWidget(self.table)
        else:
            self.text_edit = QTextEdit()
            self.text_edit.setReadOnly(True)
            layout.addWidget(self.text_edit)

    def append_text(self, text):
        if not self.is_table:
            self.text_edit.append(text)

    def add_error(self, line: int, col: int, message: str):
        if self.is_table:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(line)))
            self.table.setItem(row, 1, QTableWidgetItem(str(col)))
            self.table.setItem(row, 2, QTableWidgetItem(message))

    def clear(self):
        if self.is_table:
            self.table.setRowCount(0)
        else:
            self.text_edit.clear()

    def scale_font(self, delta):
        if self.is_table:
            font = self.table.font()
            font.setPointSize(max(8, min(72, font.pointSize() + delta)))
            self.table.setFont(font)
        else:
            font = self.text_edit.font()
            font.setPointSize(max(8, min(72, font.pointSize() + delta)))
            self.text_edit.setFont(font)