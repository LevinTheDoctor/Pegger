from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from pathlib import Path
from DragAndDropArea import DragAndDropArea


class PeggerUI(QWidget):
    format_compatibility = {
        "PNG": ["JPG", "WEBP", "BMP"],
        "JPG": ["PNG", "WEBP"],
        "WEBP": ["PNG", "JPG"]
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pegger")
        self.resize(400, 700)

        with open("PeggerUIStyle.qss", "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.current_format = None

        main_vbox = QVBoxLayout()

        self.drag_and_drop_area = DragAndDropArea(self)
        self.drag_and_drop_area.image_loaded.connect(self.on_image_loaded)
        main_vbox.addWidget(self.drag_and_drop_area)

        # Format-Auswahl
        format_hbox = QHBoxLayout()
        format_hbox.addWidget(QLabel("Aktuelles Format:"))
        self.format_label = QLabel("Keine Datei geladen")
        format_hbox.addWidget(self.format_label)

        format_hbox.addWidget(QLabel("Formatieren In:"))
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(self.format_compatibility.keys())
        format_hbox.addWidget(self.format_combobox)

        main_vbox.addLayout(format_hbox)

        # Button-Bereich
        buttons_hbox = QHBoxLayout()
        buttons_hbox.addWidget(QPushButton("Zuentfernende Farbe"))
        buttons_hbox.addWidget(QPushButton("Formatieren"))
        main_vbox.addLayout(buttons_hbox)

        self.setLayout(main_vbox)

    def on_image_loaded(self, file_path):
        # Erkenne das Format aus der Dateiendung
        file_extension = Path(file_path).suffix.upper().lstrip(".")

        if file_extension == "JPEG":
            file_extension = "JPG"

        self.current_format = file_extension

        # Aktualisiere das Format-Label
        self.format_label.setText(file_extension)

        # Aktualisiere die ComboBox
        if file_extension in self.format_compatibility:
            self.format_combobox.clear()
            self.format_combobox.addItems(self.format_compatibility[file_extension])