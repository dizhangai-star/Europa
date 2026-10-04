"""Europa's ground: a camera-centred polar terrain patch on the curved surface, the Conamara chaos height field
(`Ground`), the ice material, proxies.

Copied from ../Io/blender/lib/io_world.py (Sprint 0.3); the ground and the ice are Europa's since Sprint 2.1 (the
Sprint 1 spike `lib/chaos.py` promoted and extended: ridged plains on the plates, double ridges, a jumble of blocks
in the matrix, far plates, masks for the material, the PIA01403 pattern).

Conventions (tools/physics.py "Blender local frame"): 1 BU = 1 m, X = right as you face Jupiter (≈ north at
Conamara), Y = toward Jupiter (≈ west), Z = up; the ground under the camera's foot is z = 0. Europa's curvature is
real: a point r metres away sits r²/2R lower (R = 1560.8 km).

The patch is one polar grid around the camera (rings dense where the shot needs silhouette detail, a `band`),
cut to the shot's azimuth sector, heights from `Ground` (or any height function). Detail below the mesh spacing is
in the material (bump).
"""
import math
import os

import bpy
import numpy as np
import physics as P
from . import nodes

R_EU_M = P.R_EU * 1000.0


# ---------------------------------------------------------------- numpy value-noise fbm (deterministic)
def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h & 0xFFFF) / 65535.0


def vnoise(x, y, seed=0):
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - ix, y - iy
    ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _hash(ix, iy, seed), _hash(ix + 1, iy, seed)
    c, d = _hash(ix, iy + 1, seed), _hash(ix + 1, iy + 1, seed)
    return (a + (b - a) * ux) * (1 - uy) + (c + (d - c) * ux) * uy


def fbm(x, y, oct=5, seed=0, gain=0.5):
    """0..1, mean ~0.5."""
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(oct):
        s = s + amp * vnoise(x, y, seed + o * 17)
        tot += amp
        x, y, amp = x * 2.03 + 3.1, y * 2.03 - 1.7, amp * gain
    return s / tot


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- terrain
def rings(r0, r1, step_frac=0.004, bands=()):
    """Ring radii: geometric (spacing = step_frac × r) from r0 to r1, plus dense bands (a, b, spacing m)."""
    r = list(np.geomspace(r0, r1, int(math.log(r1 / r0) / step_frac)))
    for a, b, s in bands:
        r += list(np.arange(a, b, s))
    return np.unique(np.array(r))


