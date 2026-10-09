// Shorts (Sprint 6, user 2026-10-09): a 1080×1920 Short from the film's kept renders (frames/<clip>/NNNN.png, 1920×804),
// square-in-portrait (tools/shorts-lib.mjs LAYOUT): each segment's 804×804 square → lanczos 1080 → on black at SQ_Y,
// the hook + captions (tools/short-overlay.mjs) over it, the sound cut from the film's pre-master
// (audio/build/film.wav, film seconds from out/timeline.json) with a 0.2 s fade in and 1 s out, one gain to −14 LUFS
// and a −1.5 dB peak limiter at 4× (as compile.mjs: no loudnorm, the eclipse's silence would make it dynamic).
// Usage: node shorts.mjs <id> [--stills t1,t2,… (Short seconds → frames/shorts/<id>-tNN.png + <id>-sheet.png)]
//   Spec: shorts/<id>.js. No re-render: frames/ must still hold the clips (kept until Sprint 6 is done).
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import { rel, config, argv } from '../../_kit/lib/film.mjs';
import { SRC, LAYOUT, loadShort } from './tools/shorts-lib.mjs';

const A = argv();
const [id] = A.positional();
if (!id) { console.error('usage: node shorts.mjs <id> [--stills t1,t2,…]'); process.exit(1); }
const Sh = await loadShort(id);
const fps = config.fps, { W, H, SQ, SQ_Y } = LAYOUT, side = SRC.h;
const LUFS = -14, LIMIT = -1.5, FADE_IN = 0.2, FADE_OUT = 1.0;

// segments: first frame, frame count, start in the Short
let at = 0;
const segs = Sh.segments.map((s) => {
  const dir = rel(`frames/${s.clip}`), f0 = Math.round(s.in * fps), nf = Math.round((s.out - s.in) * fps);
  const last = `${dir}/${String(f0 + nf).padStart(4, '0')}.png`;
  if (!fs.existsSync(last)) { console.error(`missing ${last.replace(rel(''), '')} (frames/ deleted or clip shorter)`); process.exit(1); }
  const g = { ...s, dir, f0, nf, t0: at };
  at += nf / fps;
  return g;
});
const dur = at;

// the square's left edge: a number (its centre) or [[segment s, centre], …] eased (smoothstep) between keys
const clampX = (c) => Math.min(SRC.w - side, Math.max(0, c - side / 2));
function xExpr(x) {
  if (typeof x === 'number') return String(clampX(x));
  let e = String(clampX(x[x.length - 1][1]));
  for (let i = x.length - 2; i >= 0; i--) {
    const [ta, ca] = x[i], [tb, cb] = x[i + 1], u = `clip((t-${ta})/${tb - ta},0,1)`;
    e = `if(lt(t,${tb}),${clampX(ca)}+${clampX(cb) - clampX(ca)}*${u}*${u}*(3-2*${u}),${e})`;
  }
  return `if(lt(t,${x[0][0]}),${clampX(x[0][1])},${e})`;
}
function xAt(x, t) {
  if (typeof x === 'number') return clampX(x);
  if (t <= x[0][0]) return clampX(x[0][1]);
  for (let i = 0; i < x.length - 1; i++) {
    const [ta, ca] = x[i], [tb, cb] = x[i + 1];
    if (t < tb) { const u = (t - ta) / (tb - ta); return clampX(ca) + (clampX(cb) - clampX(ca)) * u * u * (3 - 2 * u); }
  }
  return clampX(x[x.length - 1][1]);
}
const square = (xe) => `crop=${side}:${side}:'${xe}':0,`   // quoted: the eased expression has commas
  + `scale=${SQ}:${SQ}:flags=lanczos,setsar=1`;
const place = `pad=${W}:${H}:0:${SQ_Y}:black`;

const stills = A.opt('stills');
if (stills) {
  const ts = stills.split(',').map(Number);
  execFileSync('node', [rel('tools/short-overlay.mjs'), id, '--stills', stills], { stdio: 'inherit' });
  const outs = ts.map((t) => {
    const g = [...segs].reverse().find((s) => t >= s.t0) ?? segs[0];
    const fr = Math.min(g.nf - 1, Math.round((t - g.t0) * fps));
    const png = `${g.dir}/${String(g.f0 + fr + 1).padStart(4, '0')}.png`, ov = rel(`frames/shorts/${id}-overlay-t${t.toFixed(2)}.png`);
    const out = rel(`frames/shorts/${id}-t${t.toFixed(2)}.png`);
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', png, '-i', ov, '-filter_complex',
      `[0:v]${square(xAt(g.x, fr / fps))},${place}[p];[p][1:v]overlay=0:0`, '-frames:v', '1', out]);
    fs.rmSync(ov, { force: true });
    console.log(`STILL ${id} ${t.toFixed(2)} s ← ${png.replace(rel(''), '')} → ${out.replace(rel(''), '')}`);
    return out;
  });
  const sheet = rel(`frames/shorts/${id}-sheet.png`);
  execFileSync('ffmpeg', ['-y', '-v', 'error', ...outs.flatMap((o) => ['-i', o]), '-filter_complex',
    outs.length > 1 ? `${outs.map((_, i) => `[${i}:v]`).join('')}hstack=${outs.length},scale=iw/2:-1` : 'scale=iw/2:-1', '-frames:v', '1', sheet]);
  console.log(`SHEET ${sheet.replace(rel(''), '')}`);
  process.exit(0);
}

