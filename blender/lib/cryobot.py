"""The cryobot (melt probe), built in code. 1 BU = 1 m. Its own frame: origin at the nose tip, +Z up the probe (the
nose points down when it hangs or melts), +X = the lamp port's side. Layout, sizes and sources: physics.CRYO_* (PRIME,
Tunnelbot, VALKYRIE); nothing here invents a size.

    bot = cryobot.build(sc, P, tether=2.0, pucks_above=(0.6, 1.4), open=0.0, lamp=True)
    bot['root']        empty at the nose tip: move/rotate this
    bot['swimmers']    50 objects (SWIM ⚠ concept), each with ['rest'] = its stowed matrix_basis (16 floats, row-major);
                       shots key them
    bot['lamp']        the spot (physics.CRYO_LAMP_W) at the port, aimed along the port axis

Sections from the nose (titanium brushed, the heat section bead-blasted): copper melt head (hot-water jets; ~0–100 °C, no glow) · instrument bay (lamp port tilted
`PORT_TILT` down, camera dome, sample inlets) · swimmer package (2 tiers × 25 radial wedges: their backs are the
hull here) · heat source · electronics vault · tail (puck magazine; the top puck sits in the open top, the tether runs
up through its centre: pucks are threaded on it and freeze into the hole where they are dropped). The head is 3 mm
wider than the body (the body clears the melt hole).
"""
import math

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector

from . import nodes

NSEG = 96
PORT_AZ, PORT_Z_FRAC, PORT_TILT = 0.0, 0.57, 25.0       # deg / fraction of the bay / deg down: film picks
CAM_AZ = 38.0
INLET_AZ = (120.0, 200.0, 280.0)


