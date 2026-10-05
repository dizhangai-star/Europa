"""The ice shell from inside (Sprint 2.3): the lid round the probe's hole, for 05 (the lid), 06 (descent), 07's top.
1 BU = 1 m. Nothing here invents a physical number: optics, pores, cracks and the refreezing come from physics.py.

Frames. The probe's frame is the world: its axis is world Z through x = y = 0, its nose at z = 0 (cameras follow the
probe). The ice belongs to `root` (an empty) whose z is the nose's true depth in metres, so a point of the ice sits at
local z = −(its true depth): key root's z to slide 20 km of ice up past a following camera (06). What moves with the
probe (the melt water round it, the open column above it, the freezing front) is in world coordinates; what is fixed
in the ice (pores, layers, veins, cracks, the inclusions left on the column's axis) is in root coordinates.

    sh = shell.build(sc, P, depth_m=30.0, cut=0.30)
    sh['root']     the ice (key location.z = nose depth, m)
    sh['box']      the ice volume round the probe: x ±half, y −cut…+half, z −below…+above (world)
    sh['water']    melt pocket + open column (lathe), sh['front_z'] = where the column has frozen shut (world z)
    sh['core']     with_core=True: the refrozen column's milky core above the front (physics.HOLE_CORE), else None
    shell.key_depth(sh, P, frame, depth_m)   slide the ice and key its σs with depth
    shell.key_sigma(sh, P, frame, depth_m)   06: key σs (and g) only; 06 keys root itself (a treadmill window)

Look, all physical and all homogeneous volumes (a textured volume cost 4×; homogeneous ones are sampled
analytically): the ice = pure-ice absorption (physics.ice_rgb: red dies in metres, blue travels hundreds) + pore
scattering σs (physics.pore: ≈ 6/m just under the regolith, milky; 0.14/m at 3 km; deep ice nearly clear), one keyable
value per depth. Overlapping volumes add, so structure is sheets of extra scatter: flat bands of more porous ice
(BAND_*: strata on the cut face, layers in the glow) and steep veins / flat sills of refrozen salty water (VEIN_*: deep
down the only thing the beam finds). Sheets are lenses (no hard rims), clipped to the box. The hole is bored out of all
of them by one world-fixed cylinder (live Boolean): above the probe it is clear refrozen ice (no pores) with a line
of gas/brine beads on its axis; round the probe and up to the freezing front it is melt water (IOR 1.333/1.311: the
front itself is nearly invisible, as it would be). Open cracks (air films, IOR 1/1.31: total internal reflection)
only in the brittle lid. The only light is the probe's lamp. Diffusive ice (σs ≥ SIMILAR_MIN) uses the similarity
relation σs(1 − g), g = 0 (same diffusion, ~4× fewer scattering events); it still needs ~128 volume bounces to carry
the glow a few metres (the board sets them; 8 bounces left everything past 0.5 m black).

Cut. Inside milky ice a camera sees centimetres, so the near shots are a cutaway: the box's −y face is the cut, a
polished ice face (IOR physics.N_ICE) `cut` m in front of the probe's axis (`face='none'`: a pure section without
refraction). The other faces have no surface (light leaves to the black void, no mirror walls). A camera inside the
box works too (deep clear ice: the honest view).
"""
import math

import bmesh
import bpy
import numpy as np

from . import nodes

_CACHE = {}


def _mat(name, build):
    m = bpy.data.materials.new(name)
    build(nodes.Graph(m))
    return m


