"""03 · the probe (Sprint 3.3).  The cryobot starts on the ice; its vapour throws out the loose frost; tilt up to Ganymede.

Real time at dawn after 02's night, `--after` h after Io has set (default 1.18 h: Sun 2.3° up at az −179°, directly
behind the camera, the Sun rising opposite Jupiter; Jupiter full; everything sunlit at one exposure, −4.5 EV; at night
the shot was all backlit, user chose dawn 2026-10-05). Low camera on 01/02's knoll, 35 mm, looking toward Ganymede's
azimuth (15° left of Jupiter): the ¾ disc sits in the right third, the tripod with the probe hanging nose-down on the
ice stands left of it, the astronaut beside it (Breathing Idle, leaning back to watch the frost go up). At `--fire` s
the head reaches the ice's sublimation point: the vapour (physics: 1.6 g/s at ~409 m/s, choked at the triple point)
blows the loose frost out of a ring round the nose; every flake flies its own vacuum parabola at 0.134 g and lands
(vent.frost). The vapour's own grain lobe (vent.lobe, `--lobe 1`) is off: physics puts it 4–8 stops under the lit
plain and the A/B showed noise only. The camera tilts up past the tripod head to Ganymede, 58° up, 0.23° (7.7 px),
74 % lit (9 s clip: tilt 3.0–8.0 s, 1 s hold). Sprint 4.0c: then the whip to Jupiter (physics.WHIP34: 8 frames
accelerating down toward 04's aim; the cut to 04 falls at the peak speed, in the black sky above the horizon).

    node render.mjs 03-probe --animatic                     (Workbench: motion)
    node render.mjs 03-probe --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 03-probe 1 4 11 --pct 50
Options: --cam X,Y (m on 01/02's ground)  --after H  --fire S  --lens MM  --eye M  --el0 DEG  --el1 DEG (default: Ganymede − 2.5°)  --t0 --t1 (tilt, s)
         --ev0 --ev1 --ev-lo --ev-hi (exposure ride by tilt elevation)  --probe-az --probe-d  --astro-az --astro-d
         --lean DEG --lean0 --lean1 (s)  --lobe 0|1  --mblur SHUTTER  --star-gain --star-density --nseg-deg --proxy 1
         --whip 0 (no whip tail: the clock and camera as locked in 3.3; set the clip back to 9 s)
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
from lib import nodes, rig, shot, europa_world, jupiter, sky, moons, cryobot, vent, astronaut, retarget
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky, moons, cryobot, vent, astronaut, retarget):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS

A = shot.args()
FPS = 24
LENS = float(A.opt('lens', 35.0))
EYE = float(A.opt('eye', 0.4))
AFTER = float(A.opt('after', 1.18))                     # Sun 2.3° up: dawn, behind the camera
FIRE = float(A.opt('fire', 1.0))
T0, T1 = float(A.opt('t0', 3.0)), float(A.opt('t1', 8.0))
EV0, EV1 = float(A.opt('ev0', -4.5)), float(A.opt('ev1', -4.5))
EV_LO, EV_HI = float(A.opt('ev-lo', 14.0)), float(A.opt('ev-hi', 30.0))
SHUTTER = float(A.opt('mblur', 0.5))
FR = P.site(*P.SITE[1:])
E_END = P.LAPSE_E_END[1]
DUR = P.lapse(FR, E_END, 0.0)['dur']
S = P.lapse(FR, E_END, DUR + AFTER)                       # the sky now: Io set AFTER h ago
H0_02 = -1.0 / (10.5 - 1.0) * DUR                         # 02's first frame (its Jupiter is built from there)
G_U, G_D, G_LIT = P.ganymede_seen(S['dlt'], S['elong'], FR)
G_EL, G_AZ = P.alt_az(G_U)
AZ = G_AZ                                                 # the camera's azimuth: a pure tilt ends on Ganymede
EL0, EL1 = float(A.opt('el0', 5.0)), float(A.opt('el1', G_EL - 2.5))


def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


# ---------------------------------------------------------------- ground: 01/02's (same plates, same draws)
HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=40.0, plains=1.0, tilt_deg=2.5, tdir_deg=180.0),
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]
CAM = [float(v) for v in A.opt('cam', '3,0').split(',')]   # the camera's spot on the knoll (01/02 stood at 0,0)


class Shifted(W.Ground):
    """The same ground moved so the camera's spot is the scene origin (a near boulder left of 0,0 filled the frame)."""
    def __init__(self, g, dx, dy):
        self.__dict__.update(g.__dict__)
        self._g, self._d = g, (dx, dy)

    def __call__(self, X, Y, masks=None):
        X, Y = np.asarray(X, float) + self._d[0], np.asarray(Y, float) + self._d[1]
        return self._g(X, Y) if masks is None else self._g(X, Y, masks)


height = Shifted(W.Ground(C, seed=A.opt('seed', 7), extra=HERO), *CAM)
R_EU_M = P.R_EU * 1000.0


