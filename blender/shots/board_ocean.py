"""Sprint 2.4 board: the ocean under the ice (lib/ocean.py) with the cryobot (lib/cryobot.py). Not a clip; one frame
per view.

    Blender -b --factory-startup -P blender/shots/board_ocean.py -- --views emerge,up,level,wide,down \
        --stills 1,2,3,4,5 --pct 40 --samples 64 --stills-dir frames/ocean --id melt

Views (camera, probe and EV keyed per frame): emerge (07's start: the probe half out of its hole, looking up at the
ceiling, 24 mm) · up (probe hanging 2 m under the ceiling, the lit base above it, 24 mm) · level (across the beam
into the open water, 30 mm: what drifts in it) · wide (16 mm from 18 m: how far the lamp lights the base) · down (08:
camera beside the hole looking straight down the tether at the probe `--sinks` m below; one frame per sink).
Options: --kind melt|freeze --sinks 10,30,60,100 --lampaz DEG --exposure EV (added to the views') --motes 1
--frazil 1 --cloud x,y,z,r (sphere the particles fill; default round the level view) --scatter S --novolume
--half M --n N (grid points per side)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import time
import bpy
from mathutils import Vector
import physics
from lib import nodes, rig, shot, europa_world, cryobot, ocean
for m in (physics, nodes, rig, shot, europa_world, cryobot, ocean):
    importlib.reload(m)
P = physics

A = shot.args()
sc = rig.new_scene('Board_Ocean')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.cycles.volume_bounces = int(A.opt('vbounces', 2))

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w

t0 = time.time()
oc = ocean.build(sc, P, kind=A.opt('kind', 'melt'), half=float(A.opt('half', 60.0)), n=int(A.opt('n', 801)),
                 scatter=float(A.opt('scatter')) if A.opt('scatter') else None)
if A.opt('novolume'):
    oc['water'].hide_render = True
LEN = P.CRYO_LEN
sinks = [float(x) for x in A.opt('sinks', '10,30,60,100').split(',')]
bot = cryobot.build(sc, P, loc=(0.0, 0.0, -LEN - 2.0), tether=oc['ztop'] + 4.0 + max(sinks))
cx, cy, cz, cr = (float(x) for x in A.opt('cloud', '-1.0,-1.5,-4.0,3.5').split(','))
if A.opt('motes'):
    ocean.motes(sc, P, (cx, cy, cz), cr * 2.0, oc)
if A.opt('frazil'):
    ocean.frazil(sc, P, (cx, cy, cz), cr, oc)
print(f'NOTE board_ocean: build {time.time() - t0:.1f} s')

EV = float(A.opt('exposure', 0.0))
# name: camera, target, lens, EV offset, lamp port azimuth (0 = +X; 200 ≈ away-left), nose z
VIEWS = {'emerge': ((2.0, -2.6, -2.4), (0.0, 0.0, -0.3), 24.0, 2.0, 60.0, -1.3),
         'up': ((1.6, -3.0, -7.6), (0.3, 0.4, -2.2), 20.0, 3.0, 60.0, -LEN - 2.0),
         'level': ((3.2, -4.2, -3.6), (0.0, -0.6, -2.6), 30.0, 4.0, 200.0, -LEN - 2.0),
         'wide': ((11.0, -15.0, -6.0), (-1.0, 2.0, -1.5), 16.0, 5.0, 120.0, -LEN - 2.0)}
names = []
for n in A.opt('views', 'emerge,up,level,wide,down').split(','):
    names += [f'down{s:g}' for s in sinks] if n == 'down' else [n]
cam = rig.camera(sc, (0, -3, -3), (0, 0, -3), lens=35.0, fstop=4.0)
cam.data.clip_end = 600.0
for i, n in enumerate(names):
    if n.startswith('down'):
        s = float(n[4:])
        nose = -LEN - s
        loc, tgt, lens, ev, laz = (0.55, -0.35, -0.4), (0.15, -0.1, nose - 2.0), 35.0, 4.0, 160.0
    else:
        loc, tgt, lens, ev, laz, nose = VIEWS[n]
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    cam.data.dof.focus_distance = (Vector((0, 0, nose + 1.5)) - Vector(loc)).length
    sc.view_settings.exposure = EV + ev
    bot['root'].location.z = nose
    bot['root'].rotation_euler = (0.0, 0.0, math.radians(float(A.opt('lampaz', laz))))
    cam.keyframe_insert('location', frame=i + 1)
    cam.keyframe_insert('rotation_euler', frame=i + 1)
    cam.data.keyframe_insert('lens', frame=i + 1)
    cam.data.dof.keyframe_insert('focus_distance', frame=i + 1)
    sc.view_settings.keyframe_insert('exposure', frame=i + 1)
    bot['root'].keyframe_insert('location', frame=i + 1)
    bot['root'].keyframe_insert('rotation_euler', frame=i + 1)
sc.frame_start, sc.frame_end = 1, len(names)
print(f'NOTE board_ocean: views {names}, volume bounces {sc.cycles.volume_bounces}')
shot.run(sc, A, tag='ocean')
