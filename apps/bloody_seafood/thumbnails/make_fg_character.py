"""Stake Media Editor layers (v5.4 daylight): the CHARACTER foreground alone - the
closed-mouth side-profile shark from the v5.4 rig, day-graded and given the symbols'
hand-crafted finish, trimmed tight on transparency - plus a brighter tile background with
calm detail under the editor's title band, and placement mockups.
    python3 thumbnails/make_fg_character.py"""
import ast, os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
os.chdir(os.path.dirname(os.path.abspath(__file__)))
HERO = '/root/bs-render/render/rig/h1_shark_v3/hero_v54side/hero_fixed.png'
ns = {'np': np, 'cv2': cv2, 'Image': Image}
src = ast.parse(open('/root/bs-render/pack_symbol3d.py').read())
for n in src.body:
    if getattr(n, 'name', '') == 'craft' or (isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'RIM_DIR'):
        exec(compile(ast.Module([n], []), 'craft', 'exec'), ns)
bsrc = ast.parse(open('build_tile_v2.py').read())
bns = {'np': np, 'Image': Image, 'DAY': True}
for n in bsrc.body:
    if getattr(n, 'name', '') == 'day_grade':
        exec(compile(ast.Module([n], []), 'day', 'exec'), bns)

shark = Image.open(HERO).convert('RGBA')
shark = shark.rotate(-8, resample=Image.BICUBIC, expand=True)        # a slight rising lunge
shark = shark.crop(shark.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox())
k = 1600 / max(shark.size)
shark = shark.resize((round(shark.width * k), round(shark.height * k)), Image.LANCZOS)
shark = bns['day_grade'](shark)
shark = ns['craft'](shark, 900)          # outline/rim widths scaled for a ~900 px-tall subject
# clean alpha: no colour carried in fully transparent pixels, then pad 8 px
a = np.asarray(shark).copy(); a[a[..., 3] == 0, :3] = 0
shark = Image.fromarray(a)
P = 8
out = Image.new('RGBA', (shark.width + 2 * P, shark.height + 2 * P), (0, 0, 0, 0)); out.alpha_composite(shark, (P, P))
stem = 'bloody_seafood_fg_character_v5_4_day'
out.save(stem + '.png', optimize=True); out.save(stem + '.webp', quality=92, method=6, exact=True)
for name, col in (('black', (0, 0, 0, 255)), ('white', (255, 255, 255, 255))):
    t = Image.new('RGBA', out.size, col); t.alpha_composite(out); t.convert('RGB').save(f'{stem}_on_{name}_check.jpg', quality=88)
print(stem, out.size)

# tile background: brighter, and the bottom 40% (under the editor's title band) calmed
bg = Image.open('bloody_seafood_tile_3x4_v5_4_bg_day.webp').convert('RGB')
bg = ImageEnhance.Brightness(bg).enhance(1.1)
W, H = bg.size
soft = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(6))).enhance(0.92)
m = np.clip((np.arange(H) - H * 0.55) / (H * 0.1), 0, 1)[:, None].repeat(W, 1)
bg = Image.composite(soft, bg, Image.fromarray((m * 255).astype(np.uint8)))
bg.save('bloody_seafood_tile_3x4_v5_4_bg_day.webp', quality=86, method=6)
bg.save('bloody_seafood_tile_3x4_v5_4_bg_day_preview.png')

# mockups: 16:9 with the shark in the right 60% focus box; 3:4 with it in the upper-middle
# key focus area and a stand-in for Stake's red title band over the bottom 40%
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
cov = Image.open('bloody_seafood_cover_16x9_v5_4_bg_day.webp').convert('RGBA')
box = (round(1920 * 0.4), 0, 1920, 1080)
f = out.copy(); f.thumbnail((round((box[2] - box[0]) * 0.92), round(1080 * 0.8)), Image.LANCZOS)
cov.alpha_composite(f, (box[0] + (box[2] - box[0] - f.width) // 2, (1080 - f.height) // 2))
d = ImageDraw.Draw(cov); d.rectangle(box, outline=(255, 255, 0, 255), width=3)
cov.convert('RGB').save('mockup_cover_16x9_v5_4_day.jpg', quality=88)
til = bg.convert('RGBA')
f = out.copy(); f.thumbnail((round(W * 0.9), round(H * 0.42)), Image.LANCZOS)
til.alpha_composite(f, ((W - f.width) // 2, round(H * 0.12)))
band = Image.new('RGBA', (W, round(H * 0.4)), (0, 0, 0, 0))
ba = np.linspace(0, 235, band.height)[:, None].repeat(W, 1).astype(np.uint8)
band = Image.merge('RGBA', [Image.new('L', band.size, 150), Image.new('L', band.size, 10), Image.new('L', band.size, 18), Image.fromarray(ba)])
til.alpha_composite(band, (0, H - band.height))
d = ImageDraw.Draw(til)
for txt, fnt, y in (('BLOODY SEAFOOD', font, H - 230), ('STEEL GAMING', small, H - 140)):
    w = d.textlength(txt, font=fnt); d.text(((W - w) / 2, y), txt, fill=(255, 255, 255, 255), font=fnt)
til.convert('RGB').save('mockup_tile_3x4_v5_4_day.jpg', quality=88)
print('mockups done')
