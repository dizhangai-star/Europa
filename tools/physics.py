"""Europa: every number the shots rely on, from constants. `python3 tools/physics.py` → the table for TREATMENT.md.

Adapted from ../Io/tools/physics.py (same conventions). km, h, degrees unless named. Europa is tidally locked:
Jupiter hangs at a fixed point in its sky (it rocks ±`libration` over one orbit, from the 0.009 eccentricity); the
Sun goes round once per synodic day. Jupiter's phase seen from Europa = the Sun's angle from Jupiter in its sky.
Io, the inner neighbour, passes in front of Jupiter once per Io–Europa synodic period (Ganymede, outside, never can).
"""
import json
import math
import sys

GM_EU = 3202.739          # km³/s²
R_EU = 1560.8             # km (mean)
A_EU = 671_100            # km, orbit semi-major axis
E_EU = 0.0094             # orbit eccentricity
P_ORB_EU = 85.2283        # h, sidereal orbit = rotation
V_EU = 2 * math.pi * A_EU / (P_ORB_EU * 3600)                # km/s
R_IO, A_IO, P_ORB_IO = 1821.6, 421_700, 42.4593              # Io: km, km, h
R_GA, A_GA, P_ORB_GA = 2634.1, 1_070_400, 171.7092           # Ganymede
R_J, R_J_POL = 71_492, 66_854                                # km
P_ROT_J = 9.925           # h
P_YEAR_J = 11.862 * 8766.15                                  # h
AU_J = 5.203
S_EARTH = 1361.0          # W/m²
P_GEOM_J = 0.538
P_GEOM_IO = 0.63          # Io's geometric albedo (V): its disc in 02
R_SUN, AU = 696_000, 149_597_870
EARTH_OCEAN_KM3 = 1.335e9

# Interior (published ranges, not measurements: Galileo gravity + magnetometer). Shell and ocean picked for the film.
ICE_H = (10.0, 20.0, 30.0)  # km, ice shell thickness (estimates ~3–30+; 20 = middle of the common range)
OCEAN_D = 100.0             # km, ocean depth (estimates ~60–150)
RHO_ICE, RHO_SEA = 920.0, 1030.0                             # kg/m³
# Conamara Chaos ground (film picks inside the Galileo-era descriptions: ice plates ≲ 10 km across, standing up to
# ~100–250 m over a hummocky matrix, their tops keeping the older ridged plains; shadow/stereo heights, rough)
CHAOS = dict(plate_m=(250.0, 2500.0), plate_h=(40.0, 160.0), tilt_deg=(0.0, 4.0), matrix_h=14.0,
             ridge_h=7.0, ridge_gap=(180.0, 450.0),
             # the plates are pieces of the older ridged plains, turned and shifted (they fit back together, Spaun et
             # al. 1998): ridge sets cross at several azimuths (PIA01403: 2–3 per plate), plus fragments of double
             # ridges (two crests, a central trough; 0.5–2 km wide and ~100–300 m high on the plains, the film's are
             # the smaller ones that cross the plates)
             ridge_sets=(35.0, 100.0, 160.0), plate_spin_deg=15.0, double_az=(62.0, 128.0), double_gap=3200.0,
             double_w=(250.0, 600.0), double_h=(20.0, 70.0),
             # the matrix: hummocks under a jumble of blocks down to the resolution limit (PIA01182, 9 m/px: house-size
             # blocks; PIA01403 15 m/px): film picks per scale band (cell m, block size m, height m, share of cells;
             # three overlapping grids per band)
             debris=((300.0, (30.0, 200.0), (6.0, 30.0), 0.8), (60.0, (6.0, 40.0), (1.5, 8.0), 0.8),
                     (8.0, (0.8, 5.0), (0.2, 1.2), 0.6)))
PLUME_H = 200.0             # km, tentative Hubble water plume (2012/2014), unconfirmed


def deg(x):
    return math.degrees(x)


def g_at(h=0.0):
    return GM_EU / (R_EU + h) ** 2 * 1000                    # m/s²


def jupiter_elev(theta):
    """Elevation (deg) of Jupiter's centre, observer theta deg from the sub-Jupiter point."""
    t = math.radians(theta)
    ox, oy = R_EU * math.sin(t), R_EU * math.cos(t)
    dx, dy = -ox, A_EU - oy
    return deg(math.asin((dx * math.sin(t) + dy * math.cos(t)) / math.hypot(dx, dy)))


def px_across(ang_deg, lens_mm, width_px=1920, sensor=36.0):
    return width_px * math.tan(math.radians(ang_deg / 2)) / (sensor / 2 / lens_mm)


def plume(h_max):
    """Vertical launch speed (km/s) for apex h_max (km), 1/r gravity, and the flight time (s)."""
    v = math.sqrt(2 * GM_EU * (1 / R_EU - 1 / (R_EU + h_max)))
    r, vr, t, dt = R_EU, v, 0.0, 0.5
    while True:
        vr -= GM_EU / r ** 2 * dt
        r += vr * dt
        t += dt
        if r <= R_EU:
            return v, t


def hidden(d_arc):
    return R_EU * (1 / math.cos(d_arc / R_EU) - 1)


# ---------------------------------------------------------------- the sky, Europa-centred frame co-rotating with it
# X → Jupiter, Z → north, Y = Z × X = east. Jupiter sits at (A_EU, 0, 0) for ever. Io, faster, laps Europa: its angle
# Δ from conjunction grows at ω_Io − ω_Eu; at Δ = 0 it is between Europa and Jupiter (in front of the disc).
# Inclinations (Io 0.05°, Europa 0.47°) and the site's parallax are ignored here (< 1° against a 12° disc).
W_IO_EU = 2 * math.pi * (1 / P_ORB_IO - 1 / P_ORB_EU)        # rad/h
P_SYN_IO_EU = 2 * math.pi / W_IO_EU                          # h, Io–Europa conjunctions
P_SYN = 1 / (1 / P_ORB_EU - 1 / P_YEAR_J)                    # h, Sun to Sun
P_ROT_J_EU = 1 / (1 / P_ROT_J - 1 / P_ORB_EU)                # h, Jupiter's spin seen from Europa
R_SUN_DEG = deg(math.atan(R_SUN / (AU_J * AU)))
E_SUN = S_EARTH / AU_J ** 2


def io_pos(dlt):
    """Io (km, Europa frame) at angle dlt (rad) from conjunction."""
    return (A_EU - A_IO * math.cos(dlt), -A_IO * math.sin(dlt), 0.0)


def _norm(v):
    m = math.sqrt(sum(c * c for c in v))
    return tuple(c / m for c in v), m


def _ang(a, b):
    (ua, _), (ub, _) = _norm(a), _norm(b)
    return deg(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(ua, ub))))))


def jupiter_r_deg(d=A_EU - R_EU):
    return deg(math.asin(R_J / d)), deg(math.asin(R_J_POL / d))


def io_transit():
    """(hours Io's centre spends on Jupiter's disc, Io's speed across it °/h at conjunction, Io's diameter there °)."""
    rj = jupiter_r_deg(A_EU)[0]
    lo, hi = 0.0, 1.0
    for _ in range(60):                                      # Δ where Io's centre reaches the limb
        m = (lo + hi) / 2
        lo, hi = (m, hi) if _ang(io_pos(m), (1, 0, 0)) < rj else (lo, m)
    d0 = A_EU - A_IO
    rate = deg(W_IO_EU * A_IO / d0)                         # °/h, Io across the sky near conjunction
    return 2 * lo / W_IO_EU, rate, 2 * deg(math.asin(R_IO / d0))


def io_shadow(elong):
    """Io's shadow transit (Io on the Sun–Jupiter line, every Io synodic day) seen from Europa with the Sun at
    elongation `elong` (deg, east +). The shadow sits at Jupiter's sub-solar point. Returns (Io's offset from
    Jupiter's centre, the shadow's offset, both deg; shadow on the face Europa sees?; Io's diameter deg, lit fraction)."""
    s = (math.cos(math.radians(elong)), math.sin(math.radians(elong)), 0.0)
    io = (A_EU + A_IO * s[0], A_IO * s[1], 0.0)
    sh = (A_EU + R_J * s[0], R_J * s[1], 0.0)
    _, d = _norm(io)
    phase = (1 + math.cos(math.radians(_ang(s, tuple(-x for x in io))))) / 2
    return _ang(io, (1, 0, 0)), _ang(sh, (1, 0, 0)), s[0] < 0, 2 * deg(math.asin(R_IO / d)), phase


def own_shadow(elong):
    """Europa's own shadow on Jupiter (it falls at the anti-solar point), seen from Europa: (offset from Jupiter's
    centre deg, umbra and penumbra diameters deg; on the disc?). Sun at Jupiter: R_SUN_DEG."""
    d = A_EU - R_EU
    off = abs(180.0 - abs(elong))
    spread = d * math.tan(math.radians(R_SUN_DEG))          # km the shadow cone shrinks/grows over the distance
    return off, 2 * deg((R_EU - spread) / d), 2 * deg((R_EU + spread) / d), off < jupiter_r_deg(d)[0]


def io_cast_shadow(elong, dlt, fr):
    """Io's shadow on Jupiter while Io is at `dlt` from conjunction and the Sun at `elong`: the Sun–Io line meets the
    cloud tops. Returns (Io's direction, the shadow's direction, both from the site; their separation deg), or None if
    the shadow misses the disc."""
    io = io_pos(dlt)
    s = sun_dir(elong)
    rel = tuple(a - b for a, b in zip(io, (A_EU, 0.0, 0.0)))
    b, c = _dot(rel, s), _dot(rel, rel) - R_J ** 2               # |rel − t s| = R_J, t > 0 (away from the Sun)
    disc = b * b - c
    if disc < 0:
        return None
    t = b - math.sqrt(disc)
    sh = tuple(a - t * k for a, k in zip(io, s))
    vi, vs = from_site(io, fr), from_site(sh, fr)
    return vi, vs, _ang(vi, vs)


def jupiter_shine(elong):
    a = math.radians(180 - abs(elong))
    phi = (math.sin(a) + (math.pi - a) * math.cos(a)) / math.pi
    return P_GEOM_J * E_SUN * (R_J / (A_EU - R_EU)) ** 2 * phi


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


