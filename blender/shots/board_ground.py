"""Sprint 2.1 board: the Conamara ground (europa_world.Ground) seen the way the surface clips will see it. Not a clip.
One ground over an azimuth sector, the camera on the knoll, one Sun per run; each frame is one view.

    Blender -b --factory-startup -P blender/shots/board_ground.py -- --views 150:24:1.5,6:35:-2.5 --hero 1 \
        --stills 1,2 --pct 50 --samples 32 --stills-dir frames/ground --id night

Views "heading:lens:ev[:tilt]" (heading deg, 0 = Jupiter, + = right; tilt deg up). Options: --elong (Sun, default 178:
night) --eye --seed --hero 1 (01's hand-placed plates, as test01_framing) --az0 --az1 (sector) --nseg-deg (azimuths
per degree) --step (ring spacing / radius) --rmax (m) --band a:b:s (extra rings a..b m every s m: the horizon for a
long lens) --cam x,y --star-density
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

A = shot.args()
ELONG = float(A.opt('elong', 178.0))
EYE = float(A.opt('eye', 1.6))
AZ0, AZ1 = float(A.opt('az0', -70.0)), float(A.opt('az1', 200.0))


def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=10.0),
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]
height = W.Ground(P.CHAOS, seed=A.opt('seed', 7), extra=HERO if A.opt('hero') else ())

sc = rig.new_scene('Board_Ground')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
bands = [tuple(float(x) for x in A.opt('band').split(':'))] if A.opt('band') else ()
rr = W.rings(0.5, float(A.opt('rmax', 20000.0)), float(A.opt('step', 0.006)), bands)
nseg = int(float(A.opt('nseg-deg', 16)) * (AZ1 - AZ0))
W.terrain(sc, 'Ground', rr, (AZ0 + AZ1) / 2, (AZ1 - AZ0) / 2, nseg, height, W.ice('Ice'))
W.europa_body(sc)

cx, cy = (float(x) for x in A.opt('cam', '0,0').split(','))
cam_loc = Vector((cx, cy, EYE + W.ground_z(height, cx, cy)))
sun = sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(24.0, A.pct), gain=20.0, density=float(A.opt('star-density', 0.06)), camera_only=True)
jup, _ = jupiter.build(sc, cam_loc)
jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
jupiter.lamp(sc, jup, ELONG)
cam = rig.camera(sc, cam_loc, cam_loc + Vector((0, 1000, 0)), lens=24.0, fstop=8.0)
cam.data.dof.use_dof = False
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6

views = [[float(x) for x in s.split(':')] for s in A.opt('views', '0:24:-2.5').split(',')]
for i, v in enumerate(views):
    cam.rotation_euler = (math.radians(90.0 + (v[3] if len(v) > 3 else 4.0)), 0.0, -math.radians(v[0]))
    cam.data.lens = v[1]
    sc.view_settings.exposure = v[2]
    cam.keyframe_insert('rotation_euler', frame=i + 1)
    cam.data.keyframe_insert('lens', frame=i + 1)
    sc.view_settings.keyframe_insert('exposure', frame=i + 1)
sc.frame_start, sc.frame_end = 1, len(views)
print(f'NOTE board_ground: {len(height.plates)} plates, sector {AZ0:.0f}..{AZ1:.0f}°, {len(rr)} rings × {nseg}, '
      f'Sun {ELONG:.0f}° (el {P.alt_az(P.sun_local(ELONG))[0]:.1f}°)')
shot.run(sc, A, tag='ground')
