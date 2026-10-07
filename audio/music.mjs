// Europa · 深渊's soundtrack, synthesized (user 2026-10-07: synth only, no ice/hydrophone recordings; the breaths and
// the heartbeat are Io's CC0 recordings from the shared library), cut to the film layout of tools/timeline.mjs.
// Engine copied from ../Io/audio/music.mjs (svf, syn, breath, takes, the helmet). The arc follows the physics
// (user 2026-10-07): on the surface there is no air, so nothing outside the helmet is heard; from the moment the
// camera goes into the ice, the ice itself carries sound, and in the ocean the water does.
//   head + 01  a breath before the picture; the sub drone (A) under the turn; a catch as the disc swings in, a shaky
//              release; the pad opens on Io's first chord (Am9) as the pan lands on EUROPA
//   02         Io enters: Io's diamond-ring glints, quoted; the pad dims while Europa's shadow crosses Io; Io's resolve
//              chord (A add9) under "IO. WE STOOD THERE.", a sigh; Esus4 from Io's set, waiting through the dawn
//   03         the frost burst glitters (shimmer) and a breath catches; the pad climbs with the tilt; Ganymede one high
//              glint; the whip a riser into the cut
//   04         near-silence: the drone and a thin pad through the time-lapse day, a high tone climbing to first
//              contact, where all music stops dead; a held breath; one heartbeat as the red arch comes up; a few
//              faint stars; one last breath out; the tilt into the ice: a sub swell from below (D)
//   05         in the ice: the probe's hum, muffled; the ice cracks (recorded lake ice) and settles;
//              a dark Dm pad; the front shuts over the puck: one deep struck note, the hum sealed off
//   06         the descent: a crackle as dense as the time-lapse until the brittle lid ends (3 km), then the silence of
//              warm ductile ice; a glass tick at 100 m, 1 km, 10 km (the counter's decades); the pad steps down
//   07         under the ice the water hushes; the break: a recorded crack slowed into a boom, the rush; the chord opens wide (D5), the
//              minor third under the caption; the tether brake groans to the stop
//   08         the brake lets go (a clank); the hum recedes at 1/r as the probe falls; a far boom from the ceiling;
//              everything thins with the light and is gone when it is
//   09         one held note under the title (D: a fifth under Io's A)
// Times: physical events from `python3 tools/physics.py --sound` (clip seconds), directed cues from each clip's `sfx`
// ([t, kind, {v, …}], clip seconds; t < 0 = before the cut).
// Usage: node audio/music.mjs → audio/build/film.wav (48 kHz stereo, the film's exact length, peak −1 dBFS);
// compile.mjs calls it and sets the loudness. Balance check: BUS=1 node audio/music.mjs (music | sfx | ice | title dB
// per 0.5 s).
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { rel } from '../../../_kit/lib/film.mjs';
import { rng, voices, freeverb, hpf, level, writeWav, hz, panG } from '../../../_kit/audio/dsp.mjs';
import { layout } from '../tools/timeline.mjs';

const SR = 48000, F = layout(), END = F.total, N = Math.ceil(END * SR);
const bus = () => [new Float32Array(N), new Float32Array(N)];
const MUS = bus(), SFX = bus(), ICE = bus(), TTL = bus();     // music (hall) · breath + heart (helmet) · ice/water · title
const { rnd, jit } = rng(20261007);
const V = voices({ sr: SR, n: N, rnd, music: MUS, sfx: SFX });
const { noise, glide, partials } = V;
const P = JSON.parse(execFileSync('python3', [rel('tools/physics.py'), '--sound'], { encoding: 'utf8' }));
const at = (n) => F.clips.find((c) => c.id.startsWith(n)).start;
const [t1, t2, t3, t4, t5, t6, t7, t8, t9] = ['01', '02', '03', '04', '05', '06', '07', '08', '09'].map(at);
const contact = t4 + P['04'].contact, tilt = t4 + P['04'].tilt, shut = t5 + P['05'].shut;
const lid = t6 + P['06'].marks['3000'], brk = t7 + P['07'].break, gone = t8 + P['08'].gone, blue = t8 + P['08'].blue;
const S = (t) => Math.max(0, Math.min(N, Math.floor(t * SR)));
const c01 = (x) => Math.min(1, Math.max(0, x));
const sm = (a, b, x) => { const u = c01((x - a) / (b - a)); return u * u * (3 - 2 * u); };
const lerp = (pts, t) => {                                   // piecewise-linear [[t, y], …]
  if (t <= pts[0][0]) return pts[0][1];
  for (let k = 1; k < pts.length; k++) if (t <= pts[k][0]) {
    const [a, ya] = pts[k - 1], [b, yb] = pts[k]; return ya + (yb - ya) * (t - a) / (b - a);
  }
  return pts.at(-1)[1];
};