def terrain(sc, name, rr, az_c, az_half, nseg, height, mat=None, max_verts=1_000_000):
    """Polar grid: radii rr (m) × nseg azimuths in az_c ± az_half (deg, 0 = Jupiter, + = right), z = height(X, Y)
    minus the curvature drop. A `Ground` also writes its masks as float point attributes. Split into ring bands of
    ≤ `max_verts` (sharing their edge ring): one 7.6 M-vertex mesh lost triangles under MetalRT (holes showing the sky,
    Sprint 2.1; CPU and MetalRT off were clean). Returns the first object (the rest are 'name.1', …)."""
    a = np.radians(az_c + np.linspace(-az_half, az_half, nseg))
    RR, AA = np.meshgrid(rr, a, indexing='ij')
    X, Y = RR * np.sin(AA), RR * np.cos(AA)
    masks = {} if isinstance(height, Ground) else None
    Z = (height(X, Y, masks) if masks is not None else height(X, Y)) - RR ** 2 / (2 * R_EU_M)
    nr, na = RR.shape
    step = max(2, max_verts // na)
    obs = []
    for i0 in range(0, nr - 1, step - 1):
        i1 = min(i0 + step, nr)
        sl = slice(i0, i1)
        verts = np.stack([X[sl], Y[sl], Z[sl]], -1).reshape(-1, 3)
        ii = np.arange(i1 - i0 - 1)[:, None] * na + np.arange(na - 1)[None, :]
        faces = np.stack([ii, ii + 1, ii + na + 1, ii + na], -1).reshape(-1, 4)
        nm = name if not obs else f'{name}.{len(obs)}'
        me = bpy.data.meshes.new(nm)
        me.vertices.add(len(verts))
        me.vertices.foreach_set('co', verts.ravel().astype(np.float32))
        me.loops.add(faces.size)
        me.loops.foreach_set('vertex_index', faces.ravel().astype(np.int32))
        me.polygons.add(len(faces))
        me.polygons.foreach_set('loop_start', np.arange(0, faces.size, 4, dtype=np.int32))
        me.update()
        me.shade_smooth()
        for k, v in (masks or {}).items():
            me.attributes.new(k, 'FLOAT', 'POINT').data.foreach_set('value', v[sl].ravel().astype(np.float32))
        ob = bpy.data.objects.new(nm, me)
        sc.collection.objects.link(ob)
        if mat:
            me.materials.append(mat)
        obs.append(ob)
    print(f'NOTE terrain {name}: {nr * na:,} verts in {len(obs)} objects')
    return obs[0]


def europa_body(sc, below=25.0, r1=100_000.0):
    """Europa itself as a shadow-only occluder: a full 360° curved skirt (z = −r²/2R − `below`) out to r1, so a Sun below
    the horizon, or behind the camera outside the terrain's sector, is blocked by the moon, not by nothing.
    r1 stays ~100 km: the scaled-down Jupiter (1000 km out) must not fall in its shadow."""
    rr = np.geomspace(20.0, r1, 160)
    a = np.linspace(0, 2 * math.pi, 129)[:-1]
    RR, AA = np.meshgrid(rr, a, indexing='ij')
    X, Y = RR * np.sin(AA), RR * np.cos(AA)
    Z = -RR ** 2 / (2 * R_EU_M) - below
    verts = np.concatenate([[[0.0, 0.0, -below]], np.stack([X, Y, Z], -1).reshape(-1, 3)])
    na = len(a)
    faces = [(0, 1 + (j + 1) % na, 1 + j) for j in range(na)]
    for i in range(len(rr) - 1):
        for j in range(na):
            k0, k1 = 1 + i * na + j, 1 + i * na + (j + 1) % na
            faces.append((k0, k1, k1 + na, k0 + na))
    me = bpy.data.meshes.new('EuropaBody')
    me.from_pydata(verts.tolist(), [], faces)
    ob = bpy.data.objects.new('EuropaBody', me)
    sc.collection.objects.link(ob)
    for k in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'):
        setattr(ob, k, False)
    return ob


def ground_z(height, x, y):
    """Terrain height at one point (with curvature), for placing things on it."""
    X, Y = np.array([float(x)]), np.array([float(y)])
    return float(height(X, Y)[0] - (x * x + y * y) / (2 * R_EU_M))


# ---------------------------------------------------------------- Conamara chaos ground (Sprint 2.1)
# Promoted from the Sprint 1 spike (lib/chaos.py): the plate layout draws the same random numbers, so 01's framing
# (Sprint 2.0) still holds. New: the ridged plains on the plate tops are one field turned and shifted with each plate
# (ridge sets + double-ridge fragments, physics.CHAOS), the matrix carries a jumble of blocks in three size bands
# (the ragged horizon, house-size rubble, boulders at the feet), talus aprons are rubble, far plates out to 18 km.
def plates(C, seed=7, n=26, rmin=120.0, rmax=6000.0, lane_deg=9.0, lane_r=7000.0, extra=()):
    """Random plate layout (Sprint 1's draw order). `extra`: hand-placed plates, dicts with c=(x, y), R, h and optional
    keys (n sides, rot, tilt_deg, tdir_deg, plains = the ridged plains' height on its top, default 0.3: a placed
    plate keeps the skyline it was placed for)."""
    rng = np.random.default_rng(int(seed))
    out = []
    for e in extra:
        out.append(_plate(C, e['c'], e['R'], e.get('h', C['plate_h'][1]), e))
    for _ in range(400):
        if len(out) >= n + len(extra):
            break
        R = math.exp(rng.uniform(math.log(C['plate_m'][0] / 2), math.log(C['plate_m'][1] / 2)))
        dist = rng.uniform(R + rmin, rmax)
        az = rng.uniform(-180.0, 180.0)
        half = math.degrees(math.atan2(1.3 * R, dist))
        if abs(az) - half < lane_deg and dist < lane_r:
            continue
        cx, cy = dist * math.sin(math.radians(az)), dist * math.cos(math.radians(az))
        if any(math.hypot(cx - p['c'][0], cy - p['c'][1]) < 1.1 * (R + p['R']) for p in out):
            continue
        n_ = int(rng.integers(5, 10))
        phi = rng.uniform(0, 2 * math.pi) + np.arange(n_) * 2 * math.pi / n_ + rng.uniform(-0.3, 0.3, n_)
        t = rng.uniform(0, 2 * math.pi)
        out.append(dict(c=(cx, cy), R=R, h=rng.uniform(*C['plate_h']), nrm=np.stack([np.cos(phi), np.sin(phi)], 1),
                        p=R * rng.uniform(0.75, 1.1, n_), tilt=math.tan(math.radians(rng.uniform(*C['tilt_deg']))),
                        tdir=(math.cos(t), math.sin(t))))
        rng.uniform(-25, 25), rng.uniform(*C['ridge_gap'])        # Sprint 1's ridge draws, kept for the layout
    return out


def _plate(C, c, R, h, e):
    n_ = int(e.get('n', 6))
    phi = math.radians(e.get('rot', 0.0)) + np.arange(n_) * 2 * math.pi / n_
    t = math.radians(e.get('tdir_deg', 0.0))
    return dict(c=tuple(c), R=R, h=h, nrm=np.stack([np.cos(phi), np.sin(phi)], 1), p=np.full(n_, R),
                tilt=math.tan(math.radians(e.get('tilt_deg', 1.0))), tdir=(math.cos(t), math.sin(t)),
                plains=e.get('plains', 0.3))


def blocks(X, Y, cell, size, hgt, frac, seed, sides=7):
    """A jumble of blocks: a grid of `cell` m (turned and warped per call so it doesn't show), each cell holding one
    block with probability `frac`: an irregular convex polygon (up to `sides` faces), `size` m across, some stretched
    into shards, `hgt` m tall (taller when bigger), each face its own slope (sheer to rounded), a ragged outline, a
    lumpy tilted top (some strongly tilted rafts). A block stays inside its own cell, so only that cell is evaluated.
    Returns (height, top mask)."""
    assert 0.6 * size[1] + 0.1 * cell <= 0.5 * cell
    a = 2 * math.pi * _hash(seed, 1, 99)
    wx = X + 0.3 * cell * (fbm(X / (3 * cell), Y / (3 * cell), 3, seed + 1) - 0.5)
    wy = Y + 0.3 * cell * (fbm(X / (3 * cell), Y / (3 * cell), 3, seed + 2) - 0.5)
    U, V = wx * math.cos(a) + wy * math.sin(a), -wx * math.sin(a) + wy * math.cos(a)
    ix, iy = np.floor(U / cell).astype(np.int64), np.floor(V / cell).astype(np.int64)
    Z, top = np.zeros_like(X), np.zeros_like(X)
    ii = np.nonzero(_hash(ix, iy, seed) < frac)[0]
    if not len(ii):
        return Z, top
    jx, jy = ix[ii], iy[ii]

    def hh(k):
        return _hash(jx, jy, seed + k)
    x = U[ii] - (jx + 0.4 + 0.2 * hh(1)) * cell
    y = V[ii] - (jy + 0.4 + 0.2 * hh(2)) * cell
    t = hh(3)
    R = 0.5 * (size[0] + (size[1] - size[0]) * t)
    h = hgt[0] + (hgt[1] - hgt[0]) * (0.6 * t + 0.4 * hh(4))
    rot, el = 2 * math.pi * hh(5), 1.0 + 1.2 * np.maximum(hh(8) - 0.6, 0.0) / 0.4       # 40 %: shards up to 2.2:1
    xr, yr = x * np.cos(rot) + y * np.sin(rot), (-x * np.sin(rot) + y * np.cos(rot)) * el
    rag = 0.08 * R * (fbm(X[ii] / (0.4 * size[1]), Y[ii] / (0.4 * size[1]), 3, seed + 3) - 0.5)       # ragged
    b = 2 * math.pi * hh(6)
    lean = 0.3 * (hh(7) - 0.5) + np.where(hh(40) < 0.15, 0.5 * (hh(41) - 0.5), 0.0)     # 15 %: tilted rafts
    lump = 0.35 * h * (fbm(X[ii] / (0.5 * size[1]), Y[ii] / (0.5 * size[1]), 3, seed + 4) - 0.5)
    d = np.full_like(x, 1e9)
    for k in range(sides):                       # each face its own slope: sheer (~80°) … a talus-like ~30°
        ak = k * 2 * math.pi / sides + 0.6 * (hh(10 + k) - 0.5)
        dk = R * (0.7 + 0.4 * hh(20 + k)) - (xr * np.cos(ak) + yr * np.sin(ak)) + rag
        d = np.minimum(d, dk / (h * (0.15 + 1.6 * hh(30 + k) ** 2)))
    Z[ii] = np.maximum(h + lump + lean * (x * np.cos(b) + y * np.sin(b)), 0.0) * smooth(0.0, 1.0, d)
    top[ii] = smooth(1.0, 1.6, d)
    return Z, top


class Ground:
    """Conamara chaos: height field (m, without Europa's curvature: terrain() subtracts it) and per-vertex masks.
    `g(X, Y)` → Z; `g(X, Y, out)` also fills out[...] (0..1, written as mesh attributes for `ice()`): 'plate' (plate
    top), 'ridge' (ridge crests on it), 'margin' (a double ridge's flanks), 'block' (block tops), 'talus' (aprons).
    Local frame (physics.py): +Y toward Jupiter, +X right, Z up; azimuth 0 = Jupiter, + = right. A lane toward
    Jupiter (|az| < `lane_deg`) has no plates and lower swells/blocks (`lane_debris`), so the disc keeps ¾ above the
    ice (matrix and rubble in the lane stay under a skyline cap seen from an `eye` m above the knoll, its elevation
    `lane_cap_deg` from the near value to the far one at ~3 km, so the far rubble makes the skyline: ≤ 21 % of the
    disc hidden at +0.6°, 16 % at the bare horizon);
    plates placed there by hand, as 01's limb-biting mesa, are not capped); the camera stands on a low `knoll` at the
    origin, in a clearing (`clear`: per debris band, the radius inside
    which its blocks fade out, so the view isn't walled in). Debris band i reaches out to 90 × its cell size; within a band
    the blocks of its three grids merge (max), the bands stack (sum: rubble on blocks)."""
    MASKS = ('plate', 'ridge', 'margin', 'block', 'talus')

    def __init__(self, C, seed=7, extra=(), knoll=6.0, lane_deg=9.0, lane_debris=1.0, far=(6000.0, 18000.0, 30),
                 clear=(400.0, 30.0, 0.0), lane_cap_deg=(-0.3, 0.6), eye=1.6, **kw):
        self.C, self.seed, self.knoll, self.lane_deg, self.lane_debris = C, int(seed), knoll, lane_deg, lane_debris
        self.clear, self.cap = clear, None
        self.plates = plates(C, seed, lane_deg=lane_deg, extra=extra, **kw)
        if far:                                                   # far plates (own draws): the skyline beyond 6 km
            rng = np.random.default_rng(self.seed + 1000)
            r0, r1, nf = far
            for _ in range(600):
                if nf <= 0:
                    break
                R = math.exp(rng.uniform(math.log(C['plate_m'][0]), math.log(C['plate_m'][1] / 2)))
                dist, az = rng.uniform(r0 + R, r1), rng.uniform(-180.0, 180.0)
                if abs(az) - math.degrees(math.atan2(1.3 * R, dist)) < lane_deg:
                    continue
                c = (dist * math.sin(math.radians(az)), dist * math.cos(math.radians(az)))
                if any(math.hypot(c[0] - p['c'][0], c[1] - p['c'][1]) < 1.1 * (R + p['R']) for p in self.plates):
                    continue
                n_ = int(rng.integers(5, 10))
                phi = rng.uniform(0, 2 * math.pi) + np.arange(n_) * 2 * math.pi / n_ + rng.uniform(-0.3, 0.3, n_)
                t = rng.uniform(0, 2 * math.pi)
                self.plates.append(dict(c=c, R=R, h=rng.uniform(*C['plate_h']),
                                        nrm=np.stack([np.cos(phi), np.sin(phi)], 1), p=R * rng.uniform(0.75, 1.1, n_),
                                        tilt=math.tan(math.radians(rng.uniform(*C['tilt_deg']))),
                                        tdir=(math.cos(t), math.sin(t))))
                nf -= 1
        rng = np.random.default_rng(self.seed + 2000)            # each plate's turn and drift since it broke off
        for p in self.plates:
            p['spin'] = math.radians(rng.uniform(-1, 1) * C['plate_spin_deg'])
            p['shift'] = tuple(rng.uniform(-1, 1, 2) * 0.5 * p['R'])
        if lane_cap_deg is not None:                             # the eye on the knoll sets the lane's skyline cap
            self.cap = (float(self._eval(np.zeros(1), np.zeros(1))[0][0]) + eye,
                        tuple(math.tan(math.radians(c)) for c in lane_cap_deg))

    def __call__(self, X, Y, out=None):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        shp, X, Y = X.shape, X.ravel(), Y.ravel()
        Z = np.empty_like(X)
        res = {k: np.empty_like(X) for k in self.MASKS} if out is not None else None
        for s in range(0, len(X), 400_000):
            sl = slice(s, s + 400_000)
            z, m = self._eval(X[sl], Y[sl])
            Z[sl] = z
            if res is not None:
                for k in self.MASKS:
                    res[k][sl] = m[k]
        if out is not None:
            out.update({k: v.reshape(shp) for k, v in res.items()})
        return Z.reshape(shp)

    def plains(self, gx, gy):
        """The ridged plains before the chaos broke them, at pre-chaos coords (m). Returns (height, crest, margin)."""
        C = self.C
        H, crest, margin = np.zeros_like(gx), np.zeros_like(gx), np.zeros_like(gx)
        g = 0.5 * (C['ridge_gap'][0] + C['ridge_gap'][1])
        for j, az in enumerate(C['ridge_sets']):                 # sets of ridges, fading in and out along their length
            a = math.radians(az)
            u, v = gx * math.cos(a) + gy * math.sin(a), -gx * math.sin(a) + gy * math.cos(a)
            k = np.floor(u / g).astype(np.int64)
            d = u - (k + 0.5 + 0.3 * (_hash(k, j, 71) - 0.5)) * g
            amp = (0.3 + 0.7 * _hash(k, j, 72)) * smooth(0.35, 0.6, fbm(v / 1200 + k * 7.3, k * 1.1, 3, 73 + j))
            prof = amp * np.exp(-(d / (0.1 * g)) ** 2)
            H += C['ridge_h'] * prof
            crest = np.maximum(crest, prof)
        for j, az in enumerate(C['double_az']):                  # double ridges: two crests and a trough
            a, G = math.radians(az), C['double_gap']
            u = gx * math.cos(a) + gy * math.sin(a)
            k = np.floor(u / G).astype(np.int64)
            on = _hash(k, j, 81) < 0.6
            d = u - (k + 0.5 + 0.5 * (_hash(k, j, 82) - 0.5)) * G
            w = C['double_w'][0] + (C['double_w'][1] - C['double_w'][0]) * _hash(k, j, 83)
            h = C['double_h'][0] + (C['double_h'][1] - C['double_h'][0]) * _hash(k, j, 84)
            two = np.exp(-((np.abs(d) - 0.5 * w) / (0.22 * w)) ** 2)
            H += np.where(on, h * two, 0.0)
            crest = np.maximum(crest, np.where(on, two, 0.0))
            margin = np.maximum(margin, np.where(on, np.exp(-(np.abs(d) / w) ** 2) * (1 - two), 0.0))
        return H, crest, margin

    def _eval(self, X, Y):
        C = self.C
        r, az = np.hypot(X, Y), np.degrees(np.arctan2(X, Y))
        inlane = smooth(25.0, 8.0, np.abs(az)) * smooth(60.0, 250.0, r)
        Z = (1.0 - 0.6 * inlane) * C['matrix_h'] * (fbm(X / 260, Y / 260, 5, 11) - 0.45)
        Z += self.knoll * np.exp(-(r / 120.0) ** 2)                # the camera stands on a low knoll
        for s_, a_ in ((90.0, 0.35), (25.0, 0.12)):                  # hummocks: billowy lumps under the blocks
            u, v = X * 0.8 + Y * 0.6, -X * 0.6 + Y * 0.8
            Z += (1.0 - 0.6 * inlane) * a_ * C['matrix_h'] * (1 - np.abs(2 * fbm(u / s_, v / s_, 4, 13) - 1))
        P_, A_, top_m, crest, margin, talus = (np.full_like(X, -1e9),) + tuple(np.zeros_like(X) for _ in range(5))
        for k, p in enumerate(self.plates):
            cx, cy = p['c']
            reach = 1.25 * p['R'] + 2.0 * p['h']
            m = np.nonzero((np.abs(X - cx) < reach) & (np.abs(Y - cy) < reach))[0]
            if not len(m):
                continue
            x, y = X[m] - cx, Y[m] - cy
            d = np.min(p['p'][None, :] - (x[:, None] * p['nrm'][None, :, 0] + y[:, None] * p['nrm'][None, :, 1]), 1)
            d = d + 0.06 * p['R'] * (fbm(X[m] / 70, Y[m] / 70, 4, 20 + k) - 0.5)          # ragged cliff line
            h, w = p['h'], 0.3 * p['h']
            cs, sn = math.cos(p['spin']), math.sin(p['spin'])
            ph, pc, pm = self.plains(cx + p['shift'][0] + cs * x - sn * y, cy + p['shift'][1] + sn * x + cs * y)
            top = h + p['tilt'] * (x * p['tdir'][0] + y * p['tdir'][1]) + p.get('plains', 1.0) * ph \
                + 4.0 * (fbm(X[m] / 90, Y[m] / 90, 4, 40 + k) - 0.5)
            cliff = smooth(0.0, w, d)
            ap = smooth(-1.6 * h, 0.0, d) ** 2 * (1 - cliff)          # apron: a rubble slope on the matrix
            v = top * cliff
            win = v > P_[m]
            P_[m] = np.where(win, v, P_[m])
            top_m[m] = np.where(win, cliff, top_m[m])
            crest[m] = np.where(win, pc * cliff, crest[m])
            margin[m] = np.where(win, pm * cliff, margin[m])
            talus[m] = np.maximum(talus[m], ap)
            A_[m] = np.maximum(A_[m], 0.3 * h * ap)
        D, blk = np.zeros_like(X), np.zeros_like(X)
        dl = 1.0 - (1.0 - self.lane_debris) * inlane
        for i, (cell, size, hgt, frac) in enumerate(C['debris']):
            sel = np.nonzero(r < 90.0 * cell)[0]
            if not len(sel):
                continue
            boost = 1.0 + 1.5 * talus[sel] if cell < 100 else 1.0     # aprons are rubble
            Db = np.zeros(len(sel))
            for k in range(3):                                         # three overlapping grids: a jumble
                z, t = blocks(X[sel], Y[sel], cell, size, hgt, frac, self.seed * 31 + 60 + 7 * i + 1000 * k)
                Db = np.maximum(Db, z)
                blk[sel] = np.maximum(blk[sel], t)
            D[sel] += Db * dl[sel] * boost * smooth(0.6 * self.clear[i], self.clear[i] + 1e-6, r[sel])
        Zm = Z + A_ + D * (1 - top_m)                              # the matrix with its rubble
        if self.cap:                                               # the lane's skyline ≤ cap above the eye's horizon
            z_eye, (t0, t1) = self.cap
            t = t0 + (t1 - t0) * smooth(300.0, 3000.0, r)        # low near, higher far: far rubble makes the skyline
            excess = np.maximum(Zm - (z_eye + r * t + r ** 2 / (2 * R_EU_M)), 0.0)
            Zm = Zm - 0.9 * smooth(25.0, 8.0, np.abs(az)) * excess          # from the camera's feet out
        Z = np.maximum(Zm, P_)
        return Z, dict(plate=top_m, ridge=crest, margin=margin, block=blk * (1 - top_m), talus=talus)


# ---------------------------------------------------------------- ice
# Natural tints (linear, albedo-free) from PIA19048 (`python3 tools/maps.py colour`, PROGRESS 0.4) and Conamara's
# normalised reflectance 0.66 (p5 0.52, p95 0.88) from the 500 m mosaic. Where the colours sit (enhanced colour,
# PIA01127/26446): reddish-brown non-ice on the chaos matrix and along ridges, the plates' old plains whiter/bluer.
TINT = dict(clean=(0.872, 0.973, 1.0), blue=(0.577, 0.791, 1.0), cream=(1.0, 0.922, 0.826),
            brown=(1.0, 0.716, 0.539), dark=(1.0, 0.509, 0.324))
ALB = dict(mean=0.66, lo=0.52, hi=0.88, dark=0.77)
# Galileo's Conamara mosaic (PIA01403, ~15 m/px, public domain): its grey pattern lays out the matrix's colour patches
# (a mask only: the Sun's shading is baked in). Missing file → a noise stands in.
CONAMARA = os.path.expanduser('~/dev/workspace/claude/videos/_assets/textures/europa/galileo/PIA01403.png')
CONAMARA_M_PX = 15.0


def ice(name='Ice', scale=1.0, cliff_clean=True):
    """Europa's ice. Reads the Ground masks (mesh attributes; absent → all matrix). Matrix: brown ↔ cream patches at
    albedo lo..mean, laid out by a km noise and the PIA01403 pattern, darkest brown in streaks; plate tops: the old
    plains, cream ↔ clean blue-white at mean..hi, bright ridge crests, dark brown double-ridge margins; talus and
    block tops a little fresher; steep faces: clean blue-white ice at the high albedo (fresh exposure, as the bright
    block edges in PIA01403), streaked and banded. Frost glint: a little specular, rough. Bump: 30 m swell, 1 m knobs,
    3 cm grain."""
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    pos = g.o(tc, 'Object')

    def noise(size, detail=4, rough=0.55, dist=0.0):
        n = g.add('ShaderNodeTexNoise', Scale=1.0 / (size * scale), Detail=detail, Roughness=rough, Distortion=dist)
        g.set(n, 'Vector', pos)
        return g.o(n, 'Fac')

    def attr(n):
        return g.o(g.add('ShaderNodeAttribute', attribute_name=n), 'Fac')

    def c(t, a):
        return tuple(a * x for x in TINT[t])
    big, mid = noise(1500, 3, 0.5, 0.3), noise(120, 5, 0.6)
    if os.path.exists(CONAMARA):
        img = bpy.data.images.load(CONAMARA, check_existing=True)
        img.colorspace_settings.name = 'Non-Color'
        w, h = img.size
        mp = g.add('ShaderNodeMapping')
        g.set(mp, 'Vector', pos)
        mp.inputs['Rotation'].default_value = (0.0, 0.0, math.radians(17.0))
        mp.inputs['Scale'].default_value = (1 / (w * CONAMARA_M_PX * scale), 1 / (h * CONAMARA_M_PX * scale), 1.0)
        tex = g.add('ShaderNodeTexImage', extension='MIRROR', interpolation='Cubic')
        tex.image = img
        g.set(tex, 'Vector', g.o(mp, 0))
        pat = g.maprange(g.o(tex, 'Color'), 0.25, 0.80)
    else:
        pat = noise(60, 6, 0.65)
    # the matrix
    field = g.math('ADD', g.math('MULTIPLY', big, 0.5), g.math('MULTIPLY', pat, 0.5))
    col = g.ramp(field, [(0.32, c('dark', ALB['lo'] * ALB['dark'])), (0.45, c('brown', ALB['lo'])),
                         (0.58, c('brown', ALB['mean'])), (0.72, c('cream', ALB['mean']))])
    col = g.mix(g.maprange(noise(60, 6, 0.65, 0.6), 0.64, 0.70), col, c('dark', ALB['lo'] * ALB['dark']))
    col = g.mix(g.math('MULTIPLY', attr('block'), 0.5), col, c('cream', ALB['mean']))        # block tops
    col = g.mix(g.math('MULTIPLY', attr('talus'), g.maprange(mid, 0.3, 0.7, 0.2, 0.7)), col,
                c('clean', ALB['mean']))                                                     # fresh aprons
    # the plate tops: older ridged plains
    pf = g.math('ADD', g.math('MULTIPLY', big, 0.6), g.math('MULTIPLY', mid, 0.4))
    plains = g.ramp(pf, [(0.38, c('cream', ALB['mean'])), (0.52, c('clean', ALB['mean'])),
                         (0.66, c('blue', ALB['hi']))])
    plains = g.mix(g.math('MULTIPLY', attr('ridge'), 0.8), plains, c('clean', ALB['hi']))     # crests
    plains = g.mix(g.math('MULTIPLY', attr('margin'), 0.8), plains, c('brown', ALB['lo']))    # dark flanks
    col = g.mix(attr('plate'), col, plains)
    geo = g.add('ShaderNodeNewGeometry')
    _, _, nz = g.xyz(g.o(geo, 'Normal'))
    steep = g.maprange(nz, 0.85, 0.55)
    # cliff faces: vertical gullies and fall streaks (noise stretched 8:1 up the face), a few bands of older ice
    vm = g.add('ShaderNodeMapping')
    g.set(vm, 'Vector', pos)
    vm.inputs['Scale'].default_value = (1 / (5.0 * scale), 1 / (5.0 * scale), 1 / (40.0 * scale))
    vn = g.add('ShaderNodeTexNoise', Scale=1.0, Detail=6, Roughness=0.65, Distortion=0.3)
    g.set(vn, 'Vector', g.o(vm, 0))
    streak = g.o(vn, 'Fac')
    lm = g.add('ShaderNodeMapping')
    g.set(lm, 'Vector', pos)
    lm.inputs['Scale'].default_value = (1 / (120.0 * scale), 1 / (120.0 * scale), 1 / (9.0 * scale))
    ln = g.add('ShaderNodeTexNoise', Scale=1.0, Detail=3, Roughness=0.5, Distortion=0.5)
    g.set(ln, 'Vector', g.o(lm, 0))
    if cliff_clean:
        face = g.ramp(streak, [(0.35, c('blue', ALB['mean'])), (0.5, c('clean', ALB['hi'])),
                               (0.62, c('cream', ALB['mean'])), (0.75, c('clean', ALB['hi']))])
        face = g.mix(g.maprange(g.o(ln, 'Fac'), 0.58, 0.66, 0.0, 0.35), face, c('cream', ALB['lo']))
        col = g.mix(steep, col, face)
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=0.55)
    b.inputs['Specular IOR Level'].default_value = 0.5
    b.inputs['IOR'].default_value = 1.31
    g.set(b, 'Base Color', col)
    h = g.math('ADD', g.math('MULTIPLY', noise(30, 3), 3.0), g.math('MULTIPLY', noise(1.0, 6, 0.6), 0.25))
    h = g.math('ADD', h, g.math('MULTIPLY', noise(0.03, 4, 0.5), 0.006))
    h = g.math('ADD', h, g.math('MULTIPLY', g.math('MULTIPLY', streak, steep), 2.5))      # gullies on the faces
    bp = g.add('ShaderNodeBump', Strength=1.0, Distance=1.0)
    g.set(bp, 'Height', h)
    g.set(b, 'Normal', g.o(bp, 'Normal'))
    g.output(g.o(b, 'BSDF'))
    return m


