"""Bloody Seafood - a seamless 3D hawser texture for the anticipation ropes (Anticipation.svelte
bends it along a PIXI.MeshRope, so it can thrum like a rope under strain).

    blender -b -P build_rope3d.py -- <out.png> [length_px] [samples]

Three-strand laid rope: three helical strands of tarred hemp twisted round the axis, each
strand itself fibrous (noise bump), lit with the symbol studio's scheme (warm key upper
left, teal rim behind, warm low fill). Orthographic, side on, along X; exactly PERIODS
twists across the frame so the texture repeats seamlessly. Transparent film. The height is
a power-of-two fraction of the length so it can repeat on WebGL1.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
LEN_PX = int(args[1]) if len(args) > 1 else 1024
SAMPLES = int(args[2]) if len(args) > 2 else 96
PERIODS = 3
PITCH = 1.0                  # one full twist of a strand per unit along X
R_AXIS = 0.13                # strand centre to rope axis
R_STRAND = 0.15
H_PX = LEN_PX // 4           # 1024 x 256: 0.75 units tall, the 0.56 rope plus margin

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def hemp():
    m = bpy.data.materials.new("hemp")
    m.use_nodes = True
    nt = m.node_tree
    n, l = nt.nodes, nt.links
    b = n["Principled BSDF"]
    co = n.new("ShaderNodeTexCoord").outputs["Object"]
    # fibres run along the strand: stretched noise in the strand's own direction
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (6, 60, 60)
    l.new(co, mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 10
    l.new(mp.outputs["Vector"], nz.inputs["Vector"])
    col = n.new("ShaderNodeMix"); col.data_type = "RGBA"
    col.inputs["A"].default_value = (0.42, 0.27, 0.12, 1)
    col.inputs["B"].default_value = (0.2, 0.11, 0.04, 1)
    l.new(nz.outputs["Fac"], col.inputs["Factor"]); l.new(col.outputs["Result"], b.inputs["Base Color"])
    bump = n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6
    l.new(nz.outputs["Fac"], bump.inputs["Height"]); l.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.7
    return m


mat = hemp()
x0, x1 = -PERIODS * PITCH / 2 - 0.5, PERIODS * PITCH / 2 + 0.5  # overrun so the ends are off-frame
for k in range(3):
    cu = bpy.data.curves.new(f"strand{k}", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = R_STRAND
    cu.bevel_resolution = 6
    cu.resolution_u = 4
    sp = cu.splines.new("POLY")
    n = 600
    sp.points.add(n - 1)
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        a = 2 * math.pi * x / PITCH + 2 * math.pi * k / 3
        sp.points[i].co = (x, R_AXIS * math.cos(a), R_AXIS * math.sin(a), 1)
    o = bpy.data.objects.new(f"strand{k}", cu)
    o.data.materials.append(mat)
    scene.collection.objects.link(o)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = PERIODS * PITCH
cam.location = (0, -5, 0)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam
scene.render.resolution_x, scene.render.resolution_y = LEN_PX, H_PX
cam.data.sensor_fit = "HORIZONTAL"


def area(name, loc, energy, color, size):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.color = color; d.size = size
    o = bpy.data.objects.new(name, d); scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (-Vector(loc)).to_track_quat("-Z", "Y").to_euler()


# the symbol studio's scheme in camera terms (right +X, up +Z, towards camera -Y)
area("key", (-1.3, -1.2, 1.4), 120, (1.0, 0.92, 0.82), 1.2)
area("rim", (1.5, 1.2, 0.8), 160, (0.35, 1.0, 0.85), 1.0)
area("fill", (0.6, -1.0, -1.3), 40, (1.0, 0.62, 0.35), 2.0)
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.12, 0.14, 0.15, 1)

scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES; scene.cycles.use_adaptive_sampling = True
scene.render.film_transparent = True
scene.view_settings.view_transform = "Standard"; scene.view_settings.look = "Medium High Contrast"
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("ROPE", OUT, LEN_PX, H_PX)
