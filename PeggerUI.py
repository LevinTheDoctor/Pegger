from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from pathlib import Path
from PIL import Image
import numpy as np
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
        self.resize(600, 800)

        with open("PeggerUIStyle.qss", "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.current_format = None

        main_vbox = QVBoxLayout()

        # Der "Suchen" Button AUSSERHALB der Box
        search_button = QPushButton("Suchen")
        search_button.setObjectName("searchButton")
        search_button.clicked.connect(self.open_file_dialog)
        main_vbox.addWidget(search_button)

        # Die DragAndDropArea mit nur dem Label und Umrandung
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
        color_removal_button = QPushButton("Zu entfernende Farbe")
        color_removal_button.clicked.connect(self.on_remove_color_clicked)
        buttons_hbox.addWidget(color_removal_button)
        buttons_hbox.addWidget(QPushButton("Formatieren"))
        main_vbox.addLayout(buttons_hbox)

        self.setLayout(main_vbox)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Bilddatei auswählen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.webp *.bmp);;Alle Dateien (*)"
        )

        if file_path:
            self.drag_and_drop_area.load_image_from_path(file_path)

    def on_image_loaded(self, file_path):
        file_extension = Path(file_path).suffix.upper().lstrip(".")

        if file_extension == "JPEG":
            file_extension = "JPG"

        self.current_format = file_extension
        self.format_label.setText(file_extension)

        if file_extension in self.format_compatibility:
            self.format_combobox.clear()
            self.format_combobox.addItems(self.format_compatibility[file_extension])

    def on_remove_color_clicked(self):
        """Wird aufgerufen, wenn 'Farbe entfernen' geklickt wird"""
        if self.drag_and_drop_area.current_image is None:
            QMessageBox.warning(self, "Fehler", "Erst ein Bild laden!")
            return

        # Aktiviere den Color Picker
        self.drag_and_drop_area.activate_color_picker()
        QMessageBox.information(self, "Color Picker", "Klicke auf das Bild, um eine Farbe auszuwählen!")

        # Verbinde das Signal mit einer Methode
        try:
            self.drag_and_drop_area.color_picked.disconnect()  # Trenne alte Verbindungen
        except RuntimeError:
            pass  # Keine Verbindung vorhanden
        self.drag_and_drop_area.color_picked.connect(self.on_color_picked)

    def on_color_picked(self, color):
        """Wird aufgerufen, wenn eine Farbe ausgewählt wurde"""
        try:
            img = self.drag_and_drop_area.current_image.convert("RGBA")
            data = np.array(img, dtype=np.int16)

            r, g, b = color
            tolerance = 30

            mask = (
                (np.abs(data[:, :, 0] - r) <= tolerance) &
                (np.abs(data[:, :, 1] - g) <= tolerance) &
                (np.abs(data[:, :, 2] - b) <= tolerance)
            )
            data[mask] = [0, 0, 0, 0]  # Transparent

            result_image = Image.fromarray(data.astype(np.uint8), "RGBA")
            self.drag_and_drop_area.current_image = result_image
            self.drag_and_drop_area.display_image()

            QMessageBox.information(self, "Erfolg", f"Farbe RGB{color} wurde entfernt!")

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler: {str(e)}")