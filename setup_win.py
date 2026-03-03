"""
Windows-Build mit cx_Freeze
============================
Voraussetzungen:
  pip install cx_Freeze

FFmpeg-Binaries:
  ffmpeg.exe und ffprobe.exe müssen im Projektordner liegen.
  Download: https://www.gyan.dev/ffmpeg/builds/  (ffmpeg-release-essentials.zip)
  → ffmpeg.exe und ffprobe.exe aus dem bin/-Ordner ins Projektverzeichnis kopieren.

Build starten:
  python setup_win.py build
"""

import sys
from cx_Freeze import setup, Executable

BUILD_OPTIONS = {
    "packages": [
        "PySide6",
        "numpy",
        "vtracer",
    ],
    "includes": [
        "PeggerUI",
        "DragAndDropArea",
        "ConvertingFunctions",
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtSvg",
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "email",
        "html",
        "http",
        "urllib",
        "xmlrpc",
    ],
    "include_files": [
        ("PeggerUIStyle.qss", "PeggerUIStyle.qss"),
        # ffmpeg-Binaries – neben Pegger.exe ablegen, main.py ergänzt den PATH automatisch
        ("ffmpeg.exe",  "ffmpeg.exe"),
        ("ffprobe.exe", "ffprobe.exe"),
    ],
    "silent": True,
}

setup(
    name="Pegger",
    version="1.0.0",
    options={"build_exe": BUILD_OPTIONS},
    executables=[
        Executable(
            "main.py",
            base="Win32GUI",      # Kein Konsolenfenster
            icon="MyIcon.ico",    # Windows-App-Icon
            target_name="Pegger.exe",
        )
    ],
)
