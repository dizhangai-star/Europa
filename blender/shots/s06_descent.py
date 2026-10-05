"""06 · descent (Sprint 3.6: drafted without Blender, first run on the Mac 2026-10-06; ran as written, + the end EV ride).
Cutaway, 35 mm, the camera follows the probe down the whole shell: 34 m → 19,980 m, day 2 → day 1,043, in 20 s.

The clock (physics.SHOT06, fit06): the clip is driven by depth. The nose's depth z moves in ln z (the milky top → clear
ice change, 0.1 → 3 km, gets as long as 3 → 20 km); its rate eases (log-smoothstep, as 04/05) from 05's ×2,890 up to
a peak (×27 M, 255 m of ice per frame at 11.6 s) and back down to ×2,890, 20 m above the base (07 melts the last
metres). The readout (tools/overlay.mjs, counter06): days since the head first melted · depth · the ice's temperature
· the pressure of the ice overhead.

What changes with depth, all from physics.py and keyed from the true depth z06(t): the ice's σs (physics.pore: 5.7/m,
milky, at the top → 0.14/m at 3 km → 0.006/m: the glow → a beam → dark ice; shell.key_sigma switches from the
similarity relation to the true g where it clears), the open cracks (only above BRITTLE_KM: hidden below), the open
water column above the probe (physics.refreeze: 1.3 m at the top, 6 m at 15 km, out of the frame below ~16.5 km; the
melt-water lathe stretches, the milky core and the beads' front move up with it), the puck seated in the open top (the
magazine empties: one dropped every CRYO_PUCK_KM after 05's, the last at 18 km), the exposure (a ride by depth).

Frames. As 05: the world is the probe's frame; the ice hangs on shell root (z = the nose's depth) and slides up past
a camera fixed to the probe. 20 km of ice can't be built, so the ice is a treadmill: the sheets (bands, veins, cracks,
beads) are built for a window of L m (+ blur margins) and root z wraps inside it only while the ice moves more than
--wrapstep m per frame (the frame is ~1.5 m tall at the axis: nothing can be followed from one frame to the next);
05's slow handover and the slow landing at the base each fit in the window without a wrap. Root z is keyed at the
frame and at both ends of the motion-blur shutter on the same wrap branch, LINEAR, so the blur shows the true travel
and never the wrap. The sheets are bored once (shell.fix_bore: 05's lesson, live Booleans dropped a band).

    node render.mjs 06-descent --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 06-descent 1 6 8.5 11.6 19.5 --pct 50
Options: --lens MM  --d0 --d1 M (camera distance from the axis)  --aim0 --aim1 M (aim height above the nose: the
         probe's top → its head)  --el0 --el1 DEG (looking down)  --side DEG  --move T0,T1  --ev EV --ev1 EV
         --evkm KM0,KM1 (exposure ride by depth)  --ev2 EV --evt T0,T1 (down again by time, as the camera reaches
         the lamp port)  --lampaz DEG  --win M (treadmill window)  --wrapstep M  --shutter S
         (motion blur, 0 = off)  --nocore 1  --fstop F  --vbounces N  --hide A,B
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
from lib import nodes, rig, shot, cryobot, shell
for m in (physics, nodes, rig, shot, cryobot, shell):
    importlib.reload(m)
P = physics
C6 = P.SHOT06
F6 = P.fit06()

A = shot.args()
FPS = 24
LENS = float(A.opt('lens', 35.0))
D0, D1 = float(A.opt('d0', 3.2)), float(A.opt('d1', 2.4))
AIM0, AIM1 = float(A.opt('aim0', 3.4)), float(A.opt('aim1', 0.45))
EL0, EL1 = math.radians(float(A.opt('el0', 8.0))), math.radians(float(A.opt('el1', 2.0)))   # looking down
SIDE = math.radians(float(A.opt('side', 13.0)))
MOVE = tuple(float(x) for x in A.opt('move', '1.0,17.0').split(','))
EV0, EV1 = float(A.opt('ev', 3.0)), float(A.opt('ev1', 5.0))
EVKM = tuple(float(x) for x in A.opt('evkm', '0.3,3.0').split(','))
# then down again as the camera reaches the head: the port faces it (−40°), +5 EV blew the lamp out (3.6 check)
EV2 = float(A.opt('ev2', 2.0))
EVT = tuple(float(x) for x in A.opt('evt', '12.0,16.0').split(','))
WIN = float(A.opt('win', 160.0))
WRAPSTEP = float(A.opt('wrapstep', 4.0))
SHUTTER = float(A.opt('shutter', 0.5))
assert abs(A.frames / FPS - C6['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, SHOT06 says {C6["dur"]}'


def smoothstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- the clock, per frame (and the shutter's ends)
TS = [(f - 1) / FPS for f in range(1, A.frames + 1)]
Z = {t: P.z06(t) for t in TS}
STEP = {t: P.speed06(t)[0] / FPS for t in TS}                # m of ice past the camera per frame
T_PEAK = max(TS, key=lambda t: STEP[t])
z0, z1 = F6['z0'], F6['z1']

# ---------------------------------------------------------------- the treadmill
t_a = next((t for t in TS if STEP[t] >= WRAPSTEP), T_PEAK)
t_b = next((t for t in reversed(TS) if STEP[t] >= WRAPSTEP), T_PEAK)
RUN_A, RUN_B = Z[t_a] - z0, z1 - Z[t_b]                     # the slow ends: no wrap inside them
L = max(WIN, RUN_A + 1.0, RUN_B + 1.0)
MARGIN = max(STEP.values()) * SHUTTER / 2 + 2.0              # the shutter's reach either side of a frame
TRAVEL = L + 2 * MARGIN
BASE = z0 + MARGIN                                           # root z stays in [BASE, BASE + L) at frame centres


def tread(t):
    """Root z at frame time t (the treadmill: same branch for the whole shutter around t)."""
    z = Z[t]
    if t <= T_PEAK:
        return BASE + max(0.0, z - z0) % L                           # 05's handover: no wrap while z − z0 < L
    return BASE + L - max(0.0, z1 - z) % L                           # the landing: no wrap once z1 − z < L


# ---------------------------------------------------------------- scene
sc = rig.new_scene('S06_Descent')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.cycles.volume_bounces = int(A.opt('vbounces', 128))
sc.cycles.max_bounces = max(sc.cycles.max_bounces, sc.cycles.volume_bounces + 8)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, A.frames
if SHUTTER > 0:
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, SHUTTER
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'   # per-frame keys; the treadmill jumps

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w

ABOVE = 12.0                                                 # shell.build's default box top (m above the nose)
sh = shell.build(sc, P, z0, cut=0.30, above=ABOVE, travel=TRAVEL, with_core=not A.opt('nocore'))
shell.fix_bore(sc, sh, TRAVEL)                               # root sits at z0: bored z0 − 13 … z0 + TRAVEL
top = P.CRYO_LEN
bot = cryobot.build(sc, P, tether=ABOVE + 2.0 - top)
bot['root'].rotation_euler = (0.0, 0.0, math.radians(float(A.opt('lampaz', -40.0))))
puck = bot['pucks'][0]                                       # puck 2 seated in the open top (05 dropped puck 1)
N_PUCKS = int(P.ICE_H[1] / P.CRYO_PUCK_KM)

# the open column above the probe: physics.refreeze on a depth grid, up to where it leaves the box
OPEN0 = sh['open_m']
CAP = ABOVE - top - 0.5
grid = []
for i in range(60):
    zg = z0 * (z1 / z0) ** (i / 59)
    hrs, _ = shell.refreeze(P, zg / 1000.0, P.ICE_H[1])
    grid.append((zg, hrs * P.cryo_speed(P.CRYO_P[2], P.ICE_H[1], zg / 1000.0) * 3600))
    if grid[-1][1] >= CAP:
        break


def open_at(z):
    if z >= grid[-1][0]:
        return min(grid[-1][1], CAP)
    for (za, oa), (zb, ob) in zip(grid, grid[1:]):
        if za <= z <= zb:
            return min(CAP, oa + (ob - oa) * (z - za) / (zb - za))
    return OPEN0


wat = sh['water']
wat.shape_key_add(name='Basis')
k_long = wat.shape_key_add(name='Long', from_mix=False)
KMAX = CAP / OPEN0
for i, v in enumerate(wat.data.vertices):
    if v.co.z > top + 1e-4:
        k_long.data[i].co.z = top + (v.co.z - top) * KMAX
front_nodes = [m.node_tree.nodes['Front'] for m in bpy.data.materials
               if m.name.startswith('Inclusions') and m.node_tree and 'Front' in m.node_tree.nodes]

cam = rig.camera(sc, (0, -D0, AIM0), (0, 0, AIM0), lens=LENS, fstop=float(A.opt('fstop', 4.0)))
cam.data.clip_end = 200.0

# ---------------------------------------------------------------- per frame
log, wraps, prev, events = [], 0, None, []
cracked = None
for f, t in enumerate(TS, start=1):
    z = Z[t]
    # the ice: the treadmill at the frame and at both ends of the shutter (same branch: the blur is the true travel)
    r0 = tread(t)
    for dt in ((-SHUTTER / 2, 0.0, SHUTTER / 2) if SHUTTER > 0 else (0.0,)):
        zs = P.z06(t + dt / FPS) if dt else z
        sh['root'].location.z = r0 + (zs - z)
        sh['root'].keyframe_insert('location', index=2, frame=f + dt)
    if prev is not None and abs((r0 - prev[0]) - (z - prev[1])) > 1e-6:
        wraps += 1
    prev = (r0, z)
    s = shell.key_sigma(sh, P, f, z)
    # open cracks only in the brittle lid
    c = z / 1000.0 < P.BRITTLE_KM
    if sh['cracks'] is not None and c != cracked:
        sh['cracks'].hide_render = not c
        sh['cracks'].keyframe_insert('hide_render', frame=f)
        if cracked is not None:
            events.append(f'{t:.2f}s cracks end ({z:,.0f} m)')
        cracked = c
    # the column stays open longer as the ice warms
    op = open_at(z)
    k_long.value = (op / OPEN0 - 1.0) / (KMAX - 1.0)
    k_long.keyframe_insert('value', frame=f)
    if sh['core'] is not None:
        sh['core'].location.z = op - OPEN0
        sh['core'].keyframe_insert('location', index=2, frame=f)
    for n in front_nodes:
        n.inputs[1].default_value = top + op
        n.inputs[1].keyframe_insert('default_value', frame=f)
    # the magazine empties: the seated puck is gone after the last drop
    left = N_PUCKS - 1 - int(z // (P.CRYO_PUCK_KM * 1000))
    if f == 1 or (left <= 0) != puck.hide_render:
        puck.hide_render = left <= 0
        puck.keyframe_insert('hide_render', frame=f)
        if left <= 0:
            events.append(f'{t:.2f}s magazine empty ({z:,.0f} m)')
    # the camera: fixed to the probe, easing from its top down to its head
    k = smoothstep(*MOVE, t)
    dist, aim, el = D0 + (D1 - D0) * k, AIM0 + (AIM1 - AIM0) * k, EL0 + (EL1 - EL0) * k
    tgt = Vector((0.0, 0.0, aim))
    h = dist * math.cos(el)
    cam.location = tgt + Vector((h * math.sin(SIDE), -h * math.cos(SIDE), dist * math.sin(el)))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.dof.focus_distance = dist
    cam.keyframe_insert('location', frame=f)
    cam.keyframe_insert('rotation_euler', frame=f)
    cam.data.dof.keyframe_insert('focus_distance', frame=f)
    ev = EV0 + (EV1 - EV0) * smoothstep(EVKM[0], EVKM[1], z / 1000.0) + (EV2 - EV1) * smoothstep(*EVT, t)
    sc.view_settings.exposure = ev
    sc.view_settings.keyframe_insert('exposure', frame=f)
    if f % 24 == 1 or f == sc.frame_end:
        _, rate = P.speed06(t)
        days, _, tc, bar = P.counter06(t)
        log.append(f'{t:4.1f}s ×{rate:11,.0f} {z:9,.1f} m day {days:7.1f} {tc:+6.1f} °C {bar:5.1f} bar  '
                   f'{STEP[t]:7.2f} m/frame  root {r0:7.1f}  σs {s:.3g}/m  column {op:4.2f} m  EV {ev:+.1f}')

print(f'NOTE 06: {LENS:.0f} mm; {z0:.1f} → {z1:,.0f} m (day {F6["day0"]:.1f} → {F6["day1"]:,.1f}); peak '
      f'{STEP[T_PEAK]:.0f} m/frame at {T_PEAK:.2f} s; treadmill L {L:.0f} m (slow ends {RUN_A:.0f} / {RUN_B:.0f} m, '
      f'wrap above {WRAPSTEP:g} m/frame: {t_a:.2f}–{t_b:.2f} s), margins {MARGIN:.0f} m, {wraps} wraps; '
      f'column grid {len(grid)} depths (cap {CAP:.1f} m); ' + '; '.join(events) + '\n  ' + '\n  '.join(log))
for name in filter(None, A.opt('hide', '').split(',')):    # diagnosis by elimination
    sc.objects[name].hide_render = True
shot.run(sc, A)
