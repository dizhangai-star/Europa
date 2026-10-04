"""The ocean under the ice (Sprint 2.4): the shell's base seen from the water, the water, what drifts in it. For 07
(breakthrough) and 08 (abyss). 1 BU = 1 m. Every number comes from physics.py (rows "Ice base …", "Frazil",
"Lamp seen from …"); nobody has seen this place, so the shapes are Earth's ice-shelf bases at Europa's scale.

Frame: world z = 0 is the ice base at the probe's exit hole (x = y = 0), +z up into the ice; the current runs +x.

    oc = ocean.build(sc, P, kind='melt', half=60.0, deep=400.0)
    oc['ice']      the base ice: a closed slab whose underside is the ceiling (subsurface: light enters and spreads
                   in it, as sea ice seen from below), the probe's hole bored through it (live Boolean)
    oc['water']    one homogeneous volume (pure-water absorption + particle scatter), filling the hole too
    ocean.ceiling_z(oc, x, y)   the ceiling's height there (numpy, same field as the mesh)
    ocean.motes(sc, P, centre, radius) / ocean.frazil(sc, P, centre, radius)   drifting point clouds (they move by
                   themselves with the scene time: the current OCEAN_U along +x, frazil rising at rise_speed())

Ceilings (`kind`):
- 'melt': where the base melts (the ice pump's deep side). Terraces (Icefin under Thwaites: flat treads, steep risers,
  in all orientations; BASE_RISER / BASE_TREAD / BASE_RISER_DEG) and melt scallops all over them, scallop_len() long
  for the current OCEAN_U (Curl's Re 22,500), cups up into the ice with sharp crests.
- 'freeze': where it grows (the shallow side), ⚠ model: a smooth undulating base of accreted marine ice with a fringe
  of loose frazil platelets hanging from it.
The ice: reduced scattering BASE_SIGMA_P + pure-ice absorption → physics.base_ice() gives the diffuse albedo and the
mean free path per channel for Cycles' random-walk subsurface (no tint chosen by eye: red dies in the long paths). The
surface itself barely reflects (ice → water, relative index 1.017).
"""
import math

import bpy
import numpy as np

from . import nodes
from .europa_world import fbm, _hash, smooth


def _mat(name, build):
    m = bpy.data.materials.new(name)
    build(nodes.Graph(m))
    return m


def _mesh(sc, name, verts, faces, mats=(), smooth_=False):
    me = bpy.data.meshes.new(name)
    if len({len(x) for x in faces}) != 1:                  # mixed face sizes (caps, discs): the slow path
        me.from_pydata([tuple(x) for x in verts], [], [tuple(x) for x in faces])
        return _finish(sc, name, me, mats, smooth_)
    v = np.asarray(verts, dtype=np.float32)
    f = np.asarray(faces, dtype=np.int32)
    me.vertices.add(len(v))
    me.vertices.foreach_set('co', v.ravel())
    me.loops.add(f.size)
    me.loops.foreach_set('vertex_index', f.ravel())
    me.polygons.add(len(f))
    me.polygons.foreach_set('loop_start', np.arange(0, f.size, f.shape[1], dtype=np.int32))
    me.update(calc_edges=True)
    me.validate()
    return _finish(sc, name, me, mats, smooth_)


def _finish(sc, name, me, mats, smooth_):
    for m in mats:
        me.materials.append(m)
    if smooth_:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- the ceiling's height field
def _voronoi(X, Y, cx, cy, seed):
    """F1 and F2 distances (in cell units) to jittered points on a cx × cy grid."""
    gx, gy = X / cx, Y / cy
    ix, iy = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
    f1 = np.full(X.shape, 9.0)
    f2 = np.full(X.shape, 9.0)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            jx, jy = ix + di, iy + dj
            px = jx + 0.1 + 0.8 * _hash(jx, jy, seed)
            py = jy + 0.1 + 0.8 * _hash(jx, jy, seed + 7)
            d = np.hypot(gx - px, gy - py)
            f2 = np.where(d < f1, f1, np.minimum(f2, d))
            f1 = np.minimum(f1, d)
    return f1, f2