def ground(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return height(x, y) - (x * x + y * y) / (2 * R_EU_M)


sc = rig.new_scene('S03_Probe')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
if SHUTTER > 0:
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, SHUTTER
HFOV = 2 * math.degrees(math.atan(18.0 / LENS))
VFOV = 2 * math.degrees(math.atan(18.0 * shot.RES[1] / shot.RES[0] / LENS))
HALF = HFOV / 2 + 6.0
W.terrain(sc, 'Ground', W.rings(0.3, 20000.0, 0.004, [(800.0, 6000.0, 4.0)]), AZ, HALF,
          int(float(A.opt('nseg-deg', 40)) * 2 * HALF), height, W.ice('Ice'))
W.europa_body(sc)
cam_loc = Vector((0.0, 0.0, W.ground_z(height, 0.0, 0.0) + EYE))

# ---------------------------------------------------------------- sky: the night after 02 (Sun below, full Jupiter)
u_j, _, r_eq, _, pole = P.jupiter_local()
sun = sky.sun(sc, S['elong'])
_, s_turn, _ = sky.stars(sc, sky.px_angle(LENS, A.pct), gain=float(A.opt('star-gain', 20.0)),
                         density=float(A.opt('star-density', 0.06)), axis=pole, camera_only=True)
s_turn.outputs[0].default_value = math.radians(S['turn'])   # 4.0b: turned since Io's entry (02's tail ends here)
s0 = P.lapse(FR, E_END, H0_02)
jup, _ = jupiter.build(sc, cam_loc, grs=float(A.opt('grs', -40.0)) - s0['spin'])     # 02's Jupiter, turned on
J_LOC, J_ROT, J_SCL = jup.matrix_world.decompose()
jup.rotation_mode = 'QUATERNION'
jup.rotation_quaternion = J_ROT @ Quaternion((0.0, 0.0, 1.0), math.radians(S['spin'] - s0['spin']))
jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
jupiter.lamp(sc, jup, S['elong'])
gan = moons.ganymede(sc, S['dlt'], S['elong'], cam_loc)

# ---------------------------------------------------------------- the probe on its tripod, the astronaut, the frost
_before_probe = set(bpy.data.objects)                  # → PROBE_OBJS: hidden in the whip (Sprint 4.0e)
PAZ, PD = float(A.opt('probe-az', -9.0)), float(A.opt('probe-d', 8.0))
px, py = at(PAZ, PD)
nose = (px, py, float(ground(px, py)))
bot = cryobot.build(sc, P, loc=nose, lamp=False)
reel_az = PAZ + 180.0 - 60.0                             # the reel toward the camera's right
rigs = cryobot.tripod(sc, P, nose, ground, reel_az=reel_az, feet_az=PAZ + 180.0 + 40.0)
frost, (p0, vel, t0, t1, size) = vent.frost(sc, P, nose, ground, FIRE, FPS)
if int(A.opt('lobe', 0)):                              # invisible (physics; A/B 47.9 dB = noise) at 2.2× the cost
    vent.lobe(sc, P, nose, FIRE, FPS)

AAZ, AD = float(A.opt('astro-az', -20.0)), float(A.opt('astro-d', 9.5))
ax_, ay_ = at(AAZ, AD)
face = Vector((nose[0] - ax_, nose[1] - ay_, 0.0)).normalized()
heading = math.degrees(math.atan2(face.x, -face.y)) - float(A.opt('astro-turn', -10.0))   # ¾ toward the camera
arm = astronaut.load(sc, (ax_, ay_, float(ground(ax_, ay_))), heading=heading)
LEAN = float(A.opt('lean', 22.0))
L0_, L1_ = float(A.opt('lean0', 1.6)), float(A.opt('lean1', 4.2))
if arm.type == 'ARMATURE' and not A.opt('proxy'):
    def lean(f):
        u = min(max(((f - 1) / FPS - L0_) / (L1_ - L0_), 0.0), 1.0)
        return Quaternion((1, 0, 0), -math.radians(LEAN) * u * u * (3 - 2 * u))
    retarget.retarget(sc, arm, 'Breathing Idle.fbx', extra={'chest': lean})

PROBE_OBJS = [o for o in bpy.data.objects if o not in _before_probe]

# ---------------------------------------------------------------- camera: low, 35 mm, one tilt; exposure by tilt


def ease(x, a=0.35, b=0.45):
    """0..1 → 0..1: smoothstep ramp up over `a`, cruise, ramp down over `b` (01's)."""
    v = 1.0 / (1.0 - a / 2 - b / 2)
    S_ = lambda t: t ** 3 - t ** 4 / 2
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x < a:
        return v * a * S_(x / a)
    if x > 1 - b:
        return 1.0 - v * b * S_((1 - x) / b)
    return v * (a / 2 + x - a)


def smooth(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


ASPECT = shot.RES[1] / shot.RES[0]
WHIP = int(A.opt('whip', 1))
T_HOLD = 9.0 - 1.0 / FPS                                 # 03's last held frame = whip time 0
if WHIP:
    (wa, we), _ = P.whip34_ends(ASPECT)
    assert abs(wa - AZ) < 1e-6 and abs(we - EL1) < 1e-6 and LENS == P.WHIP34['lens03'], 'whip path ≠ 03\'s end aim'
    assert A.frames == round(9.0 * FPS) + P.WHIP34['out'] or A.opt('stills'), f'clip is {A.frames} frames, 9 s + whip'
cam = rig.camera(sc, cam_loc, cam_loc + Vector((0.0, 1.0, 0.0)), lens=LENS, fstop=8.0)
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = PD
cam.data.clip_start, cam.data.clip_end = 0.05, 2.0e6
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
rows = []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    el, az = EL0 + (EL1 - EL0) * ease((t - T0) / (T1 - T0)), AZ
    if WHIP and t > T_HOLD + 1e-6:
        az, el, _ = P.whip34(t - T_HOLD, ASPECT)
    cam.rotation_euler = (math.radians(90.0 + el), 0.0, -math.radians(az))
    sc.view_settings.exposure = EV0 + (EV1 - EV0) * smooth(EV_LO, EV_HI, el)
    cam.keyframe_insert('rotation_euler', frame=f)
    sc.view_settings.keyframe_insert('exposure', frame=f)
    if WHIP and SHUTTER > 0:                                # whip frames: a full-frame smear (physics.WHIP34)
        sc.render.motion_blur_shutter = P.WHIP34['shutter'] if t > T_HOLD + 1e-6 else SHUTTER
        sc.keyframe_insert('render.motion_blur_shutter', frame=f)
    rows.append((t, el))

# Sprint 4.0e (user 2026-10-07): once the whip leaves Ganymede the probe is done with: the tripod, probe, astronaut and
# frost would smear through 03's last frames (231–235) on the way down, so they're off from the first whip frame (the
# camera has been on the sky since the tilt; 04 shows neither, continuity A). `--whip-hide 0` keeps them.
if WHIP and int(A.opt('whip-hide', 1)):
    f_w = round(9.0 * FPS) + 1                            # first whip frame (t > T_HOLD)
    for o in PROBE_OBJS:
        for f, h in ((f_w - 1, False), (f_w, True)):
            o.hide_render = h
            o.keyframe_insert('hide_render', frame=f)
    print(f'NOTE 03 whip: {len(PROBE_OBJS)} probe/tripod/astronaut/frost objects hidden from frame {f_w}')

if WHIP:                                                  # one key past the end: motion blur samples ±½ frame
    az, el, _ = P.whip34((sc.frame_end - 1 + 1) / FPS - T_HOLD, ASPECT)   # (the last frame was half-sharp without it)
    cam.rotation_euler = (math.radians(90.0 + el), 0.0, -math.radians(az))
    cam.keyframe_insert('rotation_euler', frame=sc.frame_end + 1)

g = P.g_at()
fast = np.argsort(-vel[:, 2])[:5]
apex = [(t0[i] + vel[i, 2] / g, p0[i, 2] + vel[i, 2] ** 2 / (2 * g) - cam_loc.z) for i in fast]
dur_fl = t1 - t0
pk = max(abs(rows[k + 1][1] - rows[k][1]) for k in range(len(rows) - 1)) * FPS
wl = [P.whip34(t - T_HOLD, ASPECT) for t, _ in rows if t > T_HOLD + 1e-6]
print(f'NOTE 03 whip: {len(wl)} frames, last aim az {wl[-1][0]:+.1f}° el {wl[-1][1]:.1f}° at {wl[-1][2]:.0f}°/s'
      if wl else 'NOTE 03: no whip')
print(f'NOTE 03: {LENS:.0f} mm (hfov {HFOV:.1f}°, vfov {VFOV:.1f}°), eye {EYE} m, az {AZ:+.1f}°; tilt {EL0:.1f}° → '
      f'{EL1:.1f}° over {T0}–{T1} s (peak {pk:.1f}°/s); EV {EV0} → {EV1} between {EV_LO}° and {EV_HI}° up\n'
      f'  sky {AFTER} h after Io set: Sun {S["elong"]:+.1f}°, Jupiter {100 * P.lit_fraction(S["elong"]):.0f} % lit; '
      f'Ganymede {G_EL:.1f}° up az {G_AZ:+.1f}°, {G_D:.3f}°, {100 * G_LIT:.0f} % lit\n'
      f'  probe at az {PAZ}° {PD} m (nose z {nose[2]:+.2f}, cam z {cam_loc.z:+.2f}); fire {FIRE} s; flakes '
      f'{len(t0)}: flight median {np.median(dur_fl):.2f} s, max {dur_fl.max():.1f} s; highest apexes '
      + ', '.join(f'{h:.1f} m at {ta:.1f} s ({math.degrees(math.atan2(h, PD)):.0f}° up)' for ta, h in apex))
shot.run(sc, A)
