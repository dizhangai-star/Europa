// Sprint 5.0 cost ladder: full-res A/B stills of one clip under render variants, timed, PSNR against the first
// (reference) variant, and side-by-side zooms. "Same picture" is proven here, never argued (blender-film skill).
// Usage: node tools/ab.mjs <id> <t,t,…> <name:k=v,k=v> [<name:k=v…> …] [--zoom x,y,w,h] [--gain EV] [--force]
//   e.g. node tools/ab.mjs 06-descent 4,6,19.5 ref:samples=64 s32:samples=32 vb64:samples=64,vbounces=64
//   Each variant = one Blender run at --pct 100 with --persist 1 (as the batch renders), its k=v passed as --k v
//   (samples, vbounces, mblur, …: the shot's own options). Stills → frames/ab/<id>/<name>/; a variant whose stills are
//   all on disk is not re-rendered (--force does). Per still: seconds (the first one includes the scene sync).
//   PSNR (ffmpeg, all planes): whole frame and the inner half (centre 960×402); mean luma of both (06 at 32 spp: motion
//   blur's time sampling shifted whole frames by up to 7 levels, PSNR 28.6, the denoiser can't hide that). Zooms: frames/ab/<id>-f<NNNN>.png,
//   one row per variant = reference crop | variant crop | |difference| × 8, crop --zoom on the 1920×804 picture
//   (default the centre 640×268), --gain EV brightens all three for dark frames. Report → frames/ab/<id>.md.
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import { loadClip, rel, config, argv } from '../../../_kit/lib/film.mjs';

const BLENDER = process.env.BLENDER ?? '/Applications/Blender.app/Contents/MacOS/Blender';
const A = argv(undefined, ['force']);
const [id, ts, ...vs] = A.positional();
if (!id || !ts || !vs.length) { console.error('usage: node tools/ab.mjs <id> <t,t,…> <name:k=v,…> [<name:k=v,…> …]'); process.exit(1); }
const C = loadClip(id);
const n = Math.round(C.duration * config.fps);
const fr = ts.split(',').map((t) => Math.min(n, Math.max(1, Math.round(+t * config.fps) + 1)));
const f4 = (f) => String(f).padStart(4, '0');
const V = vs.map((s) => {
  const [name, kv = ''] = s.split(':');
  return { name, args: kv.split(',').filter(Boolean).flatMap((p) => { const [k, ...v] = p.split('='); return [`--${k}`, v.join('=')]; }) };
});
const root = rel(`frames/ab/${id}`);
const still = (v, f) => `${root}/${v.name}/${id}-f${f4(f)}.png`;

