"""01 · horizon (Sprint 3.1).  The turn (user 2026-10-05, Sprint 2.0 option A): 24 → 35 mm, eye 1.6 m, night.

Night with full Jupiter: the sky of 02's first frame (Sprint 4.0b, user's option C: 01 → 02 is one shot across the
cut; `physics.lapse02_start`: Sun at elongation −174.7°, 8.4° below the horizon, Io standing 1° above the disc's top
limb with its shadow on the bands, the stars turned with 02's; before 4.0b the Sun sat at 178°, an hour and a half
later, and Io was missing). The ground is lit by Jupiter alone
(`jupiter.lamp`), so only faces turned toward it glow. The shot opens on the lit mesa ~150° right of Jupiter (its face
30° off Jupiter, 600 m out: the hero plate of Sprint 2.0), holds, then pans left ~145° through the dark middle (nothing
seen from headings 40–95° faces Jupiter: the pan runs fastest there), zooming 24 → 35 mm while the exposure rides
+1.5 → −3.5 EV with the heading (down before the disc enters; at the end −2.5 left the bands pale, −4.5 lost the faint
plain under the disc), and settles on the disc: ¾ of Jupiter above the ice, bands vertical, Europa's own shadow on it,
a mesa at az −7° / 2.4 km biting its lower-left limb (scale; full ridged plains on its top, tilted 2.5°, turned 40°
so the ridges aren't end-on: its skyline is ragged, not a flat rectangle or an 8-m sawtooth). A slow push toward the
end heading runs the whole clip (foreground parallax). Motion blur 0.5 shutter (Cycles; the pan's stars streak). Caption EUROPA · 木卫二 on the disc.

Timing (Sprint 3.1 animatic): hold 2.3 s + a 2 s ramp, peak 42°/s in the dark middle (1.3 s of it; dark 0.4 gave a
75°/s whip), within 1° of the end heading by 8.1 s, ~4 s on the disc. Heading(t) = the warped progress: time per
degree ∝ w(h), w = 1 where something is lit, `--dark` (0.75) between 40° and 95° (soft 15° edges), with smooth speed
ramps at both ends (`ease`). Lens follows the plain eased time; exposure follows the heading.

    node render.mjs 01-horizon --animatic                    (Workbench → out/01-horizon-animatic.mp4)
    node render.mjs 01-horizon --animatic --engine cycles --pct 25 --samples 16      (light in motion, ~3 s/frame)
    node preview.mjs 01-horizon 1.5 5.5 10.5 --pct 50
Options: --elong DEG (static Sun there, no Io: the pre-4.0b sky)  --h0 --h1 (headings)  --lens0 --lens1  --ev0 --ev1  --t0 --t1 (pan start / end, s)  --dark W
--drift M/S  --limb plains:tilt:rot  --tilt DEG  --mblur SHUTTER (0 = off)  --seed
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
from lib import nodes, rig, shot, europa_world, jupiter, sky, moons
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky, moons):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS

A = shot.args()
FPS = 24
EYE = 1.6
ELONG = A.opt('elong', None)
FR = P.site(*P.SITE[1:])
E_END = P.LAPSE_E_END[1]
SKY = P.lapse(FR, E_END, P.lapse02_start(FR, E_END))                   # 02's first frame (01 is real time: 12 s = 0.003 h)
H0, H1 = float(A.opt('h0', 150.0)), float(A.opt('h1', 6.0))            # heading, deg (0 = Jupiter, + = right)
L0, L1 = float(A.opt('lens0', 24.0)), float(A.opt('lens1', 35.0))
EV0, EV1 = float(A.opt('ev0', 1.5)), float(A.opt('ev1', -3.5))
T0, T1 = float(A.opt('t0', 2.3)), float(A.opt('t1', 8.8))               # pan start / end (s)
DARK = float(A.opt('dark', 0.75))                                       # time per degree in the dark middle (1 = lit)
DRIFT = float(A.opt('drift', 0.3))                                      # m/s, toward heading H1
TILT = float(A.opt('tilt', 4.0))
AZ0, AZ1 = -70.0, 200.0                                                 # ground sector (deg): the 24 mm frame at 150° ends at 187°


# ---------------------------------------------------------------- the ground (Sprint 2.1) + Sprint 2.0's hero plates
LIMB = [float(x) for x in A.opt('limb', '1.0:2.5:40').split(':')]     # limb mesa: plains on its top : tilt deg : rot deg


def at(az, d):
    return (d * math.sin(math.radians(az)), d * math.cos(math.radians(az)))


HERO = [dict(c=at(150, 600), R=200.0, h=90.0, n=6, rot=120.0, tilt_deg=1.5, tdir_deg=90.0),   # the lit mesa
        dict(c=at(-7, 2400), R=180.0, h=120.0, n=7, rot=LIMB[2], plains=LIMB[0], tilt_deg=LIMB[1], tdir_deg=180.0),  # bites the limb
        dict(c=at(27, 2600), R=650.0, h=150.0, n=6, rot=40.0)]          # flanks it on the right
height = W.Ground(C, seed=A.opt('seed', 7), extra=HERO)

sc = rig.new_scene('S01_Horizon')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, A.frames
mb = float(A.opt('mblur', 0.5))
if mb > 0:                                    # the pan cruises ~40°/s: stars and edges smear as a real shutter would
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, mb
W.terrain(sc, 'Ground', W.rings(0.5, 9000.0, 0.006), (AZ0 + AZ1) / 2, (AZ1 - AZ0) / 2, int(16 * (AZ1 - AZ0)), height,
          W.ice('Ice'))
W.europa_body(sc)

# ---------------------------------------------------------------- sky, Sun, Jupiter (lit by the Sun, lighting the ground)
D = Vector((math.sin(math.radians(H1)), math.cos(math.radians(H1)), 0.0))   # push direction
span = DRIFT * A.frames / FPS
start = Vector((0.0, 0.0, 0.0)) - D * span / 2                          # the push passes over the knoll's top


def cam_at(t):
    p = start + D * DRIFT * t
    return Vector((p.x, p.y, W.ground_z(height, p.x, p.y) + EYE))


mid = cam_at(A.frames / FPS / 2)
u_j, _, _, _, pole = P.jupiter_local()
if ELONG is not None:                         # the pre-4.0b sky
    sun = sky.sun(sc, float(ELONG))
    sky.stars(sc, sky.px_angle(L0, A.pct), gain=float(A.opt('star-gain', 20.0)),
              density=float(A.opt('star-density', 0.06)), camera_only=True)
    jup, _ = jupiter.build(sc, mid)
    jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
    jupiter.lamp(sc, jup, float(ELONG))
else:                                         # 02's first frame, built as s02_neighbour builds it
    sun = sky.sun(sc, SKY['elong'])
    _, s_turn, _ = sky.stars(sc, sky.px_angle(L0, A.pct), gain=float(A.opt('star-gain', 20.0)),
                             density=float(A.opt('star-density', 0.06)), axis=pole, camera_only=True)
    s_turn.outputs[0].default_value = math.radians(SKY['turn'])
    jup, _ = jupiter.build(sc, mid, grs=-40.0 - SKY['spin'])          # 02's: the GRS at −40° when Io enters
    sj, _ = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
    jupiter.lamp(sc, jup, P.lapse(FR, E_END, SKY['dur'] / 2)['elong'])  # 02's lamp
    moons.io(sc, SKY['dlt'], mid, sun_jupiter=sj)


# ---------------------------------------------------------------- camera: the turn
def ease(x, a=0.3, b=0.45):
    """0..1 → 0..1: speed ramps up (smoothstep) over the first `a`, cruises, ramps down over the last `b` (Io 01's, longer start ramp)."""
    v = 1.0 / (1.0 - a / 2 - b / 2)
    S = lambda t: t ** 3 - t ** 4 / 2                            # ∫ smoothstep, S(1) = ½
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x < a:
        return v * a * S(x / a)
    if x > 1 - b:
        return 1.0 - v * b * S((1 - x) / b)
    return v * (a / 2 + x - a)


def smooth(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def w(h):                                     # time per degree of pan at heading h
    return 1.0 - (1.0 - DARK) * smooth(25.0, 40.0, h) * (1.0 - smooth(95.0, 110.0, h))


# warped progress G(h) = ∫ w from H1, tabulated at 0.05°, inverted by search
NH = int(abs(H0 - H1) / 0.05)
hs = [H1 + (H0 - H1) * k / NH for k in range(NH + 1)]
G = [0.0]
for k in range(NH):
    G.append(G[-1] + w(0.5 * (hs[k] + hs[k + 1])) * abs(H0 - H1) / NH)


def heading(t):
    g = (1.0 - ease((t - T0) / (T1 - T0))) * G[-1]                       # progress from H0 (g = G[-1]) to H1 (g = 0)
    lo, hi = 0, NH
    while hi - lo > 1:
        m = (lo + hi) // 2
        lo, hi = (m, hi) if G[m] <= g else (lo, m)
    f = (g - G[lo]) / max(G[hi] - G[lo], 1e-12)
    return hs[lo] + f * (hs[hi] - hs[lo])


def ev(h):
    return EV1 + (EV0 - EV1) * smooth(20.0, 60.0, h)


cam = rig.camera(sc, mid, mid + Vector((0, 1000, 0)), lens=L0, fstop=8.0)
cam.data.dof.use_dof = False                  # 24–35 mm at f/8 focused far: everything past ~3 m sharp
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'     # a key per frame, straight between
rows = []
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    h = heading(t)
    cam.location = cam_at(t)
    cam.rotation_euler = (math.radians(90.0 + TILT), 0.0, -math.radians(h))
    cam.data.lens = L0 + (L1 - L0) * ease((t - T0) / (T1 - T0))
    sc.view_settings.exposure = ev(h)
    cam.keyframe_insert('location', frame=f)
    cam.keyframe_insert('rotation_euler', frame=f)
    cam.data.keyframe_insert('lens', frame=f)
    sc.view_settings.keyframe_insert('exposure', frame=f)
    rows.append((t, h, cam.data.lens))

# notes: cruise speed, the dark stretch, when the disc's limb enters the frame
u, _, r_eq, r_pol, _ = P.jupiter_local()
el, az = P.alt_az(u)
dh = max(abs(rows[k + 1][1] - rows[k][1]) for k in range(len(rows) - 1))
px = dh / math.degrees(sky.px_angle(L0))
dark = [r[0] for r in rows if 40.0 <= r[1] <= 95.0]
hfov = lambda L: 2 * math.degrees(math.atan(18.0 / L))
enter = next((r[0] for r in rows if r[1] - hfov(r[2]) / 2 <= r_eq), None)
print(f'NOTE 01: heading {H0:.0f}° → {H1:.0f}° over {T0}–{T1} s, peak {dh * FPS:.0f}°/s ({px:.0f} px/frame at {L0:.0f} mm); '
      f'dark 40–95° from {dark[0]:.2f} to {dark[-1]:.2f} s; disc limb enters at {enter:.2f} s; '
      f'Jupiter centre {el:.1f}° up, r {r_eq:.2f}°; push {span:.1f} m; EV {EV0} → {EV1}; mblur {mb}')
shot.run(sc, A)
