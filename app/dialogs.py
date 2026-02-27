from PyQt6.QtWidgets import QMessageBox


def AboutDialog(parent):
    msg = QMessageBox(parent)
    msg.setWindowTitle(parent.tr("О программе"))
    msg.setText(
        parent.tr("Языковой процессор v1.0\n"
                  "Пример реализации редактора кода на PyQt6")
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    return msg


def confirm_exit(parent):
    reply = QMessageBox.question(
        parent,
        parent.tr("Выход"),
        parent.tr("Вы действительно хотите выйти?"),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes