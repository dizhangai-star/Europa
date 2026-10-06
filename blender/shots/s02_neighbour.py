"""02 · neighbour (Sprint 3.2; head + tail Sprint 4.0b).  Io sets into the ice in front of Jupiter: a time-lapse.

Same knoll and ground as 01 (the 2.1 ground + 01's three hero plates: the mesa biting the disc's lower-left limb is
the same one), looking straight at Jupiter with a long lens, the ice horizon cutting the frame's foot. The clock runs
one Io transit (physics.lapse: 1.35 h from Io's centre entering the top limb to its setting behind the ice, still on
the disc) at a constant rate: Io comes down out of the black above the disc, crosses the bands and sets into the far
rubble; Jupiter turns 43° (its clouds slide down the way Io does), Io's black shadow travels beside it (Jupiter's own
Sun, light-linked: Io is a blocker), Europa's own shadow crosses toward the disc's centre as the Sun (below the
horizon behind us) nears the anti-Jupiter point, and the stars turn 5.7° about Europa's pole (they set downward
too). Night, Jupiter ≥ 99 % lit; the ground is lit by Jupiter alone (`jupiter.lamp`).

Head (4.0b, user 2026-10-06: the 01 → 02 joint): the first frame is 01's next one (35 mm, heading 6°, tilt 4°,
−3.5 EV, 01's push still drifting 0.3 m/s and easing out); it zooms 35 → 75 mm onto the locked framing over
0–`--z1` s while the clock ramps ×1 → ×512 over 0–`--tr` s (from `--tr` on the clock is the locked one: Io's shadow
window, the setting at 10.5 s and the caption are unchanged).
Tail (4.0b, the 02 → 03 joint): after Io sets, `--tt0`–`--tt1` s, the camera zooms back out 75 → 35 mm, turns to
03's azimuth and tilt and cranes down to 03's spot (3 m right, eye 0.4 m) while the clock runs on to 03's dawn (Io
set + 1.18 h: the Sun rises behind the camera and lights the ice) and stops at real time. From `--tt1` on, every
frame is 03's first frame without the probe and the astronaut: the 30-frame dissolve brings in only them. Jupiter
(clouds, own shadow), the stars and the light are the same in both, so the disc doesn't move through the dissolve.
The ground is built about 03's spot (03's `Shifted` ground), so the two tessellations match there.

    node render.mjs 02-neighbour --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 02-neighbour 0 1.3 6 12 14 --pct 50
Options: --lens MM  --foot DEG (ice below the horizon at the frame's foot)  --e-end DEG (the Sun when Io sets,
physics.LAPSE_E_END)  --t-in --t-set (s: Io's centre on the top limb / on the horizon)  --grs DEG (GRS from the
central meridian at Io's entry)  --ev EV  --mblur SHUTTER  --taps N  --star-gain --star-density --nseg-deg
--tr S (clock ramp)  --z1 S (head zoom end)  --tt0 --tt1 S (tail)  --after H (03's dawn)  --cam3 X,Y  --eye3 M
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
END = A.frames / FPS                           # the clip's length (s)
TR = float(A.opt('tr', 1.5))                   # clock ramp ×1 → ×512 over 0–TR s
Z1 = float(A.opt('z1', 2.6))                   # head zoom 35 → 75 mm over 0–Z1 s
TT0 = float(A.opt('tt0', 10.8))                # tail: Io set 10.5 s
TT1 = float(A.opt('tt1', END - 30 / FPS))      # … to the dissolve (timeline.mjs JOINTS['02-neighbour'].d = 30)
AFTER = float(A.opt('after', 1.18))            # 03's dawn, h after Io set (s03_probe --after)

# 01's last state (s01_horizon defaults: heading 6°, tilt 4°, 35 mm, −3.5 EV; push 0.3 m/s toward 6°, 12 s clip,
# centred on the knoll → at its t = 12 s, = our first frame, the camera is 1.8 m along the push)
H01, TILT01, L01, EV01, DRIFT01 = 6.0, 4.0, 35.0, -3.5, 0.3
D01 = Vector((math.sin(math.radians(H01)), math.cos(math.radians(H01)), 0.0))
P01 = D01 * DRIFT01 * 12.0 / 2
TD = 2.0                                       # 01's drift eases out over 0–TD s
# 03's first state (s03_probe defaults: camera at 3,0 on this ground, eye 0.4 m, 35 mm, az = Ganymede's, tilt 5°,
# −4.5 EV, f/8 focused on the probe at 8 m)
CAM3 = [float(v) for v in A.opt('cam3', '3,0').split(',')]
EYE3, L03, EL03, EV03, FD03, PX03 = float(A.opt('eye3', 0.4)), 35.0, 5.0, -4.5, 8.0, 35.0
R1 = 1.0 / 3600.0                              # h per s: real time
RATE = DUR / (T_SET - T_IN)                    # h per clip second (×512)
H_SET = DUR                                    # hours at T_SET (Io on the horizon)
H3 = DUR + AFTER                               # 03's sky


def _int_s(x):                                 # ∫₀ˣ smoothstep
    return x ** 3 - x ** 4 / 2


def _hermite5(h0, v0, h1, v1, d, x):
    """Quintic Hermite on [0, 1] (zero accelerations at both ends): value and slope (per unit x)."""
    m0, m1 = v0 * d, v1 * d
    h00, h10, h01, h11 = (1 - 10 * x ** 3 + 15 * x ** 4 - 6 * x ** 5, x - 6 * x ** 3 + 8 * x ** 4 - 3 * x ** 5,
                          10 * x ** 3 - 15 * x ** 4 + 6 * x ** 5, -4 * x ** 3 + 7 * x ** 4 - 3 * x ** 5)
    d00, d10, d01, d11 = (-30 * x ** 2 + 60 * x ** 3 - 30 * x ** 4, 1 - 18 * x ** 2 + 32 * x ** 3 - 15 * x ** 4,
                          30 * x ** 2 - 60 * x ** 3 + 30 * x ** 4, -12 * x ** 2 + 28 * x ** 3 - 15 * x ** 4)
    return h00 * h0 + h10 * m0 + h01 * h1 + h11 * m1, (d00 * h0 + d10 * m0 + d01 * h1 + d11 * m1) / d


def clock(t):
    """Clip second → (hours since Io's centre entered the disc, h per clip second)."""
    if t < TR:                                 # ×1 → ×512 (smoothstep rate), joined to the locked clock at TR
        x = t / TR
        rate = R1 + (RATE - R1) * (3 * x * x - 2 * x ** 3)
        return RATE * (TR - T_IN) - R1 * (TR - t) - (RATE - R1) * TR * (0.5 - _int_s(x)), rate
    if t <= TT0:
        return RATE * (t - T_IN), RATE
    if t < TT1:                                # on to 03's dawn, landing at real time
        return _hermite5(RATE * (TT0 - T_IN), RATE, H3, R1, TT1 - TT0, (t - TT0) / (TT1 - TT0))
    return H3, R1                              # 03's first frame (its sky is held over its 9 s)


def hours(t):
    return clock(t)[0]


def ease(x, a=0.4, b=0.45):
    """0..1 → 0..1: smoothstep ramp up over `a`, cruise, ramp down over `b` (01's)."""
    v = 1.0 / (1.0 - a / 2 - b / 2)
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x < a:
        return v * a * _int_s(x / a)
    if x > 1 - b:
        return 1.0 - v * b * _int_s((1 - x) / b)
    return v * (a / 2 + x - a)


def mix(a, b, u):
    return a + (b - a) * u


def lmix(a, b, u):                             # zooms, star spots: even in log
    return math.exp(mix(math.log(a), math.log(b), u))


# ---------------------------------------------------------------- ground: 01's, built about 03's spot (03's Shifted)
def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),   # 01's lit mesa
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=40.0, plains=1.0, tilt_deg=2.5, tdir_deg=180.0),  # limb mesa
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]


