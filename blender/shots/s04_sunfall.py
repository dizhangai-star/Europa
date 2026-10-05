"""04 · the fall of the Sun (Sprint 3.4).  50 mm, locked on Jupiter from 01/02's knoll; one 40 h day eased to real time.

The clock (physics.fit04, SHOT04): 0 s = 03's dawn (Sun 2.2° up behind the camera, Jupiter 99.7 % lit), real time;
the rate eases up to ×25,000 by 1.5 s (the Sun crosses the sky at 30°/s, Jupiter turns once every 1.6 s: its clouds
stream down into the ice), eases down from 6 s; the Sun comes down into the top of the frame, slows, and touches the
top limb at 10 s (×31), its bead shrinks evenly to nothing by 13.5 s (87 s real), then real time. Jupiter wanes
from full to a 0.3 % crescent on its top limb: sunset = eclipse. The ground: long shadows toward Jupiter at dawn,
short at noon (80° up), long toward the camera as the Sun comes down in front, then black.

After the Sun: the eyes adjust (exposure EV_DAY → EV_NIGHT): the stars come out (physical: the brightest V −1.5)
except where the black disc hides them; the refraction ring round the disc (jupiter._ring, keyed by the Sun's
distance from the limb as Io's 04), cut by the ice: a red arch standing on the horizon; the solar corona (sky.corona,
Baumbach profile, true surface brightness) sits on the top limb where the Sun went in (it is only 0.05° behind the
limb: the corona's inner 1–3 solar radii stand above it; off by default, user 2026-10-05); lightning on the
night side (jupiter.lightning, Galileo energies 1e9–1.6e10 J: V −0.2 … −3.2 points, physics.flash_seen) is off:
it looked odd inside the eclipse (user 2026-10-05), `--flashes N` puts true flashes back.

Light: the Sun lamp on the ground keyed by the uncovered fraction of its disc (physics.sun_visible); Jupiter has its
own copy of the Sun (light linking) shadowed by the scaled Europa (jupiter.europa_shadow, as 03), never dimmed.

    node render.mjs 04-sunfall --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 04-sunfall 0.5 4 9 11.5 17 --pct 50
Options: --lens MM  --top DEG (frame top above Jupiter's top limb)  --day EV  --night EV  --adapt T0,T1 (s)
         --arc A --haze H --focus K --tail F --haze-from DEG --arc-from DEG (ring)  --corona 0|1 (off)  --flashes N (0) --flash-t0 S  --star-mag V (brightest)
         --star-density D  --glare S  --mblur SHUTTER  --nseg-deg  --grs DEG
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
from mathutils import Quaternion, Vector
import physics
from lib import nodes, rig, shot, europa_world, jupiter, sky
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS
C4 = P.SHOT04

A = shot.args()
FPS = 24
EYE = 1.6
LENS = float(A.opt('lens', 50.0))
TOP = float(A.opt('top', 3.0))
EV_DAY, EV_NIGHT = float(A.opt('day', -4.5)), float(A.opt('night', 5.0))
ADAPT = tuple(float(x) for x in A.opt('adapt', '13.0,15.5').split(','))
SHUTTER = float(A.opt('mblur', 0.5))
FR = P.site(*P.SITE[1:])
E_END = P.LAPSE_E_END[1]
DUR02 = P.lapse(FR, E_END, 0.0)['dur']
H0_02 = -1.0 / (10.5 - 1.0) * DUR02                        # 02's first frame (its Jupiter is built from there)
F4 = P.fit04()
assert abs(A.frames / FPS - C4['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, SHOT04 says {C4["dur"]}'


def hours(t):                                              # clip second → hours since Io entered the disc in 02
    return DUR02 + P.DAWN_03 + (P.lapse04(t) + F4['pre']) / 3600.0


def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


# ---------------------------------------------------------------- ground: 01/02's knoll and plates
HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=40.0, plains=1.0, tilt_deg=2.5, tdir_deg=180.0),
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]
height = W.Ground(C, seed=A.opt('seed', 7), extra=HERO)

sc = rig.new_scene('S04_Sunfall')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
if SHUTTER > 0:
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, SHUTTER
HFOV = 2 * math.degrees(math.atan(18.0 / LENS))
VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
HALF = HFOV / 2 + 6.0
W.terrain(sc, 'Ground', W.rings(0.5, 20000.0, 0.004, [(800.0, 6000.0, 4.0)]), 0.0, HALF,
          int(float(A.opt('nseg-deg', 40)) * 2 * HALF), height, W.ice('Ice'))
W.europa_body(sc)
cam_loc = Vector((0.0, 0.0, W.ground_z(height, 0.0, 0.0) + EYE))

# ---------------------------------------------------------------- sky
e0 = P.lapse04_elong(0.0)
u_j, _, r_eq, r_pol, pole = P.jupiter_local()
J_EL = P.alt_az(u_j)[0]
sun = sky.sun(sc, e0)
sun.rotation_mode = 'QUATERNION'
disc = sky.sun_disc(sc, e0)
# stars at true brightness: the brightest (rand⁸ = 1) at V `star-mag`; a star's irradiance = gain × the spot's solid angle
px = sky.px_angle(LENS, A.pct)
omega = math.pi * (1.6 * px) ** 2 / 6
m_sun = P.M_SUN_1AU + 5 * math.log10(P.AU_J)
star_gain = P.E_SUN * 10 ** (-0.4 * (float(A.opt('star-mag', -1.5)) - m_sun)) / omega
world, turn, smear = sky.stars(sc, px, gain=star_gain, density=float(A.opt('star-density', 0.6)), axis=pole,
                               taps=3, camera_only=True)
s0 = P.lapse(FR, E_END, H0_02)
jup, shell = jupiter.build(sc, cam_loc, grs=float(A.opt('grs', -40.0)) - s0['spin'], ring=1.0, sun_elong=e0)
sj, _ = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
sj.data = sun.data.copy()                                  # Jupiter's Sun is never dimmed (only the ground's is)
sj.rotation_mode = 'QUATERNION'
if not int(A.opt('jup-bounce', 0)):          # its own lit far side leaked onto the night face through the smooth-shaded
    jup.visible_diffuse = jup.visible_glossy = False     # sphere (bounce only, 5e-5 of the lit disc: visible at +5 EV);
                                                         # its light on the ground (0.6 % of the Sun's, by day) is lost
J_LOC, J_ROT, J_SCL = jup.matrix_world.decompose()
jup.rotation_mode = 'QUATERNION'
gl = sky.glare(sc, strength=float(A.opt('glare', 1.0)))
ring = shell.active_material.node_tree.nodes
ARC, HAZE, FOCUS, TAIL = (float(A.opt(k, d)) for k, d in (('arc', 400.0), ('haze', 0.25), ('focus', 12.0), ('tail', 0.005)))
ring['RingFocus'].outputs[0].default_value = FOCUS
HAZE_FROM, ARC_FROM = float(A.opt('haze-from', 0.05)), float(A.opt('arc-from', 1.5))   # deg off the limb: ramps start

# ---------------------------------------------------------------- camera: locked, Jupiter's top limb TOP° under the frame top
PITCH = J_EL + r_eq + TOP - VFOV / 2
d = Vector((0.0, math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))))
cam = rig.camera(sc, cam_loc, cam_loc + d * 1000, lens=LENS, fstop=8.0)
cam.data.dof.use_dof = False                               # hyperfocal 10 m at f/8: the near ice starts at ~20 m
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6

cor = None
if int(A.opt('corona', 0)):                                # off (user 2026-10-05); real, kept as an option
    cor = sky.corona(sc, e0)
    sky.track(cor, cam)

# ---------------------------------------------------------------- lightning: off (user 2026-10-05: odd inside the eclipse)
flashes = []
NFL = int(A.opt('flashes', 0))                               # true flashes (Galileo energies, 1-px points) if asked
if NFL:
    rng = np.random.default_rng(int(A.opt('flash-seed', 5)))
    STORMS = [(0.42, 0.35), (-0.30, 0.55), (0.62, -0.05), (0.15, 0.78)]  # disc radii right/up (bands: right = north)
    T_FL = float(A.opt('flash-t0', 14.6))
    for k in range(NFL):
        t = T_FL + (C4['dur'] - 0.2 - T_FL) * (k + rng.uniform(0.1, 0.9)) / NFL
        si = int(rng.choice(len(STORMS), p=[0.4, 0.25, 0.2, 0.15]))
        e = math.exp(rng.uniform(math.log(P.FLASH_E[0]), math.log(P.FLASH_E[1])))
        f = int(round(t * FPS)) + 1
        for j, w in enumerate([1.0] if rng.uniform() < 0.5 else [0.6, 0.4]):
            flashes.append((si, f + j, e * w))
    jupiter.lightning(sc, jup, cam_loc, STORMS, flashes, SHUTTER / FPS, FPS)


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- the clock: one key per frame, straight between
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
q_prev, log, sun_in = None, [], None
top_el = PITCH + VFOV / 2
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    tau, rate = P.lapse04(t), P.rate04(t)
    e = P.lapse04_elong(t)
    sep, vis = P.sun_limb_sep(e), P.sun_visible(e)
    uu = Vector(P.sun_local(e))
    q = (-uu).to_track_quat('-Z', 'Y')
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    for s_ in (sun, sj):
        s_.rotation_quaternion = q
        s_.keyframe_insert('rotation_quaternion', frame=f)
    sun.data.energy = P.E_SUN * vis
    sun.data.keyframe_insert('energy', frame=f)
    for ob in (disc, cor):
        if ob is not None:
            ob.location = cam_loc + uu * ob['dist']
            ob.keyframe_insert('location', frame=f)
    h = hours(t)
    turn.outputs[0].default_value = math.radians(P.STAR_RATE * (h - hours(0.0)))
    turn.outputs[0].keyframe_insert('default_value', frame=f)
    smear.outputs[0].default_value = math.radians(P.STAR_RATE * rate / 3600 * SHUTTER / FPS)
    smear.outputs[0].keyframe_insert('default_value', frame=f)
    spin = 360.0 * (h - H0_02) / P.P_ROT_J_EU                # 03's convention: turned on from 02's first frame
    jup.location, jup.scale = J_LOC, J_SCL
    jup.rotation_quaternion = J_ROT @ Quaternion((0.0, 0.0, 1.0), math.radians(spin))
    jup.keyframe_insert('location', frame=f)
    jup.keyframe_insert('rotation_quaternion', frame=f)
    ring['RingHaze'].outputs[0].default_value = HAZE * smoothstep(HAZE_FROM, -P.R_SUN_DEG, sep)
    ring['RingArc'].outputs[0].default_value = ARC * smoothstep(ARC_FROM, 0.0, sep) * (TAIL + (1 - TAIL) * vis)
    rd = jupiter.ring_dir(shell, e)
    for i in range(3):
        ring['RingDir'].inputs[i].default_value = rd[i]
        ring['RingDir'].inputs[i].keyframe_insert('default_value', frame=f)
    for k in ('RingHaze', 'RingArc'):
        ring[k].outputs[0].keyframe_insert('default_value', frame=f)
    sc.view_settings.exposure = EV_DAY + (EV_NIGHT - EV_DAY) * smoothstep(*ADAPT, t)
    sc.view_settings.keyframe_insert('exposure', frame=f)
    el, az = P.alt_az(uu)
    if sun_in is None and el < top_el and abs(az) < HFOV / 2:
        sun_in = t
    if f % 24 == 1 or f == sc.frame_end:
        log.append(f'{t:4.1f}s ×{rate:6.0f} Sun {el:5.1f}° az {az:+6.1f} sep {sep:+.3f} vis {100 * vis:3.0f}% '
                   f'Jupiter {100 * P.lit_fraction(e):5.2f}% lit')

print(f'NOTE 04: {LENS:.0f} mm (hfov {HFOV:.1f}°, vfov {VFOV:.1f}°), pitch {PITCH:.2f}° (frame {PITCH - VFOV / 2:.2f}° … '
      f'{top_el:.2f}°), Jupiter centre {J_EL:.2f}° r {r_eq:.2f}°; peak ×{F4["r0"]:,.0f}, ingress ×{F4["ri"]:.0f}; '
      f'Sun enters the frame at {sun_in:.2f} s; stars: brightest V {A.opt("star-mag", -1.5)} = gain {star_gain:.3g}; '
      f'{len(flashes)} flash frames\n  ' + '\n  '.join(log))
if A.opt('bounces'):
    sc.cycles.max_bounces = int(A.opt('bounces'))
if A.opt('sj-angle'):
    sj.data.angle = math.radians(float(A.opt('sj-angle')))
for name in filter(None, A.opt('hide', '').split(',')):  # diagnosis by elimination
    sc.objects[name].hide_render = True
shot.run(sc, A)
