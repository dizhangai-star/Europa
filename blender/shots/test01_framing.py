"""Sprint 2.0: 01 "horizon" framing test (finding 2: the disc and the walls it lights can't share one frame).
Not a clip. One chaos ground (lib/chaos, Sprint 1 spike) over a wide sector, the camera on the knoll; each frame is
one camera (stills) or the frames make a turn (animation).

    # stills: one frame per view "heading:lens:ev[:tilt]" (heading deg, 0 = Jupiter, + = right)
    Blender -b --factory-startup -P blender/shots/test01_framing.py -- --views 170:24:1.5,125:24:0.5,18:24:-2.5 \
        --stills 1,2,3 --pct 50 --samples 32 --stills-dir frames/test01 --id h
    # a turn: --turn h0:lens0:ev0,h1:lens1:ev1 over --frames N (eased), rendered with --out DIR (or --stills)

Options: --views | --turn  --frames --hold0 --hold1 (frames held at each end of the turn) --elong --seed --eye
--az0 --az1 (ground sector, deg) --cam x,y (camera position, m) --hero 1 --star-density --star-gain
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
from lib import nodes, rig, shot, europa_world, jupiter, sky, chaos
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky, chaos):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS

A = shot.args()
ELONG = float(A.opt('elong', 178.0))
EYE = float(A.opt('eye', 1.6))
AZ0, AZ1 = float(A.opt('az0', -70.0)), float(A.opt('az1', 200.0))


def parse(s):
    v = [float(x) for x in s.split(':')]
    return dict(h=v[0], lens=v[1], ev=v[2], tilt=v[3] if len(v) > 3 else 4.0)


# hand-placed plates (--hero 1): a lit wall near the camera on the far side from Jupiter (its face toward the camera
# has its normal at az −30°: 30° off Jupiter), one block biting the disc's limb, one flanking it on the right
def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=10.0),          # bites the disc's lower-left limb
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]
plates = chaos.plates(C, seed=A.opt('seed', 7), extra=HERO if A.opt('hero') else ())
height = chaos.height_fn(C, plates)

sc = rig.new_scene('Test01_Framing')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
nseg = int(16 * (AZ1 - AZ0))
W.terrain(sc, 'Ground', W.rings(0.5, 9000.0, 0.006), (AZ0 + AZ1) / 2, (AZ1 - AZ0) / 2, nseg, height, W.ice('Ice'))
W.europa_body(sc)

cx, cy = (float(x) for x in A.opt('cam', '0,0').split(','))
cam_loc = Vector((cx, cy, EYE + W.ground_z(height, cx, cy)))
sun = sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(24.0, A.pct), gain=float(A.opt('star-gain', 20.0)), density=float(A.opt('star-density', 0.06)),
          camera_only=True)
jup, _ = jupiter.build(sc, cam_loc)
jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
jupiter.lamp(sc, jup, ELONG)
cam = rig.camera(sc, cam_loc, cam_loc + Vector((0, 1000, 0)), lens=24.0, fstop=8.0)
cam.data.dof.use_dof = False
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6


def key(f, v, interp='CONSTANT'):
    cam.rotation_euler = (math.radians(90.0 + v['tilt']), 0.0, -math.radians(v['h']))
    cam.data.lens = v['lens']
    sc.view_settings.exposure = v['ev']
    cam.keyframe_insert('rotation_euler', frame=f)
    cam.data.keyframe_insert('lens', frame=f)
    sc.view_settings.keyframe_insert('exposure', frame=f)


if A.opt('turn'):
    a, b = (parse(s) for s in A.opt('turn').split(','))
    N, h0, h1 = A.frames, int(A.opt('hold0', 24)), int(A.opt('hold1', 24))
    key(1, a), key(1 + h0, a), key(N - h1, b), key(N, b)
    from bpy_extras import anim_utils
    for ad in (cam.animation_data, cam.data.animation_data, sc.animation_data):
        for fc in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation, kp.easing = 'BEZIER', 'AUTO'
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    sc.frame_start, sc.frame_end = 1, N
    tag = 'turn'
else:
    views = [parse(s) for s in A.opt('views', '18:24:-2.5').split(',')]
    for i, v in enumerate(views):
        key(i + 1, v)
    sc.frame_start, sc.frame_end = 1, len(views)
    tag = 'framing'
print(f'NOTE test01: {len(plates)} plates, sector {AZ0:.0f}..{AZ1:.0f}°, cam {cx:.0f},{cy:.0f}, Sun {ELONG:.0f}°')
shot.run(sc, A, tag=tag)
