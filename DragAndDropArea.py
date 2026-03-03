import subprocess

import numpy as np
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import Signal

import ConvertingFunctions


class DragAndDropArea(QFrame):
    image_loaded = Signal(str)
    color_picked = Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.current_image_path = None
        self.current_image: np.ndarray | None = None
        self.is_color_picker_active = False

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("Datei per Drag & Drop\noder Datei Suchen")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("DragAndDropArea")
        self.label.setMinimumHeight(300)
        vbox.addWidget(self.label)

        self.setLayout(vbox)
        self.setObjectName("dragAndDropContainer")

    def activate_color_picker(self):
        if self.current_image is None:
            return False
        self.is_color_picker_active = True
        self.setCursor(Qt.CursorShape.CrossCursor)
        return True

    def deactivate_color_picker(self):
        self.is_color_picker_active = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        if not self.is_color_picker_active or self.current_image is None:
            return

        label_pos = self.label.mapFromGlobal(event.globalPos())
        if not self.label.rect().contains(label_pos):
            return

        pixmap = self.label.pixmap()
        if pixmap is None:
            return

        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        x_offset = (self.label.width() - pixmap_width) // 2
        y_offset = (self.label.height() - pixmap_height) // 2

        x_in_pixmap = label_pos.x() - x_offset
        y_in_pixmap = label_pos.y() - y_offset

        if x_in_pixmap < 0 or y_in_pixmap < 0 or x_in_pixmap >= pixmap_width or y_in_pixmap >= pixmap_height:
            return

        img_h, img_w = self.current_image.shape[:2]
        x_orig = int(x_in_pixmap * img_w / pixmap_width)
        y_orig = int(y_in_pixmap * img_h / pixmap_height)

        try:
            pixel = self.current_image[y_orig, x_orig]
            color = (int(pixel[0]), int(pixel[1]), int(pixel[2]))
            self.color_picked.emit(color)
            self.deactivate_color_picker()
            print(f"Farbe ausgewählt: RGB{color}")
        except Exception as e:
            print(f"Fehler beim Auslesen der Pixel-Farbe: {e}")

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
            arr = ConvertingFunctions.load_image(file_path)
            self.current_image_path = file_path
            self.current_image = arr
            self.display_image()
            self.image_loaded.emit(file_path)
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg-Fehler beim Laden: {e.stderr.decode() if e.stderr else e}")
            return False
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            return False

    def display_image(self):
        if self.current_image is None:
            return
        try:
            h, w = self.current_image.shape[:2]
            q_image = QImage(self.current_image.tobytes(), w, h, w * 4, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(q_image)
            scaled = pixmap.scaledToHeight(300, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(scaled)
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
