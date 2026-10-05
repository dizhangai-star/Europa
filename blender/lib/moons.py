"""Io (and later Ganymede) in Europa's sky, at true angular size, place, phase, and with its true shadow on Jupiter.
New in Sprint 1 (look spike for 02).

Everything far is scaled toward the camera by one factor k = jupiter.DIST / Jupiter's true distance (as jupiter.py
and jupiter.europa_shadow do), so angles, phases and shadows stay exact: Io sits at k × its true position from the
site, radius k × R_IO (≈ 370 km out, 2.7 km wide). Io is lit by the main Sun lamp; to throw its shadow on Jupiter it
joins Jupiter's own Sun's blocker collection (jupiter.europa_shadow), next to the scaled Europa.

Io's body frame: +X toward Jupiter (Io is locked: longitude 0 faces it), +Z = orbit north (Jupiter's axis),
east longitude = atan2(y, x), so the map (tools/maps.py io_globe: column 0 = 0° E) wraps without a flip. During a
transit Europa sees Io's anti-Jupiter face (180°). With Jupiter's own Sun given, Io is lit by it alone (scaled Europa
as its blocker: a mutual eclipse, Europa's shadow on Io, falls true). Albedo: map × gain so the disc's mean Lambert albedo is
1.5 × physics.P_GEOM_IO,
clamped at 1 (the mosaic's frost is stretched).
"""
import math
import os

import bpy
from mathutils import Matrix, Vector
import physics as P
from . import nodes, jupiter

IO_MAP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures/src/io_globe_2k.png')
IO_LUM = 0.2442                  # mean linear luminance of IO_MAP (tools/maps.py io_globe)


def k_scale():
    return jupiter.DIST / (P.jupiter_local()[1] * 1000.0)


def io_matrix(dlt, cam_loc):
    """Io's world matrix at `dlt` rad from conjunction (scaled place, locked face toward Jupiter, radius in the scale);
    also returns its scaled offset from the camera (m) and radius."""
    fr = P.site(*P.SITE[1:])
    k = k_scale()
    p = Vector(P.to_local(P.from_site(P.io_pos(dlt), fr), fr)) * 1000.0 * k          # m, scaled
    j = Vector(P.to_local(P.from_site((P.A_EU, 0.0, 0.0), fr), fr)) * 1000.0 * k
    r = P.R_IO * 1000.0 * k
    x = (j - p).normalized()
    axis = Vector(P.jupiter_local()[4])
    z = (axis - axis.dot(x) * x).normalized()
    y = z.cross(x)
    rot = Matrix((x, y, z)).transposed().to_4x4()
    return Matrix.Translation(Vector(cam_loc) + p) @ rot @ Matrix.Diagonal((r, r, r, 1.0)), p, r


def key_io(ob, dlt, cam_loc, frame):
    """Move Io to `dlt` and key it on `frame` (02's time-lapse). Quaternion rotation, kept on one hemisphere."""
    m, _, _ = io_matrix(dlt, cam_loc)
    loc, q, s = m.decompose()
    ob.rotation_mode = 'QUATERNION'
    if ob.rotation_quaternion.dot(q) < 0:
        q.negate()
    ob.location, ob.rotation_quaternion, ob.scale = loc, q, s
    for k in ('location', 'rotation_quaternion', 'scale'):
        ob.keyframe_insert(k, frame=frame)