def _mesh(sc, name, verts, faces, parent=None, mats=(), smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    for m in mats:
        me.materials.append(m)
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def refreeze(P, depth_km, h_ice):
    key = (round(depth_km, 3), h_ice)
    if key not in _CACHE:
        _CACHE[key] = P.refreeze(depth_km, h_ice)
    return _CACHE[key]


# ---------------------------------------------------------------- the ice volume (homogeneous: cheap)
SIMILAR_MIN = 1.0       # 1/m: below this the light is mostly single-scattered and the true g is kept


def _volume(g, P, sigma, similar, name=None):
    """Pure-ice absorption + scattering σs (a Value node, keyable: 06 keys it with depth) with the pores' g; similar
    (only where σs ≥ SIMILAR_MIN, diffusive): σs(1 − g), isotropic (same diffusion, ~4× fewer scattering events to
    carry light a few metres). A keyed σs keeps the mode chosen at build time."""
    similar = similar and (sigma >= SIMILAR_MIN or similar == 'force')
    v = g.add('ShaderNodeValue')
    v.outputs[0].default_value = sigma
    if name:
        v.name = v.label = name
    s = g.math('MULTIPLY', g.o(v, 0), 1.0 - P.PORE_G) if similar else g.o(v, 0)
    if similar and name:                                            # 06 switches to the true g when the ice clears
        s.node.name = s.node.label = name + 'Similar'
    sc_ = g.add('ShaderNodeVolumeScatter')
    if name:
        sc_.name = sc_.label = name + 'Scatter'
    g.set(sc_, 'Color', (1.0, 1.0, 1.0))
    g.set(sc_, 'Density', s)
    g.set(sc_, 'Anisotropy', 0.0 if similar else P.PORE_G)
    a = P.ice_rgb()
    amax = max(a)
    ab = g.add('ShaderNodeVolumeAbsorption')
    g.set(ab, 'Color', tuple(1.0 - x / amax for x in a))          # Cycles: σa = density × (1 − colour)
    g.set(ab, 'Density', amax)
    add = g.add('ShaderNodeAddShader')
    g.link(sc_, 0, add, 0)
    g.link(ab, 0, add, 1)
    return g.o(add, 0)


def _box_mats(P, sigma, face, similar):
    def cut(g):
        vol = _volume(g, P, sigma, similar, 'Sigma')
        b = g.add('ShaderNodeBsdfGlass', IOR=P.N_ICE, Roughness=0.0)
        g.output(g.o(b, 0), vol)

    def open_(g):
        vol = _volume(g, P, sigma, similar, 'Sigma')
        g.output(g.o(g.add('ShaderNodeBsdfTransparent'), 0), vol)
    m_open = _mat('ShellIce', open_)
    return (_mat('ShellIceCut', cut) if face == 'glass' else m_open), m_open


def _bore(ob, cutter):
    m = ob.modifiers.new('Hole', 'BOOLEAN')
    m.operation, m.solver, m.object = 'DIFFERENCE', 'EXACT', cutter


def _cutter(sc, r, z0, z1, n=48):
    """The hole as a world-fixed cylinder (hidden): bored out of the ice box, the veins and the cracks; it stays with
    the probe while the ice slides (the Boolean is re-evaluated per frame)."""
    v, f = [], []
    for z in (z0, z1):
        for j in range(n):
            a = 2 * math.pi * j / n
            v.append((r * math.cos(a), r * math.sin(a), z))
    f = [(j, (j + 1) % n, n + (j + 1) % n, n + j) for j in range(n)] + [tuple(range(n - 1, -1, -1)),
                                                                          tuple(range(n, 2 * n))]
    ob = _mesh(sc, 'HoleCutter', v, f)
    ob.hide_render = True
    ob.display_type = 'WIRE'
    return ob


# ---------------------------------------------------------------- melt water: pocket + open column (lathe)
def _water_mat(P):
    def build(g):
        a = P.water_rgb()
        amax = max(a)
        ab = g.add('ShaderNodeVolumeAbsorption')
        g.set(ab, 'Color', tuple(1.0 - x / amax for x in a))
        g.set(ab, 'Density', amax)
        b = g.add('ShaderNodeBsdfGlass', IOR=P.N_WATER / P.N_ICE, Roughness=0.0)
        g.output(g.o(b, 0), g.o(ab, 0))
    return _mat('MeltWater', build)


def water_lathe(sc, P, hole_r, top, open_m, profile, pocket=0.05, nseg=64):
    """Pocket under the nose (half-ellipsoid, `pocket` m deep), the hole round the probe, then the open column above
    the probe's top narrowing as profile [(fraction of the closing time, open radius)] says (time → height)."""
    rings = [(0.0, -pocket)]
    for k in range(1, 7):
        t = k / 6 * math.pi / 2
        rings.append((hole_r * math.sin(t), -pocket * math.cos(t)))
    rings.append((hole_r, top))
    for f, r in profile:
        if 0 < f < 1:
            rings.append((min(r, hole_r), top + f * open_m))
    rings.append((0.0, top + open_m))
    verts, faces = [], []
    for r, z in rings:
        for j in range(nseg):
            a = 2 * math.pi * j / nseg
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(len(rings) - 1):
        for j in range(nseg):
            j1 = (j + 1) % nseg
            faces.append((i * nseg + j, i * nseg + j1, (i + 1) * nseg + j1, (i + 1) * nseg + j))
    ob = _mesh(sc, 'MeltWater', verts, faces, mats=[_water_mat(P)], smooth=True)
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return ob


# ---------------------------------------------------------------- cracks and veins, in the ice's frame
def _slab(verts, faces, c, nrm, R, t, rng):
    """A lens-shaped sheet: an irregular 6–9-gon outline of radius ~R, thickness t at the centre thinning to 0 at the
    rim (sheets taper out: no hard edge), centred at c with normal nrm. Closed: two surfaces sharing the rim."""
    u = np.cross(nrm, [0.0, 0.0, 1.0])
    u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-6 else np.array([1.0, 0.0, 0.0])
    v = np.cross(nrm, u)
    k = int(rng.integers(6, 10)) * 2
    ang = np.sort(rng.uniform(0, 2 * math.pi, k))
    rad = R * rng.uniform(0.6, 1.0, k)
    rings = ((0.55, 0.84), (0.85, 0.53))                         # (radius fraction, thickness fraction): a lens
    base = len(verts)
    for side in (-0.5, 0.5):                                      # centre (2) + inner rings (2 × len(rings) × k)
        verts.append(tuple(c + nrm * side * t))
        for fr, tf in rings:
            for a, r in zip(ang, rad):
                verts.append(tuple(c + nrm * side * t * tf + (u * math.cos(a) + v * math.sin(a)) * r * fr))
    rim = len(verts)
    for a, r in zip(ang, rad):
        verts.append(tuple(c + (u * math.cos(a) + v * math.sin(a)) * r))
    nr = len(rings)
    for si, flip in ((0, True), (1, False)):
        b0 = base + si * (1 + nr * k)

        def ring(j):
            return (lambda i: b0 + 1 + j * k + i % k) if j < nr else (lambda i: rim + i % k)
        r0 = ring(0)
        for i in range(k):
            f = (b0, r0(i), r0(i + 1))
            faces.append(f[::-1] if flip else f)
        for j in range(nr):
            ra, rb = ring(j), ring(j + 1)
            for i in range(k):
                f = (ra(i), rb(i), rb(i + 1), ra(i + 1))
                faces.append(f[::-1] if flip else f)


def _clipped(sc, name, verts, faces, root, mats, half, ymin):
    """Slabs → one mesh, clipped to the box's sides (x ±half, y ymin…half) and closed again: the ice only slides in
    z, so the side clip made here in root coords stays true. Nothing pokes out in front of the cut."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    bm = bmesh.new()
    bm.from_mesh(me)
    for co, no in (((half, 0, 0), (1, 0, 0)), ((-half, 0, 0), (-1, 0, 0)), ((0, half, 0), (0, 1, 0)),
                   ((0, ymin, 0), (0, -1, 0))):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True)
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.parent = root
    return ob


def _normal(rng, dip_deg):
    dip, az = math.radians(dip_deg), rng.uniform(0, 2 * math.pi)
    return np.array([math.sin(dip) * math.cos(az), math.sin(dip) * math.sin(az), math.cos(dip)])


def cracks(sc, P, root, z_lo, z_hi, half, ymin, cutter, seed=11):
    """Open cracks in root coords z_lo..z_hi (= −depth) where depth < BRITTLE_KM: air films 2 mm thick, 0.2–2 m
    radius, dipping 55–90°. Glass IOR 1/n_ice: they flash by total internal reflection."""
    if -z_hi / 1000.0 >= P.BRITTLE_KM:
        return None
    rng = np.random.default_rng(seed)
    n = rng.poisson(P.CRACKS_PER_M3 * (2 * half) * (half - ymin) * (z_hi - z_lo))
    verts, faces = [], []
    for _ in range(n):
        c = np.array([rng.uniform(-half, half), rng.uniform(ymin, half), rng.uniform(z_lo, z_hi)])
        if -c[2] / 1000.0 < P.BRITTLE_KM:
            _slab(verts, faces, c, _normal(rng, rng.uniform(55, 90)), 0.2 * 10 ** rng.uniform(0.0, 1.0), 0.002, rng)
    if not faces:
        return None

    def mat(g):
        g.output(g.o(g.add('ShaderNodeBsdfGlass', IOR=1.0 / P.N_ICE, Roughness=0.015), 0))
    ob = _clipped(sc, 'Cracks', verts, faces, root, [_mat('Crack', mat)], half, ymin)
    _bore(ob, cutter)
    return ob


def veins(sc, P, root, z_lo, z_hi, half, ymin, cutter, similar=True, seed=12):
    """Refrozen veins (old cracks, sills) in root coords: lens sheets VEIN_T thick, 5–40 m radius, 70 % steep dikes, 30 %
    flat sills; their own homogeneous volume VEIN_BRINE_S adds to the ice's (overlapping volumes add in Cycles)."""
    rng = np.random.default_rng(seed)
    pad = 30.0                                                    # big sheets reach in from outside the box
    n = rng.poisson(P.VEINS_PER_M3 * (2 * (half + pad)) * (half + pad - ymin) * (z_hi - z_lo))
    verts, faces = [], []
    for _ in range(n):
        c = np.array([rng.uniform(-half - pad, half + pad), rng.uniform(ymin, half + pad), rng.uniform(z_lo, z_hi)])
        dip = rng.uniform(65, 90) if rng.random() < 0.7 else rng.uniform(0, 20)
        _slab(verts, faces, c, _normal(rng, dip), 5.0 * 10 ** rng.uniform(0.0, 0.9), rng.uniform(*P.VEIN_T), rng)
    if not faces:
        return None

    def mat(g):
        vol = _volume(g, P, P.VEIN_BRINE_S, similar)
        g.output(g.o(g.add('ShaderNodeBsdfTransparent'), 0), vol)
    ob = _clipped(sc, 'Veins', verts, faces, root, [_mat('Vein', mat)], half, ymin)
    _bore(ob, cutter)
    return ob


def bands(sc, P, root, z_lo, z_hi, half, ymin, cutter, sigma, similar=True, seed=14):
    """Flat-lying bands of more porous ice (dip 0–6°, 25–60 m radius, BAND_T thick at the centre): σs added = BAND_GAIN × the
    ice's (a node 'SigmaBand', keyed with the ice's by key_depth). The near-surface glow gets layers."""
    rng = np.random.default_rng(seed)
    pad = 50.0
    n = rng.poisson(P.BANDS_PER_M3 * (2 * (half + pad)) * (half + pad - ymin) * (z_hi - z_lo))
    verts, faces = [], []
    for _ in range(n):
        c = np.array([rng.uniform(-half - pad, half + pad), rng.uniform(ymin, half + pad), rng.uniform(z_lo, z_hi)])
        _slab(verts, faces, c, _normal(rng, rng.uniform(0, 6)), rng.uniform(25.0, 60.0), rng.uniform(*P.BAND_T), rng)
    if not faces:
        return None

    def mat(g):
        vol = _volume(g, P, P.BAND_GAIN * sigma, 'force' if similar and sigma >= SIMILAR_MIN else False, 'SigmaBand')
        g.output(g.o(g.add('ShaderNodeBsdfTransparent'), 0), vol)
    ob = _clipped(sc, 'Bands', verts, faces, root, [_mat('Band', mat)], half, ymin)
    _bore(ob, cutter)
    return ob


# ---------------------------------------------------------------- inclusions on the frozen column's axis
def _inclusion_mat(P, front_z):
    def build(g):
        geo = g.add('ShaderNodeNewGeometry')
        _, _, wz = g.xyz(g.o(geo, 'Position'))
        frozen = g.math('GREATER_THAN', wz, front_z)              # only where the column has frozen shut
        frozen.node.name = frozen.node.label = 'Front'            # (06 keys it: the column stays open longer deep down)
        b = g.add('ShaderNodeBsdfGlass', IOR=1.0 / P.N_ICE, Roughness=0.05)
        t = g.add('ShaderNodeBsdfTransparent')
        mx = g.add('ShaderNodeMixShader')
        g.set(mx, 0, frozen)
        g.link(t, 0, mx, 1)
        g.link(b, 0, mx, 2)
        g.output(g.o(mx, 0))
    return _mat('Inclusions', build)


def inclusions(sc, P, root, z_lo, z_hi, front_z, seed=13, per_m=260):
    """Gas/brine beads on the refrozen column's axis (root coords), radius 0.4–2.5 mm, within ~1.5 cm of the axis;
    shown only above the freezing front (world z > front_z)."""
    rng = np.random.default_rng(seed)
    n = int(per_m * (z_hi - z_lo))
    z = rng.uniform(z_lo, z_hi, n)
    r = 0.015 * np.sqrt(rng.random(n))
    a = rng.uniform(0, 2 * math.pi, n)
    pts = np.stack([r * np.cos(a), r * np.sin(a), z], -1)
    me = bpy.data.meshes.new('Inclusions')
    me.from_pydata(pts.tolist(), [], [])
    ob = bpy.data.objects.new('Inclusions', me)
    sc.collection.objects.link(ob)
    ob.parent = root
    gn = bpy.data.node_groups.new('InclusionPoints', 'GeometryNodeTree')
    gn.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    gn.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi, go = gn.nodes.new('NodeGroupInput'), gn.nodes.new('NodeGroupOutput')
    m2p = gn.nodes.new('GeometryNodeMeshToPoints')
    rv = gn.nodes.new('FunctionNodeRandomValue')
    rv.inputs['Min'].default_value, rv.inputs['Max'].default_value = 0.0004, 0.0025
    sm = gn.nodes.new('GeometryNodeSetMaterial')
    sm.inputs['Material'].default_value = _inclusion_mat(P, front_z)
    gn.links.new(gi.outputs[0], m2p.inputs['Mesh'])
    gn.links.new(rv.outputs['Value'], m2p.inputs['Radius'])
    gn.links.new(m2p.outputs['Points'], sm.inputs['Geometry'])
    gn.links.new(sm.outputs['Geometry'], go.inputs[0])
    ob.modifiers.new('Points', 'NODES').node_group = gn
    return ob


def core(sc, P, front_z, z_top, hole_r, nseg=32):
    """The refrozen column's milky core (physics.HOLE_CORE, IceCube's 'bubble column'): the gas and salt the melt held,
    pushed to the axis as the hole froze inward. World-fixed like the front: from a short cone at front_z (the last
    water to freeze) up to z_top. A homogeneous volume with the bubbles' true g (a few cm thick: not diffusive)."""
    frac, ls, g_ = P.HOLE_CORE
    rc = frac * hole_r
    rings = [(0.0, front_z)] + [(rc * math.sin(k / 4 * math.pi / 2), front_z + 2 * rc * (1 - math.cos(k / 4 * math.pi / 2)))
                                for k in range(1, 5)] + [(rc, z_top), (0.0, z_top)]
    verts, faces = [], []
    for r, z in rings:
        for j in range(nseg):
            a = 2 * math.pi * j / nseg
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(len(rings) - 1):
        for j in range(nseg):
            j1 = (j + 1) % nseg
            faces.append((i * nseg + j, i * nseg + j1, (i + 1) * nseg + j1, (i + 1) * nseg + j))

    def build(g):
        a = P.ice_rgb()
        amax = max(a)
        sc_ = g.add('ShaderNodeVolumeScatter')
        g.set(sc_, 'Color', (1.0, 1.0, 1.0))
        g.set(sc_, 'Density', 1.0 / ls)
        g.set(sc_, 'Anisotropy', g_)
        ab = g.add('ShaderNodeVolumeAbsorption')
        g.set(ab, 'Color', tuple(1.0 - x / amax for x in a))
        g.set(ab, 'Density', amax)
        add = g.add('ShaderNodeAddShader')
        g.link(sc_, 0, add, 0)
        g.link(ab, 0, add, 1)
        g.output(g.o(g.add('ShaderNodeBsdfTransparent'), 0), g.o(add, 0))
    ob = _mesh(sc, 'HoleCore', verts, faces, mats=[_mat('HoleCore', build)], smooth=True)
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return ob


# ---------------------------------------------------------------- the whole lid round the probe
def build(sc, P, depth_m, cut=0.30, half=10.0, below=16.0, above=12.0, face='glass', h_ice=None, p_kw=None,
          travel=0.0, sigma=None, similar=True, seed=11, with_core=False):
    """The shell round a probe whose nose is `depth_m` down (world z = 0 at the nose). `travel`: metres of ice that
    will slide past (06 keys root z from depth_m to depth_m + travel): cracks/veins/inclusions are made for all of
    it. sigma: the ice's σs (default physics.pore at depth_m; 06 keys it with key_depth)."""
    h_ice = h_ice or P.ICE_H[1]
    p_kw = p_kw or P.CRYO_P[2]
    hole_r = P.CRYO_D / 2
    top = P.CRYO_LEN
    pocket = 0.05
    root = bpy.data.objects.new('Shell', None)
    root.empty_display_size = 1.0
    sc.collection.objects.link(root)
    root.location = (0.0, 0.0, depth_m)
    cutter = _cutter(sc, hole_r + 0.002, -pocket - 0.01, above + 1.0)

    # the box (world), −y face = the cut, the hole bored out
    ymin = -cut
    x0, x1, y0, y1, z0, z1 = -half, half, ymin, half, -below, above
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0), (4, 5, 6, 7)]
    s0 = P.pore(depth_m / 1000.0)[1] if sigma is None else sigma
    m_cut, m_open = _box_mats(P, s0, face, similar)
    box = _mesh(sc, 'ShellIce', v, f, mats=[m_cut, m_open])
    for i, poly in enumerate(box.data.polygons):
        poly.material_index = 0 if i == 0 else 1
    _bore(box, cutter)

    # the open column above the probe (from the refreezing at this depth)
    hrs, prof = refreeze(P, depth_m / 1000.0, h_ice)
    v_mh = P.cryo_speed(p_kw, h_ice, depth_m / 1000.0) * 3600
    open_m = hrs * v_mh
    water = water_lathe(sc, P, hole_r, top, open_m, prof, pocket=pocket)
    front_z = top + open_m

    # what is fixed in the ice: made over the depths the shot will see (root coords, z = −depth)
    zl_lo = -(depth_m + travel) - below - 2.0
    zl_hi = -depth_m + above + 2.0
    cr = cracks(sc, P, root, zl_lo, zl_hi, half, ymin, cutter, seed=seed)
    vn = veins(sc, P, root, zl_lo, zl_hi, half, ymin, cutter, similar, seed=seed + 1)
    bd = bands(sc, P, root, zl_lo, zl_hi, half, ymin, cutter, s0, similar, seed=seed + 3)
    inc = inclusions(sc, P, root, max(zl_lo, -(depth_m + travel) + front_z - 0.2), zl_hi, front_z, seed=seed + 2)
    hc = core(sc, P, front_z, above, hole_r) if with_core else None
    print(f'NOTE shell: nose {depth_m:g} m down, σs {s0:.3g}/m, hole shuts {hrs:.2f} h = {open_m:.2f} m above the '
          f'probe top ({v_mh:.2f} m/h), cracks {0 if cr is None else len(cr.data.polygons)}, veins '
          f'{0 if vn is None else len(vn.data.polygons)} faces, bands {0 if bd is None else len(bd.data.polygons)} faces')
    return dict(root=root, box=box, water=water, core=hc, cracks=cr, veins=vn, bands=bd, inclusions=inc, cutter=cutter,
                front_z=front_z, open_m=open_m, hole_r=hole_r,
                mats=(m_cut, m_open) + ((bd.data.materials[0],) if bd else ()))


