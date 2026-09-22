from PIL import Image, ImageFilter, ImageEnhance
import os
S = 'static/assets/sprites/bgLayers'
W, H = 2560, 1440

def load(n): return Image.open(f'{S}/{n}').convert('RGBA')

base = Image.new('RGBA', (W, H), (0, 0, 0, 255))

def place(img, x, y, w, h):
    base.alpha_composite(img.resize((int(w), int(h)), Image.LANCZOS), (int(x), int(y)))

# Same layer order and proportions the game itself uses in Background.svelte,
# so the key art reads as the actual game rather than a separate illustration.
place(load('bg_land_sky.png'), 0, 0, W, H)
place(load('bg_land_boats.png'), -W * 0.12, 0, W * 1.25, H)
place(load('bg_land_water.png'), 0, H * 0.46, W, H * 0.24)
place(load('bg_land_nearboats.png'), 0, H * 0.50, W, H * 0.22)
place(load('bg_land_dock.png'), 0, H * 0.64, W, H * 0.36)
gulls = load('bg_land_gulls.png')
place(gulls, -W * 0.2, H * 0.05, W * 1.6, H * 0.30)
ov = load('bg_land_overlay.png').resize((W, H), Image.LANCZOS)
ov.putalpha(ov.getchannel('A').point(lambda v: int(v * 0.3)))
base.alpha_composite(ov)

base.convert('RGB').save('/tmp/keyart_bg_raw.png')
print('saved', base.size)
