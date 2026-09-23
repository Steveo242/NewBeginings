"""Bloody Seafood game tile - 3:4 portrait webp, per Stake Engine's tile spec
(tags on the platform: ratio:3:4, format:webp).

Portrait needs its own composition rather than a crop of the 16:9 master:
the landscape safe area is 1320px wide and a 3:4 crop is only 1080, so the
outer symbols would be cut.
"""
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops
import json

W, H = 1080, 1440          # 3:4
CX = W // 2
SPR = 'static/assets/sprites'
S = f'{SPR}/bgLayers'

def load(n):
    return Image.open(f'{S}/{n}').convert('RGBA')

# ---------------------------------------------------------------- background
bg = Image.new('RGBA', (W, H), (0, 0, 0, 255))

def place(img, x, y, w, h):
    bg.alpha_composite(img.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS),
                       (int(x), int(y)))

# Same layer order and proportions the game uses, refitted to portrait. The
# horizon sits higher here so the dock fills the lower half behind the symbols.
place(load('bg_land_sky.png'), 0, 0, W, H * 0.72)
place(load('bg_land_boats.png'), -W * 0.16, H * 0.02, W * 1.35, H * 0.62)
place(load('bg_land_water.png'), 0, H * 0.40, W, H * 0.16)
place(load('bg_land_nearboats.png'), 0, H * 0.44, W, H * 0.14)
place(load('bg_land_dock.png'), 0, H * 0.54, W, H * 0.46)
place(load('bg_land_gulls.png'), -W * 0.25, H * 0.05, W * 1.7, H * 0.22)
ov = load('bg_land_overlay.png').resize((W, H), Image.LANCZOS)
ov.putalpha(ov.getchannel('A').point(lambda v: int(v * 0.3)))
bg.alpha_composite(ov)

bg = bg.convert('RGB').filter(ImageFilter.GaussianBlur(2))
bg = ImageEnhance.Brightness(bg).enhance(1.02)
bg = ImageEnhance.Color(bg).enhance(1.04)
bg = bg.convert('RGBA')

# ------------------------------------------------------------------- symbols
atlas = Image.open(f'{SPR}/symbolsStatic/symbolsStatic.webp').convert('RGBA')
frames = json.load(open(f'{SPR}/symbolsStatic/symbolsStatic.json'))['frames']

def sym(k):
    f = frames[k]['frame']
    return atlas.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))

def fit(img, tw):
    s = tw / img.width
    return img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)

def pad(img, m):
    out = Image.new('RGBA', (img.width + 2 * m, img.height + 2 * m), (0, 0, 0, 0))
    out.alpha_composite(img, (m, m))
    return out

def shadow(img, blur=18, alpha=115):
    a = img.getchannel('A')
    sh = Image.new('RGBA', a.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    return pad(sh, blur * 3).filter(ImageFilter.GaussianBlur(blur))

def rim(img, strength=95):
    a = img.getchannel('A')
    edge = ImageChops.subtract(a, ImageChops.offset(a, -4, -4))
    lit = Image.new('RGBA', img.size, (255, 236, 200, 0))
    lit.putalpha(edge.point(lambda v: int(v * strength / 255)))
    return Image.alpha_composite(img, lit.filter(ImageFilter.GaussianBlur(2)))

canvas = bg.copy()

def paste(img, cx, cy):
    sh = shadow(img)
    canvas.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2 + 18)))
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

# The shark keeps its own aqua - that is its colour in game.
shark = rim(fit(sym('h1.webp'), 700), strength=105)
chest = rim(fit(sym('s.png'), 520))
bucket = rim(fit(sym('l1.webp'), 330))
anchor = rim(fit(sym('w.png'), 350), strength=125)

paste(anchor, CX + 335, 995)
paste(bucket, CX - 345, 1055)
paste(shark, CX - 40, 845)
paste(chest, CX + 60, 1150)

# ---------------------------------------------------------------------- logo
logo = fit(Image.open(f'{S}/title_plaque.png').convert('RGBA'), 1010)
halo = Image.new('RGBA', logo.size, (0, 0, 0, 0))
halo.putalpha(logo.getchannel('A').point(lambda v: int(v * 0.5)))
halo = pad(halo, 70).filter(ImageFilter.GaussianBlur(30))
lx, ly = CX - logo.width // 2, 105
canvas.alpha_composite(halo, (lx - 70, ly - 70 + 8))
canvas.alpha_composite(rim(logo, strength=110), (lx, ly))

# ------------------------------------------------------------------- grade
vig = Image.new('L', (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.34, -H * 0.24, W * 1.34, H * 1.24], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(240))
dark = Image.new('RGBA', (W, H), (10, 30, 48, 255))
dark.putalpha(vig.point(lambda v: int((255 - v) * 0.45)))
canvas = Image.alpha_composite(canvas, dark)

out = canvas.convert('RGB')
out = ImageEnhance.Contrast(out).enhance(1.05)
out = ImageEnhance.Color(out).enhance(1.06)

out.save('thumbnails/bloody_seafood_tile_3x4.webp', quality=88, method=6)
out.save('/tmp/tile_3x4_preview.png')
import os
print('3:4 tile', out.size, os.path.getsize('thumbnails/bloody_seafood_tile_3x4.webp') // 1024, 'KB')