// overlay layer
const ov = rel(`out/shorts/.overlay-${id}.mov`);
execFileSync('node', [rel('tools/short-overlay.mjs'), id, '--out', ov], { stdio: 'inherit' });

// sound: the film's pre-master, cut per segment at the clip's film time
const wav = rel('audio/build/film.wav');
if (!fs.existsSync(wav)) execFileSync('node', [rel('audio/music.mjs')], { cwd: rel(''), stdio: 'inherit' });
const TL = JSON.parse(fs.readFileSync(rel('out/timeline.json'), 'utf8')).timeline;
const filmIn = (clip) => { const c = TL.find((c) => c.id === clip); if (!c) throw new Error(`${clip} not in out/timeline.json`); return c.in; };
const aWav = rel(`out/shorts/.a-${id}.wav`);
const af = segs.map((g, k) => { const a = filmIn(g.clip) + g.f0 / fps; return `[0:a]atrim=start=${a.toFixed(4)}:end=${(a + g.nf / fps).toFixed(4)},asetpts=PTS-STARTPTS[a${k}]`; });
execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', wav, '-filter_complex',
  `${af.join(';')};${segs.map((_, k) => `[a${k}]`).join('')}concat=n=${segs.length}:v=0:a=1,` +
  `afade=t=in:st=0:d=${FADE_IN},afade=t=out:st=${(dur - FADE_OUT).toFixed(3)}:d=${FADE_OUT}[a]`, '-map', '[a]', '-c:a', 'pcm_f32le', aWav]);
const e = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', aWav, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], { encoding: 'utf8' }).stderr;
const m = JSON.parse(e.slice(e.lastIndexOf('{'), e.lastIndexOf('}') + 1)), gain = LUFS - +m.input_i;

// picture + layer + sound
const out = rel(`out/shorts/${id}.mp4`), t0 = Date.now();
const vin = segs.flatMap((g) => ['-framerate', String(fps), '-start_number', String(g.f0 + 1), '-i', `${g.dir}/%04d.png`]);
const n = segs.length;
const vf = segs.map((g, k) => `[${k}:v]trim=end_frame=${g.nf},setpts=PTS-STARTPTS,${square(xExpr(g.x))},format=yuv444p[v${k}]`);
execFileSync('ffmpeg', ['-y', '-v', 'error', ...vin, '-i', ov, '-i', aWav, '-filter_complex',
  `${vf.join(';')};${segs.map((_, k) => `[v${k}]`).join('')}concat=n=${n}:v=1:a=0,${place}[p];` +
  `[p][${n}:v]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v];` +
  `[${n + 1}:a]volume=${gain.toFixed(2)}dB,aresample=192000,alimiter=limit=${(10 ** (LIMIT / 20)).toFixed(4)}:attack=2:release=60:level=0,aresample=48000[a]`,
  '-map', '[v]', '-map', '[a]', '-r', String(fps), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
  '-c:a', 'aac', '-b:a', '192k', '-t', dur.toFixed(3), '-movflags', '+faststart', out], { stdio: 'inherit' });
fs.rmSync(aWav, { force: true });

// check: loudness + true peak of the delivered file
const q = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], { encoding: 'utf8' }).stderr;
const I = q.match(/I:\s+(-?[\d.]+) LUFS/g)?.pop(), TP = q.match(/Peak:\s+(-?[\d.]+) dBFS/g)?.pop();
const MB = fs.statSync(out).size / 1e6;
console.log(`SHORT ${id}: ${segs.map((g) => `${g.clip} ${g.in.toFixed(2)}–${g.out.toFixed(2)}`).join(' + ')} → ` +
  `${out.replace(rel(''), '')}, ${dur.toFixed(2)} s, ${MB.toFixed(1)} MB, ${((Date.now() - t0) / 1000).toFixed(0)} s`);
console.log(`  sound ${m.input_i} LUFS ${gain >= 0 ? '+' : ''}${gain.toFixed(1)} dB → ${I} · true ${TP}`);
if (dur > 60) console.warn(`  WARN ${dur.toFixed(1)} s > 60 s`);
