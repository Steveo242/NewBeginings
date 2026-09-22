"""Bloody Seafood key art.

Composed from the game's own harbour layers, logo and symbol atlas so the
art reads as the actual game. Bright, matching the in-game background -
this is deliberately NOT a dark/vignetted treatment.

Run build_keyart_bg.py first; it writes /tmp/keyart_bg_raw.png.
"""
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops
import json

W, H = 2560, 1440
CX = W // 2
SPR = 'static/assets/sprites'
OUT = 'thumbnails'

# ---------------------------------------------------------------- background
bg = Image.open('/tmp/keyart_bg_raw.png').convert('RGB')
# Just enough softening to separate the scene from the symbols in front of
# it. The brightness stays where the game has it - the harbour is a bright
# daylight scene and the art has to look like the game.
bg = bg.filter(ImageFilter.GaussianBlur(3))
bg = ImageEnhance.Brightness(bg).enhance(1.02)
bg = ImageEnhance.Color(bg).enhance(1.04)
bg = bg.convert('RGBA')

# ------------------------------------------------------------------- symbols
atlas = Image.open(f'{SPR}/symbolsStatic/symbolsStatic.webp').convert('RGBA')
frames = json.load(open(f'{SPR}/symbolsStatic/symbolsStatic.json'))['frames']

def sym(key):
    f = frames[key]['frame']
    return atlas.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))

def fit(img, target_w):
    s = target_w / img.width
    return img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)

def pad(img, m):
    """Room for blurs to spread. Without it every filter below gets clipped
    square at the symbol's own bounding box - which shows up as a hard
    rectangle behind each symbol."""
    out = Image.new('RGBA', (img.width + 2 * m, img.height + 2 * m), (0, 0, 0, 0))
    out.alpha_composite(img, (m, m))
    return out

def shadow(img, blur=24, alpha=115, spread=1.05):
    """Contact shadow so symbols sit in the scene instead of floating on it.
    Lighter than it would be on a dark background - on a bright scene a heavy
    shadow reads as dirt."""
    a = img.getchannel('A').resize(
        (int(img.width * spread), int(img.height * spread)), Image.LANCZOS)
    sh = Image.new('RGBA', a.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    return pad(sh, blur * 3).filter(ImageFilter.GaussianBlur(blur))

def rim(img, color=(255, 236, 200), strength=95, off=(-5, -5)):
    """Light rim up-left, matching the symbols' own key light."""
    a = img.getchannel('A')
    edge = ImageChops.subtract(a, ImageChops.offset(a, *off))
    lit = Image.new('RGBA', img.size, color + (0,))
    lit.putalpha(edge.point(lambda v: int(v * strength / 255)))
    return Image.alpha_composite(img, lit.filter(ImageFilter.GaussianBlur(2)))

canvas = bg.copy()

def paste(img, cx, cy):
    sh = shadow(img)
    canvas.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2 + 24)))
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

# The shark keeps its own aqua/green - that is its colour in the game and the
# art has to match what a player actually sees.
shark = rim(fit(sym('h1.webp'), 790), strength=105)
chest = rim(fit(sym('s.png'), 600))
bucket = rim(fit(sym('l1.webp'), 400))
anchor = rim(fit(sym('w.png'), 420), strength=125)

# Everything lives inside CX +/- 660 so the square tile crop keeps all of it.
paste(anchor, CX + 500, 1000)
paste(bucket, CX - 500, 1060)
paste(chest, CX + 170, 1120)
paste(shark, CX - 235, 935)

# ---------------------------------------------------------------------- logo
logo = fit(Image.open(f'{SPR}/bgLayers/title_plaque.png').convert('RGBA'), 1580)
# The wordmark is red and bone over a bright sky, so it needs a soft dark
# halo to hold its edges - without it the red letters vibrate against blue.
halo = Image.new('RGBA', logo.size, (0, 0, 0, 0))
halo.putalpha(logo.getchannel('A').point(lambda v: int(v * 0.5)))
halo = pad(halo, 90).filter(ImageFilter.GaussianBlur(38))
lx, ly = CX - logo.width // 2, 120
canvas.alpha_composite(halo, (lx - 90, ly - 90 + 10))
canvas.alpha_composite(rim(logo, color=(255, 240, 210), strength=110), (lx, ly))

# ------------------------------------------------------------------- grade
# A whisper of a vignette only - enough to hold the eye in, not enough to
# darken the scene.
vig = Image.new('L', (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.30, -H * 0.45, W * 1.30, H * 1.42], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(300))
dark = Image.new('RGBA', (W, H), (10, 30, 48, 255))
dark.putalpha(vig.point(lambda v: int((255 - v) * 0.42)))
canvas = Image.alpha_composite(canvas, dark)

out = canvas.convert('RGB')
out = ImageEnhance.Contrast(out).enhance(1.05)
out = ImageEnhance.Color(out).enhance(1.06)
out.save('/tmp/keyart_master.png')

sq = out.crop(((W - H) // 2, 0, (W - H) // 2 + H, H))
exports = {
    'bloody_seafood_keyart_2560x1440.png': out,
    'bloody_seafood_banner_1280x720.png': out.resize((1280, 720), Image.LANCZOS),
    'bloody_seafood_tile_1024.png': sq.resize((1024, 1024), Image.LANCZOS),
    'bloody_seafood_tile_512.png': sq.resize((512, 512), Image.LANCZOS),
    'bloody_seafood_tile_256.png': sq.resize((256, 256), Image.LANCZOS),
}
for name, im in exports.items():
    im.save(f'{OUT}/{name}', optimize=True)
    print(f'{name:42s} {im.size}')