# ---------------------------------------------------------------- mesh helpers
def _mesh(name, verts, faces, mats=(), mat_idx=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    for m in mats:
        me.materials.append(m)
    if mat_idx is not None:
        me.polygons.foreach_set('material_index', list(mat_idx))
    me.validate()
    me.update()
    if smooth:
        me.shade_smooth()
    return me


def _lathe(bands, nseg=NSEG):
    """bands: [(mat, [(r, z), …]), …], each a smooth band (a corner = a new band: its rings are duplicated, so the
    edge is hard). Walking a band, the surface faces right of the direction of travel (up an outer wall = outward)."""
    a = np.linspace(0.0, 2 * math.pi, nseg, endpoint=False)
    ca, sa = np.cos(a), np.sin(a)
    V, F, M = [], [], []
    for mat, prof in bands:
        rings = []
        for r, z in prof:
            i0 = len(V)
            if r < 1e-7:
                V.append((0.0, 0.0, z))
                rings.append([i0])
            else:
                V.extend(zip(r * ca, r * sa, np.full(nseg, z)))
                rings.append(list(range(i0, i0 + nseg)))
        for A, B in zip(rings, rings[1:]):
            for k in range(nseg):
                k1 = (k + 1) % nseg
                if len(A) == 1:
                    F.append((A[0], B[k1], B[k]))
                elif len(B) == 1:
                    F.append((A[k], A[k1], B[0]))
                else:
                    F.append((A[k], A[k1], B[k1], B[k]))
                M.append(mat)
    return V, F, M


def _cyl(r, h0, h1, n=24, cap=True):
    """Cylinder along local +Z from h0 to h1 (outer cap at h1)."""
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    V = [(r * math.cos(t), r * math.sin(t), h0) for t in a] + [(r * math.cos(t), r * math.sin(t), h1) for t in a]
    F = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    if cap:
        V.append((0.0, 0.0, h1))
        F += [(n + k, n + (k + 1) % n, 2 * n) for k in range(n)]
    return V, F


def _merge(parts):
    """parts: [(verts, faces, mat_idx, Matrix)] → one verts/faces/mats list."""
    V, F, M = [], [], []
    for v, f, mi, mx in parts:
        o = len(V)
        V.extend(tuple(mx @ Vector(p)) for p in v)
        F.extend(tuple(i + o for i in ff) for ff in f)
        M.extend([mi] * len(f))
    return V, F, M


def _frame(origin, axis):
    """Matrix taking local +Z to `axis` at `origin`."""
    q = Vector(axis).normalized().to_track_quat('Z', 'Y')
    return Matrix.Translation(Vector(origin)) @ q.to_matrix().to_4x4()


def _radial(az_deg, z, r, tilt_deg=0.0):
    a = math.radians(az_deg)
    rad = Vector((math.cos(a), math.sin(a), 0.0))
    t = math.radians(tilt_deg)
    return rad * r + Vector((0, 0, z)), rad * math.cos(t) - Vector((0, 0, math.sin(t)))


# ---------------------------------------------------------------- materials
def _mat(name, build):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    build(nodes.Graph(m))
    return m


def titanium(g):
    """Lathe-turned titanium: anisotropic round the axis, faint turning rings (roughness varies with z)."""
    tc = g.add('ShaderNodeTexCoord')
    _, _, z = g.xyz(g.o(tc, 'Object'))
    rings = g.add('ShaderNodeTexNoise', noise_dimensions='1D', Scale=1.0, Detail=4, Roughness=0.6)
    g.set(rings, 'W', g.math('MULTIPLY', z, 260.0))
    blot = g.add('ShaderNodeTexNoise', Scale=6.0, Detail=3)
    g.set(blot, 'Vector', g.o(tc, 'Object'))
    rough = g.math('ADD', g.maprange(g.o(rings, 'Fac'), 0.3, 0.7, 0.26, 0.31),
                   g.maprange(g.o(blot, 'Fac'), 0.4, 0.7, 0.0, 0.08))
    b = g.add('ShaderNodeBsdfPrincipled', Metallic=1.0)
    g.set(b, 'Base Color', g.mix(g.maprange(g.o(blot, 'Fac'), 0.35, 0.65), (0.44, 0.42, 0.40), (0.52, 0.50, 0.47)))
    g.set(b, 'Roughness', rough)
    tan = g.add('ShaderNodeTangent', direction_type='RADIAL', axis='Z')
    g.set(b, 'Anisotropic', 0.55)
    g.set(b, 'Tangent', g.o(tan, 'Tangent'))
    g.output(g.o(b, 'BSDF'))


def copper(g):
    """Copper melt head, worn by three years of hot water: warm metal, blotchy dark oxide."""
    tc = g.add('ShaderNodeTexCoord')
    mp = g.add('ShaderNodeMapping')
    g.set(mp, 'Vector', g.o(tc, 'Object'))
    g.set(mp, 'Scale', (1.0, 1.0, 0.25))                     # streaks along the axis (water flows back past it)
    n = g.add('ShaderNodeTexNoise', Scale=45.0, Detail=8, Roughness=0.65)
    g.set(n, 'Vector', g.o(mp, 'Vector'))
    ox = g.math('MULTIPLY', g.maprange(g.o(n, 'Fac'), 0.5, 0.75), 0.7)
    b = g.add('ShaderNodeBsdfPrincipled', Metallic=1.0)
    g.set(b, 'Base Color', g.mix(ox, (0.955, 0.638, 0.538), (0.50, 0.29, 0.19)))
    g.set(b, 'Roughness', g.maprange(ox, 0.0, 1.0, 0.22, 0.5))
    g.output(g.o(b, 'BSDF'))


def plain(color, rough, metal=0.0, coat=0.0):
    def f(g):
        b = g.add('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
        g.set(b, 'Base Color', color)
        if coat:
            g.set(b, 'Coat Weight', coat)
        g.output(g.o(b, 'BSDF'))
    return f


def blasted(g):
    """Bead-blasted titanium (the heat section): matte, no brushing, a fine speckle."""
    tc = g.add('ShaderNodeTexCoord')
    n = g.add('ShaderNodeTexNoise', Scale=900.0, Detail=2)
    g.set(n, 'Vector', g.o(tc, 'Object'))
    b = g.add('ShaderNodeBsdfPrincipled', Metallic=1.0)
    g.set(b, 'Base Color', g.mix(g.o(n, 'Fac'), (0.36, 0.35, 0.33), (0.42, 0.41, 0.39)))
    g.set(b, 'Roughness', 0.48)
    g.output(g.o(b, 'BSDF'))


def window(glow):
    """Lamp port (sapphire over the LED array): emission = the lamp's power over the port's area when on."""
    def f(g):
        b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.04)
        g.set(b, 'Base Color', (0.02, 0.02, 0.025))
        g.set(b, 'Emission Color', (1.0, 0.97, 0.92))
        g.set(b, 'Emission Strength', glow)
        g.output(g.o(b, 'BSDF'))
    return f


def swimmer_paint(R):
    """Swimmer: pale satin paint, a dark sensor tip at its inner (leading) end (local: tip at the axis)."""
    def f(g):
        tc = g.add('ShaderNodeTexCoord')
        x, _, _ = g.xyz(g.o(tc, 'Object'))
        tip = g.math('LESS_THAN', x, 0.035)
        b = g.add('ShaderNodeBsdfPrincipled')
        g.set(b, 'Base Color', g.mix(tip, (0.62, 0.62, 0.60), (0.012, 0.012, 0.014)))
        g.set(b, 'Roughness', g.maprange(tip, 0.0, 1.0, 0.40, 0.08))
        g.output(g.o(b, 'BSDF'))
    return f


# ---------------------------------------------------------------- parts
def _layout(P):
    z, out = 0.0, {}
    for name, l in P.CRYO_SECTIONS:
        out[name] = (z, z + l)
        z += l
    return out


def _groove(mat, r, z, w=0.004, d=0.003):
    """A seam: in from the wall at z, across, back out at z + w (three hard bands)."""
    return [(mat, [(r, z), (r - d, z)]), (mat, [(r - d, z), (r - d, z + w)]), (mat, [(r - d, z + w), (r, z + w)])]


def hull(P, S, mats):
    """One lathe, tip to top: copper head, seams, the swimmer bay's shelves and core, the open top with its recess."""
    cu, ti, bl = 0, 1, 2
    R1, R = P.CRYO_D / 2, P.CRYO_D / 2 - 0.003
    h0, h1 = S['head']
    zc = h1 - 0.06                                          # where the head's dome meets its cylinder
    tip = [(R1 * (1 - (1 - t) ** 1.7) ** (1 / 1.7), zc * t) for t in np.linspace(0, 1, 40)]
    B = [(cu, tip + [(R1, h1 - 0.012)]),
         (cu, [(R1, h1 - 0.012), (R, h1 - 0.004)])]
    B += _groove(ti, R, h1 - 0.004)
    b0, b1 = S['bay']
    s0, s1 = S['swim']
    B += [(ti, [(R, h1), (R, s0 - 0.006)])]
    B += _groove(ti, R, s0 - 0.006, w=0.004)
    B += [(ti, [(R, s0 - 0.002), (R, s0)]), (ti, [(R, s0), (0.008, s0)]),        # shelf under the wedges
          (ti, [(0.008, s0), (0.008, s1)]), (ti, [(0.008, s1), (R, s1)]),        # core, shelf over them
          (ti, [(R, s1), (R, s1 + 0.002)])]
    B += _groove(ti, R, s1 + 0.002)
    z = s1 + 0.006
    for name in ('vault', 'tail'):
        zs = S[name][0]
        B += [(bl if name == 'vault' else ti, [(R, z), (R, zs - 0.002)])]       # the wall below: heat, vault
        B += _groove(ti, R, zs - 0.002)
        z = zs + 0.002
    top = S['tail'][1]
    rin = P.CRYO_PUCK[0] / 2 + 0.004
    B += [(ti, [(R, z), (R, top - 0.008)]), (ti, [(R, top - 0.008), (R - 0.006, top)]),
          (ti, [(R - 0.006, top), (rin, top)]), (ti, [(rin, top), (rin, top - 0.10)]),
          (ti, [(rin, top - 0.10), (0.0, top - 0.10)])]
    V, F, M = _lathe(B)
    return _mesh('CryoHull', V, F, mats, M)


def details(P, S, mats):
    """Screws, jets, lamp port boss, camera dome, sample inlets: one mesh (materials: ti, black, cu, glass, window)."""
    TI, BLK, CU, GLASS, WIN = range(5)
    R1, R = P.CRYO_D / 2, P.CRYO_D / 2 - 0.003
    parts = []
    # screws: 12 per ring beside the seams
    sv, sf = _cyl(0.0035, -0.002, 0.0008, n=12)
    hv, hf = _cyl(0.0016, 0.0, 0.0010, n=6)                 # hex socket (dark)
    rings = [S['head'][1] + 0.016, S['swim'][0] - 0.020, S['swim'][1] + 0.020, S['vault'][0] - 0.016,
             S['vault'][0] + 0.020, S['tail'][0] - 0.016, S['tail'][0] + 0.020, S['tail'][1] - 0.025]
    for zi, z in enumerate(rings):
        for k in range(12):
            p, ax = _radial(15.0 * (zi % 2) + 30.0 * k, z, R)
            mx = _frame(p, ax)
            parts += [(sv, sf, TI, mx), (hv, hf, BLK, mx)]
    # jets on the melt head: a ring of 6 on the dome + one at the tip
    zc = S['head'][1] - 0.06
    njet = P.CRYO_JETS - 1
    t = 0.55
    p_ = 1.7
    r_of = lambda t: R1 * (1 - (1 - t) ** p_) ** (1 / p_)
    dr = (r_of(t + 1e-4) - r_of(t - 1e-4)) / 2e-4
    nrm = Vector((zc, -dr)).normalized()                    # outward normal in (r, z) from the tangent (dr, zc)
    bv, bf = _cyl(0.007, -0.004, 0.003, n=16)
    ov, of = _cyl(0.004, 0.0, 0.0032, n=16)
    for k in range(njet):
        a = math.radians(360.0 / njet * k + 30.0)
        radial = Vector((math.cos(a), math.sin(a), 0.0))
        p = radial * r_of(t) + Vector((0, 0, zc * t))
        ax = radial * nrm.x + Vector((0, 0, nrm.y))
        parts += [(bv, bf, CU, _frame(p, ax)), (ov, of, BLK, _frame(p, ax))]
    parts += [(bv, bf, CU, _frame((0, 0, 0.0005), (0, 0, -1))), (ov, of, BLK, _frame((0, 0, 0.0005), (0, 0, -1)))]
    # lamp port: a tilted boss through the hull wall, sapphire window, a bezel
    b0, b1 = S['bay']
    pz = b0 + PORT_Z_FRAC * (b1 - b0)
    p, ax = _radial(PORT_AZ, pz, R, PORT_TILT)
    mx = _frame(p, ax)
    v, f = _cyl(0.046, -0.04, 0.010, n=40)
    parts.append((v, f, TI, mx))
    v, f = _cyl(0.040, 0.0, 0.0108, n=40, cap=False)
    parts.append((v, f, BLK, mx))
    v, f = _cyl(0.035, 0.0, 0.0104, n=40)
    parts.append((v, f, WIN, mx))
    # camera dome
    p, ax = _radial(CAM_AZ, pz + 0.01, R, PORT_TILT)
    mx = _frame(p, ax)
    v, f = _cyl(0.028, -0.03, 0.006, n=32)
    parts.append((v, f, TI, mx))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.019)
    bmesh.ops.delete(bm, geom=[x for x in bm.verts if x.co.z < -1e-4], context='VERTS')
    dv = [tuple(x.co) for x in bm.verts]
    df = [tuple(x.index for x in face.verts) for face in bm.faces]
    bm.free()
    parts.append((dv, df, GLASS, mx @ Matrix.Translation((0, 0, 0.006))))
    # sample inlets: dark slots
    for a in INLET_AZ:
        p, ax = _radial(a, b0 + 0.11, R - 0.0025)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.006, 0.010, 0.06), verts=bm.verts)
        sv_ = [tuple(x.co) for x in bm.verts]
        sf_ = [tuple(x.index for x in face.verts) for face in bm.faces]
        bm.free()
        mx = Matrix.Translation(p) @ Matrix.Rotation(math.radians(a), 4, 'Z')
        parts.append((sv_, sf_, BLK, mx))
    V, F, M = _merge(parts)
    return _mesh('CryoDetails', V, F, mats, M, smooth=False)