def height(P, X, Y, kind='melt', seed=21):
    """Ceiling height z (m) at X, Y, before re-centring on the hole."""
    if kind == 'freeze':
        return 0.6 * (fbm(X / 14, Y / 14, 4, seed) - 0.5) + 0.12 * (fbm(X / 2.5, Y / 2.5, 3, seed + 3) - 0.5)
    r0, r1 = P.BASE_RISER
    t0, t1 = P.BASE_TREAD
    slope = (r0 + r1) / (t0 + t1)                       # mean riser / mean tread: the base's mean tilt
    az = math.radians(35.0)                             # film pick: the tilt's direction (terraces face every way
    f = slope * (X * math.cos(az) + Y * math.sin(az))   # anyway: the wandering term bends the contours)
    f = f + 9.0 * (fbm(X / 45, Y / 45, 3, seed) - 0.5) + 2.0 * (fbm(X / 12, Y / 12, 3, seed + 1) - 0.5)
    hs = r0 + (r1 - r0) * smooth(0.25, 0.75, fbm(X / 30, Y / 30, 3, seed + 2))     # riser height, varies by area
    q = f / hs
    k = np.floor(q)
    w = np.clip(slope / math.tan(math.radians(P.BASE_RISER_DEG)) * 1.6, 0.03, 0.4)  # riser's share of one step
    z = hs * (k + smooth(1.0 - w, 1.0, q - k))
    L = P.scallop_len()
    f1, f2 = _voronoi(X, Y, L, 1.25 * L, seed + 5)       # cells a little wider across the current than along it
    t = np.clip(2 * f1 / (f1 + f2), 0.0, 1.0)            # 0 at a cup's centre, 1 on its crest
    dep = 0.12 * L * (0.6 + 0.8 * fbm(X / 6, Y / 6, 2, seed + 6))   # film pick: depth/length ≈ 0.1 (Curl's scallops)
    return z + dep * (1.0 - t * t)                       # cups go up into the ice, crests hang down


def _axis(half, n, k=3.0):
    u = np.linspace(-1.0, 1.0, n)
    return half * np.sinh(k * u) / math.sinh(k)          # dense round the hole (~5 cm), ~0.5 m at the edge


def ceiling_z(oc, x, y):
    return height(oc['P'], np.asarray(x, float), np.asarray(y, float), oc['kind'], oc['seed']) - oc['z0']


# ---------------------------------------------------------------- materials
def ice_mat(P, name='BaseIce'):
    alb, mfp = P.base_ice()

    def build(g):
        tc = g.add('ShaderNodeTexCoord')
        n = g.add('ShaderNodeTexNoise', Scale=1 / 0.05, Detail=6, Roughness=0.6)
        g.set(n, 'Vector', g.o(tc, 'Object'))
        bp = g.add('ShaderNodeBump', Strength=0.6, Distance=0.004)
        g.set(bp, 'Height', g.o(n, 'Fac'))
        b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.25, subsurface_method='RANDOM_WALK')
        g.set(b, 'Base Color', tuple(alb) + (1.0,))
        b.inputs['Subsurface Weight'].default_value = 1.0
        b.inputs['Subsurface Radius'].default_value = tuple(mfp)
        b.inputs['Subsurface Scale'].default_value = 1.0
        b.inputs['IOR'].default_value = P.N_WATER / P.N_ICE
        b.inputs['Specular IOR Level'].default_value = 0.5
        g.set(b, 'Normal', g.o(bp, 'Normal'))
        g.output(g.o(b, 'BSDF'))
    return _mat(name, build)


def water_mat(P, scatter=None):
    def build(g):
        a = P.water_rgb()
        amax = max(a)
        ab = g.add('ShaderNodeVolumeAbsorption')
        g.set(ab, 'Color', tuple(1.0 - x / amax for x in a))          # Cycles: σa = density × (1 − colour)
        g.set(ab, 'Density', amax)
        s = g.add('ShaderNodeVolumeScatter')
        g.set(s, 'Color', (1.0, 1.0, 1.0))
        g.set(s, 'Density', P.SEA_SCATTER if scatter is None else scatter)
        g.set(s, 'Anisotropy', P.SEA_G)
        add = g.add('ShaderNodeAddShader')
        g.link(ab, 0, add, 0)
        g.link(s, 0, add, 1)
        g.output(g.o(g.add('ShaderNodeBsdfTransparent'), 0), g.o(add, 0))
    return _mat('Ocean', build)


