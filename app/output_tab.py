from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
from typing import List
from .lexical_analyzer import Token


class OutputTab(QWidget):
    def __init__(self, title="Результаты", table=False, is_results_table=False, tr=lambda x: x):
        super().__init__()
        self.tr = tr
        self.is_table = table or is_results_table
        self.is_results_table = is_results_table
        self.errors: List[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if self.is_table:
            self.table = QTableWidget()
            self.table.setColumnCount(4 if is_results_table else 3)

            if is_results_table:
                headers = [
                    self.tr("Условный код"),
                    self.tr("Тип лексемы"),
                    self.tr("Лексема"),
                    self.tr("Местоположение")
                ]
            else:
                headers = [
                    self.tr("Неверный фрагмент"),
                    self.tr("Местоположение"),
                    self.tr("Описание ошибки")
                ]
            self.table.setHorizontalHeaderLabels(headers)

            stretch_col = 3 if is_results_table else 2
            self.table.horizontalHeader().setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            layout.addWidget(self.table)
        else:
            self.text_edit = QTextEdit()
            self.text_edit.setReadOnly(True)
            layout.addWidget(self.text_edit)

    def append_text(self, text):
        if not self.is_table:
            self.text_edit.append(text)

    def add_tokens(self, tokens: List[Token]):
        if not self.is_results_table or not hasattr(self, 'table'):
            return
        self.table.setRowCount(0)
        for token in tokens:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(token.code)))
            self.table.setItem(row, 1, QTableWidgetItem(self.tr(token.type_name)))
            self.table.setItem(row, 2, QTableWidgetItem(token.lexeme))
            location = f"{self.tr('строка')} {token.line}, {token.start_col}-{token.end_col}"
            self.table.setItem(row, 3, QTableWidgetItem(location))

    def add_error(self, line: int, col: int, message: str, fragment: str = ""):
        if self.is_table and not self.is_results_table:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(fragment))
            location = f"{self.tr('строка')} {line}, {self.tr('позиция')} {col}"
            self.table.setItem(row, 1, QTableWidgetItem(location))
            self.table.setItem(row, 2, QTableWidgetItem(message))
            self.errors.append({
                "line": line,
                "col": col,
                "message": message,
                "fragment": fragment,
            })

    def clear(self):
        if self.is_table:
            self.table.setRowCount(0)
            self.errors = []
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

