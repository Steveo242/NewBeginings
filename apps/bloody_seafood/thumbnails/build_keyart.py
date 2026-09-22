from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops
import json, math

W, H = 2560, 1440
CX = W // 2
SPR = 'static/assets/sprites'

# ---------------------------------------------------------------- background
bg = Image.open('/tmp/keyart_bg_raw.png').convert('RGB')
# Push the harbour back: soften it, cool it down and drop it into shadow so
# the logo and symbols are unambiguously the subject.
bg = bg.filter(ImageFilter.GaussianBlur(7))
bg = ImageEnhance.Brightness(bg).enhance(0.46)
bg = ImageEnhance.Color(bg).enhance(0.72)

# Cool the shadows, keep a little warmth up top - a straight brightness cut
# leaves it looking grey rather than like dusk over water.
r, g, b = bg.split()
r = r.point(lambda v: int(v * 0.88))
b = b.point(lambda v: min(255, int(v * 1.14)))
bg = Image.merge('RGB', (r, g, b)).convert('RGBA')

# Glow behind where the logo will sit, so the wordmark reads off the water.
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([CX - 1150, -350, CX + 1150, 1000], fill=(90, 150, 180, 120))
glow = glow.filter(ImageFilter.GaussianBlur(220))
bg = Image.alpha_composite(bg, glow)

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
    square at the symbol's own bounding box."""
    out = Image.new('RGBA', (img.width + 2 * m, img.height + 2 * m), (0, 0, 0, 0))
    out.alpha_composite(img, (m, m))
    return out

def shadow(img, blur=26, alpha=150, spread=1.06):
    """Contact shadow so symbols sit in the scene instead of floating on it."""
    a = img.getchannel('A').resize(
        (int(img.width * spread), int(img.height * spread)), Image.LANCZOS)
    sh = Image.new('RGBA', a.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    return pad(sh, blur * 3).filter(ImageFilter.GaussianBlur(blur))

def rim(img, color=(255, 214, 140), strength=110, off=(-5, -5)):
    """Warm rim light up-left, matching the symbols' own key light."""
    a = img.getchannel('A')
    edge = ImageChops.subtract(a, ImageChops.offset(a, *off))
    lit = Image.new('RGBA', img.size, color + (0,))
    lit.putalpha(edge.point(lambda v: int(v * strength / 255)))
    return Image.alpha_composite(img, lit.filter(ImageFilter.GaussianBlur(2)))

def steel(img, desat=0.86):
    """The shark renders bright cyan, which fights the rust/brass/blood
    palette. Key art only - the in-game symbol is untouched."""
    a = img.getchannel('A')
    lum = img.convert('RGB').convert('L').convert('RGB')
    out = Image.blend(img.convert('RGB'), lum, desat)
    r, g, b = out.split()
    r = r.point(lambda v: min(255, int(v * 1.07)))
    b = b.point(lambda v: int(v * 0.97))
    out = Image.merge('RGB', (r, g, b))
    out = ImageEnhance.Contrast(out).enhance(1.18)
    out = ImageEnhance.Brightness(out).enhance(1.05)
    out = out.convert('RGBA')
    out.putalpha(a)
    return out

canvas = bg.copy()

def paste(img, cx, cy, with_shadow=True):
    if with_shadow:
        sh = shadow(img)
        canvas.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2 + 26)))
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

# Heroes sit inside the centre 1440px so a square crop keeps all of them.
shark = rim(steel(fit(sym('h1.webp'), 790)), strength=125)
chest = rim(fit(sym('s.png'), 600))
bucket = rim(fit(sym('l1.webp'), 400))
anchor = rim(fit(sym('w.png'), 420), strength=150)

paste(anchor, CX + 500, 1000)
paste(bucket, CX - 500, 1060)
paste(chest, CX + 170, 1120)
paste(shark, CX - 235, 935)

# ---------------------------------------------------------------------- logo
logo = Image.open(f'{SPR}/bgLayers/title_plaque.png').convert('RGBA')
logo = fit(logo, 1580)
# The flat wordmark needs weight against a photographic scene: a dark halo to
# separate it, then a warm rim to give the steel band and letters an edge.
halo = Image.new('RGBA', logo.size, (0, 0, 0, 0))
halo.putalpha(logo.getchannel('A').point(lambda v: int(v * 0.85)))
halo = halo.filter(ImageFilter.GaussianBlur(34))
lx, ly = CX - logo.width // 2, 120
for dx, dy in ((0, 0), (0, 12)):
    canvas.alpha_composite(halo, (lx + dx, ly + dy))
canvas.alpha_composite(rim(logo, color=(255, 226, 168), strength=125, off=(-4, -4)), (lx, ly))

# ------------------------------------------------------------------ grade
# Vignette: darken the edges so every crop pulls the eye to the centre.
vig = Image.new('L', (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.22, -H * 0.40, W * 1.22, H * 1.34], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(320))
dark = Image.new('RGBA', (W, H), (4, 12, 20, 255))
dark.putalpha(vig.point(lambda v: 255 - v))
canvas = Image.alpha_composite(canvas, dark)

out = canvas.convert('RGB')
out = ImageEnhance.Contrast(out).enhance(1.10)
out = ImageEnhance.Color(out).enhance(1.10)
out.save('/tmp/keyart_master.png')
print('master saved', out.size)