// ---------- voices (svf / syn / breath / takes as in Io's music.mjs) ----------
function svf() {
  let lp = 0, bp = 0; const o = { lp: 0, bp: 0, hp: 0 };
  return (x, fc, q = 0.7) => {
    const f = 2 * Math.sin(Math.PI * Math.min(fc, 7000) / SR);
    lp += f * bp; const hp = x - lp - q * bp; bp += f * hp;
    o.lp = lp; o.bp = bp; o.hp = hp; return o;
  };
}
const blep = (p, dt) => p < dt ? (p /= dt, p + p - p * p - 1) : p > 1 - dt ? (p = (p - 1) / dt, p * p + p + p + 1) : 0;
// Subtractive voice: n detuned PolyBLEP saws (or sines) → low-pass whose cutoff follows the envelope (c0 → c1).
function syn(b, t, d, m, v, pan, o = {}) {
  const rl = o.rel ?? 0.4, s0 = Math.floor(t * SR), n = Math.min(Math.ceil((d + rl * 3) * SR), N - s0);
  if (n <= 0 || s0 < 0) return;
  const nv = o.n ?? 3, det = o.det ?? 8, f0 = hz(m), sine = o.wave === 'sine';
  const ph = Array.from({ length: nv }, () => rnd()), fr = Array.from({ length: nv }, (_, i) => nv === 1 ? 1 : 2 ** (det * (i / (nv - 1) * 2 - 1) / 1200));
  const [gl, gr] = panG(pan), [bl, br] = b, atk = Math.max(1, (o.atk ?? 0.05) * SR), dn = d * SR, flt = svf();
  const c0 = o.c0 ?? 400, c1 = o.c1 ?? 2400, q = o.q ?? 0.8, vph = rnd() * 6.28;
  for (let i = 0; i < n; i++) {
    const u = i / dn;
    const e = (i < atk ? (o.curve ? (i / atk) ** o.curve : i / atk) : 1) * (i > dn ? Math.exp(-(i - dn) / (rl * SR)) : 1);
    const r = 2 ** ((o.vib ?? 0) * Math.min(1, u * 2) * Math.sin(2 * Math.PI * 5 * i / SR + vph) / 1200);
    let x = 0;
    for (let k = 0; k < nv; k++) {
      const dt = f0 * fr[k] * r / SR; ph[k] += dt; if (ph[k] >= 1) ph[k] -= 1;
      x += sine ? Math.sin(2 * Math.PI * ph[k]) : 2 * ph[k] - 1 - blep(ph[k], dt);
    }
    x /= nv;
    const y = sine ? x : flt(x, c0 + (c1 - c0) * e, q).lp;
    bl[s0 + i] += y * e * v * gl; br[s0 + i] += y * e * v * gr;
  }
}
const chord = (b, t, d, notes, v, o = {}) => notes.forEach((m, i) =>
  syn(b, t, d, m, v, (i / Math.max(1, notes.length - 1) - 0.5) * (o.spread ?? 0.7), { n: 3, det: 7, atk: 1.2, rel: 1.0, c0: 220, c1: 1000, q: 0.7, ...o }));
// The synth breath (Io's), only a fallback when a recording is missing.
function breath(t, kind, o = {}) {
  const IN = kind === 'in', d = o.d ?? (IN ? 1.1 : 1.8), s0 = S(t), n = Math.min(Math.ceil(d * SR), N - s0);
  if (n <= 0) return;
  const FM = IN ? [[720, 1, 0.16], [1300, 0.65, 0.14], [2650, 0.4, 0.12], [3900, 0.22, 0.12]]
    : [[620, 1, 0.18], [1150, 0.5, 0.16], [2450, 0.25, 0.14], [3500, 0.12, 0.14]];
  const fl = FM.map(() => svf()), jf = FM.map(() => 1 + jit(0.06)), dk = svf();
  const atk = Math.min(0.9, (o.atk ?? (IN ? 0.12 : 0.06)) / d), far = o.far ?? 0;
  const g = 0.075 * (o.v ?? 1) * (1 - 0.6 * far), [gl, gr] = panG(jit(0.05));
  let p0 = 0, p1 = 0;
  for (let i = 0; i < n; i++) {
    const u = i / n, w = rnd() * 2 - 1;
    const e = IN ? sm(0, atk, u) * (0.75 + 0.25 * u) * (1 - sm(0.8, 1, u)) : sm(0, atk, u) * (1 - u) ** 1.5;
    p0 = 0.985 * p0 + 0.015 * w; p1 = 0.7 * p1 + 0.3 * w;
    let y = 0;
    FM.forEach(([f, a, q], k) => { y += a * q * fl[k](p0 * 4 + p1 * 0.6, f * jf[k], q).bp; });
    y = dk(y, 7000 * (1 - 0.75 * far), 0.7).lp;
    SFX[0][s0 + i] += y * e * g * gl; SFX[1][s0 + i] += y * e * g * gr;
  }
}
// Recorded breaths + heartbeat (CC0 Freesound, `../../_assets/audio/breath`, REFERENCES.md): Io's takes, cut at the
// breath's soft edges, high-passed (mic pops < 150 Hz), denoised, faded, levelled to one RMS.
const LIB = rel('../../_assets/audio/breath');
const SRC = { mlitty: '387620__mlitty__slow-breath-relax.mp3', drew: '682884__drewsimko__shaky_breaths.wav',
  heart: '332819__loudernoises__heartbeat-80bpm-limited.wav' };