class Shifted(W.Ground):
    """The same ground moved so 03's camera spot is the scene origin (s03_probe's)."""
    def __init__(self, g, dx, dy):
        self.__dict__.update(g.__dict__)
        self._g, self._d = g, (dx, dy)

    def __call__(self, X, Y, masks=None):
        X, Y = np.asarray(X, float) + self._d[0], np.asarray(Y, float) + self._d[1]
        return self._g(X, Y) if masks is None else self._g(X, Y, masks)


height = Shifted(W.Ground(C, seed=A.opt('seed', 7), extra=HERO), *CAM3)
O = Vector((-CAM3[0], -CAM3[1], 0.0))          # 01/02's knoll top (their 0, 0) in this frame


def gz(p):
    return W.ground_z(height, p.x, p.y)


sc = rig.new_scene('S02_Neighbour')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
if SHUTTER > 0:
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, SHUTTER
HFOV = 2 * math.degrees(math.atan(18.0 / LENS))
VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
AIMEL = VFOV / 2 - FOOT
s3 = P.lapse(FR, E_END, H3)
AZ03 = P.alt_az(P.ganymede_seen(s3['dlt'], s3['elong'], FR)[0])[1]
HF35 = 2 * math.degrees(math.atan(18.0 / 35.0)) / 2
AZ_LO, AZ_HI = min(H01, 0.0, AZ03) - HF35 - 4.0, max(H01, 0.0, AZ03) + HF35 + 4.0    # 01's end and 03's start, 35 mm
W.terrain(sc, 'Ground', W.rings(0.3, 20000.0, 0.004, [(800.0, 6000.0, 4.0)]), (AZ_LO + AZ_HI) / 2,
          (AZ_HI - AZ_LO) / 2, int(float(A.opt('nseg-deg', 40)) * (AZ_HI - AZ_LO)), height, W.ice('Ice'))
