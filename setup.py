import subprocess
from setuptools import setup

APP = ["main.py"]

# FFmpeg-Pfade zur Build-Zeit ermitteln (Homebrew)
_ffmpeg  = subprocess.run(["which", "ffmpeg"],  capture_output=True, text=True).stdout.strip()
_ffprobe = subprocess.run(["which", "ffprobe"], capture_output=True, text=True).stdout.strip()

DATA_FILES = [
    ("", ["PeggerUIStyle.qss"]),
    ("ffmpeg_bin", [_ffmpeg, _ffprobe]),
]

OPTIONS = {
    "iconfile": "MyIcon.icns",
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
    "plist": {
        "CFBundleName": "Pegger",
        "CFBundleDisplayName": "Pegger",
        "CFBundleIdentifier": "com.pegger.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "Image",
                "CFBundleTypeRole": "Editor",
                "LSItemContentTypes": [
                    "public.png",
                    "public.jpeg",
                    "public.bmp",
                    "org.webmproject.webp",
                ],
            }
        ],
    },
}

setup(
    name="Pegger",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
