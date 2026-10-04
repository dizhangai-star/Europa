"""Sprint 1 look spike A: the Conamara horizon at night, lit by full Jupiter alone (seed of 01 "horizon").
Not a clip; run directly:

    Blender -b --factory-startup -P blender/shots/look_horizon.py -- --stills 1 --pct 50 --samples 64 \
        --stills-dir frames/look --id horizon --view jupiter

Chaos ground (spike geometry; Sprint 2 rebuilds it in europa_world): convex ice plates (physics.CHAOS) with cliffs,
talus aprons, tilted ridged tops, in a hummocky matrix; a lane toward Jupiter stays open. The Sun is below the
eastern horizon (`--elong`, default 178), so the ground's only light is Jupiter's lit ¾ disc, made a light source by
jupiter.lamp. `--view jupiter` (heading +18°: the disc left of centre, block walls in silhouette) | `away` (heading
170°: the walls that face Jupiter, lit, their shadows running away from it) | `side` (125°: raking light on the walls) | `wide` (14 mm, heading 42°: the disc at the left edge, walls
raking on the right). --heading overrides.
Options: --view --heading --elong --lens --exposure --seed --eye --tilt
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
from lib import nodes, rig, shot, europa_world, jupiter, sky
for m in (physics, nodes, rig, shot, europa_world, jupiter, sky):
    importlib.reload(m)
P, W = physics, europa_world
C = P.CHAOS

A = shot.args()
VIEW = A.opt('view', 'jupiter')
HEAD = float(A.opt('heading', {'jupiter': 18.0, 'away': 170.0, 'side': 125.0, 'wide': 42.0}[VIEW]))
LENS = float(A.opt('lens', 14.0 if VIEW == 'wide' else 24.0))
ELONG = float(A.opt('elong', 178.0))
EV = float(A.opt('exposure', {'jupiter': -2.5, 'away': 1.5, 'side': 0.5, 'wide': -0.5}[VIEW]))
EYE = float(A.opt('eye', 1.6))

# ---------------------------------------------------------------- chaos plates (spike)
rng = np.random.default_rng(int(A.opt('seed', 7)))
plates = []
for _ in range(400):
    if len(plates) >= 26:
        break
    R = math.exp(rng.uniform(math.log(C['plate_m'][0] / 2), math.log(C['plate_m'][1] / 2)))
    dist = rng.uniform(R + 120.0, 6000.0)
    az = rng.uniform(-180.0, 180.0)
    half = math.degrees(math.atan2(1.3 * R, dist))
    if abs(az) - half < 9.0 and dist < 7000.0:                     # keep the lane toward Jupiter open
        continue
    cx, cy = dist * math.sin(math.radians(az)), dist * math.cos(math.radians(az))
    if any(math.hypot(cx - p['c'][0], cy - p['c'][1]) < 1.1 * (R + p['R']) for p in plates):
        continue
    n = int(rng.integers(5, 10))
    phi = rng.uniform(0, 2 * math.pi) + np.arange(n) * 2 * math.pi / n + rng.uniform(-0.3, 0.3, n)
    t = rng.uniform(0, 2 * math.pi)
    plates.append(dict(c=(cx, cy), R=R, h=rng.uniform(*C['plate_h']), nrm=np.stack([np.cos(phi), np.sin(phi)], 1),
                       p=R * rng.uniform(0.75, 1.1, n), tilt=math.tan(math.radians(rng.uniform(*C['tilt_deg']))),
                       tdir=(math.cos(t), math.sin(t)), rdir=math.radians(35.0 + rng.uniform(-25, 25)),
                       gap=rng.uniform(*C['ridge_gap'])))


def height(X, Y):
    r, az = np.hypot(X, Y), np.degrees(np.arctan2(X, Y))
    lane = 1.0 - 0.6 * W.smooth(25.0, 8.0, np.abs(az)) * W.smooth(60.0, 250.0, r)    # lower swells toward Jupiter
    Z = lane * C['matrix_h'] * (W.fbm(X / 260, Y / 260, 5, 11) - 0.45)
    Z = Z + 6.0 * np.exp(-(r / 120.0) ** 2)                        # the camera stands on a low knoll
    Z = Z + 0.8 * C['matrix_h'] * np.maximum(W.fbm(X / 45, Y / 45, 4, 12) - 0.55, 0.0)      # knobs
    for k, pl in enumerate(plates):
        cx, cy = pl['c']
        reach = 1.25 * pl['R'] + 2.0 * pl['h']
        m = (np.abs(X - cx) < reach) & (np.abs(Y - cy) < reach)
        if not m.any():
            continue
        x, y = X[m] - cx, Y[m] - cy
        d = np.min(pl['p'][None, :] - (x[:, None] * pl['nrm'][None, :, 0] + y[:, None] * pl['nrm'][None, :, 1]), 1)
        d = d + 0.06 * pl['R'] * (W.fbm(X[m] / 70, Y[m] / 70, 4, 20 + k) - 0.5)            # ragged cliff line
        h, w = pl['h'], 0.35 * pl['h']
        u = x * math.cos(pl['rdir']) + y * math.sin(pl['rdir'])
        ridge = C['ridge_h'] * (1 - np.abs(np.sin(math.pi * u / pl['gap']))) ** 6
        top = h + pl['tilt'] * (x * pl['tdir'][0] + y * pl['tdir'][1]) + ridge \
            + 4.0 * (W.fbm(X[m] / 90, Y[m] / 90, 4, 40 + k) - 0.5)
        cliff = W.smooth(0.0, w, d)
        talus = 0.3 * h * W.smooth(-1.6 * h, 0.0, d) * (1 - cliff)
        Z[m] = np.maximum(Z[m], top * cliff + talus)
    return Z


sc = rig.new_scene('Look_Horizon')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, 1
sky.exposure(sc, EV)
hdg = {'jupiter': 0.0, 'wide': HEAD - 10.0}.get(VIEW, HEAD)
ground = W.terrain(sc, 'Ground', W.rings(0.5, 9000.0, 0.004), hdg, {'jupiter': 75.0, 'wide': 75.0}.get(VIEW, 60.0), 1800,
                   height, W.ice('Ice'))
W.europa_body(sc)

cam_loc = Vector((0.0, 0.0, EYE + W.ground_z(height, 0.0, 0.0)))
sun = sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=20.0, camera_only=True)
jup, _ = jupiter.build(sc, cam_loc)
sj, eu = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
jupiter.lamp(sc, jup, ELONG)
a = math.radians(HEAD)
aim = cam_loc + Vector((math.sin(a), math.cos(a), math.tan(math.radians(float(A.opt('tilt', 4.0)))))) * 1000.0
cam = rig.camera(sc, cam_loc, aim, lens=LENS, fstop=8.0, focus=aim)
cam.data.dof.use_dof = False
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6
print(f'NOTE look_horizon: view {VIEW} (heading {HEAD:.0f}°), {len(plates)} plates, Sun {ELONG:.0f}° '
      f'(el {P.alt_az(P.sun_local(ELONG))[0]:.2f}°), EV {EV:+.1f}')

shot.run(sc, A, tag='horizon')
