"""Pack build_progress_bar3d.py's renders into the progressBar atlas (492x87 frames,
meta.scale 0.25 - the contract LoadingScreen's LoadingProgress expects) + a preview.

    python3 pack_progress_bar3d.py
"""
import json
import os

from PIL import Image

SRC = "render/bar3d"
OUT = "/home/kali/web-sdk/apps/bloody_seafood/static/assets/sprites/progressBar"
FW, FH = 492, 87
names = ["progressBar.png", "progressBarBackground.png", "progressBarFrame.png"]
ims = {n: Image.open(f"{SRC}/hi_{n}").convert("RGBA").resize((FW, FH), Image.LANCZOS) for n in names}
sheet = Image.new("RGBA", (FW * 3 + 4, FH + 2), (0, 0, 0, 0))
frames = {}
for i, n in enumerate(names):
    x = 1 + i * (FW + 2)
    sheet.alpha_composite(ims[n], (x, 1))
    frames[n] = {"frame": {"x": x, "y": 1, "w": FW, "h": FH}, "rotated": False, "trimmed": False,
                 "spriteSourceSize": {"x": 0, "y": 0, "w": FW, "h": FH}, "sourceSize": {"w": FW, "h": FH}}
sheet.save(f"{OUT}/progressBar.webp", lossless=True)
json.dump({"frames": frames, "meta": {"app": "bloody-seafood build_progress_bar3d", "image": "progressBar.webp",
                                     "format": "RGBA8888", "size": {"w": sheet.width, "h": sheet.height},
                                     "scale": "0.25"}}, open(f"{OUT}/progressBar.json", "w"), indent=1)
prev = Image.new("RGBA", (FW + 40, FH * 2 + 60), (30, 60, 90, 255))
for row, frac in enumerate((1.0, 0.45)):
    y = 20 + row * (FH + 20)
    prev.alpha_composite(ims["progressBarBackground.png"], (20, y))
    prev.alpha_composite(ims["progressBar.png"].crop((0, 0, int(FW * frac), FH)), (20, y))
    prev.alpha_composite(ims["progressBarFrame.png"], (20, y))
prev.convert("RGB").save("out/fixes/progress3d_preview.png")
print("packed", OUT)
