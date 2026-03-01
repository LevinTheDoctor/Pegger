from PySide6.QtWidgets import QApplication
import sys
from PeggerUI import PeggerUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PeggerUI()
    window.show()
    sys.exit(app.exec())