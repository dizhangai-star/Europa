"""Measure / derive texture data from the shared asset library (system python3 with PIL + numpy + scipy).
Copied from Io (Sprint 0.3); `jupiter` shared as is, Io's `io` / `far` replaced by `europa` / `colour` in 0.4.

    python3 tools/maps.py jupiter    the Jupiter map's mean linear luminance and Great Red Spot position
                                     (the constants at the top of blender/lib/jupiter.py)
    python3 tools/maps.py europa     the site (physics.SITE, Conamara) cut out of the USGS 500 m Europa mosaic
                                     (greyscale) and reprojected to the film's local frame (physics: +X right of
                                     Jupiter ≈ north, +Y toward Jupiter = image top, site at the centre):
                                     blender/textures/src/europa_site_500m.png (512 km across) and
                                     europa_wide_1km.png (2048 km, Pwyll and its rays in frame: the orientation check),
                                     + the site's albedo numbers
    python3 tools/maps.py colour     Europa's natural colour, the mosaic having none: clusters of PIA19048 (Galileo,
                                     reprocessed to approximate the eye) → linear colours of the clean ice, the
                                     reddish-brown non-ice material and the darkest lineae; the Conamara colour
                                     close-ups (PIA26446 / 01127 / 01296) are enhanced, so they only say *where*
                                     the brown sits (on the chaos matrix and ridges; blue-white = Pwyll's ray frost)
    python3 tools/maps.py io_globe   Io's colour mosaic as a 2048×1024 globe map for Io's disc (02)

Blender never reads the 100–200 MB source files pixel by pixel: it loads the map as a texture and uses these numbers.
"""
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
FILM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.expanduser('~/dev/workspace/claude/videos/_assets/textures')
JUP = os.path.join(ASSETS, 'jupiter/jupiter_map_css_plus_juno_bj.png')
EU = os.path.join(ASSETS, 'europa/Europa_Voyager_GalileoSSI_global_mosaic_500m.tif')
GAL = os.path.join(ASSETS, 'europa/galileo')
IO_MAP = os.path.join(ASSETS, 'io/Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_1km.tif')
PREV = os.path.expanduser('~/dev/workspace/claude/videos/_assets/previews')
SRC = os.path.join(FILM, 'blender/textures/src')
sys.path.insert(0, os.path.join(FILM, 'tools'))
import physics as P

PWYLL = (-25.2, 271.4)          # lat, W longitude: the young rayed crater ~1,000 km south of Conamara


def lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def jupiter():
    im = Image.open(JUP).convert('RGB')
    W, H = im.size
    small = np.asarray(im.resize((W // 8, H // 8), Image.BOX)).astype(np.float64) / 255
    lum = float((lin(small) * [0.2126, 0.7152, 0.0722]).sum(-1).mean())
    red = small[..., 0] - 0.5 * (small[..., 1] + small[..., 2])
    h = small.shape[0]
    band = ndimage.uniform_filter(red[int(h * 0.55):int(h * 0.68)], 9)
    y, x = np.unravel_index(band.argmax(), band.shape)
    u, v = x / small.shape[1], 1 - (y + int(h * 0.55)) / h
    print(f'{os.path.basename(JUP)}: {W}×{H}; mean linear luminance {lum:.4f}; GRS at u {u:.4f}, v {v:.4f} '
          f'(lat {180 * v - 90:.1f}°)')


def _georef(im):
    """(lon0 east, lat0, dlon, dlat) of pixel (0, 0)'s corner and the pixel size in degrees, from the GeoTIFF tags
    (simple cylindrical in metres on the tag's sphere, x measured from the projection's centre longitude)."""
    tags = im.tag_v2
    sx, sy = tags[33550][:2]
    x0, y0 = tags[33922][3:5]
    dbl = tags.get(34736, ())
    R = dbl[5] if len(dbl) > 5 else P.R_EU * 1000.0                # semi-major axis (m)
    keys = tags.get(34735, ())
    lon_c = 0.0
    for i in range(4, len(keys), 4):                                # ProjCenterLong / ProjNatOriginLong
        if keys[i] in (3088, 3080) and keys[i + 1] == 34736:
            lon_c = dbl[keys[i + 3]]
    k = 180.0 / (math.pi * R)
    return lon_c + x0 * k, y0 * k, sx * k, -sy * k, R / 1000.0       # rows run south


def _local_grid(size, km_px):
    """Europa-frame unit vectors of a size² grid around the site, image top = +Y (toward Jupiter), right = +X."""
    right, fwd, up = (np.array(a) for a in P._local_axes())
    half = size * km_px / 2
    xs = (np.arange(size) + 0.5) * km_px - half
    ys = half - (np.arange(size) + 0.5) * km_px
    X, Y = np.meshgrid(xs, ys)
    rho = np.hypot(X, Y) + 1e-9
    phi = rho / P.R_EU
    d = (X[..., None] * right + Y[..., None] * fwd) / rho[..., None]
    return np.cos(phi)[..., None] * up + np.sin(phi)[..., None] * d


def _sample(a, geo, p):
    lon0, lat0, dlon, dlat = geo[:4]
    lat = np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1)))
    lon = np.degrees(np.arctan2(p[..., 1], p[..., 0]))              # east longitude
    col = np.mod((lon - lon0) / dlon, a.shape[1])
    row = (lat - lat0) / dlat
    return ndimage.map_coordinates(a, [row - 0.5, col - 0.5], order=1, mode='nearest')


