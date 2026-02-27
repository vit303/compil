from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QStatusBar,
    QFileDialog,
    QMessageBox,
    QToolBar,
    QSplitter, 
    QLabel
)

from PyQt6.QtGui import (
    QAction,
    QIcon,
    QKeySequence
)

from PyQt6.QtCore import Qt

from .editor_tab import EditorTab
from .output_tab import OutputTab
from .dialogs import AboutDialog, confirm_exit
from .i18n import Translator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.tr = self.translator.tr

        self.m_file = None
        self.m_edit = None
        self.m_view = None
        self.m_text = None
        self.m_pusk = None
        self.m_help = None
        self.m_lang = None

        self.text_actions = []
        self.text_menu_items = [
            "Постановка задачи",
            "Грамматика",
            "Классификация грамматики",
            "Методология анализа",
            "Тестовый пример",
            "Список литературы",
            "Исходный код программы",
        ]

        self.current_encoding = "UTF-8"

        self.setWindowTitle(self.tr("Текстовый редактор"))
        self.resize(1100, 750)

        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()

        self.retranslate()

        self.tabs_editor.currentChanged.connect(self.on_tab_changed)
        self.add_new_tab()


    def on_tab_changed(self, index):
        self.update_cursor_position()


    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(4)

        self.tabs_editor = QTabWidget()
        self.tabs_editor.setTabsClosable(True)
        self.tabs_editor.tabCloseRequested.connect(self.close_tab)

        self.tabs_output = QTabWidget()
        self.output_tab = OutputTab("Результаты", table=False, tr=self.tr)
        self.errors_tab = OutputTab("Ошибки", table=True, tr=self.tr)

        self.tabs_output.addTab(self.output_tab, self.tr("Результаты"))
        self.tabs_output.addTab(self.errors_tab, self.tr("Ошибки"))

        splitter.addWidget(self.tabs_editor)
        splitter.addWidget(self.tabs_output)
        splitter.setSizes([500, 220])

        layout.addWidget(splitter)


    def _create_actions(self):
        self.act_new = QAction(self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self.add_new_tab)

        self.act_open = QAction(self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self.open_file)

        self.act_save = QAction(self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self.save_file)

        self.act_save_as = QAction(self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self.save_file_as)

        self.act_undo = QAction(self)
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)

        self.act_redo = QAction(self)
        self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)

        self.act_cut = QAction(self)
        self.act_cut.setShortcut(QKeySequence.StandardKey.Cut)

        self.act_copy = QAction(self)
        self.act_copy.setShortcut(QKeySequence.StandardKey.Copy)

        self.act_paste = QAction(self)
        self.act_paste.setShortcut(QKeySequence.StandardKey.Paste)

        self.act_run = QAction(self)
        self.act_run.setShortcut("F5")
        self.act_run.triggered.connect(self.run_analysis)

        self.act_about = QAction(self)
        self.act_about.triggered.connect(self.show_about)

        self.act_help = QAction(self)
        self.act_help.triggered.connect(self.show_help)

        self.act_font_inc = QAction(self)
        self.act_font_inc.setShortcut("Ctrl++")
        self.act_font_inc.triggered.connect(lambda: self.change_font_size(2))

        self.act_font_dec = QAction(self)
        self.act_font_dec.setShortcut("Ctrl+-")
        self.act_font_dec.triggered.connect(lambda: self.change_font_size(-2))

        self.act_lang_ru = QAction(self)
        self.act_lang_ru.triggered.connect(lambda: self.set_language("ru"))

        self.act_lang_en = QAction(self)
        self.act_lang_en.triggered.connect(lambda: self.set_language("en"))


    def _create_menus(self):
        mb = self.menuBar()

        self.m_file = mb.addMenu(self.tr("Файл"))
        self.m_file.addAction(self.act_new)
        self.m_file.addAction(self.act_open)
        self.m_file.addAction(self.act_save)
        self.m_file.addAction(self.act_save_as)
        self.m_file.addSeparator()

        self.act_exit = QAction(self.tr("Выход"), self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        self.m_file.addAction(self.act_exit)

        self.m_edit = mb.addMenu(self.tr("Правка"))
        self.m_edit.addAction(self.act_undo)
        self.m_edit.addAction(self.act_redo)
        self.m_edit.addSeparator()
        self.m_edit.addAction(self.act_cut)
        self.m_edit.addAction(self.act_copy)
        self.m_edit.addAction(self.act_paste)

        self.m_view = mb.addMenu(self.tr("Вид"))
        self.m_view.addAction(self.act_font_inc)
        self.m_view.addAction(self.act_font_dec)

        self.m_text = mb.addMenu(self.tr("Текст"))
        for item_text in self.text_menu_items:
            act = QAction(self.tr(item_text), self)
            self.text_actions.append(act)
            self.m_text.addAction(act)

        self.m_pusk = mb.addMenu(self.tr("Пуск"))
        self.m_pusk.addAction(self.act_run)

        self.m_help = mb.addMenu(self.tr("Справка"))
        self.m_help.addAction(self.act_help)
        self.m_help.addAction(self.act_about)

        self.m_lang = mb.addMenu(self.tr("Язык"))
        self.m_lang.addAction(self.act_lang_ru)
        self.m_lang.addAction(self.act_lang_en)


    def _create_toolbar(self):
        toolbar = QToolBar("Основные действия")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(toolbar)

        style = self.style()

        act_new = QAction(
            QIcon.fromTheme("document-new", style.standardIcon(style.StandardPixmap.SP_FileIcon)),
            "", self
        )
        act_new.setToolTip(self.tr("Создать новый документ"))
        act_new.triggered.connect(lambda: self.add_new_tab())
        toolbar.addAction(act_new)

        act_open = QAction(
            QIcon.fromTheme("document-open", style.standardIcon(style.StandardPixmap.SP_DirOpenIcon)),
            "", self
        )
        act_open.setToolTip(self.tr("Открыть файл"))
        act_open.triggered.connect(self.open_file)
        toolbar.addAction(act_open)

        act_save = QAction(
            QIcon.fromTheme("document-save", style.standardIcon(style.StandardPixmap.SP_DialogSaveButton)),
            "", self
        )
        act_save.setToolTip(self.tr("Сохранить"))
        act_save.triggered.connect(self.save_file)
        toolbar.addAction(act_save)

        act_save_as = QAction(
            QIcon.fromTheme("document-save-as", style.standardIcon(style.StandardPixmap.SP_FileDialogNewFolder)),
            "", self
        )
        act_save_as.setToolTip(self.tr("Сохранить как"))
        act_save_as.triggered.connect(self.save_file_as)
        toolbar.addAction(act_save_as)

        toolbar.addSeparator()

        act_undo = QAction(QIcon.fromTheme("edit-undo"), "", self)
        act_undo.setToolTip(self.tr("Отменить"))
        act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        act_undo.triggered.connect(lambda: self.current_editor_tab().editor.undo() if self.current_editor_tab() else None)
        toolbar.addAction(act_undo)

        act_redo = QAction(QIcon.fromTheme("edit-redo"), "", self)
        act_redo.setToolTip(self.tr("Повторить"))
        act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        act_redo.triggered.connect(lambda: self.current_editor_tab().editor.redo() if self.current_editor_tab() else None)
        toolbar.addAction(act_redo)

        toolbar.addSeparator()

        act_cut = QAction(QIcon.fromTheme("edit-cut"), "", self)
        act_cut.setToolTip(self.tr("Вырезать"))
        act_cut.setShortcut(QKeySequence.StandardKey.Cut)
        act_cut.triggered.connect(lambda: self.current_editor_tab().editor.cut() if self.current_editor_tab() else None)
        toolbar.addAction(act_cut)

        act_copy = QAction(QIcon.fromTheme("edit-copy"), "", self)
        act_copy.setToolTip(self.tr("Копировать"))
        act_copy.setShortcut(QKeySequence.StandardKey.Copy)
        act_copy.triggered.connect(lambda: self.current_editor_tab().editor.copy() if self.current_editor_tab() else None)
        toolbar.addAction(act_copy)

        act_paste = QAction(QIcon.fromTheme("edit-paste"), "", self)
        act_paste.setToolTip(self.tr("Вставить"))
        act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        act_paste.triggered.connect(lambda: self.current_editor_tab().editor.paste() if self.current_editor_tab() else None)
        toolbar.addAction(act_paste)

        toolbar.addSeparator()

        act_run = QAction(
            QIcon.fromTheme("media-playback-start", style.standardIcon(style.StandardPixmap.SP_MediaPlay)),
            "", self
        )
        act_run.setToolTip(self.tr("Запустить синтаксический анализатор"))
        act_run.setShortcut("F5")
        act_run.triggered.connect(self.run_analysis)
        toolbar.addAction(act_run)

        toolbar.addSeparator()

        act_help = QAction(
            QIcon.fromTheme("help-contents", style.standardIcon(style.StandardPixmap.SP_DialogHelpButton)),
            "", self
        )
        act_help.setToolTip(self.tr("Справка / руководство пользователя"))
        act_help.triggered.connect(self.show_help)
        toolbar.addAction(act_help)

        act_about = QAction(
            QIcon.fromTheme("help-about", style.standardIcon(style.StandardPixmap.SP_MessageBoxInformation)),
            "", self
        )
        act_about.setToolTip(self.tr("О программе"))
        act_about.triggered.connect(self.show_about)
        toolbar.addAction(act_about)


    def _create_statusbar(self):
        self.statusBar().showMessage(self.tr("Готов"))

        self.cursor_pos_label = QLabel(self.tr("Строка 1 : 1"))
        self.encoding_label   = QLabel(self.current_encoding)
        self.mode_label       = QLabel(self.tr("Вставка"))
        self.stats_label      = QLabel(self.tr("0 симв. | 0 слов"))

        self.statusBar().addPermanentWidget(self.cursor_pos_label)
        self.statusBar().addPermanentWidget(self.encoding_label)
        self.statusBar().addPermanentWidget(self.mode_label)
        self.statusBar().addPermanentWidget(self.stats_label)


    def update_cursor_position(self):
        if not self.current_editor_tab():
            self.cursor_pos_label.setText(self.tr("Нет документа"))
            self.stats_label.setText("—")
            return

        editor = self.current_editor_tab().editor
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col  = cursor.columnNumber() + 1

        mode_ru = self.tr("Замена") if editor.overwriteMode() else self.tr("Вставка")

        self.cursor_pos_label.setText(
            f"{self.tr('Строка')} {line} : {col}"
        )
        self.mode_label.setText(mode_ru)

        text = editor.toPlainText()
        chars = len(text)
        words = len(text.split())
        self.stats_label.setText(
            f"{chars} {self.tr('симв.')} | {words} {self.tr('слов')}"
        )


    def retranslate(self):
        self.setWindowTitle(self.tr("Текстовый редактор"))

        if self.m_file:
            self.m_file.setTitle(self.tr("Файл"))
        if self.m_edit:
            self.m_edit.setTitle(self.tr("Правка"))
        if self.m_view:
            self.m_view.setTitle(self.tr("Вид"))
        if self.m_text:
            self.m_text.setTitle(self.tr("Текст"))
            for i, act in enumerate(self.text_actions):
                act.setText(self.tr(self.text_menu_items[i]))
        if self.m_pusk:
            self.m_pusk.setTitle(self.tr("Пуск"))
        if self.m_help:
            self.m_help.setTitle(self.tr("Справка"))
        if self.m_lang:
            self.m_lang.setTitle(self.tr("Язык"))

        self.act_new.setText(self.tr("Создать"))
        self.act_open.setText(self.tr("Открыть"))
        self.act_save.setText(self.tr("Сохранить"))
        self.act_save_as.setText(self.tr("Сохранить как"))
        self.act_exit.setText(self.tr("Выход"))

        self.act_undo.setText(self.tr("Отменить"))
        self.act_redo.setText(self.tr("Повторить"))
        self.act_cut.setText(self.tr("Вырезать"))
        self.act_copy.setText(self.tr("Копировать"))
        self.act_paste.setText(self.tr("Вставить"))

        self.act_font_inc.setText(self.tr("Увеличить шрифт"))
        self.act_font_dec.setText(self.tr("Уменьшить шрифт"))

        self.act_lang_ru.setText(self.tr("Русский"))
        self.act_lang_en.setText(self.tr("English"))

        self.act_help.setText(self.tr("Справка"))
        self.act_about.setText(self.tr("О программе"))

        self.tabs_output.setTabText(0, self.tr("Результаты"))
        self.tabs_output.setTabText(1, self.tr("Ошибки"))

        if hasattr(self, 'errors_tab') and self.errors_tab.is_table:
            headers = [
                self.tr("Строка"),
                self.tr("Позиция"),
                self.tr("Сообщение")
            ]
            self.errors_tab.table.setHorizontalHeaderLabels(headers)

        for i in range(self.tabs_editor.count()):
            tab = self.tabs_editor.widget(i)
            title = getattr(tab, 'filename', None) or self.tr("Новый файл")
            if getattr(tab, 'modified', False):
                title += " *"
            self.tabs_editor.setTabText(i, title)

        self.statusBar().showMessage(self.tr("Готов"))
        self.update_cursor_position()

    def set_language(self, lang):
        self.translator.set_language(lang)
        self.retranslate()


    def add_new_tab(self, filename=None, content=""):
        tab = EditorTab(filename, content)
        title = filename or self.tr("Новый файл")
        idx = self.tabs_editor.addTab(tab, title)
        self.tabs_editor.setCurrentIndex(idx)

        tab.editor.cursorPositionChanged.connect(self.update_cursor_position)
        tab.editor.textChanged.connect(self.update_cursor_position)

        self.update_cursor_position()


    def current_editor_tab(self):
        return self.tabs_editor.currentWidget()


    def close_tab(self, index):
        tab = self.tabs_editor.widget(index)
        if getattr(tab, 'modified', False):
            reply = QMessageBox.question(
                self,
                self.tr("Сохранить?"),
                self.tr("Сохранить изменения?"),
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            if reply == QMessageBox.StandardButton.Cancel:
                return

        self.tabs_editor.removeTab(index)


    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Открыть файл"), "", "Все файлы (*);;Текстовые файлы (*.txt *.lang)"
        )
        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                self.add_new_tab(path, content)
            except Exception as e:
                QMessageBox.warning(self, self.tr("Ошибка"), f"{self.tr('Не удалось открыть файл')}:\n{e}")


    def save_file(self):
        tab = self.current_editor_tab()
        if not tab:
            return

        filename = getattr(tab, 'filename', None)
        if not filename:
            filename, _ = QFileDialog.getSaveFileName(
                self, self.tr("Сохранить файл"), "", "Все файлы (*)"
            )
            if not filename:
                return
            tab.filename = filename

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(tab.get_text())
            tab.modified = False
            self.retranslate()
        except Exception as e:
            QMessageBox.warning(self, self.tr("Ошибка"), f"{self.tr('Не удалось сохранить')}:\n{e}")


    def save_file_as(self):
        tab = self.current_editor_tab()
        if not tab:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, self.tr("Сохранить файл как"), "", "Все файлы (*)"
        )
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(tab.get_text())
            tab.filename = filename
            tab.modified = False
            idx = self.tabs_editor.currentIndex()
            title = filename or self.tr("Новый файл")
            self.tabs_editor.setTabText(idx, title)
            self.retranslate()
        except Exception as e:
            QMessageBox.warning(self, self.tr("Ошибка"), f"{self.tr('Не удалось сохранить')}:\n{e}")


    def change_font_size(self, delta):
        tab = self.current_editor_tab()
        if tab and hasattr(tab, 'scale_font'):
            tab.scale_font(delta)

        current_output = self.tabs_output.currentWidget()
        if current_output and hasattr(current_output, 'scale_font'):
            current_output.scale_font(delta)


    def run_analysis(self):
        tab = self.current_editor_tab()
        if not tab:
            return

        self.output_tab.clear()
        self.errors_tab.clear()

        text = tab.get_text()

        self.output_tab.append_text(self.tr("Исходный код:") + "\n" + "=" * 50)
        preview = text[:500] + "..." if len(text) > 500 else text
        self.output_tab.append_text(preview)
        self.output_tab.append_text("=" * 50)

        self.output_tab.append_text("\n" + self.tr("Анализ завершён"))

        self.statusBar().showMessage(self.tr("Анализ завершён"), 5000)


    def show_about(self):
        AboutDialog(self).exec()


    def show_help(self):
        QMessageBox.information(
            self,
            self.tr("Справка"),
            self.tr("Учебный редактор для языкового процессора.\nПока — базовый функционал. В будущем добавится парсер.")
        )


    def closeEvent(self, event):
        has_modified = any(
            getattr(self.tabs_editor.widget(i), 'modified', False)
            for i in range(self.tabs_editor.count())
        )
        if has_modified:
            if not confirm_exit(self):
                event.ignore()
                return
        event.accept()


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                try:
                    with open(path, encoding="utf-8") as f:
                        content = f.read()
                    self.add_new_tab(path, content)
                except Exception:
                    pass