# ---------------------------------------------------------------- proxies (Sprint 2 replaces them)
def _mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    g = nodes.Graph(m)
    b = g.add('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
    g.set(b, 'Base Color', color)
    g.output(g.o(b, 'BSDF'))
    return m


def astronaut_proxy(sc, loc, height=1.85, heading=0.0):
    """Suit stand-in: a white capsule (body) + sphere (helmet) + pack box, 1.85 m tall."""
    suit = _mat('SuitProxy', (0.80, 0.79, 0.76), 0.7)
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=height * 0.62, location=(0, 0, height * 0.42))
    parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(0, 0, height * 0.85))
    parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.26, height * 0.55))
    parts.append(bpy.context.object)
    parts[-1].scale = (0.45, 0.22, 0.6)
    for p in parts:
        p.data.materials.append(suit)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = 'Astronaut'
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(heading))
    return ob


def lander_proxy(sc, loc, heading=0.0):
    """Lander stand-in: octagonal body 2.8 m across on four splayed legs with pads, gold-foil skirt; ~4 m tall."""
    body = _mat('LanderBody', (0.62, 0.62, 0.60), 0.35, 0.6)
    foil = _mat('LanderFoil', (0.80, 0.55, 0.18), 0.28, 1.0)
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.4, depth=1.6, location=(0, 0, 2.0))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(body)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.5, depth=0.7, location=(0, 0, 0.95))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(foil)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.5, radius2=0.25, depth=0.7, location=(0, 0, 3.1))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(body)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        top, foot = (1.2 * math.cos(a), 1.2 * math.sin(a), 1.4), (2.3 * math.cos(a), 2.3 * math.sin(a), 0.1)
        mid = tuple((p + q) / 2 for p, q in zip(top, foot))
        d = math.dist(top, foot)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=d, location=mid)
        leg = bpy.context.object
        v = np.subtract(top, foot)
        leg.rotation_euler = (0, math.atan2(math.hypot(v[0], v[1]), v[2]), math.atan2(v[1], v[0]))
        leg.data.materials.append(body)
        parts.append(leg)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.08, location=foot)
        parts.append(bpy.context.object)
        parts[-1].data.materials.append(body)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = 'Lander'
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(heading))
    return ob