def fix_bore(sc, sh, travel):
    """For a shot whose ice slides up `travel` m along the hole's axis (05): bore the sheets (cracks, veins, bands)
    once, at root's current z, with a cutter reaching `travel` m further below the nose, and drop their live Booleans.
    A slide along the axis leaves the hole where it was, so the only change is a spurious hole up to `travel` m below
    the nose (out of 05's frame). Needed, not an optimisation: re-run per frame, the EXACT solver dropped a whole band
    sheet at some positions (05's animatic: a band vanished between frames 52 and 53, Bands 922 → 821 faces)."""
    me = sh['cutter'].data
    zmin = min(v.co.z for v in me.vertices)
    long_ = bpy.data.objects.new('HoleCutterLong', me.copy())
    sc.collection.objects.link(long_)
    long_.hide_render = True
    for v in long_.data.vertices:
        if v.co.z <= zmin + 1e-6:
            v.co.z -= travel
    dg = bpy.context.evaluated_depsgraph_get()
    for k in ('cracks', 'veins', 'bands'):
        ob = sh.get(k)
        if ob is None:
            continue
        ob.modifiers['Hole'].object = long_
        dg.update()
        new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.remove(ob.modifiers['Hole'])
        ob.data = new
    bpy.data.objects.remove(long_, do_unlink=True)


