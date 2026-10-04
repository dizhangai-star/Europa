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
R_SUN, AU = 696_000, 149_597_870
EARTH_OCEAN_KM3 = 1.335e9

# Interior (published ranges, not measurements: Galileo gravity + magnetometer). Shell and ocean picked for the film.
ICE_H = (10.0, 20.0, 30.0)  # km, ice shell thickness (estimates ~3–30+; 20 = middle of the common range)
OCEAN_D = 100.0             # km, ocean depth (estimates ~60–150)
RHO_ICE, RHO_SEA = 920.0, 1030.0                             # kg/m³
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


def c_ice(T):
    return 185.0 + 7.037 * T                                 # J/kg/K (Fukusako 1990)


def shell_T(z, h_ice):
    """Conductive-lid temperature (K) at depth z (km) of an h_ice km shell (k ∝ 1/T → exponential profile)."""
    tb = 273.15 + DTM_DP * RHO_ICE * g_at() * h_ice * 1000 / 1e5
    return T_SURF * (tb / T_SURF) ** (z / h_ice), tb


def cryobot(p_kw, h_ice, d=CRYO_D, eta=CRYO_ETA):
    """Days to melt through h_ice km at p_kw thermal; speed (m/h) at the top and at the base."""
    a = math.pi * (d / 2) ** 2

    def rate(z):                                             # m/s at depth z km
        t, tb = shell_T(z, h_ice)
        q = 185.0 * (tb - t) + 7.037 / 2 * (tb ** 2 - t ** 2) + L_ICE
        return eta * p_kw * 1000 / (RHO_ICE * a * q)
    n, sec = 2000, 0.0
    for i in range(n):
        sec += h_ice * 1000 / n / rate((i + 0.5) * h_ice / n)
    return sec / 86400, rate(0) * 3600, rate(h_ice * 0.999) * 3600


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
                     f'lower limb {e - rj:.1f}° ({"half below the horizon, for ever" if e - rj < 0 < e else "clear"})'))
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
                 f'{f_w / f_h:.0f}× darker than the faces turned to Jupiter (half the disc is below the horizon)'))
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
    rows.append(('Lamp in pure water (e-fold distance)', ', '.join(f'{wl} nm {1 / a:.0f} m' for wl, a in A_WATER.items())
                 + ': red gone within metres, blue reaches ~100 m (before 1/r²)'))
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f'| {a:<{w}} | {b} |')