def puck_mesh(P, mats):
    """Relay puck: anodised disc, rounded rim, a hole for the tether, a groove ring on its faces. Origin at its base."""
    ro, h = P.CRYO_PUCK[0] / 2, P.CRYO_PUCK[1]
    rh, e = P.CRYO_TETHER_D, 0.008
    arc = lambda c0, c1, a0, a1: [(c0 + e * math.cos(t), c1 + e * math.sin(t)) for t in np.linspace(a0, a1, 6)]
    B = [(0, [(rh, 0.0), (ro - e, 0.0)] + arc(ro - e, e, -math.pi / 2, 0)[1:] + arc(ro - e, h - e, 0, math.pi / 2)),
         (0, [(ro - e, h), (0.06, h)]), (0, [(0.06, h), (0.06, h - 0.002)]), (0, [(0.06, h - 0.002), (0.055, h - 0.002)]),
         (0, [(0.055, h - 0.002), (0.055, h)]), (0, [(0.055, h), (rh, h)]), (0, [(rh, h), (rh, 0.0)])]
    V, F, M = _lathe(B, nseg=64)
    return _mesh('CryoPuck', V, F, mats, M)


def swimmer_mesh(P, R, h, mats, nslice):
    """One radial wedge (a slice of the package), back at radius R, centred on +X, z 0..h. Gap 1.5 mm to its
    neighbours, edges bevelled by a modifier."""
    rin, gap = 0.02, 0.0015
    half = math.pi / nslice
    outer = [(R * math.cos(t), R * math.sin(t)) for t in np.linspace(-(half - gap / 2 / R), half - gap / 2 / R, 10)]
    inner = [(rin * math.cos(t), rin * math.sin(t)) for t in (half - gap / 2 / rin, -(half - gap / 2 / rin))]
    ring = outer + inner
    n = len(ring)
    V = [(x, y, 0.0) for x, y in ring] + [(x, y, h) for x, y in ring]
    F = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    me = _mesh('CryoSwimmer', V, F, mats, smooth=False)
    return me


