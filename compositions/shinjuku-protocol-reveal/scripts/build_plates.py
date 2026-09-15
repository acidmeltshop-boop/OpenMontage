"""Derive every visual plate for the Shinjuku Protocol press-sheet trailer.

All subject matter comes from the three supplied posters — no image generation
provider is configured on this machine. Operations here are crops, duotone
separations and a real clustered-dot halftone screen, all local and deterministic.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference"
OUT = ROOT / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

STOCK = (0xF2, 0xEF, 0xE9)
INK = (0x0B, 0x0B, 0x0C)
CRIMSON = (0xC8, 0x10, 0x2E)
CYAN = (0x1F, 0xB6, 0xC9)


def crop_pct(im: Image.Image, l: float, t: float, r: float, b: float) -> Image.Image:
    w, h = im.size
    return im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))


def duotone(im: Image.Image, dark, mid, light) -> Image.Image:
    """Three-stop duotone ramp — how a two-plate offset print actually separates."""
    g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    stops = np.array([dark, mid, light], dtype=np.float32)
    pos = np.array([0.0, 0.55, 1.0], dtype=np.float32)
    out = np.empty(g.shape + (3,), dtype=np.float32)
    for c in range(3):
        out[..., c] = np.interp(g, pos, stops[:, c])
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGB")


def halftone(im: Image.Image, cell: int = 6, angle: float = 45.0) -> Image.Image:
    """Clustered-dot halftone screen at a given cell size and screen angle.

    Builds a rotated spiral-dot threshold matrix and tiles it under the image —
    the same geometry a real screen uses, so the dots grow from a centre rather
    than dithering into noise.
    """
    g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(angle)
    # rotate sample coords into screen space, then take position within one cell
    u = (xx * np.cos(a) - yy * np.sin(a)) % cell
    v = (xx * np.sin(a) + yy * np.cos(a)) % cell
    c = (cell - 1) / 2.0
    # distance from cell centre, normalised -> threshold ramp (spiral dot)
    d = np.sqrt((u - c) ** 2 + (v - c) ** 2) / (cell * 0.7071)
    thresh = np.clip(d, 0.0, 1.0)
    dots = (g > thresh).astype(np.uint8)
    rgb = np.where(dots[..., None] == 1, np.array(STOCK, np.uint8), np.array(INK, np.uint8))
    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def save(im: Image.Image, name: str, max_w: int | None = 1920) -> dict:
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    p = OUT / name
    im.save(p, "PNG", optimize=True)
    return {"name": name, "path": str(p.relative_to(ROOT)), "size": f"{im.width}x{im.height}"}


def main() -> None:
    p1 = Image.open(REF / "poster_01_illustrated.png").convert("RGB")
    p2 = Image.open(REF / "poster_02_photographic.png").convert("RGB")
    p3 = Image.open(REF / "poster_03_editorial.png").convert("RGB")

    made: list[dict] = []

    # --- primary art plates -------------------------------------------------
    art1 = crop_pct(p1, 0.055, 0.302, 0.945, 0.700)          # illustrated art panel, below the poster's own PROTOCOL
    made.append(save(art1, "plate_art_illustrated.png"))

    band = crop_pct(p1, 0.080, 0.500, 0.780, 0.700)           # hand + glass letterbox band
    made.append(save(band, "plate_band_glass.png"))

    photo = crop_pct(p2, 0.040, 0.490, 0.960, 0.960)          # photographic panel
    made.append(save(photo, "plate_photo.png"))

    face = crop_pct(p3, 0.185, 0.168, 0.470, 0.585)           # editorial face, clear of the SHINJUKU wordmark
    made.append(save(face, "plate_face.png", max_w=1100))

    ots = crop_pct(p3, 0.605, 0.105, 0.960, 0.660)            # editorial over-shoulder, clear of the top furniture
    made.append(save(ots, "plate_ots.png", max_w=1100))

    edit = crop_pct(p3, 0.035, 0.105, 0.965, 0.900)           # editorial wide, inside the poster frame
    made.append(save(edit, "plate_editorial.png"))

    # --- dedicated type-fill plate (the signature shot) ----------------------
    # The letterforms are ~2030px wide at 352px Archivo Black, so the fill has to be
    # that wide AND carry recognisable subject matter at letter scale. The photographic
    # panel wins here: two faces and the glass read where flat illustration turns to mush.
    fill = crop_pct(p2, 0.100, 0.520, 0.920, 0.880)
    fill = fill.resize((2100, round(fill.height * 2100 / fill.width)), Image.LANCZOS)
    fill = ImageEnhance.Contrast(fill).enhance(1.45)
    fill = ImageEnhance.Brightness(fill).enhance(1.22)
    made.append(save(fill, "plate_typefill.png", max_w=2100))

    # --- s09 panel C: the neon window, not another portrait ------------------
    neon = crop_pct(p3, 0.430, 0.150, 0.720, 0.620)
    made.append(save(neon, "plate_neon.png", max_w=900))

    # --- separations --------------------------------------------------------
    made.append(save(duotone(photo, INK, CRIMSON, STOCK), "plate_photo_duotone.png"))
    made.append(save(duotone(art1, INK, CRIMSON, STOCK), "plate_art_duotone.png"))
    made.append(save(duotone(photo, INK, CYAN, STOCK), "plate_photo_cyan.png"))

    # --- halftone screens ---------------------------------------------------
    made.append(save(halftone(art1, cell=6, angle=45.0), "plate_art_halftone.png"))
    made.append(save(halftone(photo, cell=5, angle=15.0), "plate_photo_halftone.png"))

    print(json.dumps(made, indent=2))


if __name__ == "__main__":
    main()
