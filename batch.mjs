// Batch renderer (Sprint 5.1, from ../../childhood-desktop/batch.mjs): clips → frames/<id>/ → out/<id>.mp4, resumable,
// started by the user any time (day or night); rerun = resume.
// Usage: node batch.mjs [id…] [--animatic] [--samples N] [--pct P] [--look L] [--engine E] [--until HH:MM] [--dry] [--clean]
//   ids: clip ids or their NN prefixes (08 02 …), rendered in the order given; none = every clip without an
//   out/<id>.mp4 yet (with --animatic: all), cheapest first by the clip's measured `spf` × frames (Sprint 5.0).
//   Per clip as render.mjs: `samples` (else config.samples), `freeze`, persistent data, 09's card via tools/card.mjs,
//   the letterbox pad, 4:4:4 masters (animatics 4:2:0, Workbench at 50 %).
//   Resume: frames already in frames/<id>/ are kept and skipped (Blender's no-overwrite); a truncated PNG (no IEND,
//   from a killed render) is deleted first. A clip that fails is logged and the batch goes on with the next one.
//   --until 18:00: stop launching clips after that time and stop the running one then (its frames stay; rerun resumes).
//   --dry: the plan only (frames on disk, estimated hours from `spf`, the finish time); nothing renders.
//   caffeinate -is keeps the Mac awake while the batch runs. Full Blender output → logs/batch-<stamp>.log; the summary
//   (done / failed, frames, s/frame, wall time) → out/batch-report.md, rewritten after every clip.
//   Final frames are kept after encoding (resume, re-encode, regrade); --clean deletes them. Animatic frames are always
//   deleted after encoding, as render.mjs does. No previews while it runs: they share the one GPU.
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { loadClip, rel, config, argv, clipIds } from '../../_kit/lib/film.mjs';

const BLENDER = process.env.BLENDER ?? '/Applications/Blender.app/Contents/MacOS/Blender';
const A = argv(undefined, ['animatic', 'dry', 'clean']);
const anim = A.has('animatic');
const all = clipIds();
const pick = A.positional().map((p) => all.find((id) => id === p || id.startsWith(`${p.padStart(2, '0')}-`)) ?? p);
const bad = pick.filter((p) => !all.includes(p));
if (bad.length) { console.error(`unknown clips: ${bad.join(', ')} (have ${all.join(' ')})`); process.exit(1); }
const nFrames = (C) => Math.round(C.duration * config.fps);
const cost = (id) => { const C = loadClip(id); return C.card ? 0 : (C.spf ?? 1e3) * nFrames(C); };   // s at 64 spp
const ids = pick.length ? pick
  : all.filter((id) => anim || !fs.existsSync(rel(`out/${id}.mp4`))).sort((a, b) => (anim ? 0 : cost(a) - cost(b)));

const opt = (k) => A.opt(k) ?? (anim ? { engine: 'workbench', pct: '50' }[k] : undefined);
const pass = ['pct', 'look', 'engine'].flatMap((k) => (opt(k) ? [`--${k}`, opt(k)] : []));
const until = (() => {
  const u = A.opt('until');
  if (!u) return null;
  const [h, m] = u.split(':').map(Number), d = new Date();
  d.setHours(h, m, 0, 0);
  if (d <= new Date()) d.setDate(d.getDate() + 1);
  return d;
})();

const started = new Date(), p2 = (x) => String(x).padStart(2, '0');
const stamp = `${started.getFullYear()}${p2(started.getMonth() + 1)}${p2(started.getDate())}-${p2(started.getHours())}${p2(started.getMinutes())}`;
const suffix = anim ? '-animatic' : '';
const logRel = `logs/batch-${stamp}${suffix}${A.has('dry') ? '-dry' : ''}.log`;
fs.mkdirSync(rel('logs'), { recursive: true });
fs.mkdirSync(rel('out'), { recursive: true });
const log = fs.createWriteStream(rel(logRel), { flags: 'a' });
const say = (s) => { const l = `[${new Date().toTimeString().slice(0, 8)}] ${s}`; console.log(l); log.write(`${l}\n`); };
const hhmm = (d) => d.toTimeString().slice(0, 5);
const fmt = (s) => (s >= 3600 ? `${(s / 3600).toFixed(1)} h` : `${(s / 60).toFixed(1)} min`);

