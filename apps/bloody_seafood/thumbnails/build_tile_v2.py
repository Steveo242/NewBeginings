"""Bloody Seafood game tile v2 - 3:4 portrait webp (Stake Engine tile spec: ratio 3:4, webp).

The 3D-era redesign: the storm harbour the game now plays in, the riveted 3D tank
full of real board symbols, and the rigged 3D great white breaching out of the top
of the tank, jaws open. Run from apps/bloody_seafood:

    python3 thumbnails/build_tile_v2.py [tile|cover|keyart|banner|square]

`cover` lays the same scene out as the 16:9 cover (1920x1080): logo on the left,
tank and shark right of centre.

Needs the hero render from /root/bs-render (see HERO below): the shark's win action,
frame 34, CAM="45,-10,20,110" MARGIN=1.6, 1800 px - sharper than the 640 px game frames.
"""
import json
import math
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

# Everything that differs between the two formats. Positions are top-left corners.
LAYOUTS = {
    'tile': dict(W=1080, H=1440, horizon=700, sky_dx=-180, sea_k=1.35 * 0.62, head_k=0.62, head_x=-150,
                 trawl_k=0.56, trawl_dx=150, TK=0.44, TX=None, TY=640, SH=1010, SX_off=-20, SY_off=-185,
                 chest=(300, -10, 1110), anchor=(360, 800, 1050), logo_w=900, logo=(None, 18),
                 focus=(0.5, 0.48), out='bloody_seafood_tile_3x4'),
    'cover': dict(W=1920, H=1080, horizon=500, sky_dx=0, sea_k=0.95, head_k=0.5, head_x=-60,
                  trawl_k=0.45, trawl_dx=40, TK=0.34, TX=1000, TY=300, SH=800, SX_off=-15, SY_off=-160,
                  chest=(250, 330, 790), anchor=(300, 1700, 740), logo_w=820, logo=(90, 150),
                  focus=(0.62, 0.5), out='bloody_seafood_cover_16x9_v2'),
}
# The legacy sizes (key art, banner) are the cover drawn at another scale: every pixel
# measure in the layout and the script goes through px().
GEOM = ('horizon', 'sky_dx', 'head_x', 'trawl_dx', 'TX', 'TY', 'SH', 'SX_off', 'SY_off', 'logo_w')
KS = ('sea_k', 'head_k', 'trawl_k', 'TK')


def rescaled(base, S, out):
    L = dict(base, W=round(base['W'] * S), H=round(base['H'] * S), out=out, S=S)
    for k in GEOM:
        if L[k] is not None:
            L[k] = round(L[k] * S)
    for k in KS:
        L[k] *= S
    L['chest'], L['anchor'] = (tuple(round(v * S) for v in L[k]) for k in ('chest', 'anchor'))
    L['logo'] = tuple(None if v is None else round(v * S) for v in L['logo'])
    return L


LAYOUTS['keyart'] = rescaled(LAYOUTS['cover'], 4 / 3, 'bloody_seafood_keyart_2560x1440')
LAYOUTS['banner'] = rescaled(LAYOUTS['cover'], 2 / 3, 'bloody_seafood_banner_1280x720')
# square tiles: laid out at 1024, drawn at 2x and downsampled for 1024/512/256
LAYOUTS['square'] = rescaled(dict(
    W=1024, H=1024, horizon=500, sky_dx=-120, sea_k=0.84, head_k=0.45, head_x=-110,
    trawl_k=0.42, trawl_dx=110, TK=0.36, TX=None, TY=445, SH=760, SX_off=-15, SY_off=-150,
    chest=(220, -10, 800), anchor=(260, 790, 760), logo_w=640, logo=(None, 14),
    focus=(0.5, 0.5)), 2, 'bloody_seafood_tile')
L = LAYOUTS[sys.argv[1] if len(sys.argv) > 1 else 'tile']
W, H = L['W'], L['H']
S = L.get('S', 1)


def px(v):
    return max(1, round(v * S))


def odd(v):
    return px(v) | 1
SPR = 'static/assets/sprites'
STORM = f'{SPR}/storm'
HERO = '/root/bs-render/render/rig/h1_shark_v3/hero/win_0001.png'
CHEST = '/root/bs-render/render/rig/sw/s_chest/final/static.png'
ANCHOR = '/root/bs-render/render/rig/sw/w_anchor/final/static.png'
BOOK = '/root/bs-render/gameplay_capture/books/base_big.json'
OUT = 'thumbnails'
random.seed(7)


def load(p):
    return Image.open(p).convert('RGBA')


def scaled(img, k):
    return img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), Image.LANCZOS)


def tight(img):
    return img.crop(img.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox())


