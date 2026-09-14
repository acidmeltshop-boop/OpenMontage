"""Key the cutouts, normalise every still to 1080x1920, write into assets/prepped/."""
import numpy as np
from PIL import Image
import os

SRC, DST = "assets", "assets/prepped"
W, H = 1080, 1920
os.makedirs(DST, exist_ok=True)


def cover(im, w=W, h=H):
    """Scale to cover then centre-crop — the sources are 768x1376 (0.558 vs 0.5625)."""
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def key_green(im):
    """Green-screen key with despill. The delivered key sits near (10,240,5)."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    is_green = (g > 120) & (g > r * 1.45) & (g > b * 1.45)
    # soft edge: how far into "greenness" each pixel is
    excess = g - np.maximum(r, b)
    alpha = np.clip(1.0 - (excess - 18.0) / 42.0, 0, 1)
    alpha[~is_green] = 1.0
    # despill — pull green down to the max of the other two channels
    spill = is_green | (excess > 6)
    g2 = g.copy()
    g2[spill] = np.maximum(r[spill], b[spill]) + np.minimum(excess[spill], 6) * 0.3
    out = np.dstack([r, g2, b, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def key_white(im, thresh=252):
    """The receipt arrived on white: body is luma 239-248, ground 254-255."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    luma = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    bg = (luma >= thresh) & (sat < 6)
    alpha = np.where(bg, 0.0, 255.0)
    out = np.dstack([a[..., 0], a[..., 1], a[..., 2], alpha]).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    # drop any fully-transparent border so the object can be positioned by its own box
    return img


PLAIN = ["img-02-hero-vertical", "img-03-hero-plate", "img-05-face-closeup",
         "img-07-feed-a", "img-08-feed-b", "img-10-standing", "img-11-bus"]
GREEN = ["img-04-char-cutout", "img-06-phone-object"]
WHITE = ["img-09-receipt"]

for name in PLAIN:
    cover(Image.open(f"{SRC}/{name}.png").convert("RGB")).save(f"{DST}/{name}.png")
    print("plain  ", name)

for name in GREEN:
    im = key_green(Image.open(f"{SRC}/{name}.png"))
    im = cover(im)
    im.save(f"{DST}/{name}.png")
    a = np.asarray(im)[..., 3]
    print(f"green  {name}  opaque={100*(a>128).mean():.1f}%")

for name in WHITE:
    im = key_white(Image.open(f"{SRC}/{name}.png"))
    im = cover(im)
    im.save(f"{DST}/{name}.png")
    a = np.asarray(im)[..., 3]
    print(f"white  {name}  opaque={100*(a>128).mean():.1f}%")

print("done ->", DST)
