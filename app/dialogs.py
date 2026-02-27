from PyQt6.QtWidgets import QMessageBox


def AboutDialog(parent):
    msg = QMessageBox(parent)
    msg.setWindowTitle(parent.tr("О программе"))
    msg.setText(
        parent.tr("Учебный текстовый редактор с элементами языкового процессора\n"
                  "Разработан в рамках задания «Разработка пользовательского интерфейса (GUI) для языкового процессора»\n\n"
                  "Исходный код проекта:\n"
                  "https://github.com/vit303/compil\n\n"
                  )
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