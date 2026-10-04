"""Sprint 2.3 board: the ice shell from inside (lib/shell.py) round the cryobot (lib/cryobot.py). Not a clip; one
frame per view, one depth per run.

    Blender -b --factory-startup -P blender/shots/board_shell.py -- --depth 30 --views lid,probe,nose \
        --stills 1,2,3 --pct 40 --samples 64 --stills-dir frames/shell --id d30

Views (camera keyed per frame): lid (outside the cut, the probe's top, the open column narrowing, the frozen column
above with its axis line, 35 mm) · probe (whole probe through the cut, 28 mm) · nose (melt head in its pocket, 50 mm)
· inside (camera 2.5 m off the axis inside the ice: the honest view where the ice is clear, 24 mm) · beam (wide,
the lamp's cone across the frame: what it lights in clear ice). Each view has its own EV offset and port azimuth.
Options: --depth M (nose, m down) --cut M (cut face in front of the axis) --face glass|none --lampaz DEG (port
azimuth for every view; 0 = +X, −90 = toward the camera side) --pucks h1,h2 (dropped pucks, m above the top) --sigma S (the ice's
σs per m instead of physics.pore at the depth: look-dev) --aniso 1 (true g instead of the
similarity σs(1 − g), g 0: same diffusion, ~4× fewer scattering events) --exposure EV (added to the views') --vbounces N
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
from mathutils import Vector
import physics
from lib import nodes, rig, shot, cryobot, shell
for m in (physics, nodes, rig, shot, cryobot, shell):
    importlib.reload(m)
P = physics

A = shot.args()
DEPTH = float(A.opt('depth', 30.0))
sc = rig.new_scene('Board_Shell')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.cycles.volume_bounces = int(A.opt('vbounces', 128))
sc.cycles.max_bounces = max(sc.cycles.max_bounces, sc.cycles.volume_bounces + 8)

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w

pucks = tuple(float(x) for x in A.opt('pucks', '').split(',') if x)
sh = shell.build(sc, P, DEPTH, cut=float(A.opt('cut', 0.30)), face=A.opt('face', 'glass'),
                 sigma=float(A.opt('sigma')) if A.opt('sigma') else None, similar=not A.opt('aniso'))
top = P.CRYO_LEN
bot = cryobot.build(sc, P, tether=sh['front_z'] - top + 9.0, pucks_above=pucks)

F = sh['front_z']
EV = float(A.opt('exposure', 0.0))
# name: camera, target, lens, EV offset, lamp port azimuth (0 = +X, across the frame; −90 = toward the camera)
VIEWS = {'lid': ((0.8, -3.4, top + 0.4), (0.0, 0.0, top + 0.5), 35.0, 3.0, -40.0),
         'probe': ((1.1, -5.2, 1.6), (0.0, 0.0, 1.6), 28.0, 0.0, -40.0),
         'nose': ((0.35, -1.5, 0.35), (0.0, 0.0, 0.25), 50.0, -1.0, 20.0),
         'inside': ((-1.5, -2.0, 2.4), (0.0, 0.0, 1.2), 24.0, 2.0, 0.0),
         'beam': ((-0.6, -4.5, 3.4), (1.6, 0.0, -0.6), 24.0, 3.0, 0.0)}
names = A.opt('views', 'lid,probe,nose').split(',')
cam = rig.camera(sc, (0, -3, 0), (0, 0, 0), lens=35.0, fstop=4.0)
cam.data.clip_end = 200.0
for i, n in enumerate(names):
    loc, tgt, lens, ev, laz = VIEWS[n]
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    cam.data.dof.focus_distance = (Vector(tgt) - Vector(loc)).length
    sc.view_settings.exposure = EV + ev
    bot['root'].rotation_euler = (0.0, 0.0, math.radians(float(A.opt('lampaz', laz))))
    cam.keyframe_insert('location', frame=i + 1)
    cam.keyframe_insert('rotation_euler', frame=i + 1)
    cam.data.keyframe_insert('lens', frame=i + 1)
    cam.data.dof.keyframe_insert('focus_distance', frame=i + 1)
    sc.view_settings.keyframe_insert('exposure', frame=i + 1)
    bot['root'].keyframe_insert('rotation_euler', frame=i + 1)
sc.frame_start, sc.frame_end = 1, len(names)
print(f'NOTE board_shell: depth {DEPTH:g} m, views {names}, front {F:.2f} m (probe top {top:.2f}), '
      f'pucks {pucks}, volume bounces {sc.cycles.volume_bounces}')
shot.run(sc, A, tag='shell')