W.europa_body(sc)
cam3 = Vector((0.0, 0.0, gz(Vector((0.0, 0.0, 0.0))) + EYE3))
cam_loc = cam3                                 # far bodies are built about it (k-scaled: 3 m moves nothing)

# ---------------------------------------------------------------- sky: Sun, turning stars, Jupiter (spinning), Io
s0 = P.lapse(FR, E_END, hours(0.0))
u_j, _, r_eq, _, pole = P.jupiter_local()
sun = sky.sun(sc, s0['elong'])
sun.rotation_mode = 'QUATERNION'
PX0 = sky.px_angle(24.0, A.pct)                # 01's star spot (built for its 24 mm)
world, turn, smear = sky.stars(sc, PX0, gain=float(A.opt('star-gain', 20.0)),
                               density=float(A.opt('star-density', 0.06)), axis=pole, taps=int(A.opt('taps', 3)),
                               camera_only=True)
spots = [n for n in world.node_tree.nodes if n.type == 'MAP_RANGE' and abs(n.inputs[1].default_value - PX0 * 1.6) < 1e-9]
GRS = float(A.opt('grs', -40.0))
jup, _ = jupiter.build(sc, cam_loc, grs=GRS - s0['spin'])     # the GRS sits at `grs` when Io enters
sj, _ = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
sj.rotation_mode = 'QUATERNION'
jupiter.lamp(sc, jup, P.lapse(FR, E_END, DUR / 2)['elong'])
io = moons.io(sc, s0['dlt'], cam_loc, sun_jupiter=sj)
J_LOC, J_ROT, J_SCL = jup.matrix_world.decompose()
jup.rotation_mode = 'QUATERNION'

# ---------------------------------------------------------------- camera: 01's end → locked 75 mm → 03's start
el_j, _ = P.alt_az(u_j)
p_head = O + P01
p_main = p_head + D01 * DRIFT01 * TD / 2
z_head, z_main = gz(p_head) + EYE, gz(p_main) + EYE
cam = rig.camera(sc, cam3, cam3 + Vector((0.0, 1.0, 0.0)), lens=LENS, fstop=8.0)
cam.data.dof.use_dof = True                    # off in effect (f/64, focused far) until the tail lands on 03's f/8
cam.data.clip_start, cam.data.clip_end = 0.05, 2.0e6
sc.view_settings.exposure = EV


def pose(t):
    """Clip second → (location, heading deg, tilt deg, lens mm, EV, star-spot lens mm, 1/focus m⁻¹, f-number)."""
    if t < TT0:
        u = ease(t / Z1)
        tau = t - t * t / (2 * TD) if t < TD else TD / 2
        p = p_head + D01 * DRIFT01 * tau
        loc = Vector((p.x, p.y, mix(z_head, z_main, min(tau / (TD / 2), 1.0))))
        return loc, mix(H01, 0.0, u), mix(TILT01, AIMEL, u), lmix(L01, LENS, u), mix(EV01, EV, u), \
            lmix(24.0, LENS, u), 0.0, 64.0
    u = ease((t - TT0) / (TT1 - TT0))
    loc = Vector((mix(p_main.x, cam3.x, u), mix(p_main.y, cam3.y, u), mix(z_main, cam3.z, u)))
    return loc, mix(0.0, AZ03, u), mix(AIMEL, EL03, u), lmix(LENS, L03, u), mix(EV, EV03, u), \
        lmix(LENS, PX03, u), u / FD03, lmix(64.0, 8.0, u)