def key_depth(sh, P, frame, depth_m):
    """Slide the ice so the nose is depth_m down on `frame`, its σs following physics.pore."""
    sh['root'].location.z = depth_m
    sh['root'].keyframe_insert('location', index=2, frame=frame)
    key_sigma(sh, P, frame, depth_m)


def key_sigma(sh, P, frame, depth_m):
    """Key the ice's σs (and the bands') for depth_m on `frame`. A material built in similarity mode (σs(1 − g),
    g = 0: diffusive ice) switches to the true σs and g where σs < SIMILAR_MIN: the light is mostly single-scattered
    there and the beam's side-look depends on g (06 goes from 5.7/m to 0.006/m). Returns σs."""
    s = P.pore(depth_m / 1000.0)[1]
    sim = s >= SIMILAR_MIN
    for m in set(sh['mats']):
        nt = m.node_tree.nodes
        for name, val in (('Sigma', s), ('SigmaBand', P.BAND_GAIN * s)):
            node = nt.get(name)
            if node:
                node.outputs[0].default_value = val
                node.outputs[0].keyframe_insert('default_value', frame=frame)
            mul, sct = nt.get(name + 'Similar'), nt.get(name + 'Scatter')
            if mul and sct:
                mul.inputs[1].default_value = 1.0 - P.PORE_G if sim else 1.0
                mul.inputs[1].keyframe_insert('default_value', frame=frame)
                sct.inputs['Anisotropy'].default_value = 0.0 if sim else P.PORE_G
                sct.inputs['Anisotropy'].keyframe_insert('default_value', frame=frame)
    return s