def io(sc, dlt, cam_loc, sun_jupiter=None):
    """Io at `dlt` rad from conjunction with Europa (physics.io_pos), seen from the site. `sun_jupiter`: Jupiter's own
    Sun (jupiter.europa_shadow) → Io shadows Jupiter. Returns the object."""
    mw, p, r = io_matrix(dlt, cam_loc)
    k = k_scale()
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1.0)
    ob = bpy.context.object
    ob.name = 'Io'
    ob.matrix_world = mw
    bpy.ops.object.shade_smooth()

    m = bpy.data.materials.new('Io')
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    ox, oy, oz = g.xyz(g.o(tc, 'Object'))
    lon = g.add('ShaderNodeMath', operation='ARCTAN2')
    g.set(lon, 0, oy)
    g.set(lon, 1, ox)
    uu = g.math('DIVIDE', g.o(lon, 0), 2 * math.pi)
    vv = g.math('ADD', g.math('DIVIDE', g.math('ARCSINE', g.math('MINIMUM', g.math('MAXIMUM', oz, -1.0), 1.0)),
                                  math.pi), 0.5)
    tex = g.add('ShaderNodeTexImage', interpolation='Cubic', extension='REPEAT')
    tex.image = bpy.data.images.load(IO_MAP, check_existing=True)
    g.set(tex, 'Vector', g.combine(uu, vv))
    gain = 1.5 * P.P_GEOM_IO / IO_LUM
    col = g.mix(1.0, g.o(tex, 'Color'), (gain, gain, gain), blend='MULTIPLY', clamp=True)   # brightest frost ≤ 1
    b = g.add('ShaderNodeBsdfDiffuse')
    g.set(b, 'Color', col)
    g.output(g.o(b, 0))
    ob.data.materials.append(m)
    if sun_jupiter is not None and sun_jupiter.light_linking.blocker_collection:
        c = sun_jupiter.light_linking.blocker_collection
        c.objects.link(ob)
        for co in c.collection_objects:
            co.light_linking.link_state = 'INCLUDE'
        # lit by Jupiter's Sun too, not by the main one: at scale k the only Europa that may shadow Io is the scaled
        # one (Sprint 3.2: the real-size body eclipsed the scaled Io); Europa's true shadow on Io then falls exactly
        for name, state in (('OnlyJupiter', 'INCLUDE'), ('NotJupiter', 'EXCLUDE')):
            for col in bpy.data.collections:
                if col.name.startswith(name):
                    col.objects.link(ob)
                    for o_, co in zip(col.objects, col.collection_objects):     # same order (no .object)
                        if o_ == ob:
                            co.light_linking.link_state = state
    el, az = P.alt_az(tuple(p.normalized()))
    print(f'NOTE io: Δ {dlt:+.4f} rad, el {el:.2f}° az {az:+.2f}°, {2 * math.degrees(math.asin(r / p.length)):.2f}° '
          f'wide at {p.length / 1000:.0f} km (k {k:.5f}), albedo gain {gain:.2f}')
    return ob


P_GEOM_GA = 0.43                 # Ganymede's geometric albedo (V)


def ganymede(sc, dlt, elong, cam_loc, seed=3.0):
    """Ganymede (Sprint 3.3, 03) at its Laplace place for Io at `dlt` (physics.ganymede_pos), scale k like Io, lit by
    the main Sun (it is never near Europa's or Jupiter's shadow on the transits that put it in the sky). At ~8 px no
    map is resolved: a mottled albedo (dark old terrain, bright grooved) round P_GEOM_GA. Returns the object."""
    fr = P.site(*P.SITE[1:])
    k = k_scale()
    p = Vector(P.to_local(P.from_site(P.ganymede_pos(dlt), fr), fr)) * 1000.0 * k
    r = P.R_GA * 1000.0 * k
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=r, location=Vector(cam_loc) + p)
    ob = bpy.context.object
    ob.name = 'Ganymede'
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new('Ganymede')
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    n = g.add('ShaderNodeTexNoise', Scale=2.5, Detail=4.0, Roughness=0.6, W=seed, noise_dimensions='4D')
    g.set(n, 'Vector', g.o(tc, 'Object'))
    a = 1.5 * P_GEOM_GA                                           # mean Lambert albedo, as Io's
    col = g.ramp(g.o(n, 'Fac'), [(0.40, (0.55 * a, 0.52 * a, 0.48 * a)), (0.60, (1.3 * a, 1.28 * a, 1.25 * a))])
    b = g.add('ShaderNodeBsdfDiffuse')
    g.set(b, 'Color', col)
    g.output(g.o(b, 0))
    ob.data.materials.append(m)
    u, dd, lit = P.ganymede_seen(dlt, elong, fr)
    el, az = P.alt_az(u)
    print(f'NOTE ganymede: Δ {dlt:+.4f} rad, el {el:.2f}° az {az:+.2f}°, {dd:.3f}° wide, {100 * lit:.0f} % lit, '
          f'at {p.length / 1000:.0f} km (k {k:.5f})')
    return ob