# ---------------------------------------------------------------- the clock + the camera: one key per frame
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
q_prev, log, clear = None, [], []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    h, rate = clock(t)
    s = P.lapse(FR, E_END, h)
    q = (-Vector(P.sun_local(s['elong']))).to_track_quat('-Z', 'Y')
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    for s_ in (sun, sj):
        s_.rotation_quaternion = q
        s_.keyframe_insert('rotation_quaternion', frame=f)
    turn.outputs[0].default_value = math.radians(s['turn'])
    turn.outputs[0].keyframe_insert('default_value', frame=f)
    smear.outputs[0].default_value = math.radians(360.0 / P.P_ORB_EU * rate * SHUTTER / FPS)
    smear.outputs[0].keyframe_insert('default_value', frame=f)
    jup.location, jup.scale = J_LOC, J_SCL
    jup.rotation_quaternion = J_ROT @ Quaternion((0.0, 0.0, 1.0), math.radians(s['spin'] - s0['spin']))
    jup.keyframe_insert('location', frame=f)
    jup.keyframe_insert('rotation_quaternion', frame=f)
    moons.key_io(io, s['dlt'], cam_loc, f)

    loc, hd, el, lens, ev, pxl, inv_fd, fno = pose(t)
    cam.location = loc
    cam.rotation_euler = (math.radians(90.0 + el), 0.0, -math.radians(hd))
    cam.data.lens = lens
    cam.data.dof.focus_distance = 1.0 / max(inv_fd, 1e-5)
    cam.data.dof.aperture_fstop = fno
    sc.view_settings.exposure = ev
    cam.keyframe_insert('location', frame=f)
    cam.keyframe_insert('rotation_euler', frame=f)
    for k in ('lens', 'dof.focus_distance', 'dof.aperture_fstop'):
        cam.data.keyframe_insert(k, frame=f)
    sc.view_settings.keyframe_insert('exposure', frame=f)
    for n in spots:
        n.inputs[1].default_value = sky.px_angle(pxl, A.pct) * 1.6
        n.inputs[1].keyframe_insert('default_value', frame=f)
    clear.append(loc.z - gz(loc))
    if f % 24 == 1 or f == sc.frame_end:
        r = P.io_cast_shadow(s['elong'], s['dlt'], FR)
        el_i = P.alt_az(P._norm(P.to_local(P.from_site(P.io_pos(s['dlt']), FR), FR))[0])[0]
        log.append(f'{t:4.1f}s {h:+5.2f}h ×{rate * 3600:5.0f} E{s["elong"]:+6.1f} Sun {P.alt_az(P.sun_local(s["elong"]))[0]:+5.1f}° '
                   f'Io {el_i:5.1f}° up, shadow {f"{r[2]:.2f}°" if r else "off"}, own {P.own_shadow(s["elong"])[0]:.1f}° | '
                   f'cam {lens:4.1f} mm hd {hd:+5.1f} el {el:4.2f} EV {ev:+.2f}')

print(f'NOTE 02: {LENS:.0f} mm (hfov {HFOV:.1f}°, vfov {VFOV:.1f}°), aim {AIMEL:.2f}° up, Jupiter centre {el_j:.2f}° up '
      f'r {r_eq:.2f}°; transit {DUR:.2f} h in {T_SET - T_IN:.1f} s = ×{RATE * 3600:.0f}, Sun {E_END:.0f}° at setting; '
      f'spin {P.lapse(FR, E_END, DUR)["spin"]:.1f}°\nNOTE   head: clock ×1 → ×{RATE * 3600:.0f} over 0–{TR} s, zoom 0–{Z1} s; '
      f'tail {TT0}–{TT1:.2f} s → 03 (az {AZ03:+.2f}°, Io set + {AFTER} h); ground az {AZ_LO:.1f}…{AZ_HI:.1f}°; '
      f'min clearance {min(clear):.2f} m; {len(spots)} star spots keyed\nNOTE   ' + '\nNOTE   '.join(log))
shot.run(sc, A)
