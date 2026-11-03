#!/bin/bash
# v5.4 tile + cover from the v5.4 hero (bs-render v54_hero.sh: eyes + lids, closed mouth),
# with the symbols' hand-crafted finish (CRAFT=1), plus background-only plates (storm and day)
cd "$(dirname "$0")/.."
H=/root/bs-render/render/rig/h1_shark_v3/hero_v54side/hero_fixed.png
HERO=$H VERSION=v5_4 CRAFT=1 HERO_ROT=-14 SH_K=0.62 SX_DX=120 SY_DY=40 python3 thumbnails/build_tile_v2.py tile
HERO=$H VERSION=v5_4 CRAFT=1 HERO_ROT=-10 SH_K=0.72 SX_DX=0 SY_DY=10 python3 thumbnails/build_tile_v2.py cover
for d in "" 1; do for lay in tile cover; do DAY=$d BG_ONLY=1 VERSION=v5_4 python3 thumbnails/build_tile_v2.py $lay; done; done
