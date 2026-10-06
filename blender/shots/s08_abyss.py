"""08 · abyss (Sprint 3.8). Locked camera just under the ice beside the hole, looking down the tether: the probe hangs
where 07's brake stopped it, the brake lets go and it falls away into the ocean; its light shrinks to a blue point
and goes out.

The clock (physics.SHOT08, fit08): real time (the probe held 7.0 m below the base; brake off at 1 s; free fall at
0.134 g, 0.89 m/s² → terminal 4.5 m/s), then ×1 → ×3 over 2.5–7 s: 130 m down at 14 s (31.9 s real). The light is
a blue point by ~40 m and gone by ~100 m (lamp_seen; 2.4 board 'down'): it goes out under the caption.

Head (Sprint 4.0e, physics.SEAM78): the clip opens on 07's end pose (24 mm beside the probe, looking out along its
beam, EV +5) under a 12-frame dissolve, then one move (0.5–3.5 s) cranes up 5.7 m beside the hole and turns down onto
the locked view (24 → 35 mm, EV +4); 08's own clock starts 2.5 s into the clip, so the brake lets go as the camera
settles. The port sits at 07's 40° (08 alone had 30°). `--head 0`: the locked shot as in 3.8 (clip 12 s).

Frame: lib/ocean's (world z = 0 = the ice base at the hole, +z up into the ice). The camera sits R m from the hole's
axis, Z m under the ceiling, aimed at the axis AIM m down, rolled so the axis offset lies across the frame (the probe
starts at the side and slides into the vanishing point at the centre).

    node render.mjs 08-abyss --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 08-abyss 0.5 6 11 --pct 50
Options: --head 0  --lens MM  --camaz DEG  --r M  --z M (camera)  --aim M (gaze point on the axis, depth)  --lampaz DEG (port
         azimuth off the camera's, 0 = straight away)  --ev EV  --shutter S  --fstop F  --motes 1  --vbounces N  --hide A,B
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(FILM, 'tools')]
import importlib
import bpy
from mathutils import Matrix, Vector
import physics
from lib import nodes, rig, shot, cryobot, ocean
for m in (physics, nodes, rig, shot, cryobot, ocean):
    importlib.reload(m)
P = physics
C8 = P.SHOT08
F8 = P.fit08()

A = shot.args()
FPS = 24
LEN = P.CRYO_LEN
LENS = float(A.opt('lens', 35.0))
CAMAZ = math.radians(float(A.opt('camaz', -60.0)))               # 07's camera side of the hole
R, Z = float(A.opt('r', 1.2)), float(A.opt('z', -0.6))
AIM = float(A.opt('aim', 60.0))
SM = P.SEAM78                                                     # 07 → 08 head (Sprint 4.0e): from 07's end pose
HEAD = int(A.opt('head', 1))
H = SM['head'] if HEAD else 0.0                                   # clip s before 08's own clock starts
LAMPAZ = float(A.opt('lampaz', SM['lampaz07'] if HEAD else 30.0))   # with the head: 07's port, no twist at the seam
EV = float(A.opt('ev', 4.0))
SHUTTER = float(A.opt('shutter', 0.5))
assert abs(A.frames / FPS - C8['dur'] - H) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, SHOT08 + head say {C8["dur"] + H}'

TS = [(f - 1) / FPS for f in range(1, A.frames + 1)]

# ---------------------------------------------------------------- scene
sc = rig.new_scene('S08_Abyss')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
if A.opt('vbounces'):
    sc.cycles.volume_bounces = int(A.opt('vbounces'))
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, A.frames
if SHUTTER > 0:
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, SHUTTER
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'

w = bpy.data.worlds.new('Black')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
sc.world = w

TB = P.tube07()
oc = ocean.build(sc, P, kind='melt', half=60.0, hole_r=TB['a'] + 0.001)
bot = cryobot.build(sc, P, loc=(0.0, 0.0, -F8['start']), tether=F8['end'] + 20.0)
PORT = CAMAZ + math.pi + math.radians(LAMPAZ)                     # the port's azimuth (world)
bot['root'].rotation_euler = (0.0, 0.0, PORT)

# the camera: locked; gaze at the axis AIM m down, the offset from the axis across the frame (screen x)
C_LOC = Vector((R * math.cos(CAMAZ), R * math.sin(CAMAZ), Z))
fwd = (Vector((0.0, 0.0, -AIM)) - C_LOC).normalized()
zc = -fwd
off = Vector((math.cos(CAMAZ), math.sin(CAMAZ), 0.0))
xc = (off - off.dot(zc) * zc).normalized()
yc = zc.cross(xc)
cam = rig.camera(sc, tuple(C_LOC), (0, 0, -AIM), lens=LENS, fstop=float(A.opt('fstop', 4.0)))
cam.rotation_euler = Matrix((xc, yc, zc)).transposed().to_euler()
cam.data.clip_end = 1000.0
sc.view_settings.exposure = EV
Q08 = cam.rotation_euler.to_quaternion()
if HEAD:                                                          # 07's end pose (s07's defaults = SEAM78)
    PORT7 = math.radians(SM['camaz']) + math.pi + math.radians(SM['lampaz07'])
    PDIR = Vector((math.cos(PORT7), math.sin(PORT7), 0.0))
    SDIR = Vector((math.cos(PORT7 + math.pi / 2), math.sin(PORT7 + math.pi / 2), 0.0))
    PORT_W = Vector((0.0, 0.0, -F8['start'] + SM['port_z']))
    E_LOC = PORT_W + SDIR * SM['side'] - PDIR * SM['back'] + Vector((0.0, 0.0, SM['up']))
    E_TGT = PORT_W + PDIR * SM['reach']
    E_YAW = math.atan2(E_TGT.y - E_LOC.y, E_TGT.x - E_LOC.x)
    el = math.radians(SM['el1'])
    look = Vector((math.cos(E_YAW) * math.cos(el), math.sin(E_YAW) * math.cos(el), math.sin(el)))
    Q07 = look.to_track_quat('-Z', 'Y')
    if A.opt('motes', '1') != '0':                                # 07's grain cloud ahead of its end pose
        gaze = Vector((math.cos(E_YAW), math.sin(E_YAW), 0.0))
        ocean.motes(sc, P, tuple(E_LOC + gaze * (SM['motesr'] + 0.35)), SM['motesr'], oc)
if A.opt('motes', '0') != '0' and not HEAD:                                    # grains round the probe's start (sub-pixel beyond ~1 m)
    ocean.motes(sc, P, (0.0, 0.0, -F8['start'] - 1.0), 3.0, oc)

# ---------------------------------------------------------------- per frame
PORT_Z = bot['port_z']
log = []
prev = cam.rotation_euler.copy()
for f, t in enumerate(TS, start=1):
    for dt in ((-SHUTTER / 2, 0.0, SHUTTER / 2) if SHUTTER > 0 else (0.0,)):
        bot['root'].location.z = P.nose08(t - H + dt / FPS)
        bot['root'].keyframe_insert('location', index=2, frame=f + dt)
    nz = P.nose08(t - H)
    loc = C_LOC
    if HEAD:                                                      # 07's end pose → the locked view, one move
        a, b = SM['move']
        u = min(1.0, max(0.0, (t - a) / (b - a)))
        k = u * u * (3 - 2 * u)
        loc = E_LOC.lerp(C_LOC, k)
        cam.location = loc
        cam.rotation_euler = Q07.slerp(Q08, k).to_euler('XYZ', prev)
        prev = cam.rotation_euler.copy()
        cam.data.lens = SM['lens07'] * (LENS / SM['lens07']) ** k
        sc.view_settings.exposure = SM['ev07'] + (EV - SM['ev07']) * k
        for ob, path in ((cam, 'location'), (cam, 'rotation_euler'), (cam.data, 'lens'), (sc.view_settings, 'exposure')):
            ob.keyframe_insert(path, frame=f)
    cam.data.dof.focus_distance = (Vector((0.0, 0.0, nz + PORT_Z)) - loc).length   # on the port
    cam.data.dof.keyframe_insert('focus_distance', frame=f)
    if f % 24 == 1 or f == sc.frame_end:
        sec, depth, bar = P.counter08(t if HEAD else t + SM['head'])
        log.append(f'{t:4.1f}s ×{P._rate08(t - H):4.2f} nose {nz:+8.2f} m  +{sec:5.1f} s {depth:9,.1f} m {bar:6.2f} bar  '
                   f'blue {P.lamp_seen(max(-nz, 5.0))[2][1]:+5.1f} EV')

print(f'NOTE 08: {LENS:.0f} mm, camera {R:g} m off the axis, {-Z:g} m under the base, gaze at {AIM:g} m; held '
      f'{F8["start"]:.1f} m → brake off {C8["rel"]:g} s → {F8["end"]:.0f} m at {C8["dur"]:g} s ({F8["real"]:.1f} s '
      f'real); EV {EV:+g}\n  ' + '\n  '.join(log))
for name in filter(None, A.opt('hide', '').split(',')):    # diagnosis by elimination
    sc.objects[name].hide_render = True
shot.run(sc, A)