# ---------------------------------------------------------------- one site's local sky
# Site frame from (lat, W longitude): up, east, north as Europa-frame unit vectors. The Sun at elongation E (deg from
# Jupiter, east +) and declination dec: (cos dec cos E, cos dec sin E, sin dec). E falls by 360° per synodic day
# (Europa turns prograde), so the Sun rises in the east (E = 180° side) and sets toward Jupiter.
SITE = ('Conamara Chaos', 9.7, 273.7)
LAPSE_E_END = (180.0, 179.0, 178.0)   # deg, 02's Sun when Io sets (film pick: 179 locked 2026-10-05; the others printed)
DEC_SUN = 3.13              # deg, Jupiter's axial tilt: the Sun's declination over Europa's equator, ± over 11.9 y


def site(lat, lon_w):
    la, lo = math.radians(lat), math.radians(360 - lon_w)
    up = (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
    east, _ = _norm(_cross((0, 0, 1), up))
    return up, east, _cross(up, east)


def from_site(p, fr):
    return tuple(a - R_EU * b for a, b in zip(p, fr[0]))


def altaz(v, fr):
    """(elevation, azimuth from north through east) in deg of direction v seen from site frame fr."""
    (u, _), (up, east, north) = _norm(v), fr
    return deg(math.asin(_dot(u, up))), deg(math.atan2(_dot(u, east), _dot(u, north))) % 360


def sun_dir(elong, dec=0.0):
    e, d = math.radians(elong), math.radians(dec)
    return (math.cos(d) * math.cos(e), math.cos(d) * math.sin(e), math.sin(d))


def sky_angle(a, c, fr):
    """Angle (deg) of direction a projected on the sky at c, from straight up; + toward north."""
    (c, _), (up, _, north) = _norm(c), fr
    pa = tuple(x - _dot(a, c) * y for x, y in zip(a, c))
    pv = tuple(x - _dot(up, c) * y for x, y in zip(up, c))
    pn = _cross(c, pv)                                       # 90° from up on the sky, sign fixed below
    s = 1 if _dot(pn, north) > 0 else -1
    return deg(math.atan2(s * _dot(pa, pn) / math.sqrt(_dot(pn, pn)), _dot(pa, pv) / math.sqrt(_dot(pv, pv))))


def disc_light(c, r_deg, normal, fr, n=161):
    """Fraction of a uniformly bright disc's facing irradiance that a surface with `normal` receives, the disc cut by
    the horizon (full phase, no limb darkening)."""
    (c, _), up = _norm(c), fr[0]
    u, _ = _norm(_cross(c, (0, 0, 1)) if abs(c[2]) < 0.9 else _cross(c, (1, 0, 0)))
    v = _cross(c, u)
    r = math.radians(r_deg)
    tot = got = 0
    for i in range(n):
        for j in range(n):
            x, y = (2 * i / (n - 1) - 1) * r, (2 * j / (n - 1) - 1) * r
            if x * x + y * y > r * r:
                continue
            d, _ = _norm(tuple(a + x * b + y * w for a, b, w in zip(c, u, v)))
            tot += 1
            if _dot(d, up) > 0:
                got += max(0.0, _dot(d, normal))
    return got / tot


def sun_track(fr, dec):
    """Scan the Sun's day at a site (E falling 182° → −182°, 0.002° steps): elongations of sunrise, first/second/third
    contact with Jupiter's limb and sunset, with the Sun's elevation at each (None if it doesn't happen above ground)."""
    c = from_site((A_EU, 0, 0), fr)
    rj = deg(math.asin(R_J / _norm(c)[1]))
    ev, prev = {}, None
    e = 182.0
    while e > -182.0:
        s = sun_dir(e, dec)
        el, sep = altaz(s, fr)[0], _ang(s, c)
        cur = (el > 0, sep < rj + R_SUN_DEG, sep < rj - R_SUN_DEG)
        if prev:
            if cur[0] and not prev[0]:
                ev.setdefault('sunrise', (e, el))
            if prev[0] and not cur[0]:
                ev.setdefault('sunset', (e, el))
            if cur[1] and not prev[1]:
                ev.setdefault('first contact', (e, el))
            if cur[2] and not prev[2]:
                ev.setdefault('second contact', (e, el))
            if prev[2] and not cur[2]:
                ev.setdefault('third contact', (e, el))
        prev = cur
        e -= 0.002
    return ev, rj


def io_track(fr):
    """Io's transit seen from the site: (elevation where its centre enters the disc, entry Δ rad, Δ where it sets or
    leaves, how it ends, its motion angle on the sky from straight up)."""
    c = from_site((A_EU, 0, 0), fr)
    rj = deg(math.asin(R_J / _norm(c)[1]))
    on, ent, end = False, None, None
    dl = -0.2
    while dl < 0.2:
        p = from_site(io_pos(dl), fr)
        inside, up = _ang(p, c) < rj, altaz(p, fr)[0] > 0
        if inside and not on and ent is None:
            ent = (altaz(p, fr)[0], dl)
        if ent and end is None and (not up or (on and not inside)):
            end = (dl, 'sets behind the horizon, still on the disc' if not up else 'leaves the disc')
        on = inside
        dl += 1e-5
    a, b = from_site(io_pos(-1e-3), fr), from_site(io_pos(1e-3), fr)
    mv = tuple(y / _norm(b)[1] - x / _norm(a)[1] for x, y in zip(a, b))
    return ent, end, sky_angle(mv, c, fr)


def europa_on_io(elong, dlt, dec=0.0):
    """Europa's shadow on Io (a mutual eclipse, "2E1" in the PHEMU campaigns): Io at `dlt`, Sun at `elong`, `dec`.
    Returns (distance of Io's centre from the shadow's axis, umbra and penumbra radii there; all km). Needs the Sun
    near Jupiter's equator (equinox seasons) and Europa near its orbit's node: its 0.47° inclination (ignored here)
    puts it up to 5,500 km off the plane, and the shadow misses Io beyond R_IO + penumbra (≈ 3,600 km)."""
    s = sun_dir(elong, dec)
    io = io_pos(dlt)
    t = -_dot(io, s)                                         # along the shadow, away from the Sun
    rho = math.sqrt(max(_dot(io, io) - t * t, 0.0))
    k = t * math.tan(math.radians(R_SUN_DEG))
    return rho, R_EU - k, R_EU + k


def eclipse_span(fr, e_end, n=4000):
    """02: (first touch, deepest, last touch) hours after Io's entry when Europa's penumbra is on Io, or None."""
    d = lapse(fr, e_end, 0.0)['dur']
    hs, on, best = [], [], None
    for i in range(n + 1):
        h = d * (-0.3 + 1.6 * i / n)
        s = lapse(fr, e_end, h)
        rho, um, pen = europa_on_io(s['elong'], s['dlt'])
        if rho < R_IO + pen:
            on.append(h)
        if best is None or rho < best[0]:
            best = (rho, h)
    return (on[0], best[1], on[-1]) if on else None


_TRACK = {}


def lapse(fr, e_end, h):
    """02's time-lapse (Sprint 3.2): the sky `h` hours after Io's centre enters the disc, on a transit that ends (Io
    sets) with the Sun at elongation `e_end`. Returns dict: dlt (Io, rad from conjunction), elong (Sun, wrapped
    ±180; it falls 360/P_SYN °/h), spin (Jupiter's rotation seen from Europa so far, deg: its clouds move the way Io
    does), turn (the stars' turn about Europa's pole so far, deg: one sidereal day P_ORB_EU), dur (the transit, h)."""
    key = repr(fr)
    if key not in _TRACK:
        _TRACK[key] = io_track(fr)
    ent, end, _ = _TRACK[key]
    dur = (end[0] - ent[1]) / W_IO_EU
    e = e_end + 360.0 / P_SYN * (dur - h)
    return dict(dlt=ent[1] + W_IO_EU * h, elong=(e + 180.0) % 360.0 - 180.0, spin=360.0 * h / P_ROT_J_EU,
                turn=360.0 * h / P_ORB_EU, dur=dur)


# ---------------------------------------------------------------- Blender local frame (the libs copied from Io)
# The scene frame at the site (SITE): +Y = toward Jupiter along the ground (azimuth 0), +X = right of it as you face
# Jupiter, +Z = up. At Conamara Jupiter is about due west, so +X ≈ north and Jupiter's pole lies near horizontal:
# its bands stand vertical. Same shape as Io's (west, south, up): blender/lib/jupiter.py, sky.py read only this.
def _local_axes(fr=None):
    fr = fr or site(*SITE[1:])
    up = fr[0]
    c, _ = _norm(from_site((A_EU, 0, 0), fr))
    fwd, _ = _norm(tuple(a - _dot(c, up) * b for a, b in zip(c, up)))
    return _cross(fwd, up), fwd, up


def to_local(v, fr=None):
    """Europa-frame vector → local (right, toward Jupiter, up)."""
    return tuple(_dot(v, ax) for ax in _local_axes(fr))


def jupiter_local(fr=None):
    """Jupiter as seen from the site: (unit direction, distance km, angular radius eq deg, polar deg, axis unit)."""
    fr = fr or site(*SITE[1:])
    u, d = _norm(from_site((A_EU, 0, 0), fr))
    return (to_local(u, fr), d, *jupiter_r_deg(d), to_local((0.0, 0.0, 1.0), fr))


def sun_local(elong, dec=0.0, fr=None):
    """Unit vector (local) toward the Sun at elongation `elong` (deg, east +) and declination `dec`."""
    return to_local(sun_dir(elong, dec), fr)


def alt_az(u):
    """(elevation, azimuth) deg of a local unit vector; azimuth 0 = toward Jupiter, + = to the right."""
    return deg(math.asin(u[2])), deg(math.atan2(u[0], u[1]))


def lit_fraction(elong):
    """Fraction of Jupiter's disc lit; phase angle = 180° − |elongation|."""
    return (1 - math.cos(math.radians(abs(elong)))) / 2


# ---------------------------------------------------------------- the ice shell, the cryobot, the water
T_SURF = 100.0              # K, Conamara surface mean (equatorial ~86–132 K over a day)
K_ICE = 651.0               # W/m: ice conductivity k = 651/T (Petrenko & Whitworth)
L_ICE = 334e3               # J/kg
DTM_DP = -0.0074            # K/bar, ice Ih melting point vs pressure (Clausius–Clapeyron)
CRYO_D = 0.25               # m, probe diameter (film pick; Europa cryobot concepts 0.15–0.3 m)
CRYO_P = (1.0, 5.0, 10.0)   # kW thermal (concepts: RTG/fission, ~1–10 kW); film pick in TREATMENT.md
CRYO_ETA = 0.5              # share of the heat that melts the ice ahead (the rest warms the walls); film pick
DOSE_SV_DAY = 5.4           # Sv/day at Europa's surface (commonly cited Galileo-era figure)
LD50_SV = 4.5               # Sv, ~50 % lethal without treatment
# Pure water absorption, 1/m (Pope & Fry 1997). The ocean's salts/particles are unknown: this is the clearest case.
A_WATER = {420: 0.00454, 450: 0.00922, 500: 0.0257, 550: 0.0565, 600: 0.2224, 650: 0.340, 700: 0.650}
RGB_BANDS = ((600, 700), (500, 600), (420, 500))           # nm: the render's R, G, B, box-averaged
SEA_SCATTER = 0.02          # 1/m, particles (film pick: clearest open ocean ~0.01–0.05; Europa's is unknown)
SEA_G = 0.85                # their forward-scattering anisotropy (ocean particles, Petzold ~0.9)
CRYO_LAMP_W = 50.0          # W radiant, the probe's one lamp (film pick: ~15,000 lm LED, an ROV floodlight)
# The probe's layout, nose (z = 0) up, m. Sources: JPL PRIME (Hand et al. 2022: Ø 0.25 m, radioisotope heat, comm
# relays left in the ice, the SWIM micro-swimmer package), NASA Compass "Europa Tunnelbot" (2019: heat section,
# electronics vault, fibre tether paid out from the probe, repeater "pucks" every few km), Stone Aerospace
# VALKYRIE/PROMETHEUS (hot-water jets from the melt head). Lengths per section, CRYO_LEN, puck size/spacing, jet
# count and the tether's Ø are film picks inside those designs. The melt head runs at ~0–100 °C: it does not glow.
CRYO_LEN = 3.0
CRYO_SECTIONS = (('head', 0.30),            # copper melt head, hot-water jets
                 ('bay', 0.35),             # instruments: lamp port, camera dome, sample inlets
                 ('swim', 0.10),            # SWIM package: 10 cm × Ø 25 cm, up to 50 wedges (PRIME/SWIM) ⚠ concept
                 ('heat', 0.85),            # heat source (RTG / fission core) and its pumped water loop
                 ('vault', 0.45),           # electronics vault (radiation shield)
                 ('tail', 0.95))            # tether spool + puck magazine; tether out through the top cap
CRYO_JETS = 7                # melt-head jets: 6 round the cone + 1 at the tip (film pick), Ø 8 mm
CRYO_TETHER_D = 0.005        # m: optical fibre in three layers (crush jacket, Kevlar, buffer), film pick
CRYO_PUCK = (0.20, 0.07)     # m Ø × height, threaded on the tether; film pick (Tunnelbot repeaters)
CRYO_PUCK_KM = 2.0           # km between pucks (film pick, "every few km") → 9 in a 20 km shell + 1 spare
SWIM_N, SWIM_TIERS = 50, 2   # wedges in the package: 2 tiers × 25 radial slices (fits PRIME's 10 cm × Ø 25 cm)
SWIM_LEN = 0.12              # m, one swimmer (SWIM concept ~12 cm)

# The shell seen from inside (Sprint 2.3), lit only by the probe's lamp.
# Pure ice: imaginary refractive index (Warren & Brandt 2008, JGR 113 D14220, table IOP_2008 at −7 °C; colder ice
# absorbs slightly less in the red, ignored). Absorption α = 4π m_im / λ: blue travels ~400 m, red ~2–8 m.
M_IM_ICE = {400: 2.365e-11, 420: 3.135e-11, 450: 9.239e-11, 480: 2.861e-10, 500: 5.889e-10, 520: 1.076e-9,
            550: 2.289e-9, 580: 4.159e-9, 600: 5.730e-9, 620: 8.580e-9, 650: 1.430e-8, 680: 2.090e-8, 700: 2.900e-8}
N_ICE, N_WATER = 1.311, 1.333   # real index at 550 nm (Warren & Brandt; water ~1.333): ice → water edge almost unseen
# Pores and bubbles make ice white. Europa's top is porous regolith; how much porosity survives below it is unknown:
# cold ice creeps pores shut only slowly, so models allow a few % through the top ~km, closing with depth and warmth
# (Nimmo et al. 2003; Johnson et al. 2017, both model ranges). Film picks inside that: φ(z) = PORE_PHI0·e^(−z/PORE_ZC)
# down to PORE_FLOOR (bubbles / brine inclusions of deep ice). Scattering, geometric optics: σs = 1.5 φ / r (Q_ext = 2),
# asymmetry g ≈ 0.75 for air bubbles in ice (Mullen & Warren 1988; Warren's ice-optics work uses ~0.75–0.89).
PORE_R = 0.5e-3              # m, pore/bubble radius (film pick; glacier-ice bubbles 0.1–1 mm)
PORE_PHI0, PORE_ZC, PORE_FLOOR = 0.002, 0.8, 2e-6            # porosity under the regolith, e-fold km, deep floor
PORE_G = 0.75
# The brittle lid: open cracks only where the ice is cold and stiff (elastic/brittle thickness estimates ~1–6 km;
# film pick 3 km). Below it cracks heal; old cracks survive as veins of refrozen (salty) water.
BRITTLE_KM = 3.0
VEINS_PER_M3 = 0.0015        # old cracks and sills refilled with refrozen water, per m³ (film pick; any depth)
VEIN_T = (0.03, 0.6)         # m, their thickness at the centre (film pick); 70 % steep (dikes), 30 % flat-lying (sills)
VEIN_BRINE_S = 0.3           # 1/m: salt/brine inclusions of the refrozen water (film pick, added to the ice's own
                             # σs): faint sheets in the porous top, deep down the only thing that shows
BANDS_PER_M3 = 0.0003        # flat-lying bands of more porous ice (porosity varies layer to layer: old surfaces,
BAND_T, BAND_GAIN = (0.1, 1.2), 0.5   # refrozen flows; film picks): m thick, σs added = gain × the ice's σs
CRACKS_PER_M3 = 0.004        # open cracks (0.4–4 m air films) per m³ of brittle lid (film pick)

# Under the ice (Sprint 2.4): the shell's base seen from the water, lit only by the probe's lamp. Nobody has seen it;
# the shapes are Earth's ice-shelf bases (the closest analog) at the scale physics gives for Europa's water.
NU_SEA = 1.8e-6              # m²/s, kinematic viscosity of seawater near its freezing point
OCEAN_U = 0.03               # m/s, current along the ice base (film pick: Europa ocean models give ~mm/s–cm/s,
                             # Soderlund et al. 2014): drifts the particles and sets the scallop length
SCALLOP_RE = 22500.0         # Curl (1974): melt/dissolution scallops settle at Re = u·L/ν ≈ 22,500 (limestone caves,
                             # ice-shelf bases and lab ice scallops alike, Bushuk et al. 2019)
# Terraces: Icefin under Thwaites (Schmidt et al. 2023, Nature 614: 471) found the base a staircase of flat treads
# and steep risers, in all orientations and many scales, wherever the base melts. Film picks at Icefin's scale:
BASE_RISER = (0.4, 2.5)      # m, riser height
BASE_TREAD = (3.0, 14.0)     # m, tread width
BASE_RISER_DEG = 65.0        # steep faces (Icefin's crevasse walls and risers melt fastest: they stay steep)
# The base ice: freshly accreted ice at the interface holds brine (a porous "mushy" layer; Buffo et al. 2020), so it
# scatters like sea ice seen from below: white-blue, the lamp's spot spreading inside it. Its strength is unknown:
# film pick, a reduced scattering σs' = 3/m (transport length 0.33 m), with pure-ice absorption (ice_rgb).
BASE_SIGMA_P = 3.0           # 1/m, reduced scattering σs(1 − g) of the base ice (film pick)
# ⚠ Frazil (model): where water rises along a sloping base it supercools ("ice pump") and grows free ice discs that
# float up and settle on the ceiling as marine ice (Earth: under the Ross / Amery shelves; Europa: Wolfenbarger et al.
# 2022, Lawrence et al. 2024). Discs ~0.2–3.4 mm across (Gosink & Osterkamp 1983, rivers: ~2 mm typical, rising
# edge-on at ~10 mm/s); the thickness is chosen so rise_speed() gives that measured Earth speed; the count is a film pick.
FRAZIL_D, FRAZIL_T = 2.0e-3, 0.21e-3       # m, disc diameter and thickness (calibrated, above)
FRAZIL_PER_M3 = 3000.0                     # discs per m³ near the ceiling (film pick)
MOTES_PER_M3 = 400.0                       # mineral/salt grains 0.2–1 mm per m³ (film pick; makes SEA_SCATTER's
                                           # particles visible inside the beam)


def _band_avg(f):
    return tuple(sum(f(lo + (hi - lo) * (k + 0.5) / 50) for k in range(50)) / 50 for lo, hi in RGB_BANDS)


def _interp(tab, x):
    wl = sorted(tab)
    for w0, w1 in zip(wl, wl[1:]):
        if w0 <= x <= w1:
            return tab[w0] + (tab[w1] - tab[w0]) * (x - w0) / (w1 - w0)
    return tab[wl[0]] if x < wl[0] else tab[wl[-1]]


def water_rgb():
    """Pure water's absorption (1/m) per render channel R, G, B: A_WATER interpolated, averaged over RGB_BANDS."""
    return _band_avg(lambda x: _interp(A_WATER, x))


def ice_rgb():
    """Pure ice's absorption (1/m) per render channel R, G, B, from M_IM_ICE (α = 4π m_im / λ)."""
    return _band_avg(lambda x: 4 * math.pi * _interp(M_IM_ICE, x) / (x * 1e-9))


def pore(z_km):
    """Porosity, scattering coefficient σs (1/m) and transport length (m) of the ice at depth z_km."""
    phi = max(PORE_PHI0 * math.exp(-z_km / PORE_ZC), PORE_FLOOR)
    s = 1.5 * phi / PORE_R
    return phi, s, 1 / ((1 - PORE_G) * s)


def scallop_len(u=OCEAN_U):
    """Melt-scallop length (m) on the ice base under a current u (m/s): Curl's Re_L = 22,500."""
    return SCALLOP_RE * NU_SEA / u


def base_ice():
    """The base ice seen from below as a diffusing slab: per render channel (R, G, B) the diffuse albedo (Jensen et
    al. 2001, total diffuse reflectance, matched boundary: ice→water 0.98) and the mean free path (m) for a random-walk
    subsurface shader. Pure-ice absorption makes the red darker by itself (long paths eat it)."""
    alb, mfp = [], []
    for sa in ice_rgb():
        st = BASE_SIGMA_P + sa
        a = BASE_SIGMA_P / st
        s = math.sqrt(3 * (1 - a))
        alb.append(a / 2 * (1 + math.exp(-4 / 3 * s)) * math.exp(-s))
        mfp.append(1 / st)
    return tuple(alb), tuple(mfp)


def rise_speed(d=FRAZIL_D, t=FRAZIL_T, g=None, rho=RHO_SEA):
    """Terminal speed (m/s) of an ice disc rising edge-on (as frazil discs rise, Gosink & Osterkamp 1983) through
    water of density rho: buoyancy (rho − ρ_ice) g V against the edge-on Stokes disc drag F = (16/3) μ d v with an
    Oseen factor (1 + Re/2π) (Re ≲ 50). g: default Europa's."""
    g = g_at() if g is None else g
    mu = NU_SEA * rho
    f = (rho - RHO_ICE) * g * math.pi * (d / 2) ** 2 * t
    v = f / (16 / 3 * mu * d)
    for _ in range(50):
        v = f / (16 / 3 * mu * d * (1 + v * d / NU_SEA / (2 * math.pi)))
    return v


def lamp_seen(d):
    """The lamp seen from d m through the water: per channel the direct beam's transmission e^(−(a + b) d) (pure-water
    absorption + particle scattering out of the ray) and its brightness vs 5 m in EV (with 1/r²)."""
    out = []
    for a in water_rgb():
        tr = math.exp(-(a + SEA_SCATTER) * d)
        out.append((tr, math.log2((5 / d) ** 2 * tr / math.exp(-(a + SEA_SCATTER) * 5))))
    return out


# The refrozen hole's bubble column (real on Earth: IceCube's 'hole ice'). A water-filled hole freezes from the walls
# inward and pushes the gas (and on Europa the salt) it holds to the centre: the last water to freeze leaves a milky
# core. IceCube's 55–60 cm holes have a ~16 cm column (0.27 of the hole) with a scattering length of 2–30 cm
# (Rongen 2016, EPJ Web Conf. 116, 06011; IceCube 2023, arXiv:2307.15298). Europa's melt (radiolytic O2, sulfate and
# chloride salts in the ice) should do the same; how much is a film pick: the fraction scaled from IceCube, the
# scattering length in its middle.
HOLE_CORE = (0.27, 0.05, 0.75)   # core diameter / hole diameter, scattering length m, g (bubbles, forward)


def refreeze(z_km, h_ice, a=CRYO_D / 2, wall=0.0):
    """The borehole behind the probe freezing shut at depth z_km: radial conduction with ice k(T) = K_ICE/T, c(T),
    enthalpy method. Water at the melting point fills r < a; the ice beyond starts at the lid's temperature, warmed
    by `wall` K near the hole (the probe's side heat, 1 − η, is ignored at 0: a lower bound on the time).
    Returns (hours to close, [(fraction of the time, open radius m), …])."""
    t_far, tm = shell_T(z_km, h_ice)
    dT = tm - t_far
    k_m, c_m = K_ICE / tm, c_ice(tm)
    t_est = RHO_ICE * L_ICE * a * a / (4 * k_m * max(dT, 0.05)) * 3
    dr = a / 6
    n = int((a + 6 * math.sqrt(k_m / (RHO_ICE * c_m) * t_est)) / dr) + 2
    r = [(i + 0.5) * dr for i in range(n)]

    def h_of(T):                                          # J/kg below the melt (sensible heat of ice)
        return 185.0 * (T - tm) + 7.037 / 2 * (T * T - tm * tm)

    def t_of(h):
        if h >= 0:
            return tm
        b, cc = 185.0, -7.037 / 2 * tm * tm - 185.0 * tm - h        # 3.5185 T² + 185 T + cc = 0
        return (-b + math.sqrt(b * b - 4 * 3.5185 * cc)) / (2 * 3.5185)
    H = [L_ICE if ri < a else h_of(min(t_far + wall * math.exp(-(ri - a) / a), tm)) for ri in r]
    dt = 0.2 * dr * dr * RHO_ICE * c_ice(t_far) / (K_ICE / t_far)
    t, hist = 0.0, []
    while True:
        T = [t_of(h) for h in H]
        flux = [0.0] * (n + 1)                           # W/m per unit length across face i (between i−1 and i)
        for i in range(1, n):
            k = 2 * K_ICE / (T[i] + T[i - 1])
            flux[i] = -k * (T[i] - T[i - 1]) / dr * 2 * math.pi * (i * dr)
        for i in range(n - 1):
            H[i] -= (flux[i + 1] - flux[i]) * dt / (RHO_ICE * 2 * math.pi * r[i] * dr)
        t += dt
        open_r = sum(1 for h in H if h > 0) * dr
        hist.append((t, open_r))
        if open_r == 0:
            break
    return t / 3600, [(ti / t, ri) for ti, ri in hist[::max(1, len(hist) // 40)]]


def c_ice(T):
    return 185.0 + 7.037 * T                                 # J/kg/K (Fukusako 1990)


def shell_T(z, h_ice):
    """Conductive-lid temperature (K) at depth z (km) of an h_ice km shell (k ∝ 1/T → exponential profile)."""
    tb = 273.15 + DTM_DP * RHO_ICE * g_at() * h_ice * 1000 / 1e5
    return T_SURF * (tb / T_SURF) ** (z / h_ice), tb


def cryo_speed(p_kw, h_ice, z, d=CRYO_D, eta=CRYO_ETA):
    """The probe's descent speed (m/s) at depth z km: the share eta of its heat warms and melts the ice ahead."""
    t, tb = shell_T(z, h_ice)
    q = 185.0 * (tb - t) + 7.037 / 2 * (tb ** 2 - t ** 2) + L_ICE
    return eta * p_kw * 1000 / (RHO_ICE * math.pi * (d / 2) ** 2 * q)


def cryobot(p_kw, h_ice, d=CRYO_D, eta=CRYO_ETA):
    """Days to melt through h_ice km at p_kw thermal; speed (m/h) at the top and at the base."""
    def rate(z):                                             # m/s at depth z km
        return cryo_speed(p_kw, h_ice, z, d, eta)
    n, sec = 2000, 0.0
    for i in range(n):
        sec += h_ice * 1000 / n / rate((i + 0.5) * h_ice / n)
    return sec / 86400, rate(0) * 3600, rate(h_ice * 0.999) * 3600


# ---------------------------------------------------------------- 03: the probe starts in vacuum (Sprint 3.3)
# Below water's triple point the head can't melt the surface ice: it sublimates it. The vapour leaves the gap round
# the probe, choked at about the triple point (the contact self-regulates there), and expands into vacuum; part of it
# condenses into µm grains (as at Enceladus's vents). Lab tests in cryo-vacuum: after a short sublimation phase the
# channel closes round the probe (vapour freezes onto the cold walls) and a pressurised pocket of liquid forms
# (Experimental validation of cryobot thermal models, PSJ 2023; sublimation slows the start ×7.7, Kömle et al.).
# Liquid that does meet vacuum boils and freezes at once: the boiling takes the latent heat of the rest.
L_SUB = 2.834e6               # J/kg, ice → vapour near 273 K
L_VAP = 2.501e6               # J/kg, water → vapour at 0 °C
C_WATER = 4186.0              # J/kg/K
T_TRIPLE, P_TRIPLE = 273.16, 611.657                         # K, Pa
R_H2O, GAMMA_H2O = 461.5, 1.33                               # J/kg/K, cp/cv of water vapour
JET_CONDENSE = 0.1            # share of the vapour that condenses into grains in the free expansion (estimate: a few
                              # to ~20 % for saturated vapour expanding into vacuum)
JET_GRAIN_R = 1.0e-6          # m, grain radius (Enceladus plume grains ~1 µm)
JET_G = 0.85                  # Henyey–Greenstein asymmetry of µm ice grains (diffraction peak ~15° wide; estimate)
A_PLAIN = 0.5                 # Conamara's dark plain, albedo (Europa's Bond albedo ~0.68; the brown matrix lower)
# The vapour leaves a point source on the ice (the nose's contact) into a half-space: a cos² lobe about the vertical,
# density ∝ cos²θ / r² (free expansion; the probe's body stands in the middle of it).
# Loose surface frost blown out by that vapour (Europa's regolith: fine frost and flakes of crust; the amount and the
# speeds are film picks: the gas leaves at ~400 m/s, the flakes take a few m/s at most):
FROST_N = 5000                # flakes
FROST_RING = (0.14, 0.7)      # m from the nose: where they lie (the head's footprint outward)
FROST_SIZE = (0.002, 0.015)   # m across
FROST_V = (0.3, 6.5)          # m/s, most slow (v = lo + (hi − lo)·u^FROST_V_POW)
FROST_V_POW = 1.2
FROST_EL = (15.0, 80.0)       # deg up, steeper for the ones near the nose
FROST_TAU = 0.6               # s, e-fold of the burst: the vapour clears the loose frost from the ring
# The deployment tripod (film pick: a borehole tripod with a sheave, the tether to a reel on the ice)
TRIPOD_H = 4.2                # m, sheave above the ice (the 3 m probe hangs with its nose on the ice)
TRIPOD_FOOT_R = 1.7           # m
TRIPOD_LEG_D = 0.05           # m
TRIPOD_SHEAVE = 0.12          # m, sheave radius
REEL = (0.55, 0.40, 0.35, 2.2)  # m: the tether reel box (l, w, h) and its distance from the probe


def vacuum_start(p_kw, eta=CRYO_ETA, d=CRYO_D):
    """The probe's first contact in vacuum: (vapour kg/s, head descent m/h while sublimating, choked exit speed m/s,
    terminal expansion speed m/s)."""
    q = 185.0 * (T_TRIPLE - T_SURF) + 7.037 / 2 * (T_TRIPLE ** 2 - T_SURF ** 2) + L_SUB
    m = eta * p_kw * 1000 / q
    v_head = m / (RHO_ICE * math.pi * (d / 2) ** 2) * 3600
    a = math.sqrt(GAMMA_H2O * R_H2O * T_TRIPLE)
    v_max = math.sqrt(2 * GAMMA_H2O / (GAMMA_H2O - 1) * R_H2O * T_TRIPLE)
    return m, v_head, a, v_max


def jet_s0(p_kw):
    """The grain lobe's scattering coefficient σs = S0 · cos²θ / r² (1/m, r in m from the vent): returns S0."""
    m, _, _, v = vacuum_start(p_kw)
    return JET_CONDENSE * m / v * 3 / (2 * math.pi) * 3 / (4 * JET_GRAIN_R * RHO_ICE)


def hg(theta_deg, g=JET_G):
    """Henyey–Greenstein phase function, 4π-normalised (1 = isotropic)."""
    return (1 - g * g) / (1 + g * g - 2 * g * math.cos(math.radians(theta_deg))) ** 1.5


def jet_seen(p_kw, h, f_plain, theta_deg):
    """Optical depth across the grain lobe h m above the vent (a line through its axis: ∫ S0 h²/r⁴ dx = S0 π / 2h),
    and its brightness in Jupiter-light against the lit plain's (f_plain: the plain's share of the facing
    irradiance), seen theta_deg from forward scatter."""
    tau = jet_s0(p_kw) * math.pi / (2 * h)
    return tau, tau * hg(theta_deg) / 4 / (A_PLAIN * f_plain)


def flash(t_c=0.0):
    """Liquid water at t_c °C meeting vacuum: the share that boils away to freeze the rest (to ice at 0 °C)."""
    return (C_WATER * t_c + L_ICE) / (L_VAP + L_ICE)


def ballistic(v, el_deg):
    """A grain thrown at v m/s, el_deg up, in Europa's gravity: (apex m, time to apex s, flight s, range m)."""
    g = g_at()
    vz, vh = v * math.sin(math.radians(el_deg)), v * math.cos(math.radians(el_deg))
    return vz * vz / (2 * g), vz / g, 2 * vz / g, vh * 2 * vz / g


def ganymede_pos(dlt):
    """Ganymede (km, Europa frame) when Io is dlt rad from conjunction. Laplace 1:2:4 (λIo − 3λEu + 2λGa = 180°)
    ties it to Io: Ganymede's angle from Europa (ahead +) is −90° − dlt/2, on the transits that put it in the sky
    (the other branch, +90° − dlt/2, alternates with it: Ganymede below the horizon)."""
    g = -math.pi / 2 - dlt / 2
    return (A_EU - A_GA * math.cos(g), -A_GA * math.sin(g), 0.0)


def ganymede_seen(dlt, elong, fr):
    """(local unit vector, diameter deg, lit fraction) of Ganymede from the site."""
    p = ganymede_pos(dlt)
    v, d = _norm(from_site(p, fr))
    s = sun_dir(elong)
    lit = (1 + sum(a * -b for a, b in zip(s, _norm(p)[0]))) / 2
    return to_local(v, fr), 2 * deg(math.asin(R_GA / d)), lit


# ---------------------------------------------------------------- 04 · the fall of the Sun (Sprint 3.4)
SUN_RATE = 360.0 / P_SYN      # deg/h: the Sun's elongation falls (east → Jupiter)
STAR_RATE = 360.0 / P_ORB_EU  # deg/h: the stars about Europa's pole
DAWN_03 = 1.18                # h after Io set: 03's sky (s03_probe --after); 04 opens on it
# 04 (film picks, the clip's timing): real time at 0 s (cut from 03); the log-rate eases up over `up` s to r0, holds,
# eases (smoothstep, from `t0` s) down to a steady ingress rate ri at first contact (`contact` s), holds it so the
# Sun's bead shrinks evenly, and eases to real time over the last `tail` s before second contact (`gone` s). fit04
# solves ri (the ingress fits contact → gone) and r0 (03's dawn → first contact fits 0 → contact).
SHOT04 = dict(dur=18.0, up=1.5, t0=6.0, contact=10.0, gone=13.5, tail=1.0)
# Lightning on Jupiter's night side. Galileo SSI: optical energy per flash up to 1.6e10 J (several terrestrial
# superbolts), spots 45–80 km HWHM (light diffused through the clouds; Little et al. 1999, Icarus 142). Juno SRU:
# 1e5–1e8 J, pulses 5.4 ms apart by tens of ms, like in-cloud lightning on Earth (Becker et al. 2020, Nature 584;
# Kolmašová et al. 2023, Nat. Comm. 14). From Europa only the large ones show: the shot uses Galileo's range.
FLASH_E = (1.0e9, 1.6e10)     # J, optical
FLASH_HWHM = (45.0, 80.0)     # km
M_SUN_1AU = -26.74            # V
# The solar corona (K+F), Baumbach (1937): radiance / the disc centre's = 1e-6 Σ a·r^-n, r in solar radii. Its surface
# brightness doesn't depend on distance: from Europa it is as bright as at an eclipse on Earth, 5.2× smaller.
CORONA = ((0.0532, 2.5), (1.425, 7.0), (2.565, 17.0))
LIMB_DARK = 0.8               # the Sun's mean disc radiance / its centre's (V)


def sun_limb_sep(elong, dec=0.0):
    """Angular distance (deg) of the Sun's centre outside Jupiter's limb (< 0: behind it), along the line from
    Jupiter's centre, using the oblate disc's radius at the Sun's position angle."""
    u, _, r_eq, r_pol, ax = jupiter_local()
    s = sun_local(elong, dec)
    z = tuple(a - _dot(ax, u) * b for a, b in zip(ax, u))              # north on the disc
    y = _cross(u, z)
    phi = math.atan2(_dot(s, z), _dot(s, y))
    r = r_eq * r_pol / math.hypot(r_pol * math.cos(phi), r_eq * math.sin(phi))
    return deg(math.acos(max(-1.0, min(1.0, _dot(s, u))))) - r


def sun_visible(elong):
    """Fraction of the Sun's disc not hidden by Jupiter (the limb is straight across a 0.1° Sun)."""
    x = max(-1.0, min(1.0, sun_limb_sep(elong) / R_SUN_DEG))
    return 1 - (math.acos(x) - x * math.sqrt(1 - x * x)) / math.pi


def _elong_at_sep(sep):
    lo, hi = 0.0, 40.0
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if sun_limb_sep(m) < sep else (lo, m)
    return lo


def _ss(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def _rate04(s, L, Li):
    """04: time rate (real s per clip s) at clip second s for log peak rate L and log ingress rate Li."""
    c = SHOT04
    d1, d2 = _ss(c['t0'], c['contact'], s), _ss(c['gone'] - c['tail'], c['gone'], s)
    return math.exp(L * _ss(0.0, c['up'], s) * (1.0 - d1) + Li * d1 * (1.0 - d2))


def _int04(a, b, L, Li, n=600):
    h = (b - a) / n
    return h / 3 * sum((1 if i in (0, n) else 4 if i % 2 else 2) * _rate04(a + i * h, L, Li) for i in range(n + 1))


_FIT04 = {}


def _bisect(f, target, lo=0.0, hi=20.0):
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) < target else (lo, m)
    return (lo + hi) / 2


def fit04():
    """04: solve the log ingress rate Li (first → second contact in contact → gone s) and the log peak rate L (03's
    dawn → first contact in 0 → contact s); cached. Returns dict L, Li, r0, ri, e0 (03's dawn), e1, e2 (first,
    second contact), pre and cover (real s)."""
    if not _FIT04:
        c, fr = SHOT04, site(*SITE[1:])
        d = lapse(fr, LAPSE_E_END[1], 0.0)['dur']
        e0 = lapse(fr, LAPSE_E_END[1], d + DAWN_03)['elong']
        e1, e2 = _elong_at_sep(R_SUN_DEG), _elong_at_sep(-R_SUN_DEG)
        pre, cover = (e0 - e1) / SUN_RATE * 3600, (e1 - e2) / SUN_RATE * 3600
        Li = _bisect(lambda x: _int04(c['contact'], c['gone'], 0.0, x), cover)
        L = _bisect(lambda x: _int04(0.0, c['contact'], x, Li), pre)
        _FIT04.update(L=L, Li=Li, r0=math.exp(L), ri=math.exp(Li), e0=e0, e1=e1, e2=e2, pre=pre, cover=cover)
    return _FIT04


def lapse04(s):
    """04: clip second → real seconds since first contact (< 0 before it)."""
    f, c = fit04(), SHOT04
    return _int04(c['contact'], s, f['L'], f['Li'], n=max(40, 2 * int(abs(s - c['contact']) * 60)))


def rate04(s):
    f = fit04()
    return _rate04(s, f['L'], f['Li'])


def lapse04_elong(s):
    """04: the Sun's elongation (deg) at clip second s."""
    return fit04()['e1'] - lapse04(s) / 3600 * SUN_RATE


# 05 (film picks, Sprint 3.5, user 2026-10-05): the first relay puck is dropped just under the regolith (30 m), then
# one every CRYO_PUCK_KM. The camera stays in the ice with the puck while the probe sinks away. Real time at 0 s (the
# puck has just left the probe's open top); the log-rate eases up over up0 → up1 s to a steady rate r, held to the
# end (06's time-lapse takes over); fit05 solves r so that the freezing front (it trails the probe by refreeze's
# open column) comes down onto the puck's top at `shut` s.
CRYO_PUCK_FIRST = 0.03        # km, puck 1 (film pick: below the cracked regolith, where the tether is still short)
SHOT05 = dict(dur=10.0, up0=0.5, up1=3.0, shut=5.0)
_FIT05 = {}


def _rate05(s, L):
    c = SHOT05
    return math.exp(L * _ss(c['up0'], c['up1'], s))


def _int05(a, b, L, n=None):
    n = n or max(40, 2 * int(abs(b - a) * 60))
    h = (b - a) / n
    return h / 3 * sum((1 if i in (0, n) else 4 if i % 2 else 2) * _rate05(a + i * h, L) for i in range(n + 1))


def fit05():
    """05: the puck's drop at CRYO_PUCK_FIRST. Returns v (m/s, 10 kW), hrs/prof (refreeze), open_m (open column above
    the probe's top), z0 (puck bottom, m above the nose, seated in the open top), d_shut (m the probe sinks until the
    front reaches the puck's top), t_shut (real s), L, r (steady rate), end (real s at the clip's end), d_end (m)."""
    if not _FIT05:
        c, z = SHOT05, CRYO_PUCK_FIRST
        v = cryo_speed(CRYO_P[2], ICE_H[1], z)
        hrs, prof = refreeze(z, ICE_H[1])
        open_m = hrs * 3600 * v
        z0 = CRYO_LEN - 0.015 - CRYO_PUCK[1]
        d_shut = CRYO_LEN + open_m - (z0 + CRYO_PUCK[1])
        L = _bisect(lambda x: _int05(0.0, c['shut'], x), d_shut / v)
        end = _int05(0.0, c['dur'], L)
        _FIT05.update(v=v, hrs=hrs, prof=prof, open_m=open_m, z0=z0, d_shut=d_shut, t_shut=d_shut / v, L=L,
                      r=math.exp(L), end=end, d_end=end * v)
    return _FIT05


def lapse05(s):
    """05: clip second → real seconds since the puck left the probe."""
    return _int05(0.0, s, fit05()['L'])


def counter05(s):
    """05's clock (tools/overlay.mjs): hours since the puck's drop, the probe's nose depth (m)."""
    sec = lapse05(s)
    return sec / 3600, CRYO_PUCK_FIRST * 1000 + fit05()['v'] * sec


def corona(r):
    """Corona radiance relative to the Sun's mean disc radiance at r solar radii (Baumbach)."""
    return 1e-6 * sum(a * r ** -n for a, n in CORONA) / LIMB_DARK


def flash_seen(e_j, shutter_s=0.5 / 24, d_km=None):
    """A lightning flash of optical energy e_j (J) near the disc centre, Lambertian from the cloud tops, all inside
    one frame's shutter: (fluence J/m², mean irradiance over the shutter W/m², V magnitude, × the Sun's irradiance)."""
    d = (d_km or jupiter_local()[1]) * 1000.0
    flu = e_j / (math.pi * d * d)
    irr = flu / shutter_s
    m_sun = M_SUN_1AU + 5 * math.log10(AU_J)
    return flu, irr, m_sun - 2.5 * math.log10(irr / E_SUN), irr / E_SUN


def ocean(h_ice, d=OCEAN_D):
    """Pressure (bar) at the ice base and the sea floor, and the Earth-ocean depth (m) of the same pressure.
    g taken constant at its surface value (a dense core keeps it near-flat through the outer 120 km)."""
    g = g_at()
    p1 = RHO_ICE * g * h_ice * 1000
    p2 = p1 + RHO_SEA * g * d * 1000
    vol = 4 / 3 * math.pi * ((R_EU - h_ice) ** 3 - (R_EU - h_ice - d) ** 3)
    return p1 / 1e5, p2 / 1e5, p2 / (RHO_SEA * 9.81), vol


def card(h_ice=ICE_H[1]):
    """The numbers on the 09 title card (tools/card.mjs reads `python3 tools/physics.py --card`)."""
    p_base, p_floor, _, vol = ocean(h_ice)
    return {'oceans': round(vol / EARTH_OCEAN_KM3, 1), 'ocean_km': round(OCEAN_D), 'ice_km': round(h_ice),
            'base_bar': round(p_base), 'floor_bar': round(p_floor), 'lethal_h': round(LD50_SV / DOSE_SV_DAY * 24)}


if __name__ == '__main__' and '--card' in sys.argv:
    print(json.dumps(card()))
elif __name__ == '__main__':
    rows = []
    d_sub = A_EU - R_EU
    rj, rjp = jupiter_r_deg()
    dj = 2 * rj
    rows.append(('Jupiter angular diameter (sub-Jupiter point)', f'{dj:.2f}° equatorial, {2 * rjp:.2f}° polar; '
                 f'{dj / 0.52:.0f}× the Moon from Earth (Io: 19.6°)'))
    lib = deg(2 * E_EU)
    rows.append(('Jupiter wobble (eccentricity libration)', f'±{lib:.2f}° east–west and ±{100 * E_EU:.1f} % in size over '
                 f'{P_ORB_EU:.1f} h: {lib * 2 * math.pi / P_ORB_EU:.3f}°/h at most → "never moves" holds for any shot'))
    for th in (30, 60, 70, 75, 80):
        e = jupiter_elev(th)
        rows.append((f'Jupiter centre elevation, {th}° from sub-Jupiter point', f'{e:.1f}° (lower limb {e - rj:.1f}°)'))
    for name, lat, lon_w in (('Conamara Chaos', 9.7, 273.7), ('Pwyll crater', -25.2, 271.4)):
        th = deg(math.acos(math.cos(math.radians(lat)) * math.cos(math.radians(lon_w))))
        e = jupiter_elev(th)
        rows.append((f'{name} ({lat:+.1f}°, {lon_w:.1f}° W)', f'{th:.1f}° from sub-Jupiter point: Jupiter centre {e:.1f}°, '
                     f'lower limb {e - rj:.1f}° ({"partly below the horizon, for ever" if e - rj < 0 < e else "clear"})'))
    rows.append(('Sun', f'{2 * R_SUN_DEG:.3f}° wide; {E_SUN:.1f} W/m² = 1/{AU_J ** 2:.1f} of Earth'))
    e_js = jupiter_shine(180)
    rows.append(('Full-Jupiter shine (facing it)', f'{e_js:.2f} W/m² = {100 * e_js / E_SUN:.2f} % of sunlight '
                 f'({math.log2(E_SUN / e_js):.1f} stops down), ≈ {e_js / (S_EARTH * 2.0e-6):.0f}× full moonlight; '
                 f'{100 * (A_IO - 1821.6) ** 2 / d_sub ** 2:.0f} % of Io\'s'))
    rows.append(('Day (Sun to Sun) = eclipse period', f'{P_SYN:.2f} h = {P_SYN / 24:.2f} d; Sun and stars {360 / P_SYN:.2f}°/h'))
    rows.append(('Eclipse', f'{2 * R_J / V_EU / 3600:.2f} h ({2 * R_J:,} km shadow at {V_EU:.2f} km/s)'))
    rows.append(('Jupiter rotation seen from Europa', f'{P_ROT_J_EU:.2f} h'))
    rows.append(('Surface gravity', f'{g_at():.3f} m/s² = {g_at() / 9.81:.3f} g'))
    rows.append(('Horizon distance, eye 2 m', f'{math.sqrt(2 * R_EU * 0.002) * 1000:,.0f} m'))
    # neighbours
    tr_h, tr_rate, io_d = io_transit()
    d_far = A_EU + A_IO
    rows.append(('Io from Europa', f'{io_d:.2f}° at conjunction ({A_EU - A_IO:,} km, {io_d / 0.52:.1f}× the Moon), '
                 f'{2 * deg(math.asin(R_IO / d_far)):.2f}° at its farthest; conjunction every {P_SYN_IO_EU:.1f} h'))
    rows.append(('Io transits Jupiter', f'every conjunction (orbits near-coplanar); {tr_h:.2f} h on the disc, '
                 f'{tr_rate:.2f}°/h; Io {io_d / dj * 100:.1f} % of Jupiter\'s width'))
    for E in (180, 170, 150, 120, 90):
        io_o, sh_o, vis, io_dd, ph = io_shadow(E)
        rows.append((f'Io shadow transit, Sun elongation {E}°', f'Jupiter {100 * (1 - math.cos(math.radians(E))) / 2:.0f} % '
                     f'lit; shadow {sh_o:.2f}° from disc centre ({"visible" if vis else "far side"}); Io {io_o:.2f}° from '
                     f'centre ({"on the disc" if io_o < rj else "off the disc"}), {io_dd:.2f}° wide, {100 * ph:.0f} % lit'))
    rows.append(('Ganymede from Europa', f'{2 * deg(math.asin(R_GA / (A_GA - A_EU))):.2f}° at its nearest '
                 f'(opposite Jupiter in the sky: it never crosses the disc)'))
    v, t = plume(PLUME_H)
    rows.append((f'Plume {PLUME_H:.0f} km (tentative)', f'vent {v * 1000:.0f} m/s, flight {t / 60:.1f} min (ballistic); '
                 f'a {PLUME_H:.0f} km top at 500 km: {hidden(500):.0f} km hidden'))
    for h in ICE_H:
        p1, p2, z, vol = ocean(h)
        rows.append((f'Ice {h:.0f} km + ocean {OCEAN_D:.0f} km', f'ice base {p1:,.0f} bar, sea floor {p2:,.0f} bar '
                     f'(= {z / 1000:.1f} km down in Earth\'s sea; Mariana 10.9 km); ocean {vol / EARTH_OCEAN_KM3:.1f}× Earth\'s'))
    for lens in (24, 35, 50, 85, 135):
        rows.append((f'{lens} mm (hfov {2 * deg(math.atan(18 / lens)):.1f}°)',
                     f'Jupiter ≈ {px_across(dj, lens):.0f} px, Io (conjunction) ≈ {px_across(io_d, lens):.0f} px of 1920'))

    # ------------------------------------------------ Conamara's local sky
    name, lat, lon_w = SITE
    fr = site(lat, lon_w)
    jc = from_site((A_EU, 0, 0), fr)
    j_el, j_az = altaz(jc, fr)
    rows.append((f'{name}: Jupiter', f'azimuth {j_az:.1f}° (west), centre {j_el:.2f}° up; north pole '
                 f'{sky_angle((0, 0, 1), jc, fr):+.0f}° from straight up (+ = toward north, right when facing west): '
                 f'axis near horizontal, bands near vertical'))
    rows.append((f'{name}: Jupiter\'s clouds', f'the near face turns {sky_angle((0, -1, 0), jc, fr):+.0f}° from '
                 f'straight up (±180 = down): the bands roll down into the horizon, one turn per {P_ROT_J_EU:.2f} h'))
    ev, rj_s = sun_track(fr, 0.0)
    t_of = lambda e: (180 - e) / 360 * P_SYN                 # hours after full Jupiter
    for E in (180, ev['sunrise'][0], 150, 120, 90, 60, 30):
        s = sun_dir(E)
        el, az = altaz(s, fr)
        rows.append((f'{name}: Sun at elongation {E:.1f}°', f't = {t_of(E):5.1f} h after full Jupiter; Sun {el:+.1f}° '
                     f'(az {az:.0f}°); Jupiter {100 * (1 - math.cos(math.radians(E))) / 2:.0f} % lit'))
    west = _norm((jc[0] - _dot(jc, fr[0]) * fr[0][0], jc[1] - _dot(jc, fr[0]) * fr[0][1],
                  jc[2] - _dot(jc, fr[0]) * fr[0][2]))[0]
    f_h, f_w = disc_light(jc, rj_s, fr[0], fr), disc_light(jc, rj_s, west, fr)
    rows.append((f'{name}: full-Jupiter light', f'flat ice {e_js * f_h * 1000:.1f} mW/m² ({100 * f_h:.1f} % of facing), '
                 f'a wall facing Jupiter {e_js * f_w * 1000:.0f} mW/m² ({100 * f_w:.0f} %): the ground is '
                 f'{f_w / f_h:.0f}× darker than the faces turned to Jupiter (the disc partly below the horizon)'))
    for dec in (-DEC_SUN, 0.0, DEC_SUN):
        ev, _ = sun_track(fr, dec)
        fc, sc = ev.get('first contact'), ev.get('second contact')
        tc = ev.get('third contact')
        if fc and sc:
            ingress = (fc[0] - sc[0]) / 360 * P_SYN * 60
            rows.append((f'{name}: sunset, Sun dec {dec:+.1f}°', f'the Sun sinks into Jupiter: first contact at '
                         f'{fc[1]:.2f}° up (t = {t_of(fc[0]):.1f} h), gone at {sc[1]:.2f}° up after {ingress:.0f} min; '
                         f'would reappear at {tc[1]:+.2f}° → '
                         f'{"never seen setting: sunset = eclipse" if tc[1] < 0 else "comes back out, then sets"}; '
                         f'sunrise at t = {t_of(ev["sunrise"][0]):.1f} h'))
    day_h = (ev['sunrise'][0] - ev['second contact'][0]) / 360 * P_SYN
    rows.append((f'{name}: day and night', f'Sun up {day_h:.1f} h (full Jupiter → wanes → half at noon, Sun near the '
                 f'zenith → crescent → eclipse), down {P_SYN - day_h:.1f} h (Jupiter black → waxes → full at dawn)'))
    ent, end, mv = io_track(fr)
    rows.append((f'{name}: Io\'s transit', f'enters the disc at {ent[0]:.1f}° up, moves {mv:+.0f}° from straight up '
                 f'(±180 = down), {end[1]} after {(end[0] - ent[1]) / W_IO_EU:.2f} h'))
    de = (360 * (1 - P_SYN_IO_EU / P_SYN)) % 360
    cyc = 360 / de * P_SYN_IO_EU / 24
    sr = ev['sunrise'][0]
    for pct in (90, 97):
        e_lo = deg(math.acos(1 - 2 * pct / 100))             # lit ≥ pct while |E| ≥ e_lo; dark sky while E > sunrise
        win = (360 - e_lo) - sr
        rows.append((f'{name}: Io transit, Jupiter ≥ {pct} % lit, Sun down', f'transits drift {de:.2f}° of Sun '
                     f'elongation per conjunction: {win / de:.0f} transits in a row (≈ {win / de * P_SYN_IO_EU / 24:.0f} d), '
                     f'once every {cyc:.0f} d'))
    for sgn, tag in ((1, 'behind Europa (−90°)'), (-1, 'ahead (+90°)')):
        g = from_site((A_EU, sgn * A_GA, 0), fr)
        el, az = altaz(g, fr)
        s = sun_dir(190)
        lit = (1 + math.cos(math.radians(_ang(s, tuple(-x for x in g))))) / 2
        rows.append((f'{name}: Ganymede during Io\'s transit, {tag}', f'{el:+.1f}° up (az {az:.0f}°), '
                     f'{2 * deg(math.asin(R_GA / _norm(g)[1])):.2f}° wide, {100 * lit:.0f} % lit at elongation 190°; '
                     f'Laplace 1:2:4 alternates the two cases transit by transit'))
    off, um, pen, on = own_shadow(176.5)
    rows.append((f'{name}: Europa\'s own shadow on Jupiter', f'at the anti-solar point: on the disc while the Sun is '
                 f'within {rj_s:.1f}° of the point opposite Jupiter (≈ {2 * rj_s / 360 * P_SYN:.1f} h, = the eclipse), '
                 f'most of it in the last hours of the night (Sun down while E > {sr:.1f}°); umbra {um:.2f}° in a '
                 f'{pen:.2f}° penumbra (135 mm: {px_across(um, 135):.0f} / {px_across(pen, 135):.0f} px)'))
    for E in (178.0, 180.0):
        r = io_cast_shadow(E, (ent[1] + end[0]) / 2, fr)
        if r:
            el, az = altaz(r[1], fr)
            rows.append((f'{name}: Io\'s shadow, mid-transit, Sun {E:.0f}°', f'{r[2]:.2f}° from Io '
                         f'(shadow at {el:.1f}° up): Io and its own black dot on the bands'))
    for e_end in LAPSE_E_END:
        a = lapse(fr, e_end, 0.0)
        b = lapse(fr, e_end, a['dur'])
        sh = []
        for s in (a, b):
            r = io_cast_shadow(s['elong'], s['dlt'], fr)
            sh.append(f'{r[2]:.2f}°' if r else 'off the disc')
        rows.append((f'{name}: 02 time-lapse, Io sets with the Sun at {e_end:.0f}°',
                     f'{b["dur"]:.2f} h: Sun {a["elong"]:+.1f}° → {b["elong"]:+.1f}° ('
                     f'{altaz(sun_dir(a["elong"]), fr)[0]:+.1f}° → {altaz(sun_dir(b["elong"]), fr)[0]:+.1f}° up), '
                     f'Jupiter spins {b["spin"]:.1f}°, stars turn {b["turn"]:.2f}°; Io\'s shadow {sh[0]} → {sh[1]} '
                     f'from Io; Europa\'s shadow {own_shadow(a["elong"])[0]:.1f}° → {own_shadow(b["elong"])[0]:.1f}° '
                     f'from the centre'))
        sp = eclipse_span(fr, e_end)
        if sp:
            rho, um, pen = europa_on_io(lapse(fr, e_end, sp[1])['elong'], lapse(fr, e_end, sp[1])['dlt'])
            rows.append((f'{name}: 02, Europa\'s shadow on Io (Sun {e_end:.0f}° at setting)',
                         f'penumbra on Io from {sp[0]:+.2f} h to {sp[2]:+.2f} h ({(sp[2] - sp[0]) * 60:.0f} min; transit '
                         f'{b["dur"]:.2f} h), deepest at {sp[1]:+.2f} h, {rho:.0f} km off centre: umbra r {um:.0f} km, '
                         f'penumbra {pen:.0f} km on Io\'s {R_IO:.0f} (umbra covers {100 * (um / R_IO) ** 2:.0f} % of '
                         f'the disc we see; Sun dec 0 = Jupiter\'s equinox season, Europa near its node)'))
    # 03: the probe starts (Sprint 3.3), on the night of 02's transit (Sun 179° at Io's setting)
    m, vh, a, vm = vacuum_start(CRYO_P[2])
    rows.append((f'03: cryobot {CRYO_P[2]:g} kW starts in vacuum', f'sublimates {m * 1000:.1f} g/s of ice (head '
                 f'{vh:.2f} m/h, {cryo_speed(CRYO_P[2], ICE_H[1], 0) * 3600 / vh:.1f}× slower than melting); vapour '
                 f'choked at ~{P_TRIPLE:.0f} Pa leaves at {a:.0f} m/s, expands to ≤ {vm:.0f} m/s'))
    for hh, th in ((0.1, 20.0), (0.3, 20.0), (1.0, 20.0), (0.3, 60.0)):
        tau, rel = jet_seen(CRYO_P[2], hh, f_h, th)
        rows.append((f'03: the grain lobe {hh:g} m above the vent, {th:g}° from forward', f'τ {tau:.1e} across; in '
                     f'Jupiter-light {rel:.3f}× the lit plain ({math.log2(max(rel, 1e-9)):+.1f} stops; '
                     f'{100 * JET_CONDENSE:.0f} % condensed, {JET_GRAIN_R * 1e6:g} µm, HG g {JET_G}; '
                     f'S0 {jet_s0(CRYO_P[2]):.2e})'))
    ap, tu, tf, rg = ballistic(a, 90.0)
    rows.append(('03: grains at the exit speed, straight up', f'apex {ap / 1000:.0f} km after {tu / 60:.1f} min '
                 f'(they leave the frame in milliseconds: the lobe is steady)'))
    rows.append(('03: loose frost blown out (film picks)', f'{FROST_N} flakes {FROST_SIZE[0] * 1e3:g}–'
                 f'{FROST_SIZE[1] * 1e3:g} mm from {FROST_RING[0]}–{FROST_RING[1]} m round the nose, '
                 f'{FROST_V[0]}–{FROST_V[1]} m/s at {FROST_EL[0]:g}–{FROST_EL[1]:g}° up, burst e-fold {FROST_TAU} s; '
                 f'fastest: apex {ballistic(FROST_V[1], FROST_EL[1])[0]:.1f} m, '
                 f'{ballistic(FROST_V[1], FROST_EL[1])[2]:.1f} s in flight'))
    # momentum check: the flakes (frost ~300 kg/m³, ellipsoids 1 × 0.7 × 0.3 of their size) vs the vapour's thrust
    k = (0.7 * 0.3 * math.pi / 6) * 300.0
    s3 = (FROST_SIZE[1] ** 3 - FROST_SIZE[0] ** 3) / (3 * math.log(FROST_SIZE[1] / FROST_SIZE[0]))   # <size³>, log-uniform
    vbar = FROST_V[0] + (FROST_V[1] - FROST_V[0]) / (FROST_V_POW + 1)
    mf = FROST_N * k * s3
    rows.append(('03: frost momentum vs vapour thrust', f'flakes {mf * 1000:.0f} g, ≈ {mf * vbar:.2f} N·s at a mean '
                 f'{vbar:.1f} m/s; the vapour carries {m * a:.2f} N ({m * a * 4 * FROST_TAU:.2f} N·s over the burst): '
                 f'{100 * mf * vbar / (m * a * 4 * FROST_TAU):.0f} % of it'))
    for v, el in ((1.0, 60.0), (3.0, 60.0), (5.0, 75.0)):
        ap, tu, tf, rg = ballistic(v, el)
        rows.append((f'03: an ice chip thrown {v:g} m/s, {el:g}° up', f'apex {ap:.2f} m after {tu:.1f} s, lands '
                     f'{rg:.1f} m away after {tf:.1f} s (Earth: {v * v * math.sin(math.radians(el)) ** 2 / 19.62:.2f} m, '
                     f'{2 * v * math.sin(math.radians(el)) / 9.81:.2f} s)'))
    rows.append(('03: liquid water meeting vacuum', f'boils and freezes at once: {100 * flash(0):.1f} % boils away '
                 f'at 0 °C ({100 * flash(20):.1f} % at 20 °C), the rest freezes'))
    ent, end, _ = io_track(fr)
    for tag, dl, E in (('Io sets (02 end)', end[0], LAPSE_E_END[1]),
                       ('1 h later', end[0] + W_IO_EU, LAPSE_E_END[1] - 360 / P_SYN)):
        u, dd, lit = ganymede_seen(dl, E, fr)
        el, az = alt_az(u)
        rows.append((f'03: Ganymede, {tag}', f'{el:.1f}° up, {az:+.1f}° from Jupiter (local), {dd:.3f}° wide, '
                     f'{100 * lit:.0f} % lit; {px_across(dd, 35):.1f} px at 35 mm, {px_across(dd, 135):.0f} px at 135'))
    f4, c4 = fit04(), SHOT04
    el = lambda e: alt_az(sun_local(e))
    noon = max((el(e)[0], e) for e in [f4['e0'] - 0.5 * i for i in range(int(f4['e0'] / 0.5))])
    rows.append(('04: the day, 03\'s dawn → first contact', f'{f4["pre"] / 3600:.1f} h: Sun {f4["e0"]:.1f}° → '
                 f'{f4["e1"]:.2f}° elongation ({el(f4["e0"])[0]:+.1f}° up, az {el(f4["e0"])[1]:+.0f}° → '
                 f'{el(f4["e1"])[0]:.2f}° up, az {el(f4["e1"])[1]:+.1f}°); highest {noon[0]:.1f}° at {noon[1]:.0f}°; '
                 f'Jupiter {100 * lit_fraction(f4["e0"]):.1f} % → {100 * lit_fraction(f4["e1"]):.2f} % lit; '
                 f'Jupiter spins {f4["pre"] / 3600 / P_ROT_J_EU:.1f} turns'))
    rows.append(('04: ingress (first → second contact)', f'{f4["cover"]:.0f} s real; gone {el(f4["e2"])[0]:.2f}° up'))
    rows.append(('04: clock (fit04)', f'real time at 0 s → ×{f4["r0"]:,.0f} by {c4["up"]} s (Sun {SUN_RATE * f4["r0"] / 3600:.0f}°/s, '
                 f'Jupiter a turn every {P_ROT_J_EU * 3600 / f4["r0"]:.1f} s) → eases from {c4["t0"]} s to ×{f4["ri"]:.0f} at '
                 f'first contact ({c4["contact"]} s), holds (the bead shrinks evenly) → real time at second contact '
                 f'({c4["gone"]} s); {c4["dur"] - c4["gone"]:.1f} s of night in real time'))
    for e_j in (1e8, FLASH_E[0], FLASH_E[1]):
        flu, irr, mag, rel = flash_seen(e_j)
        rows.append((f'04: lightning {e_j:.0e} J seen from Europa', f'{flu:.1e} J/m²; in one 1/48 s shutter '
                     f'{irr:.1e} W/m² = {rel:.1e}× the Sun, V {mag:+.1f} (Sirius −1.5); spot '
                     f'{2 * FLASH_HWHM[0]:.0f}–{2 * FLASH_HWHM[1]:.0f} km = '
                     f'{px_across(deg(2 * FLASH_HWHM[0] / jupiter_local()[1]), 50):.1f}–'
                     f'{px_across(deg(2 * FLASH_HWHM[1] / jupiter_local()[1]), 50):.1f} px at 50 mm: a point'))
    b_sun = E_SUN / (math.pi * math.sin(math.radians(R_SUN_DEG)) ** 2)
    rows.append(('04: the solar corona over the limb (Baumbach)', ', '.join(f'{r:g} R☉ {b_sun * corona(r):.3g}'
                 for r in (1.05, 1.5, 2, 3, 5)) + f' W/m²/sr (the Sun\'s disc {b_sun:.2e}; sunlit ice ≈ 10); 1 R☉ = '
                 f'{R_SUN_DEG:.3f}° = {px_across(R_SUN_DEG, 50):.1f} px at 50 mm; the Sun\'s centre is '
                 f'{-sun_limb_sep(fit04()["e2"]):.3f}° behind the limb at second contact, '
                 f'{-sun_limb_sep(lapse04_elong(SHOT04["dur"])):.3f}° at the clip\'s end'))
    rows.append(('Radiation at the surface', f'{DOSE_SV_DAY} Sv/day: a ~50 %-lethal dose ({LD50_SV} Sv) in '
                 f'{LD50_SV / DOSE_SV_DAY * 24:.0f} h'))
    # ------------------------------------------------ down
    h = ICE_H[1]
    for z in (0, 1, 5, 10, 15, 19.9):
        t, tb = shell_T(z, h)
        rows.append((f'Ice {h:.0f} km, {z:g} km down', f'{t:.0f} K ({t - 273.15:+.0f} °C), {RHO_ICE * g_at() * z * 1e3 / 1e5:.0f} bar'))
    rows.append(('Ice base (melting point under the shell)', f'{tb:.2f} K = {tb - 273.15:+.2f} °C pure '
                 f'(salt lowers it further)'))
    for p in CRYO_P:
        days, v0, v1 = cryobot(p, h)
        rows.append((f'Cryobot {p:g} kW, Ø {CRYO_D} m, {100 * CRYO_ETA:.0f} % into the ice', f'{days:,.0f} days '
                     f'({days / 365.25:.1f} y) to {h:.0f} km; {v0:.2f} m/h at the top, {v1:.2f} m/h at the base; '
                     f'the hole refreezes behind it'))
    npk = int(h / CRYO_PUCK_KM)
    rows.append(('Cryobot layout (nose up)', ' · '.join(f'{n} {l:.2f}' for n, l in CRYO_SECTIONS)
                 + f' m = {sum(l for _, l in CRYO_SECTIONS):.2f} m; {npk} pucks every {CRYO_PUCK_KM:g} km '
                 f'({npk * CRYO_PUCK[1]:.2f} m of magazine); {SWIM_N} swimmers ⚠ concept'))
    rgb = water_rgb()
    rows.append(('Pure water absorption, render R / G / B', ' / '.join(f'{a:.4f}' for a in rgb) + ' per m (e-fold '
                 + ' / '.join(f'{1 / a:.0f}' for a in rgb) + f' m); particles {SEA_SCATTER}/m, g {SEA_G} (film pick); '
                 f'lamp {CRYO_LAMP_W:.0f} W'))
    irgb = ice_rgb()
    rows.append(('Pure ice absorption, render R / G / B', ' / '.join(f'{a:.4f}' for a in irgb) + ' per m (e-fold '
                 + ' / '.join(f'{1 / a:.0f}' for a in irgb) + f' m; Warren & Brandt 2008); n ice {N_ICE}, water '
                 f'{N_WATER}: relative {N_WATER / N_ICE:.3f}'))
    for z in (0.02, 0.1, 0.5, 1, 3, 10):
        phi, s, lt = pore(z)
        rows.append((f'Shell ice {z:g} km down: pores', f'φ {phi:.2g}, σs {s:.3g}/m (g {PORE_G}), transport length '
                     f'{lt:.3g} m{"; cracked lid" if z < BRITTLE_KM else "; healed: only refrozen veins"}'))
    for z in (0.02, 1, 5, 10, 15, 19.5):
        t, tb = shell_T(z, h)
        v = cryo_speed(CRYO_P[2], h, z) * 3600
        hrs, _ = refreeze(z, h)
        rows.append((f'Hole refreezes, {z:g} km down ({t:.0f} K)', f'shut {hrs:.2g} h behind the probe = '
                     f'≈ {hrs * v:.2g} m above it at ~{v:.2f} m/h (10 kW; walls not pre-warmed: lower bound)'))
    f5, c5 = fit05(), SHOT05
    gap = (CRYO_D - CRYO_PUCK[0]) / 2
    rows.append((f'05: puck 1 dropped {CRYO_PUCK_FIRST * 1000:g} m down (film pick)', f'the probe sinks '
                 f'{f5["v"] * 3600:.3f} m/h; the column stays open {f5["hrs"]:.2f} h = {f5["open_m"]:.2f} m above its '
                 f'top; the front reaches the puck\'s top after the probe has sunk {f5["d_shut"]:.2f} m = '
                 f'{f5["t_shut"] / 3600:.2f} h; a {gap * 1000:.0f} mm ring of '
                 f'water round the puck itself shuts sooner (~{(gap / (CRYO_D / 2)) ** 2 * f5["hrs"] * 60:.0f} '
                 f'min by a²: invisible in milky ice)'))
    rows.append(('05: clock (fit05)', f'real time at 0 s → ×{f5["r"]:,.0f} by {c5["up1"]} s (eased from {c5["up0"]} s), '
                 f'held; the front meets the puck at {c5["shut"]} s; {f5["end"] / 3600:.2f} h by {c5["dur"]:g} s: the probe '
                 f'{f5["d_end"]:.2f} m below where it dropped the puck ({CRYO_PUCK_FIRST * 1000 + f5["d_end"]:.1f} m down)'))
    rows.append(('Lamp in pure water (e-fold distance)', ', '.join(f'{wl} nm {1 / a:.0f} m' for wl, a in A_WATER.items())
                 + ': red gone within metres, blue reaches ~100 m (before 1/r²)'))
    rows.append(('Ice base: current, scallops, terraces', f'current {OCEAN_U * 100:g} cm/s (film pick) → melt scallops '
                 f'{scallop_len():.1f} m long (Curl Re 22,500; {scallop_len(0.01):.1f} m at 1 cm/s, '
                 f'{scallop_len(0.1):.2f} m at 10 cm/s); terraces: risers {BASE_RISER[0]}–{BASE_RISER[1]} m at '
                 f'{BASE_RISER_DEG:.0f}°, treads {BASE_TREAD[0]:g}–{BASE_TREAD[1]:g} m (Icefin, Thwaites)'))
    alb, mfp = base_ice()
    rows.append(('Ice base seen from the water (σs\' {:g}/m)'.format(BASE_SIGMA_P), 'diffuse albedo R / G / B '
                 + ' / '.join(f'{x:.2f}' for x in alb) + ', mean free path ' + ' / '.join(f'{x:.2f}' for x in mfp)
                 + f' m; surface reflectance ice→water {((N_WATER - N_ICE) / (N_WATER + N_ICE)) ** 2:.1e} '
                 '(head-on: no mirror, the light comes from inside the ice)'))
    ve, vt = rise_speed(), rise_speed(g=9.81, rho=1000.0)
    rows.append((f'⚠ Frazil disc Ø {FRAZIL_D * 1e3:g} mm × {FRAZIL_T * 1e3:g} mm rising', f'{ve * 1e3:.1f} mm/s on '
                 f'Europa (same formula in an Earth river: {vt * 1e3:.1f} mm/s; measured ~10 mm/s at 2 mm, Gosink & '
                 f'Osterkamp 1983): in a 14 s shot it rises '
                 f'{ve * 14 * 100:.1f} cm while the current carries it {OCEAN_U * 14 * 100:.0f} cm sideways; '
                 f'{FRAZIL_PER_M3:,.0f}/m³ (film pick); disc reflectance at grazing only (relative index '
                 f'{N_ICE / N_WATER:.3f})'))
    for d in (10, 20, 40, 80, 150, 250):
        ls = lamp_seen(d)
        rows.append((f'Lamp seen from {d} m', 'R / G / B transmission ' + ' / '.join(f'{t:.2g}' for t, _ in ls)
                     + ', vs 5 m ' + ' / '.join(f'{e:+.1f}' for _, e in ls) + ' EV'))
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f'| {a:<{w}} | {b} |')