const TAKES = {
  headIn: ['mlitty', 0.85, 2.60], headOut: ['mlitty', 3.95, 5.90],
  catch: ['mlitty', 65.70, 66.35],     // a small, quick intake
  shaky: ['drew', 0.85, 3.10],         // out, a hitch, a trailing out
  armIn: ['mlitty', 39.15, 41.30], armOut: ['mlitty', 68.10, 70.10],
  holdIn: ['mlitty', 7.55, 9.30],
  sigh: ['mlitty', 101.90, 104.30],
  farIn: ['mlitty', 46.90, 48.70], farOut: ['mlitty', 49.95, 52.00],
  heart: ['heart', 2.985, 3.70, { af: 'highpass=f=25', rms: 0.0112 }],
};
const cache = {};
function take(name) {
  if (name in cache) return cache[name];
  const [src, a, b, o = {}] = TAKES[name], f = `${LIB}/${SRC[src]}`;
  if (!fs.existsSync(f)) return (cache[name] = null);
  const d = b - a, raw = execFileSync('ffmpeg', ['-v', 'error', '-ss', String(a), '-t', d.toFixed(3), '-i', f, '-ac', '1', '-ar', String(SR),
    '-af', `${o.af ?? 'highpass=f=180,highpass=f=180,afftdn=nr=10:nf=-60,afade=t=in:d=0.06'},afade=t=out:st=${(d - 0.18).toFixed(3)}:d=0.18`,
    '-f', 'f32le', '-'], { maxBuffer: 1 << 28 });
  const x = new Float32Array(raw.buffer, raw.byteOffset, raw.length / 4), w = Math.round(0.2 * SR);
  let pk = 0;
  for (let i = 0; i + w <= x.length; i += w / 4) { let s = 0; for (let k = i; k < i + w; k++) s += x[k] * x[k]; pk = Math.max(pk, s / w); }
  return (cache[name] = x.map((v) => v * (o.rms ?? 0.0063) / Math.sqrt(pk || 1)));
}
function recorded(t, name, o) {
  const x = take(name); if (!x) return false;
  const far = o.far ?? 0, g = (o.v ?? 1) * (1 - 0.6 * far), [gl, gr] = panG(jit(0.05)), s0 = S(t), dk = svf();
  for (let i = 0; i < x.length && s0 + i < N; i++) {
    const y = far ? dk(x[i], 7000 * (1 - 0.75 * far), 0.7).lp : x[i];
    SFX[0][s0 + i] += y * g * gl; SFX[1][s0 + i] += y * g * gr;
  }
  return true;
}
// A glass tick (Io's hour tick): a struck partial set + a click.
function tick(t, m, v, pan, b = MUS) {
  const f = hz(m);
  partials(t, [[f, v, 0.32], [f * 2.76, v * 0.22, 0.07], [f * 5.4, v * 0.08, 0.025]], pan, 1.6, b, 0.002);
  noise(t, 0.006, v * 0.12, pan, b, { bp: 5200, q: 1.5 });
}

// ---------- the ice and the water (new for Europa) ----------
// Cracks (user 2026-10-07: the synth "pew" chirps read as 80s/90s electronics): recorded lake-ice cracks, Andrew5DMII
// "Frozen Lake Ice and Water Sounds" (Freesound 146419, CC-BY 3.0, microphones lowered through a hole in the ice; shared
// library, REFERENCES.md). Mono, 17.7 s: ~20 sharp cracks (10–40 ms) on a low rumble; its low "booms" are 16–22 Hz
// pressure thumps (nothing above 150 Hz: unusable). Onsets measured 2026-10-07 (high band > 2 kHz, ≥ 20 dB over the
// floor). A take = 5 ms before the onset to 0.3 s, high-passed at 120 Hz (the rumble), faded from 0.1 s, levelled to
// one peak (loudest 10 ms RMS). Size → playback rate (slower = bigger and lower: a bigger plate rings lower); a big
// one adds a copy at ×0.3 for its body. Without the file, the synth crack below.
const ICE_SRC = rel('../../_assets/audio/ice/146419__andrew5dmii__frozen-lake-ice-and-water-sounds-shotgun-ice-cracking.wav');
const ICE_ON = [1.530, 2.142, 4.312, 4.690, 5.836, 5.942, 6.260, 6.353, 6.502, 6.816, 7.178, 7.261, 7.369, 7.428,
  7.504, 7.910, 8.234, 8.570, 8.995, 9.491, 11.044, 11.308, 15.629, 15.964];
