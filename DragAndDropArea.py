from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class DragAndDropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.current_image_path = None
        self.current_image = None

        vbox = QVBoxLayout()

        self.label = QLabel("Datei per Drag & Drop\noder Datei Suchen")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("DragAndDropArea")
        vbox.addWidget(self.label)


        self.search_button = QPushButton("Suchen")
        self.search_button.setObjectName("dragDropButton")
        vbox.addWidget(self.search_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(vbox)
        self.setObjectName("dragAndDropContainer")