def build(sc, P, loc=(0.0, 0.0, 0.0), tether=0.0, pucks_above=(), open=0.0, lamp=True, lamp_cone=90.0, seed=5):
    """The probe at `loc` (nose tip), upright. tether: metres of tether above the top; pucks_above: heights above the
    top where dropped pucks sit on it; open: metres each swimmer has drifted out (0 = stowed)."""
    S = _layout(P)
    R1, R = P.CRYO_D / 2, P.CRYO_D / 2 - 0.003
    top = S['tail'][1]
    root = bpy.data.objects.new('Cryobot', None)
    root.empty_display_size = 0.3
    sc.collection.objects.link(root)
    m_ti, m_cu = _mat('CryoTitanium', titanium), _mat('CryoCopper', copper)
    m_blk = _mat('CryoBlack', plain((0.008, 0.008, 0.009), 0.5))
    m_glass = _mat('CryoGlass', plain((0.01, 0.01, 0.012), 0.03))
    area = math.pi * 0.035 ** 2
    m_win = _mat('CryoWindow', window(P.CRYO_LAMP_W / area if lamp else 0.0))
    m_puck = _mat('CryoPuck', plain((0.035, 0.037, 0.040), 0.35, coat=0.3))
    m_teth = _mat('CryoTether', plain((0.78, 0.52, 0.10), 0.65))

    def link(me, name=None):
        ob = bpy.data.objects.new(name or me.name, me)
        sc.collection.objects.link(ob)
        ob.parent = root
        return ob

    parts = [link(hull(P, S, [m_cu, m_ti, _mat('CryoBlasted', blasted)])),
             link(details(P, S, [m_ti, m_blk, m_cu, m_glass, m_win]))]

    # swimmers: 2 tiers × 25, the upper tier turned half a slice
    s0, s1 = S['swim']
    nsl = P.SWIM_N // P.SWIM_TIERS
    th = (s1 - s0 - 0.002 * (P.SWIM_TIERS + 1)) / P.SWIM_TIERS
    m_sw = _mat('CryoSwimmer', swimmer_paint(R - 0.0005))
    sm = swimmer_mesh(P, R - 0.0005, th, [m_sw], nsl)
    rng = np.random.default_rng(seed)
    swimmers = []
    for tier in range(P.SWIM_TIERS):
        for j in range(nsl):
            ob = link(sm, f'Swimmer.{tier}.{j:02d}')
            bev = ob.modifiers.new('Bevel', 'BEVEL')
            bev.width, bev.segments, bev.limit_method = 0.0012, 2, 'ANGLE'
            a = 2 * math.pi * (j + 0.5 * tier) / nsl
            ob.location = (0.0, 0.0, s0 + 0.002 + tier * (th + 0.002))
            ob.rotation_euler = (0.0, 0.0, a)
            ob['rest'] = [x for row in ob.matrix_basis for x in row]          # row-major 4×4
            if open > 0:
                d = open * (0.7 + 0.6 * rng.random())
                ob.location = Vector(ob.location) + Vector((math.cos(a) * d, math.sin(a) * d,
                                                            open * 0.4 * (rng.random() - 0.5)))
                ob.rotation_euler = (rng.normal(0, 0.5) * min(open * 4, 1), rng.normal(0, 0.5) * min(open * 4, 1),
                                     a + rng.normal(0, 0.6) * min(open * 4, 1))
            swimmers.append(ob)

    # pucks: the top one in the open top, dropped ones on the tether
    pm = puck_mesh(P, [m_puck])
    pucks = []
    for i, zz in enumerate([top - 0.015 - P.CRYO_PUCK[1]] + [top + d for d in pucks_above]):
        ob = link(pm, f'Puck.{i}')
        ob.location = (0.0, 0.0, zz)
        pucks.append(ob)

    teth = None
    if tether > 0:
        v, f = _cyl(P.CRYO_TETHER_D / 2, top - 0.03, top + tether, n=12, cap=False)
        teth = link(_mesh('CryoTether', v, f, [m_teth]))

    L = None
    if lamp:
        b0, b1 = S['bay']
        pz = b0 + PORT_Z_FRAC * (b1 - b0)
        p, ax = _radial(PORT_AZ, pz, R, PORT_TILT)
        ld = bpy.data.lights.new('CryoLamp', 'SPOT')
        ld.energy = P.CRYO_LAMP_W
        ld.spot_size = math.radians(lamp_cone)
        ld.spot_blend = 0.4
        ld.shadow_soft_size = 0.035
        L = bpy.data.objects.new('CryoLamp', ld)
        sc.collection.objects.link(L)
        L.parent = root
        L.location = p + ax * 0.012
        L.rotation_euler = ax.to_track_quat('-Z', 'Y').to_euler()

    root.location = loc
    return dict(root=root, parts=parts, swimmers=swimmers, pucks=pucks, tether=teth, lamp=L, sections=S,
                top=top, port_z=S['bay'][0] + PORT_Z_FRAC * (S['bay'][1] - S['bay'][0]))