def shadow(img, blur, alpha, grow=0):
    pad = blur * 3 + grow
    a = Image.new('L', (img.width + 2 * pad, img.height + 2 * pad), 0)
    a.paste(img.getchannel('A'), (pad, pad))
    if grow:
        a = a.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    a = a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    s = Image.new('RGBA', a.size, (0, 0, 0, 0))
    s.putalpha(a)
    return s, pad


canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255))

# ------------------------------------------------------------- storm harbour
# The game's own layers (Background.svelte), refitted to portrait: horizon high so
# the lighthouse and the trawler both show past the tank.
HORIZON = L['horizon']
sky = load(f'{STORM}/bg_sky.webp')
k = max(HORIZON * 1.25 / sky.height, W / sky.width)
sky = scaled(sky, k)
canvas.alpha_composite(sky, ((W - sky.width) // 2 + L['sky_dx'], 0))

sea = load(f'{STORM}/bg_sea.webp')
sea = scaled(sea, L['sea_k'])
canvas.alpha_composite(sea, ((W - sea.width) // 2, HORIZON - px(70)))

headland = scaled(load(f'{STORM}/bg_headland.webp'), L['head_k'])
HX, HY = L['head_x'], HORIZON - headland.height + round(110 * L['head_k'] / 0.62)
canvas.alpha_composite(headland, (HX, HY))
lamp = (HX + 612 * L['head_k'], HY + 80 * L['head_k'])

trawler = scaled(load(f'{STORM}/bg_trawler.webp'), L['trawl_k'])
canvas.alpha_composite(trawler, (W - trawler.width + L['trawl_dx'], HORIZON - trawler.height + round(150 * L['trawl_k'] / 0.56)))

dock = load(f'{STORM}/bg_dock.webp')
dock = scaled(dock, (H - HORIZON - px(120)) / dock.height * 1.1)
canvas.alpha_composite(dock, ((W - dock.width) // 2, H - dock.height + px(40)))

# lighthouse lamp bloom + a beam raking left, like the live scene
glow = load(f'{STORM}/fx_glow.webp')
for size, a in ((px(420), 150), (px(170), 255)):
    g = scaled(glow, size / glow.width)
    g.putalpha(g.getchannel('A').point(lambda v, a=a: v * a // 255))
    canvas.alpha_composite(g, (round(lamp[0] - g.width / 2), round(lamp[1] - g.height / 2)))
beam = load(f'{STORM}/fx_beam.webp')
beam = scaled(beam, 0.9 * S).rotate(-4, resample=Image.BICUBIC, expand=True)
beam.putalpha(beam.getchannel('A').point(lambda v: v * 150 // 255))
canvas.alpha_composite(beam, (round(lamp[0]), round(lamp[1] - beam.height / 2)))

# ------------------------------------------------------------------ the tank
TK = L['TK']                                # tank art is 2240 px square
tank_back = scaled(load(f'{STORM}/tank_back.webp'), TK)
tank_front = scaled(load(f'{STORM}/tank_front.webp'), TK)
TX = L['TX'] if L['TX'] is not None else (W - tank_back.width) // 2
TY = L['TY']
sh, pad = shadow(tank_front, px(30), 170, grow=px(6))
canvas.alpha_composite(sh, (TX - pad, TY - pad + px(18)))
canvas.alpha_composite(tank_back, (TX, TY))

# the 7x7 grid registers on the tank's opening (tank_back's interior: 397..1842 px)
GX0, GY0 = TX + 397 * TK, TY + 398 * TK
CELL = (1842 - 397) * TK / 7

atlas = Image.open(f'{SPR}/symbolsStatic/symbolsStatic.webp').convert('RGBA')
frames = json.load(open(f'{SPR}/symbolsStatic/symbolsStatic.json'))['frames']


def sym(name):
    f = frames[name]
    r = f['frame']
    im = atlas.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']))
    ss = f['sourceSize']
    cell = Image.new('RGBA', (ss['w'], ss['h']), (0, 0, 0, 0))
    cell.alpha_composite(im, (f['spriteSourceSize']['x'], f['spriteSourceSize']['y']))
    return cell


# same relative scales as the game (constants.ts): FILL 1.1, lows 0.86, shark 1.18
SCALE = {'H1': 1.18, 'L1': 0.86, 'L2': 0.86, 'L3': 0.86}
ART = {'H1': 'h1.webp', 'H2': 'h2.webp', 'H3': 'h3.webp', 'H4': 'h4.webp',
       'L1': 'l1.webp', 'L2': 'l2.webp', 'L3': 'l3.webp', 'W': 'w.png', 'S': 's.png'}
board = json.load(open(BOOK))['events'][0]['board']          # a real reveal
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for reel in range(7):
    for row in range(7):
        name = board[reel][row + 1]['name']
        if name not in ART or ART[name] not in frames:
            continue
        size = CELL * 1.3 * SCALE.get(name, 1)       # key art: a denser board than the game
        cell = sym(ART[name])
        s = scaled(cell, size / cell.width)       # atlas cells are 400 px now (were 200)
        cx, cy = GX0 + CELL * (reel + 0.5), GY0 + CELL * (row + 0.5)
        layer.alpha_composite(s, (round(cx - s.width / 2), round(cy - s.height / 2)))
canvas.alpha_composite(layer)

# blood clouding the water around where the shark tore through
blood = Image.new('L', (W, H), 0)
bd = np.zeros((H, W), np.float32)
yy, xx = np.mgrid[0:H, 0:W]
for _ in range(9):
    cx = random.uniform(GX0 + CELL * 1.5, GX0 + CELL * 5.5)
    cy = random.uniform(GY0 + CELL * 0.5, GY0 + CELL * 4.5)
    r = random.uniform(55, 120) * S
    bd += np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))) * random.uniform(0.35, 0.7)
blood = Image.fromarray(np.clip(bd * 170, 0, 150).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px(18)))
inner = Image.new('L', (W, H), 0)
inner.paste(255, (round(GX0), round(GY0), round(GX0 + CELL * 7), round(GY0 + CELL * 7)))
blood = ImageChops.multiply(blood, inner)
red = Image.new('RGBA', (W, H), (120, 6, 12, 0))
red.putalpha(blood)
canvas.alpha_composite(red)

# ------------------------------------------------------------ the great white
shark = tight(load(HERO))
SH = L['SH']                                # on-tile height
shark = scaled(shark, SH / shark.height)
SX = TX + tank_back.width // 2 - shark.width // 2 + L['SX_off']
SY = TY + L['SY_off']                       # jaws clear the top beam
ssh, spad = shadow(shark, px(22), 150)
canvas.alpha_composite(ssh, (SX - spad + px(14), SY - spad + px(24)))

# Below the waterline the shark is IN the tank (behind the front frame and glass);
# from there up it bursts out over the front edge, in front of the top beam.
RIM = round(GY0)                            # the water's surface: the top of the grid
inside = shark.copy()
canvas.alpha_composite(inside, (SX, SY))

# the water itself over everything in the tank: teal wash deepening toward the
# floor, and the blood the shark is trailing clouding around its body
OX0, OY0, OX1, OY1 = round(GX0), round(GY0), round(GX0 + CELL * 7), round(GY0 + CELL * 7)
wash = np.zeros((OY1 - OY0, OX1 - OX0, 4), np.float32)
depth = np.linspace(0, 1, OY1 - OY0)[:, None]
wash[..., 0], wash[..., 1], wash[..., 2] = 10, 84, 98
wash[..., 3] = 70 + 80 * depth
canvas.alpha_composite(Image.fromarray(wash.astype(np.uint8), 'RGBA'), (OX0, OY0))
body = Image.new('L', (W, H), 0)
body.paste(shark.getchannel('A'), (SX, SY))
# wisps, not a coat: blotchy noise, only just around (and mostly below) the body
noise = np.random.default_rng(3).random((H // px(24) + 1, W // px(24) + 1)).astype(np.float32)
noise = Image.fromarray((noise * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(px(14)))
halo = ImageChops.subtract(body.filter(ImageFilter.MaxFilter(odd(61))).filter(ImageFilter.GaussianBlur(px(28))), body)
halo = ImageChops.multiply(halo, noise.point(lambda v: max(0, v - 90) * 2))
trail = ImageChops.multiply(halo.point(lambda v: min(120, int(v * 0.8))), inner)
red2 = Image.new('RGBA', (W, H), (105, 4, 10, 0))
red2.putalpha(trail)
canvas.alpha_composite(red2)
canvas.alpha_composite(tank_front, (TX, TY))
outside = shark.copy()
cut = Image.new('L', shark.size, 0)
cut.paste(255, (0, 0, shark.width, max(0, RIM - SY + px(8))))
cut = cut.filter(ImageFilter.GaussianBlur(px(6)))
outside.putalpha(ImageChops.multiply(outside.getchannel('A'), cut))
canvas.alpha_composite(outside, (SX, SY))

# broken froth where the body cuts the surface
fl = Image.new('L', (W, H), 0)
fl.paste(255, (0, RIM - px(4), W, RIM + px(6)))
fn = np.random.default_rng(11).random((H // px(6) + 1, W // px(6) + 1)).astype(np.float32)
fn = Image.fromarray((fn * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
band = ImageChops.multiply(body.filter(ImageFilter.MaxFilter(odd(25))), fl).filter(ImageFilter.GaussianBlur(px(3)))
band = ImageChops.multiply(band, fn.point(lambda v: 255 if v > 120 else v))
froth = Image.new('RGBA', (W, H), (236, 246, 250, 0))
froth.putalpha(band.filter(ImageFilter.GaussianBlur(1.5 * S)).point(lambda v: min(200, v)))
canvas.alpha_composite(froth)

# spray thrown off the breach: fine white water streaking up and out from the
# waterline, with a few drops of blood in it
drops = Image.new('RGBA', (W, H), (0, 0, 0, 0))
from PIL import ImageDraw
dr = ImageDraw.Draw(drops)
for _ in range(170):
    ang = random.uniform(math.pi * 1.08, math.pi * 1.92)
    dist = random.uniform(10, 300) * random.random() ** 0.7 * S
    x = TX + tank_back.width // 2 - px(30) + math.cos(ang) * dist * 1.6
    y = RIM - px(10) + math.sin(ang) * dist * 0.8
    r = random.uniform(0.8, 3.2) * (1.1 - dist / (330 * S)) * S
    if r <= 0.4:
        continue
    tail = 2.5 * S + r * 3                      # streak back along its flight
    tx, ty = x - math.cos(ang) * tail, y - math.sin(ang) * tail
    col = (140, 10, 16) if random.random() < 0.18 else (228, 240, 246)
    a = random.randint(120, 215)
    dr.line((tx, ty, x, y), fill=(*col, a // 2), width=max(1, round(r)))
    dr.ellipse((x - r, y - r, x + r, y + r), fill=(*col, a))
# thrown OFF the body: no drops over the shark itself (they read as a rash on its throat)
drops.putalpha(ImageChops.multiply(drops.getchannel('A'), ImageChops.invert(body.filter(ImageFilter.MaxFilter(5)))))
canvas.alpha_composite(drops.filter(ImageFilter.GaussianBlur(0.7 * S)))

# ---------------------------------------------------------- chest and anchor
for path, (h, x, y) in ((CHEST, L['chest']), (ANCHOR, L['anchor'])):
    obj = tight(load(path))
    obj = scaled(obj, h / obj.height)
    osh, opad = shadow(obj, px(16), 180)
    canvas.alpha_composite(osh, (x - opad + px(10), y - opad + px(16)))
    canvas.alpha_composite(obj, (x, y))

# --------------------------------------------------------------------- rain
rain = scaled(load(f'{STORM}/fx_rain.webp'), S)
rl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for ty in range(0, H, rain.height):
    for tx in range(0, W, rain.width):
        rl.alpha_composite(rain, (tx, ty))
rl = rl.rotate(-8, resample=Image.BICUBIC)
rl.putalpha(rl.getchannel('A').point(lambda v: v * 80 // 255))
canvas.alpha_composite(rl)

# ---------------------------------------------------------------------- logo
logo = load(f'{SPR}/bgLayers/logo3d.webp')
logo = scaled(logo, L['logo_w'] / logo.width)
lsh, lpad = shadow(logo, px(20), 190)
LX, LY = L['logo'][0] if L['logo'][0] is not None else (W - logo.width) // 2, L['logo'][1]
canvas.alpha_composite(lsh, (LX - lpad + px(8), LY - lpad + px(16)))
canvas.alpha_composite(logo, (LX, LY))

# ------------------------------------------------------------------- finish
rgb = canvas.convert('RGB')
rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
rgb = ImageEnhance.Color(rgb).enhance(1.08)
# soft vignette so the eye lands on the shark
v = np.ones((H, W), np.float32)
FX, FY = L['focus']
d = np.sqrt(((xx - W * FX) / (W * 0.75)) ** 2 + ((yy - H * FY) / (H * 0.75)) ** 2)
v = np.clip(1.12 - 0.42 * d ** 2, 0.6, 1.0)
rgb = Image.fromarray((np.asarray(rgb, np.float32) * v[..., None]).clip(0, 255).astype(np.uint8))

if L['out'] == 'bloody_seafood_tile':
    for size in (1024, 512, 256):
        rgb.resize((size, size), Image.LANCZOS).save(f"{OUT}/{L['out']}_{size}.png", optimize=True)
elif 'S' in L:                              # the legacy sizes were always PNG
    rgb.save(f"{OUT}/{L['out']}.png", optimize=True)
else:
    rgb.save(f"{OUT}/{L['out']}.webp", quality=82, method=6)
    rgb.save(f"{OUT}/{L['out']}_preview.png")
print(L['out'], rgb.size)
