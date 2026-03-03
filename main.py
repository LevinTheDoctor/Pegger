import os
import sys

from PySide6.QtWidgets import QApplication
from PeggerUI import PeggerUI


def _setup_ffmpeg_path():
    """Binaries (ffmpeg/ffprobe) im PATH registrieren wenn die App gebundelt läuft."""
    if not getattr(sys, "frozen", False):
        return

    exe_dir = os.path.dirname(sys.executable)

    if sys.platform == "darwin":
        # py2app: .app/Contents/MacOS/Pegger → Resources liegt eine Ebene höher
        resources = os.path.normpath(os.path.join(exe_dir, "..", "Resources", "ffmpeg_bin"))
    else:
        # cx_Freeze / Windows: ffmpeg.exe liegt neben Pegger.exe
        resources = exe_dir

    if os.path.isdir(resources):
        os.environ["PATH"] = resources + os.pathsep + os.environ.get("PATH", "")


if __name__ == "__main__":
    _setup_ffmpeg_path()
    app = QApplication(sys.argv)
    window = PeggerUI()
    window.show()
    sys.exit(app.exec())
