
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class PeggerUIMain(QWidget):

    format_compatibility = {
        "PNG": ["JPG", "WEBP", "BMP"],
        "JPG": ["PNG", "WEBP"],
        "WEBP": ["PNG", "JPG"]
    }

    def __init__(self):
        super().__init__(self)
        self.setWindowTitle("Pegger")
        self.resize(400,700)


        with open("PeggerUIStyle.qss", "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.current_format = None

        main_vbox = QVBoxLayout()

        drag_and_drop_vbox = QVBoxLayout()


        main_vbox.addLayout(drag_and_drop_vbox)

        menu_vbox = QVBoxLayout()
        # Aktuelles Format
        format_hbox = QHBoxLayout()
        format_hbox.addWidget(QLabel("Format:" + self.current_format))

        # Formate Combo Box mit label
        format_hbox.addWidget(QLabel("Formatieren In:"))
        format_combobox = QComboBox()
        format_combobox.addItems(self.format_compatibility[self.current_format])
        format_hbox.addWidget(format_combobox)

        menu_vbox.addLayout(format_hbox)
        # Button hbox
        buttons_hbox = QHBoxLayout()

        buttons_hbox.addWidget(QPushButton("Zuentfernende Farbe"))
        buttons_hbox.addWidget(QPushButton("Formatieren"))

        # Layout wird Hinzugefuegt
        menu_vbox.addLayout(buttons_hbox)

        main_vbox.addLayout(menu_vbox)

        # Layout wird zum Widget hinzugefügt
        self.setLayout(main_vbox)






