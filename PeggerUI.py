from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from pathlib import Path
from DragAndDropArea import DragAndDropArea
import ConvertingFunctions


class PeggerUI(QWidget):
    format_compatibility = {
        "PNG":  ["PNG", "JPG", "WEBP", "BMP", "SVG", "ICO", "ICNS"],
        "JPG":  ["PNG", "WEBP", "BMP", "ICO"],
        "WEBP": ["PNG", "JPG", "BMP", "SVG", "ICO", "ICNS"],
    }

    format_extensions = {
        "PNG": "*.png",
        "JPG": "*.jpg",
        "WEBP": "*.webp",
        "BMP": "*.bmp",
        "SVG": "*.svg",
        "ICO": "*.ico",
        "ICNS": "*.icns",
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

        search_button = QPushButton("Suchen")
        search_button.setObjectName("searchButton")
        search_button.clicked.connect(self.open_file_dialog)
        main_vbox.addWidget(search_button)

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

        # Buttons
        buttons_hbox = QHBoxLayout()
        color_removal_button = QPushButton("Zu entfernende Farbe")
        color_removal_button.clicked.connect(self.on_remove_color_clicked)
        buttons_hbox.addWidget(color_removal_button)

        convert_button = QPushButton("Formatieren")
        convert_button.clicked.connect(self.on_convert_clicked)
        buttons_hbox.addWidget(convert_button)

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
        if self.drag_and_drop_area.current_image is None:
            QMessageBox.warning(self, "Fehler", "Erst ein Bild laden!")
            return

        self.drag_and_drop_area.activate_color_picker()

        try:
            self.drag_and_drop_area.color_picked.disconnect()
        except RuntimeError:
            pass
        self.drag_and_drop_area.color_picked.connect(self.on_color_picked)

    def on_color_picked(self, color):
        try:
            result = ConvertingFunctions.remove_color(
                self.drag_and_drop_area.current_image,
                color,
                tolerance=30
            )
            self.drag_and_drop_area.current_image = result
            self.drag_and_drop_area.display_image()
            QMessageBox.information(self, "Erfolg", f"Farbe RGB{color} wurde entfernt!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def on_convert_clicked(self):
        if self.drag_and_drop_area.current_image is None:
            QMessageBox.warning(self, "Fehler", "Erst ein Bild laden!")
            return

        target_format = self.format_combobox.currentText()
        ext = self.format_extensions.get(target_format, f"*.{target_format.lower()}")
        filter_str = f"{target_format}-Datei ({ext});;Alle Dateien (*)"

        default_name = ""
        if self.drag_and_drop_area.current_image_path:
            stem = Path(self.drag_and_drop_area.current_image_path).stem
            default_name = f"{stem}.{target_format.lower()}"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Bild speichern",
            default_name,
            filter_str
        )

        if not save_path:
            return

        try:
            ConvertingFunctions.save_image(
                self.drag_and_drop_area.current_image,
                save_path,
                target_format
            )
            QMessageBox.information(self, "Erfolg", f"Gespeichert als {target_format}:\n{save_path}")
        except ImportError as e:
            QMessageBox.warning(self, "Fehlende Abhängigkeit", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