def frazil_mat(P):
    def build(g):                                         # an ice disc in water: glass at the relative index
        g.output(g.o(g.add('ShaderNodeBsdfGlass', IOR=P.N_ICE / P.N_WATER, Roughness=0.02), 0))
    return _mat('Frazil', build)


def mote_mat():
    def build(g):
        b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.8)
        g.set(b, 'Base Color', (0.55, 0.52, 0.48, 1.0))
        g.output(g.o(b, 'BSDF'))
    return _mat('Mote', build)


# ---------------------------------------------------------------- the ice slab and the water
def _slab(H, xs, ys, ztop):
    """Closed slab: the height field H (nx × ny) underneath, a flat top at ztop, four walls. Outward normals."""
    nx, ny = H.shape
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    bot = np.stack([X, Y, H], -1).reshape(-1, 3)
    top = np.stack([X, Y, np.full_like(H, ztop)], -1).reshape(-1, 3)
    nb = nx * ny
    ii = (np.arange(nx - 1)[:, None] * ny + np.arange(ny - 1)[None, :]).ravel()
    fb = np.stack([ii, ii + 1, ii + ny + 1, ii + ny], -1)            # underside faces −z
    ft = np.stack([ii, ii + ny, ii + ny + 1, ii + 1], -1) + nb      # top faces +z
    rim = ([(i * ny) for i in range(nx)] + [(nx - 1) * ny + j for j in range(1, ny)]
           + [i * ny + ny - 1 for i in range(nx - 2, -1, -1)] + [j for j in range(ny - 2, 0, -1)])
    walls = [(rim[(k + 1) % len(rim)], rim[k], rim[k] + nb, rim[(k + 1) % len(rim)] + nb) for k in range(len(rim))]
    return np.concatenate([bot, top]), np.concatenate([fb, ft, np.asarray(walls)])


def _cutter(sc, r, z0, z1, n=48):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    v = [(r * math.cos(t), r * math.sin(t), z) for z in (z0, z1) for t in a]
    f = [(j, (j + 1) % n, n + (j + 1) % n, n + j) for j in range(n)] + [tuple(range(n - 1, -1, -1)),
                                                                          tuple(range(n, 2 * n))]
    ob = _mesh(sc, 'ExitHole', v, f)
    ob.hide_render = True
    ob.display_type = 'WIRE'
    return ob


def build(sc, P, kind='melt', half=60.0, deep=400.0, n=801, seed=21, hole=True, scatter=None, platelets=True):
    """The base ice (slab), the exit hole, the water below. kind 'melt' | 'freeze' (⚠ model, with platelets)."""
    xs = _axis(half, n)
    X, Y = np.meshgrid(xs, xs, indexing='ij')
    z0 = float(height(P, np.zeros(1), np.zeros(1), kind, seed)[0])
    H = height(P, X, Y, kind, seed) - z0
    ztop = float(H.max()) + 3.0
    v, f = _slab(H, xs, xs, ztop)
    ice = _mesh(sc, 'BaseIce', v, f, mats=[ice_mat(P)], smooth_=True)
    hole_r = P.CRYO_D / 2 + 0.002
    cut = None
    if hole:
        cut = _cutter(sc, hole_r, float(H.min()) - 1.0, ztop + 1.0)
        m = ice.modifiers.new('Hole', 'BOOLEAN')
        m.operation, m.solver, m.object = 'DIFFERENCE', 'EXACT', cut

    # the water: a box from the deep up into the slab (the hole is water too); inside the ice's random walk no
    # volume applies, so the overlap only fills the hole
    x0, x1, zb = -half * 0.995, half * 0.995, -deep
    bv = [(x0, x0, zb), (x1, x0, zb), (x1, x1, zb), (x0, x1, zb),
          (x0, x0, ztop - 0.5), (x1, x0, ztop - 0.5), (x1, x1, ztop - 0.5), (x0, x1, ztop - 0.5)]
    bf = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0), (4, 5, 6, 7)]
    water = _mesh(sc, 'Ocean', bv, bf, mats=[water_mat(P, scatter)])
    oc = dict(ice=ice, water=water, cutter=cut, hole_r=hole_r, P=P, kind=kind, seed=seed, z0=z0, ztop=ztop,
              half=half)
    if kind == 'freeze' and platelets:
        oc['platelets'] = platelet_fringe(sc, P, oc)
    print(f'NOTE ocean: {kind} ceiling ±{half:g} m ({n}² verts, z {H.min():.1f}…{H.max():.1f} m), scallops '
          f'{P.scallop_len():.2f} m, base-ice albedo {tuple(round(a, 2) for a in P.base_ice()[0])}, water '
          f'{deep:g} m deep')
    return oc