const pngOk = (f) => {                       // a PNG is complete when its last chunk is IEND
  try {
    const fd = fs.openSync(f, 'r'), { size } = fs.fstatSync(fd), b = Buffer.alloc(12);
    if (size < 64) { fs.closeSync(fd); return false; }
    fs.readSync(fd, b, 0, 12, size - 12); fs.closeSync(fd);
    return b.toString('latin1', 4, 8) === 'IEND';
  } catch { return false; }
};
const onDisk = (dir, n) => {
  if (!fs.existsSync(dir)) return 0;
  let k = 0;
  for (const f of fs.readdirSync(dir).filter((x) => /^\d{4}\.png$/.test(x))) {
    if (pngOk(`${dir}/${f}`)) k += +f.slice(0, 4) <= n;
    else { fs.rmSync(`${dir}/${f}`); say(`  removed truncated ${f}`); }
  }
  return k;
};

const rows = [];
const report = () => {
  const head = `# Batch ${anim ? 'animatic' : 'render'} report\n\nStarted ${started.toLocaleString()}` +
    `${pass.length ? ` · ${pass.join(' ')}` : ''}${until ? ` · until ${hhmm(until)}` : ''} · log \`${logRel}\`\n\n`;
  const table = ['| clip | status | samples | frames | s/frame | wall | note |', '|---|---|---|---|---|---|---|',
    ...rows.map((r) => `| ${r.id} | ${r.status} | ${r.samples ?? '–'} | ${r.frames} | ${r.spf ?? '–'} | ${r.wall ?? '–'} | ${r.note ?? ''} |`)].join('\n');
  fs.writeFileSync(rel(`out/batch-report${suffix}${A.has('dry') ? '-dry' : ''}.md`), `${head}${table}\n`);
};

let child = null, stopped = false;
const stop = (why) => { if (stopped) return; stopped = true; say(`stopping: ${why}`); if (child) child.kill('SIGTERM'); };
process.on('SIGINT', () => stop('interrupted (Ctrl-C)'));
if (until) setTimeout(() => stop(`--until ${A.opt('until')}`), until - Date.now()).unref();

