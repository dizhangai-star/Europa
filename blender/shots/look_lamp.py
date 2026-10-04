"""Sprint 1 look spike C: the cryobot's one lamp in black water under the ice ceiling (seed of 07/08). Not a clip:

    Blender -b --factory-startup -P blender/shots/look_lamp.py -- --stills 1 --pct 50 --samples 64 \
        --stills-dir frames/look --id lamp

The point is the water volume's cost and look. Water: pure-water absorption per render channel (physics.water_rgb:
red gone in metres, blue reaches ~75 m) + particle scattering (physics.SEA_SCATTER, forward, SEA_G) as one
homogeneous volume (no textures: Cycles samples its distances analytically, no ray marching), plus marine-snow flecks
(a point cloud, 1–4 mm) close to the probe. Ice ceiling: the shell's base, undulating ±0.5 m, scalloped (bump),
sub-surface blue-white, almost no specular (ice in water: relative IOR 0.985). Probe: Ø physics.CRYO_D, 3 m, on a
tether into the ice; its lamp a spot of physics.CRYO_LAMP_W aimed out and down (`--lampdown` deg).
Options: --exposure --hang M (probe top below the ceiling) --lampdown --lampaz --cone --scatter --snow N --vbounces
         --novolume --lens
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
import numpy as np
from mathutils import Vector
import physics
from lib import nodes, rig, shot, europa_world
for m in (physics, nodes, rig, shot, europa_world):
    importlib.reload(m)
P, W = physics, europa_world

A = shot.args()
HANG = float(A.opt('hang', 2.0))
LEN = 3.0
RAD = P.CRYO_D / 2

sc = rig.new_scene('Look_Lamp')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, 1
sc.cycles.volume_bounces = int(A.opt('vbounces', 1))
sc.view_settings.exposure = float(A.opt('exposure', 0.0))

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w


def mat(name, build):
    m = bpy.data.materials.new(name)
    build(nodes.Graph(m))
    return m


# ---------------------------------------------------------------- ice ceiling (z ≈ 0, seen from below)
def ceiling_mat(g):
    tc = g.add('ShaderNodeTexCoord')
    pos = g.o(tc, 'Object')
    vor = g.add('ShaderNodeTexVoronoi', Scale=1 / 0.9, Randomness=0.9)
    g.set(vor, 'Vector', pos)
    sc_ = g.math('POWER', g.maprange(g.o(vor, 'Distance'), 0.0, 0.7), 0.6)               # scallops
    n = g.add('ShaderNodeTexNoise', Scale=1 / 0.08, Detail=5, Roughness=0.6)
    g.set(n, 'Vector', pos)
    h = g.math('ADD', g.math('MULTIPLY', sc_, 0.12), g.math('MULTIPLY', g.o(n, 'Fac'), 0.01))
    bp = g.add('ShaderNodeBump', Strength=1.0, Distance=1.0)
    g.set(bp, 'Height', h)
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.35)
    g.set(b, 'Base Color', (0.80, 0.90, 0.96))
    b.inputs['Specular IOR Level'].default_value = 0.05
    b.inputs['IOR'].default_value = 1.0 / 0.985
    b.inputs['Subsurface Weight'].default_value = 0.6
    b.inputs['Subsurface Radius'].default_value = (0.4, 0.9, 1.6)
    b.inputs['Subsurface Scale'].default_value = 0.4
    g.set(b, 'Normal', g.o(bp, 'Normal'))
    g.output(g.o(b, 'BSDF'))


n = 321
xs = np.linspace(-40.0, 40.0, n)
X, Y = np.meshgrid(xs, xs, indexing='ij')
Z = 1.0 * (W.fbm(X / 7, Y / 7, 4, 3) - 0.5) + 0.25 * (W.fbm(X / 1.5, Y / 1.5, 3, 9) - 0.5)
Z = Z + 0.35 * np.exp(-((X ** 2 + Y ** 2) / 1.2 ** 2))           # a shallow dome where the probe melted out
verts = np.stack([X, Y, Z], -1).reshape(-1, 3)
ii = np.arange(n - 1)[:, None] * n + np.arange(n - 1)[None, :]
faces = np.stack([ii, ii + n, ii + n + 1, ii + 1], -1).reshape(-1, 4)
me = bpy.data.meshes.new('Ceiling')
me.from_pydata(verts.tolist(), [], faces.tolist())
me.shade_smooth()
ceil = bpy.data.objects.new('Ceiling', me)
sc.collection.objects.link(ceil)
me.materials.append(mat('IceBase', ceiling_mat))

# ---------------------------------------------------------------- probe, tether, lamp
def metal(g):
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.32, Metallic=1.0)
    g.set(b, 'Base Color', (0.62, 0.62, 0.64))
    g.output(g.o(b, 'BSDF'))


def copper(g):
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.25, Metallic=1.0)
    g.set(b, 'Base Color', (0.80, 0.45, 0.30))
    g.output(g.o(b, 'BSDF'))


top = -HANG
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=RAD, depth=LEN - RAD, location=(0, 0, top - (LEN - RAD) / 2))
body = bpy.context.object
body.data.materials.append(mat('Titanium', metal))
bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=RAD, location=(0, 0, top - (LEN - RAD)))
nose = bpy.context.object
nose.data.materials.append(mat('HotNose', copper))
bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.008, depth=HANG + 1.0, location=(0, 0, top + (HANG + 1.0) / 2))
teth = bpy.context.object
teth.data.materials.append(mat('Tether', lambda g: g.output(g.o(g.add('ShaderNodeBsdfPrincipled', Roughness=0.6), 'BSDF'))))

DOWN = math.radians(float(A.opt('lampdown', 35.0)))
lz = top - 0.6
L = bpy.data.lights.new('Lamp', 'SPOT')
L.energy = P.CRYO_LAMP_W
L.spot_size = math.radians(float(A.opt('cone', 90.0)))
L.spot_blend = 0.4
L.shadow_soft_size = 0.02
L.color = (1.0, 1.0, 1.0)
lamp = bpy.data.objects.new('Lamp', L)
sc.collection.objects.link(lamp)
AZ = math.radians(float(A.opt('lampaz', 200.0)))                # 180 = −X (across the frame, away from the camera)
h = Vector((math.cos(AZ), math.sin(AZ), 0.0))
lamp.location = Vector((0.0, 0.0, lz)) + h * (RAD + 0.01)
d = Vector((h.x * math.cos(DOWN), h.y * math.cos(DOWN), -math.sin(DOWN)))
lamp.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- water + snow
if not A.opt('novolume'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -48.0))
    box = bpy.context.object
    box.name = 'Water'
    box.scale = (150.0, 150.0, 100.0)                         # top at z = +2: through the ice (opaque), closed
    def water(g):
        a = P.water_rgb()
        amax = max(a)
        ab = g.add('ShaderNodeVolumeAbsorption')
        g.set(ab, 'Color', tuple(1.0 - x / amax for x in a))      # Cycles: σa = density × (1 − colour)
        g.set(ab, 'Density', amax)
        s = g.add('ShaderNodeVolumeScatter')
        g.set(s, 'Color', (1.0, 1.0, 1.0))
        g.set(s, 'Density', float(A.opt('scatter', P.SEA_SCATTER)))
        g.set(s, 'Anisotropy', P.SEA_G)
        add = g.add('ShaderNodeAddShader')
        g.link(ab, 0, add, 0)
        g.link(s, 0, add, 1)
        g.nt.links.new(g.o(add, 0), g.out.inputs['Volume'])
    box.data.materials.append(mat('Water', water))

N = int(A.opt('snow', 40000))
rng = np.random.default_rng(3)
u = rng.normal(size=(N, 3))
u /= np.linalg.norm(u, axis=1)[:, None]
pts = u * (14.0 * rng.random(N) ** (1 / 3))[:, None] + np.array([0.0, -4.0, top - 2.0])
pts = pts[pts[:, 2] < -0.6]
pc = bpy.data.meshes.new('Snow')
pc.from_pydata(pts.tolist(), [], [])
snow = bpy.data.objects.new('Snow', pc)
sc.collection.objects.link(snow)
gn = bpy.data.node_groups.new('SnowPoints', 'GeometryNodeTree')
gn.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
gn.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
gi, go = gn.nodes.new('NodeGroupInput'), gn.nodes.new('NodeGroupOutput')
m2p = gn.nodes.new('GeometryNodeMeshToPoints')
rv = gn.nodes.new('FunctionNodeRandomValue')
rv.inputs['Min'].default_value, rv.inputs['Max'].default_value = 0.0005, 0.002
sm = gn.nodes.new('GeometryNodeSetMaterial')
sm.inputs['Material'].default_value = mat('Snow', lambda g: (lambda b: (g.set(b, 'Base Color', (0.8, 0.8, 0.78)),
                                                                      g.output(g.o(b, 'BSDF'))))(
    g.add('ShaderNodeBsdfPrincipled', Roughness=0.8)))
gn.links.new(gi.outputs[0], m2p.inputs['Mesh'])
gn.links.new(rv.outputs['Value'], m2p.inputs['Radius'])
gn.links.new(m2p.outputs['Points'], sm.inputs['Geometry'])
gn.links.new(sm.outputs['Geometry'], go.inputs[0])
snow.modifiers.new('Points', 'NODES').node_group = gn

# ---------------------------------------------------------------- camera
cam_loc = Vector((3.2, -4.2, top - 1.6))
aim = Vector((0.0, -0.6, top - 0.6))
cam = rig.camera(sc, cam_loc, aim, lens=float(A.opt('lens', 30.0)), fstop=2.8, focus=Vector((0, 0, top - 0.8)))
cam.data.clip_end = 300.0
print(f'NOTE look_lamp: water σa RGB {tuple(round(x, 4) for x in P.water_rgb())}, scatter '
      f'{float(A.opt("scatter", P.SEA_SCATTER))}/m g {P.SEA_G}, lamp {P.CRYO_LAMP_W} W, {len(pts):,} flecks, '
      f'volume bounces {sc.cycles.volume_bounces}')

shot.run(sc, A, tag='lamp')
