"""Foreground layer for the studio's title art: the finished composite minus its background,
on full transparency, registered pixel-for-pixel so fg over bg reproduces the composite.
    python3 thumbnails/split_fg.py <composite.webp> <bg.webp> <alpha.png> <out stem>
alpha = the foreground's coverage (build_tile_v2.py FG_ALPHA); colour is un-composited
(c = (C - B(1-a)) / a), so there is no background fringe in the soft edges."""
import sys
import numpy as np
from PIL import Image
C = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
B = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.float32)
A = np.asarray(Image.open(sys.argv[3])).astype(np.float32) / 255
a = np.where(A < 2 / 255, 0, A)[..., None]
F = np.where(a > 0, (C - B * (1 - a)) / np.maximum(a, 1e-3), 0).clip(0, 255)
out = np.dstack([F, a[..., 0] * 255]).round().astype(np.uint8)
im = Image.fromarray(out, 'RGBA')
im.save(sys.argv[4] + '.png', optimize=True)
im.save(sys.argv[4] + '.webp', quality=92, method=6, exact=True)
# checks: fg over bg vs the composite, and the edges on black and on white
back = Image.fromarray(B.astype(np.uint8)).convert('RGBA'); back.alpha_composite(im)
diff = np.abs(np.asarray(back.convert('RGB')).astype(int) - C.astype(int))
print(sys.argv[4], im.size, 'fg-over-bg vs composite: mean', round(float(diff.mean()), 3), 'p99.9', int(np.percentile(diff, 99.9)))
for name, col in (('black', (0, 0, 0, 255)), ('white', (255, 255, 255, 255))):
    t = Image.new('RGBA', im.size, col); t.alpha_composite(im); t.convert('RGB').save(f'{sys.argv[4]}_on_{name}_check.jpg', quality=88)
