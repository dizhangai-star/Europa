"""07 · breakthrough (Sprint 3.7). In the water under the ice ceiling, 24 mm, looking up, then tilting down to level.
The last metre melts (the base ice glows round the lamp inside it), the head breaks through, the probe falls out under
0.134 g, the tether brake stops it; the beam sweeps out over the terraced ceiling and the hole it left reads as a black
well with the tether rising into it (physics.tube07: 351 m of water above, a fibre that carries light away: black
from below, board_tube); the camera tilts down to level: the beam into water no sunlight has ever reached.

The clock (physics.SHOT07, fit07): 06's ×2,890 eases to real time over 0.3–3.4 s; the nose starts 0.88 m above the
base and breaks through at 3.5 s; then real time: the drop (drop07: 0.89 m/s², peak 2.45 m/s, brake 1 m/s² from 4 m)
stops it 7.0 m down at 9.0 s.

Frame: lib/ocean's (world z = 0 = the ice base at the hole, +z up into the ice). Until the break the slab's bore is
plugged below the nose (a base-ice cylinder from the ceiling up to the melt pocket, hidden from the break on): the
slab's Boolean stays static (a moving cutter would re-bore 1.3 M vertices a frame).

    node render.mjs 07-breakthrough --animatic --engine cycles --pct 25 --samples 16
    node preview.mjs 07-breakthrough 2.5 6.5 12 --pct 50
Options: --lens MM  --camaz DEG (the camera's azimuth about the hole)  --r0 M --z0 M --el0 DEG (start pose)
         --side M --back M --up M --reach M --el1 DEG (end pose behind/beside the probe)  --move T0,T1  --lampaz DEG (port azimuth off the
         line of sight, away)  --ev EV --ev1 EV --evt T0,T1 --ev2 EV --evt2 T0,T1 --motesr M  --shutter S  --fstop F  --motes 0
         --gbounces N  --vbounces N  --icevol 0 (random-walk ice: blotchy glow)  --sss M  --hide A,B
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
from mathutils import Vector
import physics
from lib import nodes, rig, shot, europa_world, cryobot, ocean
for m in (physics, nodes, rig, shot, europa_world, cryobot, ocean):
    importlib.reload(m)
P = physics
C7 = P.SHOT07
F7 = P.fit07()

A = shot.args()
FPS = 24
LEN = P.CRYO_LEN
LENS = float(A.opt('lens', 24.0))
CAMAZ = math.radians(float(A.opt('camaz', -60.0)))
R0 = float(A.opt('r0', 2.2))                                      # start: distance from the axis, height (the
Z0 = float(A.opt('z0', -2.0))                                     # ceiling at the hole = 0), gaze at the hole
EL0, EL1 = math.radians(float(A.opt('el0', 40.0))), math.radians(float(A.opt('el1', -3.0)))   # gaze up (+) / level
# the port faces away from the lens (2.4 finding 1: at it, the window blows the frame out), LAMPAZ off the line of
# sight, so its beam lights the ceiling behind the hole; the end pose sits behind and beside the probe (BACK m behind
# the port, SIDE m to the camera's side of it, UP m above it) looking at a point REACH m out along the beam: the probe's
# head and lit flank in the frame (user 2026-10-06), the window turned away, the grains in the beam ahead
LAMPAZ = float(A.opt('lampaz', 40.0))
SIDE, UP = float(A.opt('side', 1.0)), float(A.opt('up', 0.25))
BACK, REACH = float(A.opt('back', 1.6)), float(A.opt('reach', 3.0))
MOVE = tuple(float(x) for x in A.opt('move', '6.5,12.5').split(','))   # 8–13 left 7–9 s dark (3.7 animatic)
EV0, EV1, EV2 = float(A.opt('ev', 0.0)), float(A.opt('ev1', 4.0)), float(A.opt('ev2', 5.0))
EVT = tuple(float(x) for x in A.opt('evt', '3.5,8.0').split(','))
EVT2 = tuple(float(x) for x in A.opt('evt2', '9.0,13.0').split(','))
SHUTTER = float(A.opt('shutter', 0.5))
FILM_W = 0.002                                                    # the melt film under the head (m): the plug's top
assert abs(A.frames / FPS - C7['dur']) < 1e-6 or A.opt('stills'), f'clip is {A.frames / FPS} s, SHOT07 says {C7["dur"]}'
S78 = P.SEAM78                                                    # 08's head starts on this shot's end pose (Sprint 4.0e)
if (round(math.degrees(CAMAZ), 6), LAMPAZ, SIDE, UP, BACK, REACH, round(math.degrees(EL1), 6), LENS, EV2) != tuple(
        S78[k] for k in ('camaz', 'lampaz07', 'side', 'up', 'back', 'reach', 'el1', 'lens07', 'ev07')):
    print('NOTE 07: end pose ≠ physics.SEAM78 (08\'s head starts on SEAM78\'s): look-dev only')


def smoothstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


TS = [(f - 1) / FPS for f in range(1, A.frames + 1)]

# ---------------------------------------------------------------- scene
sc = rig.new_scene('S07_Breakthrough')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.cycles.volume_bounces = int(A.opt('vbounces', 64))           # the glow diffuses metres (σs' 3/m)
gb = int(A.opt('gbounces', 64))                                   # the tube's wall reflects at grazing (TIR)
sc.cycles.glossy_bounces = gb
sc.cycles.max_bounces = max(gb, sc.cycles.volume_bounces) + 16
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
tu = ocean.tube(sc, P, oc, TB['prof'])
if A.opt('icevol', '1') != '0':                                   # the base ice as a volume (lit from inside: 3.7)
    oc['ice'].data.materials[0] = ocean.ice_volume_mat(P)
bot = cryobot.build(sc, P, loc=(0.0, 0.0, F7['d0']), tether=TB['length'] + 10.0)
PORT = CAMAZ + math.pi + math.radians(LAMPAZ)                     # the port's azimuth (world)
bot['root'].rotation_euler = (0.0, 0.0, PORT)

# the plug: base ice in the bore from the ceiling (its bottom follows the ceiling, 1 mm proud) up to the melt film
# under the head; its top comes down with the nose by a shape key; hidden from the break on
NP = 48
pr = oc['hole_r'] + 0.004
ang = np.linspace(0, 2 * math.pi, NP, endpoint=False)
bx, by = pr * np.cos(ang), pr * np.sin(ang)
bz = ocean.ceiling_z(oc, bx, by) - 0.001
z_c = float(ocean.ceiling_z(oc, np.zeros(1), np.zeros(1))[0]) - 0.001
ZLOW = float(np.max(bz)) + 0.002
TOP0 = F7['d0'] - FILM_W
pv = [(bx[j], by[j], bz[j]) for j in range(NP)] + [(bx[j], by[j], TOP0) for j in range(NP)] + [(0, 0, z_c), (0, 0, TOP0)]
pf = ([(j, (j + 1) % NP, NP + (j + 1) % NP, NP + j) for j in range(NP)] +
      [((j + 1) % NP, j, 2 * NP) for j in range(NP)] + [(NP + j, NP + (j + 1) % NP, 2 * NP + 1) for j in range(NP)])
pme = bpy.data.meshes.new('Plug')
pme.from_pydata(pv, [], pf)
for p_ in pme.polygons:
    p_.use_smooth = False
pme.materials.append(oc['ice'].data.materials[0])
plug = bpy.data.objects.new('Plug', pme)
sc.collection.objects.link(plug)
plug.shape_key_add(name='Basis')
k_low = plug.shape_key_add(name='Low', from_mix=False)
for i in list(range(NP, 2 * NP)) + [2 * NP + 1]:
    k_low.data[i].co.z = ZLOW

MC = float(A.opt('motesr', 1.2))                                  # the grains' cloud radius

PORT_Z = 0.5                                                      # the port above the nose (cryobot PORT_Z_FRAC)
S_LOC = Vector((R0 * math.cos(CAMAZ), R0 * math.sin(CAMAZ), Z0))
S_YAW = CAMAZ + math.pi
PDIR = Vector((math.cos(PORT), math.sin(PORT), 0.0))
SDIR = Vector((math.cos(PORT + math.pi / 2), math.sin(PORT + math.pi / 2), 0.0))   # the camera's side (nearer S_LOC)
PORT_W = Vector((0.0, 0.0, -F7['stop'] + PORT_Z))
E_LOC = PORT_W + SDIR * SIDE - PDIR * BACK + Vector((0.0, 0.0, UP))
E_TGT = PORT_W + PDIR * REACH
E_YAW = math.atan2(E_TGT.y - E_LOC.y, E_TGT.x - E_LOC.x)
if A.opt('motes', '1') != '0':                                    # a cloud round the beam's flank ahead of the lens
    gaze = Vector((math.cos(E_YAW), math.sin(E_YAW), 0.0))
    ocean.motes(sc, P, tuple(E_LOC + gaze * (MC + 0.35)), MC, oc)
cam = rig.camera(sc, tuple(S_LOC), (0, 0, 0), lens=LENS, fstop=float(A.opt('fstop', 4.0)))
cam.data.clip_end = 1000.0

# ---------------------------------------------------------------- per frame
log = []
broke = False
for f, t in enumerate(TS, start=1):
    for dt in ((-SHUTTER / 2, 0.0, SHUTTER / 2) if SHUTTER > 0 else (0.0,)):
        bot['root'].location.z = P.nose07(t + dt / FPS)
        bot['root'].keyframe_insert('location', index=2, frame=f + dt)
    nz = P.nose07(t)
    # the plug fills the bore from the ceiling up to the melt film under the nose; gone once the head is through
    gone = t >= C7['brk']
    k_low.value = min(1.0, max(0.0, (TOP0 - max(nz - FILM_W, ZLOW)) / (TOP0 - ZLOW)))
    k_low.keyframe_insert('value', frame=f)
    if f == 1 or gone != broke:
        plug.hide_render = gone
        plug.keyframe_insert('hide_render', frame=f)
        broke = gone
    # the camera: one move, a tilt from the ceiling (and the hole) down to level while it sinks and backs off
    k = smoothstep(*MOVE, t)
    loc = S_LOC.lerp(E_LOC, k)
    yaw = S_YAW + (math.remainder(E_YAW - S_YAW, 2 * math.pi)) * k
    el = EL0 + (EL1 - EL0) * k
    look = Vector((math.cos(yaw) * math.cos(el), math.sin(yaw) * math.cos(el), math.sin(el)))
    cam.location = loc
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    # focus: the probe's head (port) once it is out, the hole before
    tgt = Vector((0.0, 0.0, min(nz + 0.5, 0.0)))
    cam.data.dof.focus_distance = max((tgt - loc).length, 0.5)
    for ob, path in ((cam, 'location'), (cam, 'rotation_euler'), (cam.data.dof, 'focus_distance')):
        ob.keyframe_insert(path, frame=f)
    ev = EV0 + (EV1 - EV0) * smoothstep(*EVT, t) + (EV2 - EV1) * smoothstep(*EVT2, t)
    sc.view_settings.exposure = ev
    sc.view_settings.keyframe_insert('exposure', frame=f)
    if f % 24 == 1 or f == sc.frame_end:
        _, v, ph = P.drop07(P.lapse07(C7['brk'], t)) if t > C7['brk'] else (0, 0.0, 'melting')
        log.append(f'{t:4.1f}s ×{P._rate07(t):7,.1f} nose {nz:+7.3f} m  {v:4.2f} m/s {ph:8s} cam {loc.x:+.2f} {loc.y:+.2f} {loc.z:+.2f} '
                   f'el {math.degrees(el):+5.1f}°  EV {ev:+.1f}')

print(f'NOTE 07: {LENS:.0f} mm; nose {F7["d0"]:.2f} m above the base → break {C7["brk"]:g} s → stops '
      f'{F7["stop"]:.1f} m down at {F7["t_stop"]:.1f} s; tube {TB["length"]:.0f} m (bore {TB["a"]:.3f} m); plug from '
      f'{z_c:+.3f} m (top ≥ {ZLOW:+.3f})\n  ' + '\n  '.join(log))
if A.opt('sss'):                                            # look-dev (with --icevol 0): random walk vs BURLEY
    for n in oc['ice'].data.materials[0].node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.subsurface_method = A.opt('sss')
for name in filter(None, A.opt('hide', '').split(',')):    # diagnosis by elimination
    sc.objects[name].hide_render = True
shot.run(sc, A)