const ICE_BIG = [6.353, 7.428, 11.308, 7.178, 5.942];         // the strongest (−34 … −43 dB in the high band)
let iceBuf;
function iceRaw() {
  if (iceBuf !== undefined) return iceBuf;
  if (!fs.existsSync(ICE_SRC)) return (iceBuf = null);
  const raw = execFileSync('ffmpeg', ['-v', 'error', '-i', ICE_SRC, '-ac', '1', '-ar', String(SR), '-af', 'highpass=f=120,highpass=f=120',
    '-f', 'f32le', '-'], { maxBuffer: 1 << 28 });
  return (iceBuf = new Float32Array(raw.buffer, raw.byteOffset, raw.length / 4));
}
const iceCache = {};
function iceTake(on) {                                         // the levelled slice at its own speed
  if (iceCache[on]) return iceCache[on];
  const x = iceRaw(), a = Math.round((on - 0.005) * SR), n = Math.round(0.305 * SR), y = new Float32Array(n);
  for (let i = 0; i < n; i++) y[i] = (x[a + i] ?? 0) * Math.min(1, i / (0.002 * SR)) * (i < 0.1 * SR ? 1 : Math.exp(-(i - 0.1 * SR) / (0.05 * SR)));
  const w = Math.round(0.01 * SR); let pk = 0;
  for (let i = 0; i + w <= n; i += w / 2) { let e = 0; for (let k = i; k < i + w; k++) e += y[k] * y[k]; pk = Math.max(pk, e / w); }
  return (iceCache[on] = y.map((v) => v * 0.25 / Math.sqrt(pk || 1)));
}
function playIce(t, on, rate, v, pan, b = ICE) {               // linear-interpolated at `rate` (< 1: slower, lower)
  const y = iceTake(on), n = Math.floor((y.length - 1) / rate), s0 = S(t), [gl, gr] = panG(pan), [bl, br] = b;
  for (let i = 0; i < n && s0 + i < N; i++) {
    const u = i * rate, k = Math.floor(u), z = (y[k] + (y[k + 1] - y[k]) * (u - k)) * v;
    bl[s0 + i] += z * gl; br[s0 + i] += z * gr;
  }
}
const pick = (a) => a[Math.floor(rnd() * a.length)];
function crack(t, v, pan, size = 0.5, b = ICE) {
  if (!iceRaw()) return synthCrack(t, v, pan, size, b);
  playIce(t, pick(size > 0.6 ? ICE_BIG : ICE_ON), (1.15 - 0.7 * size) * (1 + jit(0.08)), v, pan, b);
  if (size > 0.6) {
    playIce(t + 0.004, pick(ICE_BIG), 0.3, v * 0.9 * size, pan * 0.5, b);
    noise(t + 0.01, 1.4 + 1.5 * size, v * 0.6 * size, pan * 0.3, b, { bp: 90, q: 0.7, lp: 160, dec: 0.5 + 0.5 * size });
  }
}
// A cluster of small cracks over d s (the ice settling; replaces the synth creak in 05 and 07).
const cluster = (t, d, k, v, size = 0.3) => { for (let i = 0; i < k; i++) crack(t + d * rnd(), v * (0.4 + 0.6 * rnd()), jit(0.6), size * (0.5 + rnd())); };
// The synth crack (fallback only): a snap, then the dispersive "pew" of singing lake ice (group speed ∝ √f, so the
// pitch falls as 1/t²); big ones end in a low boom. size 0..1.
function synthCrack(t, v, pan, size = 0.5, b = ICE) {
  const d = 0.25 + 0.9 * size, f0 = 2400 + 1400 * rnd(), f1 = 260 - 140 * size, t0 = d / (Math.sqrt(f0 / f1) - 1);
  noise(t, 0.02 + 0.03 * size, v * 0.55, pan, b, { bp: 1800 + 1500 * rnd(), q: 0.5, dec: 0.004 + 0.01 * size });
  for (let k = 0; k < 3; k++) {
    const dl = k * 0.012 * (1 + rnd()), g = v * [0.22, 0.12, 0.07][k];
    glide(t + dl, d, g, (u) => f0 * (1 + 0.05 * k) * (t0 / (t0 + u * d)) ** 2, pan + jit(0.15),
      (u) => Math.min(1, u * 60) * Math.exp(-u * (3.2 - 1.2 * size)), b);
  }
  if (size > 0.45) {
    glide(t + 0.02, 1.2 + 1.6 * size, v * 0.5 * size, (u) => 62 - 26 * u, pan * 0.3, (u) => Math.min(1, u * 30) * Math.exp(-u * 3.5), b);
    noise(t + 0.01, 1.4 + 1.5 * size, v * 0.9 * size, pan * 0.3, b, { bp: 90, q: 0.7, lp: 160, dec: 0.5 + 0.5 * size });
  }
}
// A creak: stick-slip friction, a train of tiny impulses at a wandering rate (r0 → r1 Hz) through two wall
// resonances; metal (o.metal) rings higher and longer (the tether brake).
function creak(t, d, v, pan, o = {}) {
  const s0 = S(t), n = Math.min(Math.ceil(d * SR), N - s0); if (n <= 0) return;
  const [r0, r1] = o.rate ?? [18, 45], [fa, fb] = o.f ?? (o.metal ? [880, 2330] : [430, 1150]), q = o.metal ? 0.04 : 0.12;
  const ra = svf(), rb = svf(), [gl, gr] = panG(pan), [bl, br] = o.bus ?? ICE;
  let ph = 0, wob = 0;
  for (let i = 0; i < n; i++) {
    const u = i / n; wob += 0.0005 * ((rnd() * 2 - 1) - wob);
    ph += (r0 + (r1 - r0) * u) * (1 + 6 * wob) / SR;
    let x = 0; if (ph >= 1) { ph -= 1; x = 0.5 + 0.5 * rnd(); }
    const y = ra(x, fa * (1 + 0.04 * wob), q).bp + 0.6 * rb(x, fb, q).bp;
    const e = sm(0, 0.25, u) * (1 - sm(0.7, 1, u));
    bl[s0 + i] += y * e * v * gl; br[s0 + i] += y * e * v * gr;
  }
}
// A metal clank (latch / brake): inharmonic struck partials + a click.
function clank(t, v, pan, f = 310, b = ICE) {
  partials(t, [[f, v, 0.5], [f * 2.32, v * 0.6, 0.3], [f * 4.25, v * 0.35, 0.15], [f * 6.8, v * 0.2, 0.06]], pan, 2.0, b, 0.001);
  noise(t, 0.03, v * 0.7, pan, b, { bp: 2600, q: 0.8, dec: 0.006 });
}
// The probe's hum through the ice / water: its pumps and power converter on D2 (the ocean's key), harmonics 1–5,
// pulsing at the pump's 2.2 Hz; gain and muffling (low-pass Hz) follow breakpoint tracks in film seconds.
function hum(t0, t1, gain, cut) {
  const s0 = S(t0), s1 = S(t1), f0 = hz(38), H = [[1, 1], [2, 0.55], [3, 0.35], [4, 0.12], [5, 0.18]];
  const ph = H.map(() => rnd()), lpa = svf(), lpb = svf(), [bl, br] = ICE;
  for (let i = s0; i < s1; i++) {
    const t = i / SR, g = gain(t); if (g <= 0) continue;
    let x = 0;
    H.forEach(([k, a], j) => { ph[j] += f0 * k * (1 + 0.0007 * j) / SR; if (ph[j] >= 1) ph[j] -= 1; x += a * Math.sin(2 * Math.PI * ph[j]); });
    x *= 1 + 0.18 * Math.sin(2 * Math.PI * 2.2 * t);
    const c = cut(t), y = lpb(lpa(x, c, 0.7).lp, c, 0.7).lp * g;
    bl[i] += y * 0.97; br[i] += y;
  }
}
// The ocean heard from inside it: a low wandering rumble (no surf, no life), a breath of hiss.
function water(t0, t1, gain) {
  const s0 = S(t0), s1 = S(t1), a = svf(), b2 = svf(), hs = svf(), [bl, br] = ICE;
  let w = 0, w2 = 0;
  for (let i = s0; i < s1; i++) {
    const t = i / SR, g = gain(t); w += 0.00002 * ((rnd() * 2 - 1) - w); w2 += 0.00003 * ((rnd() * 2 - 1) - w2);
    if (g <= 0) continue;
    const n1 = rnd() * 2 - 1, n2 = rnd() * 2 - 1;
    const yl = a(n1, 140 + 60 * w, 0.6).lp * (1 + 40 * w) + 0.04 * hs(n1, 2500, 0.8).bp;
    const yr = b2(n2, 140 + 60 * w2, 0.6).lp * (1 + 40 * w2) + 0.04 * hs(n2, 2500, 0.8).bp;
    bl[i] += yl * g; br[i] += yr * g;
  }
}

