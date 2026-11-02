#!/bin/bash
# v5 tile + cover from the closed-mouth side-profile hero (bs-render v5_hero.sh)
cd "$(dirname "$0")/.."
H=/root/bs-render/render/rig/h1_shark_v3/hero_v5/win_0001.png
HERO=$H VERSION=v5 HERO_ROT=-14 SH_K=0.62 SX_DX=120 SY_DY=40 python3 thumbnails/build_tile_v2.py tile
HERO=$H VERSION=v5 HERO_ROT=-10 SH_K=0.72 SX_DX=0 SY_DY=10 python3 thumbnails/build_tile_v2.py cover
