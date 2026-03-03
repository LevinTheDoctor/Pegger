import os
import tempfile
import numpy as np
from PIL import Image


def remove_color(image: Image.Image, color: tuple, tolerance: int = 30) -> Image.Image:
    """Entfernt eine Farbe (mit Toleranz) aus einem Bild und macht sie transparent."""
    img = image.convert("RGBA")
    data = np.array(img, dtype=np.int16)

    r, g, b = color
    mask = (
        (np.abs(data[:, :, 0] - r) <= tolerance) &
        (np.abs(data[:, :, 1] - g) <= tolerance) &
        (np.abs(data[:, :, 2] - b) <= tolerance)
    )
    data[mask] = [0, 0, 0, 0]

    return Image.fromarray(data.astype(np.uint8), "RGBA")


def _flatten_alpha(image: Image.Image) -> Image.Image:
    """Legt ein RGBA-Bild auf weißem Hintergrund ab (für Formate ohne Alpha)."""
    background = Image.new("RGB", image.size, (255, 255, 255))
    if image.mode == "P":
        image = image.convert("RGBA")
    if image.mode == "RGBA":
        background.paste(image, mask=image.split()[3])
    else:
        background.paste(image)
    return background


def save_image(image: Image.Image, path: str, target_format: str):
    """Speichert ein PIL-Image im Zielformat. Unterstützt PNG, JPG, WEBP, BMP, SVG, ICO, ICNS."""
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

    pil_format = "JPEG" if fmt == "JPG" else fmt

    if fmt in ("JPG", "BMP"):
        image = _flatten_alpha(image)

    image.save(path, format=pil_format)


def _save_as_ico(image: Image.Image, path: str):
    """Speichert als Windows-Icon (.ico) mit Standard-Größen."""
    img = image.convert("RGBA")
    img.save(path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def _save_as_icns(image: Image.Image, path: str):
    """Speichert als macOS-Icon (.icns) via iconutil."""
    import subprocess

    img = image.convert("RGBA")
    iconset_sizes = [16, 32, 128, 256, 512]

    with tempfile.TemporaryDirectory() as tmp_dir:
        iconset_path = os.path.join(tmp_dir, "icon.iconset")
        os.makedirs(iconset_path)

        for size in iconset_sizes:
            img.resize((size, size), Image.LANCZOS).save(
                os.path.join(iconset_path, f"icon_{size}x{size}.png")
            )
            img.resize((size * 2, size * 2), Image.LANCZOS).save(
                os.path.join(iconset_path, f"icon_{size}x{size}@2x.png")
            )

        result = subprocess.run(
            ["iconutil", "-c", "icns", iconset_path, "-o", path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"iconutil fehlgeschlagen:\n{result.stderr}")


def _save_as_svg(image: Image.Image, path: str):
    """Konvertiert ein Rasterbild via Vektorisierung in SVG (benötigt: pip install vtracer)."""
    try:
        import vtracer
    except ImportError:
        raise ImportError(
            "SVG-Export benötigt das Paket 'vtracer'.\n"
            "Installieren mit: pip install vtracer"
        )

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        image.convert("RGBA").save(tmp_path, "PNG")

        vtracer.convert_image_to_svg_py(
            tmp_path,
            path,
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

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