// ---------- cue kinds (clip sfx) ----------
const KINDS = {
  // breath: [t, 'in' | 'out', { take, v, far }] (TAKES; synth fallback without the file)
  in: (t, v, o) => recorded(t, o.take, { ...o, v }) || breath(t, 'in', { ...o, v }),
  out: (t, v, o) => recorded(t, o.take, { ...o, v }) || breath(t, 'out', { ...o, v }),
  heartbeat: (t, v) => recorded(t, 'heart', { v }),
  crack: (t, v, o) => crack(t, v, o.pan ?? jit(0.6), o.size ?? 0.5),
  cluster: (t, v, o) => cluster(t, o.d ?? 1.4, o.k ?? 4, v * 0.5, o.size ?? 0.3),
  // 03: the frost glitters as it flies (Io's plume shimmer)
  shimmer: (t, v, o) => {
    const d = o.d ?? 2.2;
    [[88, 0.02], [93, 0.015], [95, 0.011], [100, 0.006]].forEach(([m, g], i) =>
      syn(MUS, t + i * 0.08, d, m, g * v, (i - 1.5) * 0.4, { n: 1, wave: 'sine', atk: 0.15, rel: 1.4, vib: 6 }));
  },
};
let sfxN = 0;
for (const c of F.clips) for (const [t, kind, o = {}] of c.A.sfx ?? []) {
  if (!KINDS[kind]) throw new Error(`${c.id}: unknown sfx ${kind}`);
  KINDS[kind](c.start + t, o.v ?? 1, o); sfxN++;
}
// the helmet: two early reflections off the visor colour the breath
for (const a of SFX) for (let i = N - 1; i >= 131; i--) a[i] += 0.3 * a[i - 77] + 0.18 * a[i - 131];

