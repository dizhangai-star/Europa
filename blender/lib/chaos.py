"""Conamara chaos ground, spike version (Sprint 1 look_horizon, factored out 2026-10-05 for the 01 framing test).
Sprint 2's ground build replaces it in europa_world (ragged horizon, ridges, PIA01403 pattern).

Local frame (physics.py): +Y toward Jupiter along the ground, +X right of it, Z up; azimuth 0 = Jupiter, + = right.
Plates: convex ice polygons (physics.CHAOS sizes) with ragged cliffs, talus aprons, tilted ridged tops, in a
hummocky matrix; a lane toward Jupiter (|az| < `lane_deg`) stays open; the camera stands on a low knoll at the origin.
"""
import math

import numpy as np

from . import europa_world as W


def plates(C, seed=7, n=26, rmin=120.0, rmax=6000.0, lane_deg=9.0, lane_r=7000.0, extra=()):
    """Random plate layout (same draw order as Sprint 1's look_horizon). `extra`: hand-placed plates, dicts with
    c=(x, y), R, h and optional keys (n sides, rot, tilt_deg, tdir_deg, ridge_deg, gap)."""
    rng = np.random.default_rng(int(seed))
    out = []
    for e in extra:
        out.append(_plate(rng, C, e['c'], e['R'], e.get('h', C['plate_h'][1]), e))
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
                        tdir=(math.cos(t), math.sin(t)), rdir=math.radians(35.0 + rng.uniform(-25, 25)),
                        gap=rng.uniform(*C['ridge_gap'])))
    return out


def _plate(rng, C, c, R, h, e):
    n_ = int(e.get('n', 6))
    rot = math.radians(e.get('rot', 0.0))
    phi = rot + np.arange(n_) * 2 * math.pi / n_
    t = math.radians(e.get('tdir_deg', 0.0))
    return dict(c=tuple(c), R=R, h=h, nrm=np.stack([np.cos(phi), np.sin(phi)], 1), p=np.full(n_, R),
                tilt=math.tan(math.radians(e.get('tilt_deg', 1.0))), tdir=(math.cos(t), math.sin(t)),
                rdir=math.radians(e.get('ridge_deg', 35.0)), gap=e.get('gap', 300.0))


def height_fn(C, pl, knoll=6.0):
    def height(X, Y):
        r, az = np.hypot(X, Y), np.degrees(np.arctan2(X, Y))
        lane = 1.0 - 0.6 * W.smooth(25.0, 8.0, np.abs(az)) * W.smooth(60.0, 250.0, r)    # lower swells toward Jupiter
        Z = lane * C['matrix_h'] * (W.fbm(X / 260, Y / 260, 5, 11) - 0.45)
        Z = Z + knoll * np.exp(-(r / 120.0) ** 2)                  # the camera stands on a low knoll
        Z = Z + 0.8 * C['matrix_h'] * np.maximum(W.fbm(X / 45, Y / 45, 4, 12) - 0.55, 0.0)      # knobs
        for k, p in enumerate(pl):
            cx, cy = p['c']
            reach = 1.25 * p['R'] + 2.0 * p['h']
            m = (np.abs(X - cx) < reach) & (np.abs(Y - cy) < reach)
            if not m.any():
                continue
            x, y = X[m] - cx, Y[m] - cy
            d = np.min(p['p'][None, :] - (x[:, None] * p['nrm'][None, :, 0] + y[:, None] * p['nrm'][None, :, 1]), 1)
            d = d + 0.06 * p['R'] * (W.fbm(X[m] / 70, Y[m] / 70, 4, 20 + k) - 0.5)            # ragged cliff line
            h, w = p['h'], 0.35 * p['h']
            u = x * math.cos(p['rdir']) + y * math.sin(p['rdir'])
            ridge = C['ridge_h'] * (1 - np.abs(np.sin(math.pi * u / p['gap']))) ** 6
            top = h + p['tilt'] * (x * p['tdir'][0] + y * p['tdir'][1]) + ridge \
                + 4.0 * (W.fbm(X[m] / 90, Y[m] / 90, 4, 40 + k) - 0.5)
            cliff = W.smooth(0.0, w, d)
            talus = 0.3 * h * W.smooth(-1.6 * h, 0.0, d) * (1 - cliff)
            Z[m] = np.maximum(Z[m], top * cliff + talus)
        return Z
    return height
