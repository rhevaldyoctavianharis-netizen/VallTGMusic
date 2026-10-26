import os
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter, ImageStat

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "assets", "main.png")
FONT_PATH = os.path.join(BASE_DIR, "assets", "KaushanScript-Regular.ttf")

# Area teks "Welcome to" pada main.png (1672x940) dan posisi teks pengganti.
TEXT_BOX = (700, 95, 1090, 222)        # area yang dibersihkan
TEXT_X = 727                           # sisi kiri teks (sama dgn "Welcome to" asli)
TEXT_BASELINE = 163                    # garis dasar teks (di atas "OneDot Music")
TEXT_MAX_RIGHT = 1490                  # batas kanan (sebelum tulisan "Just Send /Play")
BASE_FONT_SIZE = 100
TEXT_COLOR = (10, 186, 246)            # cyan asli template

_clean_cache = None


def _clean_template():
    """Template dengan teks 'Welcome to' dihapus (di-cache di memori)."""
    global _clean_cache
    if _clean_cache is not None:
        return _clean_cache.copy()

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    region = img.crop(TEXT_BOX)
    r, g, b = region.split()

    # Piksel teks = biru/cyan jenuh (B jauh lebih besar dari R). Putih "OneDot" tidak ikut.
    text_mask = ImageChops.subtract(b, r).point(lambda v: 255 if v > 30 else 0)
    # Lindungi piksel terang (huruf putih OneDot di bawahnya).
    bright = r.point(lambda v: 255 if v > 110 else 0)

    grow = text_mask.filter(ImageFilter.MaxFilter(15))                  # ~7px, mencakup glow
    grow = ImageChops.subtract(grow, bright.filter(ImageFilter.MaxFilter(3)))
    soft = grow.filter(ImageFilter.GaussianBlur(2))

    keep = ImageChops.invert(grow)
    bg = tuple(int(v) for v in ImageStat.Stat(region, mask=keep).median[:3])
    region.paste(Image.new("RGB", region.size, bg), (0, 0), soft)
    img.paste(region, TEXT_BOX[:2])

    _clean_cache = img
    return img.copy()


def _safe_name(name):
    """Font script hanya mendukung Latin: ubah huruf 'fancy' ke ASCII, buang emoji/simbol."""
    n = unicodedata.normalize("NFKD", str(name or ""))
    n = n.encode("ascii", "ignore").decode()
    n = "".join(c for c in n if c.isalnum() or c in " ._-'")
    n = " ".join(n.split())[:18].strip()
    return n or "Friend"


def _fit_font(text, max_width):
    size = BASE_FONT_SIZE
    while size > 40:
        font = ImageFont.truetype(FONT_PATH, size)
        if font.getlength(text) <= max_width:
            return font
        size -= 4
    return ImageFont.truetype(FONT_PATH, 40)


def generate_start_image(pfp_path, user_name, output_path="start_img.jpg"):
    """Bikin thumbnail /start: 'Welcome (Nama) To' di atas OneDot Music.
    pfp_path dipertahankan hanya demi kompatibilitas pemanggil lama (tidak dipakai)."""
    bg = _clean_template().convert("RGBA")

    text = f"Welcome {_safe_name(user_name)} To"
    font = _fit_font(text, TEXT_MAX_RIGHT - TEXT_X)
    anchor_xy = (TEXT_X, TEXT_BASELINE)

    # Glow lembut di belakang teks (mirip template asli)
    glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text(anchor_xy, text, font=font, fill=TEXT_COLOR + (255,), anchor="ls")
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.55)))
    bg = Image.alpha_composite(bg, glow)

    ImageDraw.Draw(bg).text(anchor_xy, text, font=font, fill=TEXT_COLOR + (255,), anchor="ls")

    out = bg.convert("RGB").resize((1280, 720), Image.LANCZOS)
    out.save(output_path, quality=92)
    return output_path