// ---------- music: the surface (A, Io's chords) ----------
const AM9 = [45, 52, 59, 64], FMAJ7 = [41, 48, 57, 64], ADD9 = [45, 52, 57, 61, 64, 71], ESUS = [40, 47, 57, 59, 64];
const land01 = t1 + 8.1, ioIn = t2 + P['02'].in, ioSet = t2 + P['02'].set;
const [eA, eDeep, eB] = P['02'].eclipse.map((x) => t2 + x);
const capt02 = t2 + 6.5, tilt03 = t3 + 3.0, gany = t3 + 8.0, whip = t3 + 9.0;
// the sub drone, A1 + A2, from the pan's start to first contact (the gate cuts it)
syn(MUS, t1 + 2.3, contact - t1 - 2.0, 33, 0.11, 0, { n: 1, wave: 'sine', atk: 3, rel: 1, curve: 2 });
syn(MUS, t1 + 4.5, contact - t1 - 4.2, 45, 0.09, 0, { n: 3, det: 9, atk: 6, rel: 1, c0: 110, c1: 420, q: 1.1, curve: 2 });
chord(MUS, land01, ioIn - land01 + 0.5, AM9, 0.045, { atk: 1.6 });                          // EUROPA: Io's first chord
[[81, 0.05], [88, 0.035], [93, 0.025]].forEach(([m, g], i) =>                                  // Io enters: its diamond glints
  partials(ioIn + i * 0.07, [[hz(m), g, 2.4], [hz(m) * 2.01, g * 0.2, 0.6], [hz(m) * 3.02, g * 0.08, 0.25]], (i - 1) * 0.3, 4, MUS, 0.003));
chord(MUS, ioIn, eDeep - ioIn + 0.6, AM9, 0.04, { atk: 0.6, c1: 1300 });
chord(MUS, eA + 0.4, capt02 - eA, FMAJ7, 0.04, { atk: 2.0, c0: 160, c1: 600 });              // Europa's shadow on Io: darker
chord(MUS, capt02, ioSet - capt02 + 0.8, ADD9, 0.05, { atk: 1.5, c1: 1400 });                 // "IO. WE STOOD THERE."
chord(MUS, ioSet, whip - ioSet + 0.4, ESUS, 0.04, { atk: 2.0, rel: 0.2 });                    // Io gone: Esus4 waits
chord(MUS, tilt03, whip - tilt03 + 0.4, [64, 69, 71], 0.03, { atk: 4.0, curve: 1.6, rel: 0.2, c1: 1800 });   // the tilt climbs
partials(gany, [[hz(95), 0.03, 1.8], [hz(95) * 2.01, 0.006, 0.5]], 0.35, 3, MUS, 0.02);           // Ganymede: one glint
noise(whip - 0.6, t4 - whip + 0.6, 0.16, 0, MUS, { sweep: [300, 5200], q: 1.0, atk: 0.01, shape: (u) => u ** 3 });   // the whip
// 04: the time-lapse day, near-silent: a thin Esus pad and a high tone climbing to first contact; then nothing
chord(MUS, t4 + 0.1, contact - t4, ESUS.slice(1), 0.022, { atk: 2.5, c0: 180, c1: 700 });
syn(MUS, t4 + 4.0, contact - t4 - 4.0, 76, 0.03, 0.1, { n: 1, wave: 'sine', atk: contact - t4 - 4.0, curve: 2.5, vib: 3 });
const stars = t4 + 16.1;
[[96, 0.008], [100, 0.006], [103, 0.004]].forEach(([m, g], i) =>                              // the stars, faint (past the gate)
  syn(TTL, stars + i * 0.5, 2.6, m, g, (i - 1) * 0.5, { n: 1, wave: 'sine', atk: 1.0, rel: 1.2, vib: 5 }));

