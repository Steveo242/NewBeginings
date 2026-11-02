"""Half-resolution mirror of static/assets/sprites for low-memory devices (phones).

    python3 tools/make_mobile_sprites.py        (run from apps/bloody_seafood)

Writes static/assets/sprites_m/ with the same tree:
- every spritesheet JSON: its image at half size, every frame / spriteSourceSize /
  sourceSize halved and meta.scale halved, so Pixi sees the same logical sizes
- every loose image: half size, saved as <name>@0.5x.<ext> - Pixi reads the @0.5x
  resolution suffix, so the texture keeps its logical size
Halving every side quarters the GPU memory, and no page ends up over 2048 px (the full
set's 4096 sheets become 2048). game/assets.ts switches to this tree on phones.
"""
import glob
import json
import os
import shutil

from PIL import Image

SRC = "static/assets/sprites"
DST = "static/assets/sprites_m"
shutil.rmtree(DST, ignore_errors=True)
done_images = set()


def half(p_in, p_out):
    im = Image.open(p_in)
    im = im.convert("RGBA") if im.mode not in ("RGB", "RGBA") else im
    w, h = im.size
    im = im.resize((max(1, round(w / 2)), max(1, round(h / 2))), Image.LANCZOS)
    os.makedirs(os.path.dirname(p_out), exist_ok=True)
    ext = os.path.splitext(p_out)[1].lower()
    if ext == ".webp":
        im.save(p_out, quality=92, method=6)
    elif ext in (".jpg", ".jpeg"):
        im.convert("RGB").save(p_out, quality=90)
    else:
        im.save(p_out, optimize=True)


def halve_rect(r):
    return {k: round(v / 2) for k, v in r.items()}


n_sheets = n_loose = 0
for js in glob.glob(f"{SRC}/**/*.json", recursive=True):
    if js.endswith(".basis.json"):
        continue
    try:
        data = json.load(open(js))
    except Exception:
        continue
    meta = data.get("meta", {})
    if "image" not in meta or "frames" not in data:
        continue
    rel = os.path.relpath(js, SRC)
    img = os.path.join(os.path.dirname(js), meta["image"])
    if not os.path.exists(img):
        continue
    out_img = os.path.join(DST, os.path.dirname(rel), meta["image"])
    half(img, out_img)
    done_images.add(os.path.abspath(img))
    frames = data["frames"]
    items = frames.items() if isinstance(frames, dict) else [(None, f) for f in frames]
    for _, f in items:
        for k in ("frame", "spriteSourceSize"):
            if k in f:
                f[k] = halve_rect(f[k])
        if "sourceSize" in f:
            f["sourceSize"] = halve_rect(f["sourceSize"])
    meta["scale"] = str(float(meta.get("scale", 1)) / 2)
    if "size" in meta:
        meta["size"] = halve_rect(meta["size"])
    os.makedirs(os.path.dirname(os.path.join(DST, rel)), exist_ok=True)
    json.dump(data, open(os.path.join(DST, rel), "w"))
    n_sheets += 1

for img in glob.glob(f"{SRC}/**/*", recursive=True):
    if not img.lower().endswith((".png", ".webp", ".jpg", ".jpeg")) or os.path.abspath(img) in done_images:
        continue
    rel = os.path.relpath(img, SRC)
    base, ext = os.path.splitext(rel)
    half(img, os.path.join(DST, base + "@0.5x" + ext))
    n_loose += 1

size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(DST) for f in fs)
print(f"sprites_m: {n_sheets} sheets, {n_loose} loose images, {size / 2**20:.1f} MB")
