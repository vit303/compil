from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt
import sys

from app.main_window import MainWindow


def setup_dark_theme(app: QApplication):
    app.setStyle("Fusion")

    palette = QPalette()

    bg_color = QColor(30, 30, 30)
    base_color = QColor(45, 45, 45) 
    text_color = QColor(230, 230, 230)
    disabled_text = QColor(110, 110, 110)
    highlight_color = QColor(0, 120, 215)
    link_color = QColor(100, 180, 255)

    palette.setColor(QPalette.ColorRole.Window, bg_color)
    palette.setColor(QPalette.ColorRole.WindowText, text_color)
    palette.setColor(QPalette.ColorRole.Base, base_color)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(55, 55, 55))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
    palette.setColor(QPalette.ColorRole.Text, text_color)
    palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Link, link_color)
    palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_text)

    app.setPalette(palette)

    app.setStyleSheet("""
        QMainWindow, QDialog, QWidget {
            background-color: #1e1e1e;
            color: #e6e6e6;
        }
        QMenuBar {
            background-color: #252525;
            color: #e6e6e6;
        }
        QMenuBar::item:selected {
            background-color: #0d6efd;
        }
        QMenu {
            background-color: #2d2d2d;
            border: 1px solid #444444;
        }
        QMenu::item:selected {
            background-color: #0d6efd;
            color: white;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #1e1e1e;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            border: 1px solid #444;
            padding: 6px 12px;
        }
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom: 2px solid #0d6efd;
        }
        QPlainTextEdit, QTextEdit, QTableWidget, QTableView {
            background-color: #2b2b2b;
            border: 1px solid #444;
            selection-background-color: #0d6efd;
            selection-color: white;
        }
        QTableWidget {
            gridline-color: #555;
        }
        QStatusBar {
            background-color: #252525;
            color: #e6e6e6;
        }
        QToolBar {
            background-color: #252525;
            border-bottom: 1px solid #444;
        }
        QLineEdit {
            background-color: #3c3c3c;
            border: 1px solid #555;
            color: #e6e6e6;
        }
    """)

def main():
    app = QApplication(sys.argv)
    
    setup_dark_theme(app)

    font = QFont("Segoe UI", 10)
    if sys.platform == "win32":
        font = QFont("Segoe UI", 10)
    elif sys.platform == "darwin":
        font = QFont("SF Pro", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()