# ---------------------------------------------------------------- what drifts in the water
def _disc(r, t, nseg=6):
    a = np.linspace(0, 2 * math.pi, nseg, endpoint=False)
    v = [(r * math.cos(x), r * math.sin(x), z) for z in (-t / 2, t / 2) for x in a]
    f = [tuple(range(nseg - 1, -1, -1)), tuple(range(nseg, 2 * nseg))]
    f += [(j, (j + 1) % nseg, nseg + (j + 1) % nseg, nseg + j) for j in range(nseg)]
    return v, f


def _cloud(centre, radius, per_m3, seed, below=0.0, oc=None):
    """Uniform points in a sphere, kept under the ceiling (minus `below`)."""
    rng = np.random.default_rng(seed)
    N = int(per_m3 * 4 / 3 * math.pi * radius ** 3)
    u = rng.normal(size=(N, 3))
    u /= np.linalg.norm(u, axis=1)[:, None]
    p = u * (radius * rng.random(N) ** (1 / 3))[:, None] + np.asarray(centre, float)
    if oc is not None:
        p = p[p[:, 2] < ceiling_z(oc, p[:, 0], p[:, 1]) - below]
    return p, rng


def _drift_nodes(name, P, rise, flutter, inst=None, rmin=0.0, rmax=0.0, mat=None):
    """GN: (instances on) points that move with the scene time: the current +x, rising `rise` m/s (± 40 % per
    point), instances turning slowly (frazil flutters as it rises)."""
    gn = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    gn.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    gn.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = gn.nodes
    L = gn.links.new
    gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput')
    m2p = N.new('GeometryNodeMeshToPoints')
    L(gi.outputs[0], m2p.inputs['Mesh'])
    t = N.new('GeometryNodeInputSceneTime')
    rv = N.new('FunctionNodeRandomValue')
    rv.inputs['Min'].default_value, rv.inputs['Max'].default_value = 0.6, 1.4
    rv.inputs['Seed'].default_value = 3
    up = N.new('ShaderNodeMath')
    up.operation = 'MULTIPLY'
    up.inputs[1].default_value = rise
    L(rv.outputs['Value'], up.inputs[0])
    vel = N.new('ShaderNodeCombineXYZ')
    vel.inputs['X'].default_value = P.OCEAN_U
    L(up.outputs[0], vel.inputs['Z'])
    off = N.new('ShaderNodeVectorMath')
    off.operation = 'SCALE'
    L(vel.outputs[0], off.inputs[0])
    L(t.outputs['Seconds'], off.inputs['Scale'])
    sp = N.new('GeometryNodeSetPosition')
    L(m2p.outputs['Points'], sp.inputs['Geometry'])
    L(off.outputs[0], sp.inputs['Offset'])
    geo = sp.outputs['Geometry']
    if inst is not None:
        oi = N.new('GeometryNodeObjectInfo')
        oi.inputs['Object'].default_value = inst
        iop = N.new('GeometryNodeInstanceOnPoints')
        r0 = N.new('FunctionNodeRandomValue')
        r0.data_type = 'FLOAT_VECTOR'
        r0.inputs['Max'].default_value = (6.2832, 6.2832, 6.2832)
        r0.inputs['Seed'].default_value = 5
        L(geo, iop.inputs['Points'])
        L(oi.outputs['Geometry'], iop.inputs['Instance'])
        L(r0.outputs['Value'], iop.inputs['Rotation'])
        rs = N.new('FunctionNodeRandomValue')
        rs.inputs['Min'].default_value, rs.inputs['Max'].default_value = rmin, rmax
        rs.inputs['Seed'].default_value = 9
        L(rs.outputs['Value'], iop.inputs['Scale'])
        rot = N.new('GeometryNodeRotateInstances')
        spin = N.new('FunctionNodeRandomValue')
        spin.data_type = 'FLOAT_VECTOR'
        spin.inputs['Min'].default_value = (-flutter,) * 3
        spin.inputs['Max'].default_value = (flutter,) * 3
        spin.inputs['Seed'].default_value = 11
        ang = N.new('ShaderNodeVectorMath')
        ang.operation = 'SCALE'
        L(spin.outputs['Value'], ang.inputs[0])
        L(t.outputs['Seconds'], ang.inputs['Scale'])
        L(iop.outputs['Instances'], rot.inputs['Instances'])
        L(ang.outputs[0], rot.inputs['Rotation'])
        rot.inputs['Local Space'].default_value = True
        geo = rot.outputs['Instances']
    else:
        rs = N.new('FunctionNodeRandomValue')
        rs.inputs['Min'].default_value, rs.inputs['Max'].default_value = rmin, rmax
        L(rs.outputs['Value'], m2p.inputs['Radius'])
    if mat is not None:
        sm = N.new('GeometryNodeSetMaterial')
        sm.inputs['Material'].default_value = mat
        L(geo, sm.inputs['Geometry'])
        geo = sm.outputs['Geometry']
    L(geo, go.inputs[0])
    return gn