for (const v of V) {
  const times = `${root}/${v.name}/times.json`;
  if (!A.has('force') && fr.every((f) => fs.existsSync(still(v, f))) && fs.existsSync(times)) {
    const T = JSON.parse(fs.readFileSync(times, 'utf8'));
    if (fr.every((f) => T[f] != null)) { v.t = T; console.log(`${v.name}: on disk`); continue; }
  }
  fs.mkdirSync(`${root}/${v.name}`, { recursive: true });
  const args = v.args.includes('--samples') ? v.args : ['--samples', String(config.samples), ...v.args];
  const t0 = Date.now();
  const log = execFileSync(BLENDER, ['-b', '--factory-startup', '-P', rel(`blender/shots/${C.shot}`), '--',
    '--frames', String(n), '--pct', '100', '--persist', '1', ...args, '--id', id, '--stills', fr.join(','),
    '--stills-dir', `${root}/${v.name}`], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const err = log.split('\n').filter((l) => /Traceback|Error:/.test(l) && !/Not freed memory/.test(l));
  if (err.length) { console.error(err.join('\n')); process.exit(1); }
  const T = fs.existsSync(times) ? JSON.parse(fs.readFileSync(times, 'utf8')) : {};
  for (const m of log.matchAll(/^STILL (\d+) ([\d.]+)$/gm)) T[+m[1]] = +m[2];
  fs.writeFileSync(times, JSON.stringify(T));
  v.t = T;
  console.log(`${v.name}: ${fr.map((f) => `f${f} ${T[f]}s`).join(' · ')} (run ${((Date.now() - t0) / 1000).toFixed(0)} s)`);
}

const yavg = (a) => +(spawnSync('ffmpeg', ['-v', 'error', '-i', a, '-vf', 'signalstats,metadata=print:file=-', '-f', 'null', '-'],
  { encoding: 'utf8' }).stdout.match(/YAVG=([\d.]+)/)?.[1] ?? NaN);   // mean luma (8-bit): a sampling bias moves it
const psnr = (a, b, crop) => {
  const g = crop ? `[0]crop=960:402[a];[1]crop=960:402[b];[a][b]psnr` : '[0][1]psnr';
  const r = spawnSync('ffmpeg', ['-v', 'info', '-i', a, '-i', b, '-lavfi', g, '-f', 'null', '-'], { encoding: 'utf8' });
  const m = r.stderr.match(/average:([\d.]+|inf)/);
  return m ? (m[1] === 'inf' ? Infinity : +m[1]) : NaN;
};
const [zx, zy, zw, zh] = String(A.opt('zoom', '640,268,640,268')).split(',').map(Number);
const gain = 2 ** +A.opt('gain', 0);
const ref = V[0];
const rows = [];
for (const f of fr) {
  const cmp = [];
  for (const v of V.slice(1)) {
    const w = psnr(still(ref, f), still(v, f)), c = psnr(still(ref, f), still(v, f), true);
    rows.push({ f, v: v.name, w, c, tr: ref.t[f], tv: v.t[f], yr: yavg(still(ref, f)), yv: yavg(still(v, f)) });
    cmp.push(v);
  }
  if (!cmp.length) continue;
  const inputs = [still(ref, f), ...cmp.map((v) => still(v, f))].flatMap((p) => ['-i', p]);
  const cr = `crop=${zw}:${zh}:${zx}:${zy},format=gbrp,lutrgb=r=val*${gain}:g=val*${gain}:b=val*${gain}`;
  let g = `[0]${cr},split=${cmp.length * 2}${cmp.map((_, k) => `[r${k}][q${k}]`).join('')};`;
  cmp.forEach((_, k) => {
    g += `[${k + 1}]${cr},split[v${k}][w${k}];[q${k}][w${k}]blend=all_mode=difference,lutrgb=r=val*8:g=val*8:b=val*8[d${k}];`;
    g += `[r${k}][v${k}][d${k}]hstack=3[row${k}];`;
  });
  g += cmp.length > 1 ? `${cmp.map((_, k) => `[row${k}]`).join('')}vstack=${cmp.length}` : '[row0]null';
  execFileSync('ffmpeg', ['-y', '-v', 'error', ...inputs, '-filter_complex', g, '-frames:v', '1', '-update', '1',
    `${root}-f${f4(f)}.png`]);
}

const fmt = (x) => (x === Infinity ? '∞' : x.toFixed(1));
const mean = (v) => fr.reduce((s, f) => s + v.t[f], 0) / fr.length;
const lines = [`# ${id} A/B (${new Date().toISOString().slice(0, 16)}), reference ${ref.name} (${ref.args.join(' ') || 'defaults'})`, '',
  '| frame | variant | PSNR whole | PSNR inner | mean luma ref → variant | s ref → s variant |', '|---|---|---|---|---|---|',
  ...rows.map((r) => `| ${r.f} | ${r.v} | ${fmt(r.w)} | ${fmt(r.c)} | ${r.yr.toFixed(1)} → ${r.yv.toFixed(1)} | ${r.tr} → ${r.tv} |`), '',
  ...V.map((v) => `- ${v.name} (${v.args.join(' ') || 'defaults'}): mean ${mean(v).toFixed(1)} s/still`)];
fs.writeFileSync(`${root}.md`, lines.join('\n') + '\n');
console.log(lines.join('\n'));