// ---------- music: the ice and the ocean (D) ----------
const DM = [38, 45, 50, 53], BB_D = [38, 46, 50, 53], GM_D = [38, 43, 50, 55], ASUS = [33, 45, 50, 52], D5 = [26, 38, 45, 50, 57, 64];
const m6 = (k) => t6 + P['06'].marks[k];
syn(MUS, tilt, t5 + 3.2 - tilt, 26, 0.16, 0, { n: 1, wave: 'sine', atk: t5 + 3.0 - tilt, curve: 2.2, rel: 2 });   // the ice from below
chord(MUS, t5 + 1.5, shut - t5 - 1.0, DM, 0.04, { atk: 3.0, c0: 120, c1: 520 });
partials(shut, [[hz(26), 0.22, 4.5], [hz(26) * 2.0, 0.1, 3.0], [hz(26) * 2.76, 0.07, 2.0], [hz(26) * 5.4, 0.03, 0.8]], 0, 6, MUS, 0.004);   // no way back
chord(MUS, shut, m6('1000') - shut + 0.5, BB_D, 0.042, { atk: 1.5, c0: 120, c1: 480 });
chord(MUS, m6('1000'), t6 + P['06'].slow - m6('1000') + 0.5, GM_D, 0.04, { atk: 2.0, c0: 110, c1: 440 });
chord(MUS, t6 + P['06'].slow, brk - t6 - P['06'].slow + 0.1, ASUS, 0.045, { atk: 4.0, curve: 1.5, c0: 120, c1: 650, rel: 0.3 });
[['100', 69], ['1000', 65], ['10000', 62]].forEach(([k, m], i) => tick(m6(k), m, 0.06, [-0.3, 0.3, 0][i]));
chord(MUS, brk, gone - brk, D5, 0.05, { atk: 0.5, c0: 200, c1: 1200, rel: 1.5 });              // through: open, wide
chord(MUS, t7 + 8.0, gone - t7 - 8.0, [53, 65], 0.025, { atk: 2.5, c0: 200, c1: 900, rel: 1.5 });   // the caption: the minor third
// 09: one held note under the title (D4, an A3 under it)
syn(TTL, t9 + 0.4, 3.6, 62, 0.04, 0.05, { n: 1, wave: 'sine', atk: 1.2, rel: 1.4, vib: 4 });
syn(TTL, t9 + 0.7, 3.3, 57, 0.02, -0.1, { n: 3, det: 7, atk: 1.6, rel: 1.4, c0: 300, c1: 900 });

// ---------- the ice and the water ----------
// the probe's hum: rises as 05 comes down to its glow, sealed off (muffled) when the front shuts; close again on 06's
// probe; in the water it clears; in 08 it recedes at 1/r with the fall (camera 1.2 m off the axis, 0.6 m under the base)
const fall = P['08'].fall.map(([s, z]) => [t8 + s, 7.0 / Math.hypot(z - 0.6, 1.2)]);
const humG = (t) => t < t8 ? lerp([[t5 + 0.5, 0], [t5 + 3.0, 0.7], [shut, 0.7], [shut + 0.6, 0.35], [t6, 0.35], [t6 + 0.75, 0.8],
  [brk, 0.8], [brk + 0.4, 1.0]], t) : Math.min(1, lerp(fall, t)) * (1 - sm(blue, gone, t));
const humC = (t) => lerp([[t5, 300], [shut, 420], [shut + 0.6, 170], [t6, 170], [t6 + 0.75, 520], [brk, 520], [brk + 0.4, 1100],
  [t8 + P['08'].release, 1100], [gone, 350]], t);