# ---------------------------------------------------------------- 03: the deployment tripod (Sprint 3.3)
def tripod(sc, P, nose, ground, reel_az=0.0, feet_az=90.0, top=None):
    """Borehole tripod over the probe hanging nose-down on the ice at `nose` (world xyz of the nose tip): three legs to
    a head P.TRIPOD_H above the ice, a sheave, the tether from the probe's top over it to a reel box P.REEL[3] m away
    at `reel_az` (deg, world: 0 = +Y, + toward +X). ground(x, y) → z arrays. Returns the objects."""
    top = top if top is not None else _layout(P)['tail'][1]
    nx, ny, nz = nose
    H = Vector((nx, ny, nz + P.TRIPOD_H))
    m_al = _mat('TripodAlu', plain((0.56, 0.57, 0.59), 0.35, metal=1.0))
    m_blk = _mat('CryoBlack', plain((0.008, 0.008, 0.009), 0.5))
    m_box = _mat('ReelPaint', plain((0.62, 0.62, 0.60), 0.55))
    m_teth = _mat('CryoTether', plain((0.78, 0.52, 0.10), 0.65))
    parts = []
    for k in range(3):
        a = math.radians(feet_az + 120.0 * k)
        fx, fy = nx + P.TRIPOD_FOOT_R * math.sin(a), ny + P.TRIPOD_FOOT_R * math.cos(a)
        foot = Vector((fx, fy, float(ground(np.array([fx]), np.array([fy]))[0])))
        leg = H - foot
        v, f = _cyl(P.TRIPOD_LEG_D / 2, 0.0, leg.length - 0.06, n=16)
        parts.append((v, f, 0, _frame(foot, leg)))
        v, f = _cyl(0.11, -0.01, 0.025, n=20)
        parts.append((v, f, 1, Matrix.Translation(foot)))
    v, f = _cyl(0.09, -0.06, 0.06, n=24)
    parts.append((v, f, 1, Matrix.Translation(H)))
    # sheave hangs just below the head, its rim over the probe's axis on one side and toward the reel on the other
    ra = math.radians(reel_az)
    d = Vector((math.sin(ra), math.cos(ra), 0.0))
    rs = P.TRIPOD_SHEAVE
    C = Vector((nx, ny, H.z - 0.08 - rs)) + d * rs
    v, f = _cyl(rs, -0.015, 0.015, n=32)
    parts.append((v, f, 1, _frame(C, d.cross(Vector((0, 0, 1))))))
    V, F, M = _merge(parts)
    rig = bpy.data.objects.new('Tripod', _mesh('Tripod', V, F, [m_al, m_blk], M))
    sc.collection.objects.link(rig)
    # reel box on the ice, the tether over the sheave to its drum
    R = Vector((nx, ny, 0.0)) + d * P.REEL[3]
    R.z = float(ground(np.array([R.x]), np.array([R.y]))[0])
    l, w, h = P.REEL[:3]
    bv = [(sx * l / 2, sy * w / 2, sz * h) for sz in (0, 1) for sy in (-1, 1) for sx in (-1, 1)]
    bf = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    box = bpy.data.objects.new('Reel', _mesh('Reel', bv, bf, [m_box], smooth=False))
    sc.collection.objects.link(box)
    box.matrix_world = Matrix.Translation(R) @ Matrix.Rotation(-ra, 4, 'Z')
    pts = [Vector((nx, ny, nz + top - 0.03)), Vector((nx, ny, C.z))]
    for i in range(1, 12):                                       # over the top of the sheave
        t = math.pi * i / 12
        pts.append(C - d * rs * math.cos(t) + Vector((0, 0, rs * math.sin(t))))
    pts += [C + d * rs, R + Vector((0, 0, h + 0.04))]
    tp = []
    for p0, p1 in zip(pts[:-1], pts[1:]):
        v, f = _cyl(P.CRYO_TETHER_D / 2, 0.0, (p1 - p0).length, n=10, cap=False)
        tp.append((v, f, 0, _frame(p0, p1 - p0)))
    V, F, M = _merge(tp)
    teth = bpy.data.objects.new('TripodTether', _mesh('TripodTether', V, F, [m_teth], M))
    sc.collection.objects.link(teth)
    return [rig, box, teth]
