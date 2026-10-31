"""Bloody Seafood - the loading bar as 3D renders in the symbol studio's light, replacing
build_progress_bar.py's painted version (same atlas contract: 492x87 frames, meta.scale 0.25).

    blender -b -P build_progress_bar3d.py -- <out_dir> [samples]

A stadium-shaped bar: a bevelled brass rim tube (progressBarFrame), a sunken dark-iron
trough (progressBarBackground) and a glossy wet-blood fill bulging slightly above it
(progressBar). Each part is rendered alone, orthographic and front on, on a transparent
film at 4x, then pack_progress_bar3d() downsamples and writes the atlas.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_win_titles as wt  # noqa: E402  (iron / brass materials, the tank's kit)

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
SAMPLES = int(args[1]) if len(args) > 1 else 96
FW, FH = 492, 87
K = 4
W_U = 5.66            # bar length in scene units (492:87)
H_U = 1.0
R = H_U / 2

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def stadium(name, half_len, r, z, fill=False, extrude=0.0, bevel=0.0, mat=None):
    """A closed stadium (two semicircles joined), as a curve: a tube when bevelled, a slab
    when filled and extruded."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH" if fill else "NONE"
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = 8
    sp = cu.splines.new("POLY")
    pts = []
    for i in range(33):
        a = -math.pi / 2 + math.pi * i / 32
        pts.append((half_len + r * math.cos(a), r * math.sin(a)))
    for i in range(33):
        a = math.pi / 2 + math.pi * i / 32
        pts.append((-half_len + r * math.cos(a), r * math.sin(a)))
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts):
        p.co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new(name, cu)
    o.location.z = z
    if mat:
        o.data.materials.append(mat)
    scene.collection.objects.link(o)
    return o


def blood(nt):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.32, 0.008, 0.02, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.03
    b.inputs["Subsurface Weight"].default_value = 0.2
    b.inputs["Subsurface Radius"].default_value = (0.4, 0.02, 0.02)
    return b


m_iron = wt.material("iron", wt.iron)
m_brass = wt.material("brass", wt.brass)
m_blood = wt.material("blood", blood)
half = W_U / 2 - R
rim_r = 0.075
inner = R - rim_r * 1.6
parts = {
    "progressBarFrame.png": stadium("rim", half, R - rim_r, 0.08, bevel=rim_r, mat=m_brass),
    "progressBarBackground.png": stadium("trough", half, inner + 0.02, -0.04, fill=True, extrude=0.04, mat=m_iron),
    "progressBar.png": stadium("fill", half, inner - 0.02, 0.03, fill=True, extrude=0.05, bevel=0.03, mat=m_blood),
}

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = W_U
cam.data.sensor_fit = "HORIZONTAL"
cam.location = (0, 0, 10)
scene.camera = cam
scene.render.resolution_x, scene.render.resolution_y = FW * K, FH * K


def area(name, loc, energy, color, size):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.color = color; d.size = size
    o = bpy.data.objects.new(name, d); scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (-Vector(loc)).to_track_quat("-Z", "Y").to_euler()


# the symbol studio's scheme, camera on +Z: right +X, up +Y
area("key", (-3.0, 3.0, 3.0), 260, (1.0, 0.92, 0.82), 2.0)
area("rim", (3.5, -2.0, 1.2), 200, (0.35, 1.0, 0.85), 1.5)
area("fill", (1.0, -3.0, 2.5), 80, (1.0, 0.62, 0.35), 3.0)
area("strip", (0.0, 2.5, 1.0), 120, (1.0, 0.96, 0.9), 0.4)
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.12, 0.14, 0.15, 1)
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES; scene.cycles.use_adaptive_sampling = True
scene.render.film_transparent = True
scene.view_settings.view_transform = "Standard"; scene.view_settings.look = "Medium High Contrast"

os.makedirs(OUT, exist_ok=True)
for name, obj in parts.items():
    for o in parts.values():
        o.hide_render = o is not obj
    scene.render.filepath = os.path.join(OUT, "hi_" + name)
    bpy.ops.render.render(write_still=True)
print("BAR3D", OUT)
