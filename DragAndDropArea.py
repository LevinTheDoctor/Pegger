from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import Signal
from PIL import Image
from pathlib import Path
import io


class DragAndDropArea(QFrame):
    image_loaded = Signal(str)
    color_picked = Signal(tuple)  # Neues Signal für die ausgewählte Farbe

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.current_image_path = None
        self.current_image = None
        self.is_color_picker_active = False  # Flag, ob wir gerade eine Farbe auswählen

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
        """Aktiviere den Color Picker Modus"""
        if self.current_image is None:
            return False

        self.is_color_picker_active = True

        self.setCursor(Qt.CursorShape.CrossCursor)
        return True

    def deactivate_color_picker(self):
        """Deaktiviere den Color Picker Modus"""
        self.is_color_picker_active = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        """Wird aufgerufen, wenn der Nutzer klickt"""
        if not self.is_color_picker_active or self.current_image is None:
            return

        # Berechne die Position des Klicks relativ zum Label
        label_pos = self.label.mapFromGlobal(event.globalPos())

        # Prüfe, ob der Klick im Label war
        if not self.label.rect().contains(label_pos):
            return

        # Berechne die Position im Original-Bild
        # Das Label ist skaliert, also musst du die Koordinaten anpassen
        label_width = self.label.width()
        label_height = self.label.height()

        # Hole die Größe des aktuellen Pixmaps (das skalierte Bild)
        if self.label.pixmap() is None:
            return

        pixmap = self.label.pixmap()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # Berechne, wo das Pixmap im Label positioniert ist (zentriert)
        x_offset = (label_width - pixmap_width) // 2
        y_offset = (label_height - pixmap_height) // 2

        # Berechne die Position im skaliertem Bild
        x_in_pixmap = label_pos.x() - x_offset
        y_in_pixmap = label_pos.y() - y_offset

        # Prüfe, ob der Klick im Bild-Bereich war
        if x_in_pixmap < 0 or y_in_pixmap < 0 or x_in_pixmap >= pixmap_width or y_in_pixmap >= pixmap_height:
            return

        # Skaliere die Koordinaten zum Original-Bild
        scale_x = self.current_image.width / pixmap_width
        scale_y = self.current_image.height / pixmap_height

        x_in_original = int(x_in_pixmap * scale_x)
        y_in_original = int(y_in_pixmap * scale_y)

        # Lese die Pixel-Farbe aus dem Original-Bild
        try:
            color = self.current_image.getpixel((x_in_original, y_in_original))

            # Konvertiere zu RGB, falls das Bild einen Alpha-Kanal hat
            if isinstance(color, tuple) and len(color) == 4:
                color = color[:3]  # Nimm nur RGB, nicht Alpha
            elif isinstance(color, tuple) and len(color) == 3:
                pass  # Ist schon RGB
            else:
                # Ist vielleicht Grayscale, konvertiere zu RGB
                if isinstance(color, int):
                    color = (color, color, color)

            # Sende das Signal mit der Farbe
            self.color_picked.emit(color)

            # Deaktiviere den Color Picker
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