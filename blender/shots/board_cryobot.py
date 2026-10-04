"""Sprint 2.2 board: the cryobot (lib/cryobot.py) on a dark studio set, lying along +X (nose at the origin, lamp port
toward the camera). Not a clip; one frame per view. The water look is look_lamp.py (now with this probe).

    Blender -b --factory-startup -P blender/shots/board_cryobot.py -- --views full,nose,tail,open --stills 1,2,3,4 \
        --pct 50 --samples 64 --stills-dir frames/cryobot --id studio

Views: full (whole probe, 50 mm) · nose (head, bay, swimmers, 70 mm) · tail (top, pucks on the tether, 70 mm) ·
open (the swimmers drifting out, 50 mm; swimmers keyed open on that frame only) · top (looking down the tail).
Options: --open M (how far the swimmers drift in `open`, default 0.18) --lampoff 1 --exposure
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
from mathutils import Matrix, Vector
import physics
from lib import nodes, rig, shot, cryobot
for m in (physics, nodes, rig, shot, cryobot):
    importlib.reload(m)
P = physics

A = shot.args()
sc = rig.new_scene('Board_Cryobot')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.view_settings.exposure = float(A.opt('exposure', 0.0))

bot = cryobot.build(sc, P, tether=1.6, pucks_above=(0.45, 1.15), lamp=not A.opt('lampoff'))
root = bot['root']
root.matrix_world = Matrix.Rotation(math.radians(90), 4, 'Y') @ Matrix.Rotation(math.radians(-90), 4, 'Z')
L = bot['top']                                                    # probe length along +X

rig._world(sc, (0.030, 0.032, 0.036), (0.004, 0.004, 0.005))
rig._area(sc, 'Key', (0.6, -3.0, 2.4), (1.2, 0, 0), 2.0, 450.0, (1.0, 0.97, 0.93), size_y=1.2)
rig._area(sc, 'Fill', (2.5, -2.5, -0.6), (1.5, 0, 0), 2.5, 120.0, (0.85, 0.92, 1.0))
rig._area(sc, 'Rim', (1.5, 2.6, 1.6), (1.5, 0, 0), 3.0, 500.0, (0.9, 0.95, 1.0), size_y=0.6)

VIEWS = {'full': ((L / 2, -5.6, 1.5), (L / 2 + 0.15, 0, 0), 50.0),
         'nose': ((0.15, -1.25, 0.45), (0.45, 0, 0), 70.0),
         'tail': ((L + 0.55, -1.3, 0.75), (L + 0.25, 0, 0), 60.0),
         'open': ((0.55, -1.7, 0.85), (0.70, 0, 0), 50.0),
         'top': ((L + 0.9, -0.25, 0.35), (L, 0, 0), 85.0)}
names = A.opt('views', 'full,nose,tail,open').split(',')
cam = rig.camera(sc, (0, -3, 0), (0, 0, 0), lens=50.0, fstop=8.0)
cam.data.clip_end = 100.0
for i, n in enumerate(names):
    loc, tgt, lens = VIEWS[n]
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    cam.data.dof.focus_distance = (Vector(tgt) - Vector(loc)).length
    cam.keyframe_insert('location', frame=i + 1)
    cam.keyframe_insert('rotation_euler', frame=i + 1)
    cam.data.keyframe_insert('lens', frame=i + 1)
    cam.data.dof.keyframe_insert('focus_distance', frame=i + 1)

# the swimmers drift out on the 'open' frame only (stills land on the keys)
OPEN = float(A.opt('open', 0.18))
rng = np.random.default_rng(5)
for ob in bot['swimmers']:
    rest = ob.matrix_basis.copy()
    a = ob.rotation_euler.z
    d = OPEN * (0.6 + 0.8 * rng.random())
    moved = (Vector(ob.location) + Vector((math.cos(a) * d, math.sin(a) * d, OPEN * 0.5 * (rng.random() - 0.5))),
             (rng.normal(0, 0.4), rng.normal(0, 0.4), a + rng.normal(0, 0.5)))
    for i, n in enumerate(names):
        if n == 'open':
            ob.location, ob.rotation_euler = moved
        else:
            ob.matrix_basis = rest
        ob.keyframe_insert('location', frame=i + 1)
        ob.keyframe_insert('rotation_euler', frame=i + 1)
sc.frame_start, sc.frame_end = 1, len(names)
print(f'NOTE board_cryobot: views {names}, length {L:.2f} m, {len(bot["swimmers"])} swimmers, '
      f'{len(bot["pucks"])} pucks, lamp {"on" if bot["lamp"] else "off"}')
shot.run(sc, A, tag='cryobot')
