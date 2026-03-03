import os
import struct
import subprocess
import tempfile
import numpy as np


# ---------------------------------------------------------------------------
# FFmpeg-Hilfsfunktionen
# ---------------------------------------------------------------------------

def load_image(path: str) -> np.ndarray:
    """Lädt ein Bild via FFmpeg als RGBA-Numpy-Array (H, W, 4)."""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True
    )
    w, h = map(int, probe.stdout.strip().split(","))

    result = subprocess.run(
        ["ffmpeg", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgba", "-v", "error", "pipe:1"],
        capture_output=True, check=True
    )
    return np.frombuffer(result.stdout, dtype=np.uint8).reshape((h, w, 4)).copy()


def _to_temp_png(image: np.ndarray, tmp_dir: str, name: str = "source.png") -> str:
    """Speichert ein RGBA-Array als PNG in ein temporäres Verzeichnis."""
    h, w = image.shape[:2]
    path = os.path.join(tmp_dir, name)
    result = subprocess.run(
        ["ffmpeg", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgba", "-video_size", f"{w}x{h}",
         "-i", "pipe:0", "-vcodec", "png", path],
        input=image.tobytes(), capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg-Fehler (PNG-Zwischendatei):\n{result.stderr.decode()}")
    return path


# ---------------------------------------------------------------------------
# Bildoperationen
# ---------------------------------------------------------------------------

def remove_color(image: np.ndarray, color: tuple, tolerance: int = 30) -> np.ndarray:
    """Entfernt eine Farbe (mit Toleranz) und macht sie transparent."""
    img = image.copy()
    data = img.astype(np.int16)
    r, g, b = color
    mask = (
        (np.abs(data[:, :, 0] - r) <= tolerance) &
        (np.abs(data[:, :, 1] - g) <= tolerance) &
        (np.abs(data[:, :, 2] - b) <= tolerance)
    )
    img[mask] = [0, 0, 0, 0]
    return img


def _flatten_alpha(image: np.ndarray) -> np.ndarray:
    """Legt ein RGBA-Array auf weißem Hintergrund ab (für Formate ohne Alpha)."""
    alpha = image[:, :, 3:4].astype(np.float32) / 255.0
    rgb = image[:, :, :3].astype(np.float32)
    white = np.full_like(rgb, 255.0)
    return (rgb * alpha + white * (1.0 - alpha)).astype(np.uint8)


# ---------------------------------------------------------------------------
# Speichern
# ---------------------------------------------------------------------------

def save_image(image: np.ndarray, path: str, target_format: str):
    """Speichert ein RGBA-Array im Zielformat via FFmpeg."""
    fmt = target_format.upper()

    if fmt == "SVG":
        _save_as_svg(image, path)
        return
    if fmt == "ICO":
        _save_as_ico(image, path)
        return
    if fmt == "ICNS":
        _save_as_icns(image, path)
        return

    codec_map = {
        "PNG":  ("rgba",  "png"),
        "JPG":  ("rgb24", "mjpeg"),
        "WEBP": ("rgba",  "libwebp"),
        "BMP":  ("rgb24", "bmp"),
    }
    pix_fmt, vcodec = codec_map[fmt]

    if fmt in ("JPG", "BMP"):
        arr = _flatten_alpha(image)   # (H, W, 3) RGB
    else:
        arr = image                   # (H, W, 4) RGBA

    h, w = arr.shape[:2]
    result = subprocess.run(
        ["ffmpeg", "-y",
         "-f", "rawvideo", "-pix_fmt", pix_fmt, "-video_size", f"{w}x{h}",
         "-i", "pipe:0",
         "-vcodec", vcodec,
         path],
        input=arr.tobytes(), capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg-Fehler:\n{result.stderr.decode()}")


def _save_as_ico(image: np.ndarray, path: str):
    """Erstellt eine Windows-ICO-Datei mit mehreren Größen via FFmpeg."""
    sizes = [16, 32, 48, 64, 128, 256]

    with tempfile.TemporaryDirectory() as tmp_dir:
        src = _to_temp_png(image, tmp_dir)

        png_chunks = []
        for size in sizes:
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", src,
                 "-vf", f"scale={size}:{size}:flags=lanczos",
                 "-f", "image2pipe", "-vcodec", "png", "pipe:1"],
                capture_output=True, check=True
            )
            png_chunks.append((size, result.stdout))

    # ICO-Container schreiben (PNG-in-ICO, modernes Format)
    with open(path, "wb") as f:
        f.write(struct.pack("<HHH", 0, 1, len(png_chunks)))
        offset = 6 + 16 * len(png_chunks)
        for size, data in png_chunks:
            dim = 0 if size >= 256 else size   # 0 kodiert 256 im ICO-Format
            f.write(struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset))
            offset += len(data)
        for _, data in png_chunks:
            f.write(data)


def _save_as_icns(image: np.ndarray, path: str):
    """Erstellt eine macOS-ICNS-Datei via FFmpeg + iconutil."""
    iconset_sizes = [16, 32, 128, 256, 512]

    with tempfile.TemporaryDirectory() as tmp_dir:
        src = _to_temp_png(image, tmp_dir)

        iconset_path = os.path.join(tmp_dir, "icon.iconset")
        os.makedirs(iconset_path)

        for size in iconset_sizes:
            for scale, suffix in [(1, ""), (2, "@2x")]:
                px = size * scale
                out = os.path.join(iconset_path, f"icon_{size}x{size}{suffix}.png")
                subprocess.run(
                    ["ffmpeg", "-y", "-i", src,
                     "-vf", f"scale={px}:{px}:flags=lanczos",
                     "-vcodec", "png", out],
                    capture_output=True, check=True
                )

        result = subprocess.run(
            ["iconutil", "-c", "icns", iconset_path, "-o", path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"iconutil fehlgeschlagen:\n{result.stderr}")


def _save_as_svg(image: np.ndarray, path: str):
    """Konvertiert ein Rasterbild via vtracer in SVG."""
    try:
        import vtracer
    except ImportError:
        raise ImportError(
            "SVG-Export benötigt das Paket 'vtracer'.\n"
            "Installieren mit: pip install vtracer"
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        src = _to_temp_png(image, tmp_dir)
        vtracer.convert_image_to_svg_py(
            src, path,
            colormode="color",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=4,
            color_precision=6,
            layer_difference=16,
            corner_threshold=60,
            length_threshold=4.0,
            splice_threshold=45,
            path_precision=8
        )
