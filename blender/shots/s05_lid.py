"""05 · the lid (Sprint 3.5).  Cutaway, 35 mm, the camera stays in the ice with the first relay puck; the probe sinks.

User picks (2026-10-05): puck 1 dropped 30 m down (physics.CRYO_PUCK_FIRST, film pick: just under the regolith),
the camera fixed in the ice with the puck, a small clock (tools/overlay.mjs, clip `counter`).

The clock (physics.fit05, SHOT05): 0 s = the puck has just left the probe's open top (it stays where it is: it is
threaded on the tether, now held by the ice), real time; the rate eases up to ×2,900 over 0.5–3 s and holds. The probe
sinks 0.68 m/h (1.36 m by 5 s, 4.07 m by 10 s); the melt water above it stays open 2 h (1.34 m, shell.refreeze) and
freezes from the top down, so in the ice's frame the freezing front comes down after the probe, and at 5.0 s it
reaches the puck's top: the column has closed over it. The front itself is all but invisible (ice and water differ
by 1.7 % in index); what shows it is the line of gas/brine beads left on the refrozen column's axis (shell.inclusions,
drawn above the front), growing down onto the puck. The lamp (the only light) sinks with the probe: the puck goes
from a dark disc in the probe's glow to a dark disc in fading blue (red dies first, physics.ice_rgb).

Frames: the world is the probe's frame (shell.py): the ice (shell root z = nose depth) and the puck move up by the
descent d(t); the camera is in the ice too, so it moves up by d(t) plus its own pull-back: 4.5 → 11.6 m from the
axis, aim 3.5 → 1.6 m (drop-frame heights: the puck sits at 2.92–2.99 m), level, 13° to the right of the cut's normal,
eased over MOVE s. Start: the probe's top, the puck in the open column, the bead line above; end: the frozen-in puck
in the upper third, the probe's top near the bottom, its glow from below.

    node render.mjs 05-lid --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 05-lid 0.5 5 9.5 --pct 50
Options: --lens MM  --ev EV --ev1 EV --adapt T0,T1 (exposure ride)  --el0 --el1 DEG (looking down)  --nocore 1  --live-bore 1 (per-frame Booleans: drops a band at 2.17 s)  --move T0,T1  --d0 M --d1 M (camera distance)  --aim0 Z --aim1 Z  --side DEG
         --lampaz DEG (port azimuth, −40: partly toward the camera)  --fstop F  --vbounces N  --hide A,B
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
C5 = P.SHOT05
F5 = P.fit05()

A = shot.args()
FPS = 24
DEPTH = P.CRYO_PUCK_FIRST * 1000.0
LENS = float(A.opt('lens', 35.0))
EV0, EV1 = float(A.opt('ev', 3.0)), float(A.opt('ev1', 5.5))
ADAPT = tuple(float(x) for x in A.opt('adapt', '4.0,9.5').split(','))
MOVE = tuple(float(x) for x in A.opt('move', '0.5,9.6').split(','))
D0, D1 = float(A.opt('d0', 4.0)), float(A.opt('d1', 2.6))
AIM0, AIM1 = float(A.opt('aim0', 3.05)), float(A.opt('aim1', 3.1))
EL0, EL1 = math.radians(float(A.opt('el0', 12.0))), math.radians(float(A.opt('el1', 4.0)))   # looking down
SIDE = math.radians(float(A.opt('side', 13.0)))
assert abs(A.frames / FPS - C5['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, SHOT05 says {C5["dur"]}'


def smoothstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def descent(t):                                            # m the probe has sunk since the drop
    return F5['v'] * P.lapse05(t)


sc = rig.new_scene('S05_Lid')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.cycles.volume_bounces = int(A.opt('vbounces', 128))
sc.cycles.max_bounces = max(sc.cycles.max_bounces, sc.cycles.volume_bounces + 8)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, A.frames

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w

D_END = descent(C5['dur'])
sh = shell.build(sc, P, DEPTH, cut=0.30, travel=D_END + 0.5, with_core=not A.opt('nocore'))
if not A.opt('live-bore'):                                # the slide is along the hole: bore the sheets once
    shell.fix_bore(sc, sh, D_END + 0.5)                    # (live, the EXACT Boolean dropped a band at 2.17 s)
top = P.CRYO_LEN
bot = cryobot.build(sc, P, tether=sh['front_z'] - top + 14.0)
bot['root'].rotation_euler = (0.0, 0.0, math.radians(float(A.opt('lampaz', -40.0))))
puck = bot['pucks'][0]                                     # seated in the open top; dropped at 0 s
puck.parent = None                                         # (the probe's root sits at the origin: same coordinates)
assert abs(puck.location.z - F5['z0']) < 1e-6, (puck.location.z, F5['z0'])
puck.rotation_euler = (0.0, 0.0, 0.0)

cam = rig.camera(sc, (0, -D0, AIM0), (0, 0, AIM0), lens=LENS, fstop=float(A.opt('fstop', 4.0)))
cam.data.clip_end = 200.0

log, shut_at = [], None
for f in range(1, A.frames + 1):
    t = (f - 1) / FPS
    d = descent(t)
    sh['root'].location.z = DEPTH + d
    sh['root'].keyframe_insert('location', index=2, frame=f)
    puck.location.z = F5['z0'] + d
    puck.keyframe_insert('location', index=2, frame=f)
    k = smoothstep(*MOVE, t)
    dist, aim = D0 + (D1 - D0) * k, AIM0 + (AIM1 - AIM0) * k
    tgt = Vector((0.0, 0.0, aim + d))                      # drop-frame height → world
    el = EL0 + (EL1 - EL0) * k
    h = dist * math.cos(el)
    cam.location = tgt + Vector((h * math.sin(SIDE), -h * math.cos(SIDE), dist * math.sin(el)))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.dof.focus_distance = (Vector((0.0, 0.0, F5['z0'] + P.CRYO_PUCK[1] / 2 + d)) - cam.location).length
    cam.keyframe_insert('location', frame=f)
    cam.keyframe_insert('rotation_euler', frame=f)
    cam.data.dof.keyframe_insert('focus_distance', frame=f)
    gap = sh['front_z'] - (F5['z0'] + P.CRYO_PUCK[1] + d)  # front above the puck's top (world)
    sc.view_settings.exposure = EV0 + (EV1 - EV0) * smoothstep(*ADAPT, t)   # the eye follows the fading light
    sc.view_settings.keyframe_insert('exposure', frame=f)
    if shut_at is None and gap <= 0:
        shut_at = t
    if f % 24 == 1 or f == sc.frame_end:
        log.append(f'{t:4.1f}s ×{P._rate05(t, F5["L"]):5.0f} +{P.lapse05(t) / 3600:4.2f} h  sunk {d:4.2f} m  '
                   f'front {gap:+.2f} m over the puck  cam {dist:4.1f} m aim {aim:4.2f}')

print(f'NOTE 05: {LENS:.0f} mm, EV {EV0:+g} → {EV1:+g} ({ADAPT[0]:g}–{ADAPT[1]:g} s); ×{F5["r"]:,.0f} from {C5["up1"]} s; front {F5["open_m"]:.2f} m above the '
      f'probe top, reaches the puck at {shut_at:.2f} s (SHOT05 {C5["shut"]} s); sunk {D_END:.2f} m by '
      f'{C5["dur"]:g} s\n  ' + '\n  '.join(log))
for name in filter(None, A.opt('hide', '').split(',')):   # diagnosis by elimination
    sc.objects[name].hide_render = True
shot.run(sc, A)
