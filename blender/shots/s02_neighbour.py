"""02 · neighbour (Sprint 3.2).  Io sets into the ice in front of Jupiter: a locked long lens, a time-lapse.

Same knoll and ground as 01 (the 2.1 ground + 01's three hero plates: the mesa biting the disc's lower-left limb is
the same one), looking straight at Jupiter with a long lens, the ice horizon cutting the frame's foot. The clock runs
one Io transit (physics.lapse: 1.35 h from Io's centre entering the top limb to its setting behind the ice, still on
the disc) at a constant rate: Io comes down out of the black above the disc, crosses the bands and sets into the far
rubble; Jupiter turns 43° (its clouds slide down the way Io does), Io's black shadow travels beside it (Jupiter's own
Sun, light-linked: Io is a blocker), Europa's own shadow crosses toward the disc's centre as the Sun (below the
horizon behind us) nears the anti-Jupiter point, and the stars turn 5.7° about Europa's pole (they set downward
too). Night, Jupiter ≥ 99 % lit; the ground is lit by Jupiter alone (`jupiter.lamp`).

    node render.mjs 02-neighbour --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 02-neighbour 1 6 11 --pct 50
Options: --lens MM  --foot DEG (ice below the horizon at the frame's foot)  --e-end DEG (the Sun when Io sets,
physics.LAPSE_E_END)  --t-in --t-set (s: Io's centre on the top limb / on the horizon)  --grs DEG (GRS from the
central meridian at Io's entry)  --ev EV  --mblur SHUTTER  --taps N  --star-gain --star-density --nseg-deg
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
from mathutils import Quaternion, Vector
import physics
from lib import nodes, rig, shot, europa_world, jupiter, sky, moons
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky, moons):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS

A = shot.args()
FPS = 24
EYE = 1.6
LENS = float(A.opt('lens', 75.0))
FOOT = float(A.opt('foot', 0.3))
E_END = float(A.opt('e-end', P.LAPSE_E_END[1]))
T_IN, T_SET = float(A.opt('t-in', 1.0)), float(A.opt('t-set', 10.5))
EV = float(A.opt('ev', -4.0))
SHUTTER = float(A.opt('mblur', 0.5))
FR = P.site(*P.SITE[1:])
DUR = P.lapse(FR, E_END, 0.0)['dur']


def hours(t):                                  # clip seconds → hours since Io's centre entered the disc
    return (t - T_IN) / (T_SET - T_IN) * DUR


RATE = DUR / (T_SET - T_IN)                    # h per clip second

# ---------------------------------------------------------------- ground: 01's, over the long lens's sector
def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),   # 01's lit mesa
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=40.0, plains=1.0, tilt_deg=2.5, tdir_deg=180.0),  # limb mesa
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]
height = W.Ground(C, seed=A.opt('seed', 7), extra=HERO)

sc = rig.new_scene('S02_Neighbour')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
if SHUTTER > 0:
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, SHUTTER
HFOV = 2 * math.degrees(math.atan(18.0 / LENS))
VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
HALF = HFOV / 2 + 3.0
W.terrain(sc, 'Ground', W.rings(0.5, 20000.0, 0.004, [(800.0, 6000.0, 4.0)]), 0.0, HALF,
          int(float(A.opt('nseg-deg', 40)) * 2 * HALF), height, W.ice('Ice'))
W.europa_body(sc)
cam_loc = Vector((0.0, 0.0, W.ground_z(height, 0.0, 0.0) + EYE))

# ---------------------------------------------------------------- sky: Sun, turning stars, Jupiter (spinning), Io
s0 = P.lapse(FR, E_END, hours(0.0))
u_j, _, r_eq, _, pole = P.jupiter_local()
sun = sky.sun(sc, s0['elong'])
sun.rotation_mode = 'QUATERNION'
world, turn, smear = sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('star-gain', 20.0)),
                               density=float(A.opt('star-density', 0.06)), axis=pole, taps=int(A.opt('taps', 3)),
                               camera_only=True)
GRS = float(A.opt('grs', -40.0))
jup, _ = jupiter.build(sc, cam_loc, grs=GRS - s0['spin'])     # the GRS sits at `grs` when Io enters
sj, _ = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
sj.rotation_mode = 'QUATERNION'
jupiter.lamp(sc, jup, P.lapse(FR, E_END, DUR / 2)['elong'])
io = moons.io(sc, s0['dlt'], cam_loc, sun_jupiter=sj)
J_LOC, J_ROT, J_SCL = jup.matrix_world.decompose()
jup.rotation_mode = 'QUATERNION'

# ---------------------------------------------------------------- camera: locked, the horizon at the frame's foot
AIMEL = VFOV / 2 - FOOT
el_j, _ = P.alt_az(u_j)
cam = rig.camera(sc, cam_loc, cam_loc + Vector((0.0, 1.0, 0.0)), lens=LENS, fstop=8.0)
cam.rotation_euler = (math.radians(90.0 + AIMEL), 0.0, 0.0)
cam.data.dof.use_dof = False                   # everything at infinity but a strip of ice
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6
sc.view_settings.exposure = EV

# ---------------------------------------------------------------- the clock: one key per frame, straight between
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
q_prev, log = None, []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    s = P.lapse(FR, E_END, hours(t))
    q = (-Vector(P.sun_local(s['elong']))).to_track_quat('-Z', 'Y')
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    for s_ in (sun, sj):
        s_.rotation_quaternion = q
        s_.keyframe_insert('rotation_quaternion', frame=f)
    turn.outputs[0].default_value = math.radians(s['turn'])
    turn.outputs[0].keyframe_insert('default_value', frame=f)
    smear.outputs[0].default_value = math.radians(360.0 / P.P_ORB_EU * RATE * SHUTTER / FPS)
    smear.outputs[0].keyframe_insert('default_value', frame=f)
    jup.location, jup.scale = J_LOC, J_SCL
    jup.rotation_quaternion = J_ROT @ Quaternion((0.0, 0.0, 1.0), math.radians(s['spin'] - s0['spin']))
    jup.keyframe_insert('location', frame=f)
    jup.keyframe_insert('rotation_quaternion', frame=f)
    moons.key_io(io, s['dlt'], cam_loc, f)
    if f % 24 == 1 or f == sc.frame_end:
        r = P.io_cast_shadow(s['elong'], s['dlt'], FR)
        el_i = P.alt_az(P._norm(P.to_local(P.from_site(P.io_pos(s['dlt']), FR), FR))[0])[0]
        log.append(f'{t:4.1f}s {hours(t):+5.2f}h E{s["elong"]:+6.1f} Io {el_i:4.1f}° up, shadow '
                   f'{f"{r[2]:.2f}°" if r else "off"}, own {P.own_shadow(s["elong"])[0]:.1f}°')

print(f'NOTE 02: {LENS:.0f} mm (hfov {HFOV:.1f}°, vfov {VFOV:.1f}°), aim {AIMEL:.2f}° up, Jupiter centre {el_j:.2f}° up '
      f'r {r_eq:.2f}°; transit {DUR:.2f} h in {T_SET - T_IN:.1f} s = ×{RATE * 3600:.0f}, Sun {E_END:.0f}° at setting; '
      f'spin {P.lapse(FR, E_END, DUR)["spin"]:.1f}°\n  ' + '\n  '.join(log))
shot.run(sc, A)