hum(t5, gone + 0.1, (t) => 0.02 * humG(t), humC);
// 05: the lid is brittle and flexes with the tide: a few cracks and creaks (directed in 05's sfx)
// 06: the time-lapse runs months a second through the cracked lid: a crackle as dense as the clock, until it ends at
// 3 km, then the warm ductile ice is silent
{
  let t = t6 + 0.3;
  while (t < lid) {
    const u = sm(t6, m6('1000'), t), rate = 2 + 26 * u;
    t += -Math.log(1 - rnd()) / rate;
    if (t >= lid) break;
    const sz = rnd() ** 3 * (0.3 + 0.4 * u);
    crack(t, 0.16 * (0.3 + 0.7 * rnd()) * (0.4 + 0.6 * u), jit(0.9), sz);
  }
  crack(lid - 0.05, 0.4, 0.1, 0.9);                                         // the last one: the base of the brittle lid
}
// 07: the water, from the dissolve on; the break: a boom, the rush in, the melt's gas let go; the brake's groan
water(t7 - 1.0, gone + 0.1, (t) => 0.014 * sm(t7 - 1.0, t7 + 0.5, t) * (1 + 0.5 * sm(brk, brk + 0.5, t)) * (1 - sm(blue, gone, t)));
crack(brk, 0.45, 0, 1.0);
noise(brk + 0.03, 2.2, 0.2, 0, ICE, { sweep: [1800, 180], q: 0.6, atk: 0.04, shape: (u) => (1 - u) ** 2 });
const eng = t7 + P['07'].brake, stop = t7 + P['07'].stop;
creak(eng, stop - eng + 0.2, 0.035, 0.15, { metal: true, rate: [70, 18] });
clank(stop, 0.06, 0.15, 260);
// 08: the brake lets go; a far boom from the ceiling
clank(t8 + P['08'].release, 0.05, 0.1, 340);
crack(t8 + 6.5, 0.2, -0.6, 0.8);

// ---------- mix: music in a hall (gated: dead at first contact, back with the tilt), the breath nearly dry, the ice
// and water in a short dark space, the title its own; everything out with the light ----------
const GM = 0.45, GS = 3.5, GI = 1.0, WET = 0.5, WS = 0.08, WI = 0.35;
[...MUS, ...SFX, ...ICE, ...TTL].forEach((a) => hpf(a, 24, SR));
if (process.env.BUS) {
  const db = (arr, g, a, b) => { let s = 0; for (let i = a; i < b; i++) s += (arr[i] * g) ** 2; return (10 * Math.log10(s / (b - a) + 1e-12)).toFixed(0).padStart(4); };
  for (let t = 0; t < END; t += 0.5) {
    const a = S(t), b = S(t + 0.5);
    console.log(`${t.toFixed(1).padStart(6)}  ${db(MUS[0], GM, a, b)} | ${db(SFX[0], GS, a, b)} | ${db(ICE[0], GI, a, b)} | ${db(TTL[0], 1, a, b)}`);
  }
}
const hall = { sr: SR, room: 0.86, damp: 0.5, pre: 0.03 }, helmet = { sr: SR, room: 0.3, damp: 0.8, pre: 0.002 };
const ice = { sr: SR, room: 0.7, damp: 0.85, pre: 0.012 };
const mono = ([a, b], g, hp = 140) => { const m = a.map((v, i) => (v + b[i]) * 0.5 * g); hpf(m, hp, SR); return m; };
const wet = (m, o) => [freeverb(m, 0, o), freeverb(m, 23, o)];
const [wl, wr] = wet(mono(MUS, GM), hall), [hl, hr] = wet(mono(SFX, GS), helmet);
const [il, ir] = wet(mono(ICE, GI, 60), ice), [tl, tr] = wet(mono(TTL, 1), hall);
const [L, R] = [new Float32Array(N), new Float32Array(N)];
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const gm = t >= contact && t < tilt ? 0 : 1;                               // first contact: the music stops dead
  const ge = 1 - sm(gone - 0.6, gone + 0.15, t);                             // out with the light, a beat of silence
  L[i] = ((MUS[0][i] * GM + wl[i] * WET) * gm + SFX[0][i] * GS + hl[i] * WS + ICE[0][i] * GI + il[i] * WI) * ge + TTL[0][i] + tl[i] * WET;
  R[i] = ((MUS[1][i] * GM + wr[i] * WET) * gm + SFX[1][i] * GS + hr[i] * WS + ICE[1][i] * GI + ir[i] * WI) * ge + TTL[1][i] + tr[i] * WET;
}
for (let i = Math.floor((END - 0.6) * SR); i < N; i++) { const g = (N - i) / (0.6 * SR); L[i] *= g; R[i] *= g; }
await writeWav(rel('audio/build/film.wav'), L, R, SR);
console.log(`film: ${sfxN} sfx, ${END}s → audio/build/film.wav`);