def _local_km(lat, lon_w):
    """(x, y) km of a surface point in the site's local frame, along the ground (azimuthal equidistant)."""
    right, fwd, up = (np.array(a) for a in P._local_axes())
    la, lo = math.radians(lat), math.radians(360 - lon_w)
    v = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
    phi = math.acos(np.clip(v @ up, -1, 1))
    t = v - (v @ up) * up
    t /= np.linalg.norm(t)
    return P.R_EU * phi * (t @ right), P.R_EU * phi * (t @ fwd)


def europa():
    im = Image.open(EU)
    geo = _georef(im)
    off, scl = -0.0029527571, 0.0059055141                          # GDAL metadata: DN → normalised reflectance
    print(f'{os.path.basename(EU)}: {im.size} {im.mode}; corner lon {geo[0]:.2f}° E lat {geo[1]:.2f}°, '
          f'{geo[2] * 1000 / 360 * 2 * math.pi * geo[4]:.1f} m/px on R {geo[4]:.2f} km')
    a = np.asarray(im).astype(np.float32)
    os.makedirs(PREV, exist_ok=True)
    prev = os.path.join(PREV, 'europa-usgs-mosaic-500m.jpg')
    if not os.path.exists(prev):
        Image.fromarray(a[::8, ::8].astype(np.uint8)).save(prev, quality=85)
    os.makedirs(SRC, exist_ok=True)
    for name, size, km_px in (('europa_site_500m.png', 1024, 0.5), ('europa_wide_1km.png', 2048, 1.0)):
        out = _sample(a, geo, _local_grid(size, km_px))
        Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(os.path.join(SRC, name))
        print(f'→ blender/textures/src/{name}: {size} px, {km_px} km/px ({size * km_px:.0f} km), top = toward '
              f'Jupiter, right = +X')
        if size == 1024:
            c = out[512 - 100:512 + 100, 512 - 100:512 + 100]
            print(f'  site ±50 km: DN mean {c.mean():.1f}, sd {c.std():.1f} → normalised reflectance '
                  f'{c.mean() * scl + off:.3f} (p5 {np.percentile(c, 5) * scl + off:.3f}, '
                  f'p95 {np.percentile(c, 95) * scl + off:.3f})')
            dead = (out == 0).mean()
            print(f'  no-data (DN 0) {dead * 100:.2f} %')
    x, y = _local_km(*PWYLL)
    print(f'Pwyll in the local frame: x {x:+.0f} km, y {y:+.0f} km → europa_wide_1km.png pixel '
          f'({1024 + x:.0f}, {1024 - y:.0f}); its rays should radiate from there')


def colour(k=5):
    a = np.asarray(Image.open(os.path.join(GAL, 'PIA19048.png')).convert('RGB')).astype(np.float64) / 255
    L = lin(a).reshape(-1, 3)
    L = L[L.mean(1) > 0.12]                                          # the lit disc away from the terminator
    rng = np.random.default_rng(0)
    pts = L[rng.choice(len(L), 40000, replace=False)]
    ch = pts / pts.sum(1, keepdims=True)
    cen = ch[rng.choice(len(ch), k, replace=False)]
    for _ in range(40):
        lab = np.argmin(((ch[:, None] - cen[None]) ** 2).sum(-1), 1)
        cen = np.array([ch[lab == j].mean(0) if (lab == j).any() else cen[j] for j in range(k)])
    share = np.bincount(lab, minlength=k) / len(lab)
    ref = pts[lab == np.argmin(np.abs(cen - 1 / 3).sum(1))].mean(0)
    print(f'PIA19048 (natural colour), lit disc, {len(L)} px; linear colour per chroma cluster, '
          f'relative to the greyest cluster (= albedo-free tint):')
    for j in np.argsort(cen[:, 0] - cen[:, 2]):
        m = pts[lab == j].mean(0)
        r3 = lambda v, n: tuple(round(float(x), n) for x in v)
        print(f'  {share[j] * 100:5.1f} %  linear {r3(m, 4)}  tint {r3(m / m.max(), 3)}  '
              f'brightness vs grey {m.mean() / ref.mean():.2f}')


def io_globe(w=2048):
    """Io's whole colour mosaic (USGS Galileo SSI + Voyager, 1 km) as a small equirectangular map for Io's disc in
    02 (≈ 105 px at 135 mm): column 0 = 0° E, east to the right (atan2(y, x) of the body frame, +X toward Jupiter),
    top = north → blender/textures/src/io_globe_2k.png, + its mean linear luminance (lib/moons.py's albedo gain)."""
    src = Image.open(IO_MAP)
    lon0 = _georef(src)[0]
    im = src.convert('RGB')
    a = np.asarray(im.resize((w, w // 2), Image.BOX))
    a = np.roll(a, -int(round((0.0 - lon0) / 360.0 * w)), axis=1)    # left edge lon0 (−180 E) → 0 E
    dst = os.path.join(SRC, 'io_globe_2k.png')
    Image.fromarray(a).save(dst)
    lum = float((lin(a.astype(np.float64) / 255) * [0.2126, 0.7152, 0.0722]).sum(-1).mean())
    print(f'{os.path.basename(dst)}: {w}×{w // 2}, left edge 0° E; mean linear luminance {lum:.4f}')


if __name__ == '__main__':
    {'jupiter': jupiter, 'europa': europa, 'colour': colour, 'io_globe': io_globe}[sys.argv[1]]()
