"""Sprint 3.7 board: the open water tube above the exit hole at the breakthrough (physics.tube07, lib/ocean.tube),
seen from the water. Not a clip; one frame per view.

    Blender -b --factory-startup -P blender/shots/board_tube.py -- --views mouth,below,side \
        --stills 1,2,3 --pct 40 --samples 64 --stills-dir frames/tube --id clear [--mush 1]

The probe hangs where 07's brake stops it (physics.fit07: nose `stop` m below the base), its tether up the tube's
axis to where the tube has frozen shut. Views: mouth (0.9 m under the mouth, just off the axis, looking straight up,
24 mm: up the tube) · below (2.5 m down, 0.45 m off the axis, 35 mm, looking up into the mouth) · side (4 m off,
24 mm: the lit ceiling round the hole). Options: --mush 1 (⚠ the wall's skin, physics.MUSH) or --mush T,S,G
--narrow 1 (bore = the head's, 256 m tube) --uplamp W --upcone DEG (test: a tail lamp up the hole) --lampaz DEG --exposure EV --gbounces N --nose M (override the stop)
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
sc = rig.new_scene('Board_Tube')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.cycles.volume_bounces = int(A.opt('vbounces', 4))
gb = int(A.opt('gbounces', 128))
sc.cycles.glossy_bounces = gb
sc.cycles.transmission_bounces = max(16, gb // 4)
sc.cycles.max_bounces = gb + 32

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w

t0 = time.time()
tb = P.tube07(P.CRYO_D / 2 if A.opt('narrow') else None)
oc = ocean.build(sc, P, kind='melt', half=60.0, hole_r=tb['a'] + 0.001)
mush = A.opt('mush')
if mush:
    mush = P.MUSH if mush == '1' else tuple(float(x) for x in mush.split(','))
tu = ocean.tube(sc, P, oc, tb['prof'], mush=mush or None)
if A.opt('noslab'):                                   # test: the tube without the milky base ice round its foot
    oc['ice'].hide_render = True
LEN = P.CRYO_LEN
nose = -float(A.opt('nose', P.fit07()['stop']))
bot = cryobot.build(sc, P, loc=(0.0, 0.0, nose), tether=tb['length'] - (nose + LEN) - 0.5)
bot['root'].rotation_euler = (0.0, 0.0, math.radians(float(A.opt('lampaz', 200.0))))
if A.opt('uplamp'):                                   # test only: a lamp on the tail looking back up the hole
    ld = bpy.data.lights.new('UpLamp', 'SPOT')
    ld.energy = float(A.opt('uplamp'))
    ld.spot_size = math.radians(float(A.opt('upcone', 30.0)))
    ld.shadow_soft_size = 0.02
    up = bpy.data.objects.new('UpLamp', ld)
    sc.collection.objects.link(up)
    up.location = (0.06, 0.0, nose + LEN + 0.03)
    up.rotation_euler = (math.pi, 0.0, 0.0)              # spots aim down their −Z
print(f'NOTE board_tube: build {time.time() - t0:.1f} s, tube {tb["length"]:.0f} m, bore {tb["a"]:.3f} m, '
      f'nose {nose:.2f} m')

EV = float(A.opt('exposure', 0.0))
# name: camera, target, lens, EV offset
VIEWS = {'mouth': ((0.06, -0.04, -0.9), (0.0, 0.0, 30.0), 24.0, 4.0),
         'below': ((0.45, -0.25, -2.5), (0.0, 0.0, 0.3), 35.0, 4.0),
         'side': ((3.0, -2.8, -2.2), (0.0, 0.0, -0.4), 24.0, 4.0)}
names = A.opt('views', 'mouth,below,side').split(',')
cam = rig.camera(sc, (0, -3, -3), (0, 0, -3), lens=35.0, fstop=4.0)
cam.data.clip_end = 1000.0
for i, n in enumerate(names):
    loc, tgt, lens, ev = VIEWS[n]
    cam.location = loc
    d = Vector(tgt) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    cam.data.dof.focus_distance = 3.0 if n == 'mouth' else d.length
    sc.view_settings.exposure = EV + ev
    for ob, path in ((cam, 'location'), (cam, 'rotation_euler'), (cam.data, 'lens'),
                     (cam.data.dof, 'focus_distance'), (sc.view_settings, 'exposure')):
        ob.keyframe_insert(path, frame=i + 1)
sc.frame_start, sc.frame_end = 1, len(names)
print(f'NOTE board_tube: views {names}, glossy bounces {gb}')
shot.run(sc, A, tag='tube')