def _points_object(sc, name, pts, gn):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(pts))
    me.vertices.foreach_set('co', pts.astype(np.float32).ravel())
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.modifiers.new('Drift', 'NODES').node_group = gn
    return ob


def motes(sc, P, centre, radius, oc=None, seed=31, per_m3=None):
    """Mineral/salt grains (Ø 0.2–1 mm) drifting with the current: the beam's particles made visible."""
    pts, _ = _cloud(centre, radius, P.MOTES_PER_M3 if per_m3 is None else per_m3, seed, 0.01, oc)
    gn = _drift_nodes('MoteDrift', P, 0.0, 0.0, rmin=0.0001, rmax=0.0005, mat=mote_mat())
    return _points_object(sc, 'Motes', pts, gn)


def frazil(sc, P, centre, radius, oc=None, seed=33, per_m3=None):
    """⚠ Frazil discs (Ø FRAZIL_D ± 50 %, glass at the ice/water index) rising at rise_speed() and drifting with the
    current, fluttering (≤ 1.5 rad/s, film pick)."""
    pts, _ = _cloud(centre, radius, P.FRAZIL_PER_M3 if per_m3 is None else per_m3, seed, 0.02, oc)
    v, f = _disc(P.FRAZIL_D / 2, P.FRAZIL_T)
    proto = _mesh(sc, 'FrazilDisc', v, f, mats=[frazil_mat(P)])
    proto.hide_render = True
    proto.hide_viewport = True
    gn = _drift_nodes('FrazilDrift', P, P.rise_speed(), 1.5, inst=proto, rmin=0.5, rmax=1.5, mat=frazil_mat(P))
    return _points_object(sc, 'Frazil', pts, gn)


def platelet_fringe(sc, P, oc, radius=14.0, per_m2=250.0, seed=35):
    """⚠ 'freeze' ceiling: loose platelets (2–8 cm, film pick: Earth's sub-ice platelet layers) hanging 0–15 cm below
    the base, mostly upright (their c-axes horizontal), glass at the ice/water index."""
    rng = np.random.default_rng(seed)
    N = int(per_m2 * math.pi * radius ** 2)
    r = radius * np.sqrt(rng.random(N))
    a = 2 * math.pi * rng.random(N)
    x, y = r * np.cos(a), r * np.sin(a)
    keep = np.hypot(x, y) > P.CRYO_D
    x, y = x[keep], y[keep]
    z = ceiling_z(oc, x, y) - 0.15 * rng.random(len(x)) ** 2
    v1, f1 = _disc(0.5, 0.02)
    V, F = [], []
    for i in range(len(x)):
        s = rng.uniform(0.02, 0.08)
        tilt = rng.normal(math.pi / 2, 0.35)
        az = rng.uniform(0, 2 * math.pi)
        ca, sa, ct, st = math.cos(az), math.sin(az), math.cos(tilt), math.sin(tilt)
        base = len(V)
        for (px, py, pz) in v1:
            px, py, pz = px * s, py * s, pz * s
            py, pz = py * ct - pz * st, py * st + pz * ct
            px, py = px * ca - py * sa, px * sa + py * ca
            V.append((x[i] + px, y[i] + py, z[i] + pz - s / 2))
        F += [tuple(base + k for k in face) for face in f1]
    return _mesh(sc, 'Platelets', V, F, mats=[frazil_mat(P)])
