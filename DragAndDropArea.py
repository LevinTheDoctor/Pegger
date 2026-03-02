from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import Signal
from PIL import Image
from pathlib import Path
import io


class DragAndDropArea(QFrame):
    image_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.current_image_path = None
        self.current_image = None

        # Das Layout enthält NUR das Label, nicht den Button
        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("Datei per Drag & Drop\noder Datei Suchen")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("DragAndDropArea")
        self.label.setMinimumHeight(300)
        vbox.addWidget(self.label)

        self.setLayout(vbox)
        self.setObjectName("dragAndDropContainer")


    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Bilddatei auswählen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.webp *.bmp);;Alle Dateien (*)"
        )

        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, file_path):
        try:
            pil_image = Image.open(file_path)
            self.current_image_path = file_path
            self.current_image = pil_image
            self.display_image()
            self.image_loaded.emit(file_path)
            return True
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            return False

    def display_image(self):
        if self.current_image is None:
            return

        try:
            if self.current_image.mode != "RGB":
                display_image = self.current_image.convert("RGB")
            else:
                display_image = self.current_image

            png_data = io.BytesIO()
            display_image.save(png_data, format="PNG")

            pixmap = QPixmap()
            pixmap.loadFromData(png_data.getvalue(), "PNG")

            scaled_pixmap = pixmap.scaledToHeight(300, Qt.TransformationMode.SmoothTransformation)

            self.label.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"Fehler beim Anzeigen des Bildes: {e}")
            self.show_placeholder_text()

    def show_placeholder_text(self):
        self.label.setText("Datei per Drag & Drop\noder Datei Suchen")
        self.label.setPixmap(QPixmap())

    def clear_image(self):
        self.current_image_path = None
        self.current_image = None
        self.show_placeholder_text()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Backspace:
            if self.current_image is not None:
                self.clear_image()
                print("Bild gelöscht")
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.load_image_from_path(files[0])