const run = (cmd, args, onLine = () => {}) => new Promise((done) => {
  child = spawn(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'] });
  const err = [];
  let buf = '', shot = '';
  const line = (l) => {
    log.write(`${l}\n`);
    if (/Traceback|Error:/.test(l) && !/Not freed memory/.test(l)) err.push(l);   // Blender's exit leak report is harmless
    if (/^(SHOT|NOTE|CARD)/.test(l)) shot = l;
    onLine(l);
  };
  const feed = (d) => { buf += d; const ls = buf.split('\n'); buf = ls.pop(); ls.forEach(line); };
  child.stdout.on('data', feed); child.stderr.on('data', feed);
  child.on('close', (code, sig) => { if (buf) line(buf); child = null; done({ err, shot, code, sig }); });
});

if (!A.has('dry')) spawn('caffeinate', ['-is', '-w', String(process.pid)], { stdio: 'ignore', detached: true }).unref();
const free = execFileSync('df', ['-g', rel('')], { encoding: 'utf8' }).trim().split('\n').pop().split(/\s+/)[3];
say(`batch ${anim ? 'animatic' : 'render'}${A.has('dry') ? ' (dry run)' : ''}: ${ids.join(' ')} ${pass.join(' ')}· ${free} GB free · log ${logRel}`);

let eta = Date.now();
for (const id of ids) {
  const C = loadClip(id), name = `${id}${suffix}`;
  const n = nFrames(C), dir = rel(`frames/${name}`), out = rel(`out/${name}.mp4`);
  const samples = String(A.opt('samples', anim ? config.samples : (C.samples ?? config.samples)));
  const row = { id: name, status: 'pending', frames: `0/${n}`, samples: C.card ? 'card' : samples };
  rows.push(row);
  if (stopped) { row.status = 'not started'; continue; }
  const have = C.card ? 0 : onDisk(dir, n);
  row.frames = C.card ? `${n}` : `${have}/${n}`;
  if (A.has('dry')) {
    const est = C.card ? 10 : anim ? 0 : (n - have) * (C.spf ?? NaN);
    eta += est * 1000;
    row.status = 'dry run';
    row.note = anim ? '' : `est. ${C.card ? 'seconds (tools/card.mjs)' : `${fmt(est)} (spf ${C.spf ?? '?'})`} · done ≈ ${hhmm(new Date(eta))}`;
    say(`${name}: ${row.frames}${C.card ? ' (card)' : ' on disk'} · ${row.note}`);
    continue;
  }
  const t0 = Date.now();
  if (C.card) {                               // type on black, no Blender (compile redraws it at 4K)
    row.status = 'drawing'; report();
    const r = await run('node', [rel('tools/card.mjs'), id, '--out', out]);
    row.wall = fmt((Date.now() - t0) / 1000);
    row.status = r.code === 0 && fs.existsSync(out) ? 'done' : stopped ? 'stopped' : 'FAILED';
    if (row.status === 'FAILED') row.note = (r.err.slice(-2).join(' / ') || `exit ${r.code ?? r.sig}`).replace(/\|/g, '/');
    say(`${name}: ${row.status === 'done' ? `→ out/${name}.mp4` : `${row.status} ${row.note ?? ''}`}`);
    report();
    continue;
  }
  say(`${name}: ${have}/${n} frames on disk · ${samples} spp${C.freeze && !anim ? ` · freeze ${C.freeze} s` : ''}`);
  if (have < n) {
    row.status = 'rendering'; report();
    const args = ['-b', '--factory-startup', '-P', rel(`blender/shots/${C.shot}`), '--', '--frames', String(n),
      '--samples', samples, ...pass, '--persist', '1', '--resume', '1', '--out', dir];
    if (C.freeze && !anim) args.push('--freeze', String(Math.round(C.freeze * config.fps) + 1));
    if (anim) args.push('--draft', '1');
    const times = [];
    let k = have;
    const r = await run(BLENDER, args, (l) => {
      const m = l.match(/^FRAME (\d+) ([\d.]+)s/);
      if (!m) return;
      times.push(+m[2]); k++;
      if (k % 24 === 0 || k === n) {         // the first frame's time includes the scene build + GPU warm-up
        const t = times.length > 1 ? times.slice(1) : times, spf = t.reduce((a, b) => a + b, 0) / t.length;
        say(`  ${name} ${k}/${n} · frame ${m[1]} ${m[2]} s · ${spf.toFixed(1)} s/frame · clip done ≈ ${hhmm(new Date(Date.now() + (n - k) * spf * 1000))}`);
      }
    });
    const got = onDisk(dir, n), t = times.slice(1);
    row.frames = `${got}/${n}`;
    row.spf = t.length ? (t.reduce((a, b) => a + b, 0) / t.length).toFixed(1) : undefined;
    row.wall = fmt((Date.now() - t0) / 1000);
    if (got < n) {
      row.status = stopped ? 'stopped' : 'FAILED';
      row.note = stopped ? 'rerun to resume' : (r.err.slice(-2).join(' / ') || `exit ${r.code ?? r.sig}`).replace(/\|/g, '/');
      say(`${name}: ${row.status} at ${got}/${n} (${row.note})`);
      report();
      continue;
    }
    if (r.err.length) row.note = `warnings: ${r.err.length} (see log)`;
    say(`${name}: ${r.shot || 'rendered'}`);
  }
  try {
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(config.fps), '-i', `${dir}/%04d.png`,
      '-vf', 'scale=1920:-2,pad=1920:1080:0:(oh-ih)/2:black', '-c:v', 'libx264', '-preset', 'slow', '-crf', String(config.crf),
      '-pix_fmt', anim ? 'yuv420p' : 'yuv444p', '-movflags', '+faststart', out]);
    if (anim || A.has('clean')) fs.rmSync(dir, { recursive: true, force: true });
    row.status = 'done';
    row.wall ??= fmt((Date.now() - t0) / 1000);
    say(`${name}: → out/${name}.mp4`);
  } catch (e) {
    row.status = 'FAILED'; row.note = `encode: ${String(e.message).split('\n')[0]}`.replace(/\|/g, '/');
    say(`${name}: ${row.note}`);
  }
  report();
}
report();
const ok = rows.filter((r) => r.status === 'done').length;
say(A.has('dry') ? `dry run: ${rows.length} clips, done ≈ ${new Date(eta).toLocaleString()} if started now`
  : `batch over: ${ok}/${rows.length} done → out/batch-report${suffix}.md`);
log.end();
