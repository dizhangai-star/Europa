"""Sprint 1 look spike B: Io on Jupiter's face at 135 mm (seed of 02 "neighbour"). Not a clip; run directly:

    Blender -b --factory-startup -P blender/shots/look_io.py -- --stills 1 --pct 50 --samples 64 \
        --stills-dir frames/look --id io

Night at Conamara, the Sun just below the eastern horizon (elongation `--elong`, default 178: Jupiter ~100 % lit),
Io part-way down its transit (`--io` = fraction of the way from entering the top limb to setting into the ice,
physics.io_track). Io's shadow and Europa's own shadow fall on the clouds where the Sun's lines meet them (scaled
geometry, jupiter.europa_shadow + moons.io). Camera 135 mm at eye 1.6 m, aimed at `--aimel` deg up on Jupiter's
centre line, so the ice horizon cuts the frame's foot. Options: --elong --io --aimel --lens --exposure --grs
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

A = shot.args()
LENS = float(A.opt('lens', 135.0))
ELONG = float(A.opt('elong', 178.0))
FRAC = float(A.opt('io', 0.45))
AIMEL = float(A.opt('aimel', 3.1))

sc = rig.new_scene('Look_Io')
rig.render_settings(sc, samples=A.samples, res=shot.RES, pct=A.pct)
sc.frame_start, sc.frame_end = 1, 1
sky.exposure(sc, float(A.opt('exposure', -4.5)))

hf = lambda X, Y: 0.4 * (W.fbm(X / 40, Y / 40, 4, 3) - 0.5) + 6.0 * (W.fbm(X / 900, Y / 900, 3, 5) - 0.5)
ground = W.terrain(sc, 'Ground', W.rings(1.0, 6000.0, 0.004), 0.0, 12.0, 800, hf, W.ice('Ice'))
W.europa_body(sc)

cam_loc = Vector((0.0, 0.0, 1.6 + W.ground_z(hf, 0.0, 0.0)))
sun = sky.sun(sc, ELONG)
sky.stars(sc, sky.px_angle(LENS, A.pct), gain=20.0, camera_only=True)
jup, _ = jupiter.build(sc, cam_loc, grs=float(A.opt('grs', -40.0)))
sj, eu = jupiter.europa_shadow(sc, sun, jup, (0.0, 0.0, 0.0))
fr = P.site(*P.SITE[1:])
ent, end, _ = P.io_track(fr)
dl = ent[1] + FRAC * (end[0] - ent[1])
io = moons.io(sc, dl, cam_loc, sun_jupiter=sj)

aim = cam_loc + Vector((0.0, math.cos(math.radians(AIMEL)), math.sin(math.radians(AIMEL)))) * 1000.0
cam = rig.camera(sc, cam_loc, aim, lens=LENS, fstop=8.0, focus=aim)
cam.data.dof.use_dof = False                   # everything at infinity but a strip of ice
cam.data.clip_start, cam.data.clip_end = 0.1, 2.0e6
off, um, pen, on = P.own_shadow(ELONG)
r = P.io_cast_shadow(ELONG, dl, fr)
el, az = P.alt_az(P.sun_local(ELONG))
print(f'NOTE look_io: Sun {ELONG:.1f}° (el {el:.2f}°), Jupiter {100 * P.lit_fraction(ELONG):.1f} % lit; Europa\'s shadow '
      f'{off:.2f}° from centre ({"on" if on else "off"} the disc); Io\'s shadow '
      f'{(f"{r[2]:.2f}° from Io") if r else "off the disc"}')

shot.run(sc, A, tag='io')
