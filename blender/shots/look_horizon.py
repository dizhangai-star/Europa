"""Sprint 1 look spike A: the Conamara horizon at night, lit by full Jupiter alone (seed of 01 "horizon").
Not a clip; run directly:

    Blender -b --factory-startup -P blender/shots/look_horizon.py -- --stills 1 --pct 50 --samples 64 \
        --stills-dir frames/look --id horizon --view jupiter

Chaos ground (europa_world.Ground since Sprint 2.1; Sprint 1 ran the spike): convex ice plates (physics.CHAOS) with
cliffs, talus aprons, tilted ridged tops, in a hummocky matrix; a lane toward Jupiter stays open. The Sun is below the
eastern horizon (`--elong`, default 178), so the ground's only light is Jupiter's lit ¾ disc, made a light source by
jupiter.lamp. `--view jupiter` (heading +18°: the disc left of centre, block walls in silhouette) | `away` (heading
170°: the walls that face Jupiter, lit, their shadows running away from it) | `side` (125°: raking light on the walls) | `wide` (14 mm, heading 42°: the disc at the left edge, walls
raking on the right). --heading overrides.
Options: --view --heading --elong --lens --exposure --seed --eye --tilt
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
from lib import nodes, rig, shot, europa_world, jupiter, sky
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS

A = shot.args()
VIEW = A.opt('view', 'jupiter')
HEAD = float(A.opt('heading', {'jupiter': 18.0, 'away': 170.0, 'side': 125.0, 'wide': 42.0}[VIEW]))
LENS = float(A.opt('lens', 14.0 if VIEW == 'wide' else 24.0))
ELONG = float(A.opt('elong', 178.0))
EV = float(A.opt('exposure', {'jupiter': -2.5, 'away': 1.5, 'side': 0.5, 'wide': -0.5}[VIEW]))
EYE = float(A.opt('eye', 1.6))

height = W.Ground(C, seed=A.opt('seed', 7))
plates = height.plates


sc = rig.new_scene('Look_Horizon')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, 1
sky.exposure(sc, EV)
hdg = {'jupiter': 0.0, 'wide': HEAD - 10.0}.get(VIEW, HEAD)
ground = W.terrain(sc, 'Ground', W.rings(0.5, 9000.0, 0.004), hdg, {'jupiter': 75.0, 'wide': 75.0}.get(VIEW, 60.0), 1800,
                   height, W.ice('Ice'))
W.europa_body(sc)

cam_loc = Vector((0.0, 0.0, EYE + W.ground_z(height, 0.0, 0.0)))
sun = sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=20.0, camera_only=True)
jup, _ = jupiter.build(sc, cam_loc)
sj, eu = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
jupiter.lamp(sc, jup, ELONG)
a = math.radians(HEAD)
aim = cam_loc + Vector((math.sin(a), math.cos(a), math.tan(math.radians(float(A.opt('tilt', 4.0)))))) * 1000.0
cam = rig.camera(sc, cam_loc, aim, lens=LENS, fstop=8.0, focus=aim)
cam.data.dof.use_dof = False
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6
print(f'NOTE look_horizon: view {VIEW} (heading {HEAD:.0f}°), {len(plates)} plates, Sun {ELONG:.0f}° '
      f'(el {P.alt_az(P.sun_local(ELONG))[0]:.2f}°), EV {EV:+.1f}')

shot.run(sc, A, tag='horizon')
