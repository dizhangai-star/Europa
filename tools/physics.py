"""Europa: every number the shots rely on, from constants. `python3 tools/physics.py` → the table for TREATMENT.md.

Adapted from ../Io/tools/physics.py (same conventions). km, h, degrees unless named. Europa is tidally locked:
Jupiter hangs at a fixed point in its sky (it rocks ±`libration` over one orbit, from the 0.009 eccentricity); the
Sun goes round once per synodic day. Jupiter's phase seen from Europa = the Sun's angle from Jupiter in its sky.
Io, the inner neighbour, passes in front of Jupiter once per Io–Europa synodic period (Ganymede, outside, never can).
"""
import math

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


def ocean(h_ice, d=OCEAN_D):
    """Pressure (bar) at the ice base and the sea floor, and the Earth-ocean depth (m) of the same pressure.
    g taken constant at its surface value (a dense core keeps it near-flat through the outer 120 km)."""
    g = g_at()
    p1 = RHO_ICE * g * h_ice * 1000
    p2 = p1 + RHO_SEA * g * d * 1000
    vol = 4 / 3 * math.pi * ((R_EU - h_ice) ** 3 - (R_EU - h_ice - d) ** 3)
    return p1 / 1e5, p2 / 1e5, p2 / (RHO_SEA * 9.81), vol


if __name__ == '__main__':
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
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f'| {a:<{w}} | {b} |')
