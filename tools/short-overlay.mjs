// Shorts caption layer (Sprint 6.0, from tools/overlay.mjs): a Short's hook (above the square) and its captions (below
// it) drawn in headless Chrome in the series' type (Cinzel caps, a JetBrains Mono line), on a transparent 1080×1920
// canvas → a qtrle .mov that shorts.mjs lays over the picture. English only (user 2026-10-09).
// Usage: node tools/short-overlay.mjs <id> [--out out/shorts/.overlay-<id>.mov] [--stills t1,t2,… (→ frames/shorts/<id>-overlay-tNN.png)]
// Caption text in {braces} is a Python f-string evaluated in tools/physics.py's namespace: numbers come from the script.
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { rel, config, argv, chrome, kitRoot } from '../../../_kit/lib/film.mjs';
import { LAYOUT, loadShort } from './shorts-lib.mjs';

const puppeteer = createRequire(`${kitRoot}/package.json`)('puppeteer-core');
const A = argv();
const [id] = A.positional();
const Sh = await loadShort(id);
const { W, H } = LAYOUT;
const n = Math.round(Sh.duration * config.fps);
const caps = JSON.parse(execFileSync('python3', ['-c',
  `import sys, json; sys.path.insert(0, ${JSON.stringify(rel('tools'))}); import physics as P; ` +
  `print(json.dumps([eval('f' + repr(s), vars(P)) for s in json.loads(sys.argv[1])]))`, JSON.stringify(Sh.caps.map((c) => c[2]))],
{ encoding: 'utf8' }));
const S = { hook: Sh.hook || [], caps: Sh.caps.map(([a, b], i) => [a, b, caps[i]]), L: LAYOUT };
for (const [a, b, s] of S.caps) console.log(`  ${a.toFixed(2)}–${b.toFixed(2)} s  ${s}`);

const page_ = `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=JetBrains+Mono:wght@400&display=block" rel="stylesheet">
<style>html,body{margin:0;background:transparent}</style><canvas id="cv" width="${W}" height="${H}"></canvas>
<script>
const S = ${JSON.stringify(S)};
const EN = '"Cinzel", serif', MONO = '"JetBrains Mono", monospace';
const x = document.getElementById('cv').getContext('2d');
const seg = (t, a, b) => { const u = Math.min(1, Math.max(0, (t - a) / (b - a))); return u * u * (3 - 2 * u); };
const alphaIn = (t, a, b, fade = 0.45) => seg(t, a, a + fade) * (1 - seg(t, b - fade, b));   // cg-lab's caption fade
function lines(s, font, spacing, max) {                // greedy word wrap at the tracked width; a newline forces a break
  x.font = font; x.letterSpacing = spacing + 'px';
  const out = [];
  for (const para of s.split('\\n')) for (const [j, w] of para.split(' ').entries()) {
    if (j === 0) { out.push(w); continue; }
    const t = out.length ? out[out.length - 1] + ' ' + w : w;
    if (x.measureText(t).width <= max) out[out.length - 1] = t; else out.push(w);
  }
  return out;
}
function text(s, px, py, font, color, a, spacing = 0) {
  if (a <= 0) return;
  x.save(); x.globalAlpha = a; x.font = font; x.fillStyle = color; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.letterSpacing = spacing + 'px'; x.fillText(s, px + spacing / 2, py); x.restore();
}
const L = S.L, CX = ${W} / 2;
window.renderAt = (t) => {
  x.clearRect(0, 0, ${W}, ${H});
  const [h1, h2] = S.hook;                             // hook: on from the first frame (no fade in: the Short loops)
  if (h1) lines(h1, L.hook.font, L.hook.track, L.max).forEach((s, i, all) =>
    text(s, CX, L.hook.y - (all.length - 1 - i) * L.hook.lh, L.hook.font, '#efe8d6', 1, L.hook.track));
  if (h2) text(h2, CX, L.sub.y, L.sub.font, '#8a8f96', 0.9, L.sub.track);
  for (const [a0, a1, s] of S.caps) {                  // captions under the square, wrapped
    const a = alphaIn(t, a0, a1);
    if (a > 0) lines(s, L.cap.font, L.cap.track, L.max).forEach((r, i) => text(r, CX, L.cap.y + i * L.cap.lh, L.cap.font, '#e9e2d0', a, L.cap.track));
  }
};
window.ready = (async () => {
  const fonts = [L.hook.font, L.cap.font, L.sub.font];
  const all = S.hook.join('') + S.caps.map((c) => c[2]).join('') + '0123456789.,·';
  await Promise.all(fonts.map((f) => document.fonts.load(f, all)));
  await document.fonts.ready;
  return fonts.filter((f) => !document.fonts.check(f, all));
})();
</script>`;

fs.mkdirSync(rel('frames/shorts'), { recursive: true });
const html = rel(`frames/shorts/.overlay-${id}.html`);
fs.writeFileSync(html, page_);
const browser = await puppeteer.launch({ executablePath: chrome(), headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.setViewport({ width: W, height: H });
await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
const missing = await page.evaluate(() => window.ready);
if (missing.length) { console.error(`fonts missing: ${missing.join(', ')}`); await browser.close(); process.exit(1); }
const shot = (f) => page.evaluate((ff, fps) => { window.renderAt(ff / fps); return document.getElementById('cv').toDataURL('image/png').split(',')[1]; }, f, config.fps);

const stills = A.opt('stills');
if (stills) {
  for (const t of stills.split(',').map(Number)) {
    const f = rel(`frames/shorts/${id}-overlay-t${t.toFixed(2)}.png`);
    fs.writeFileSync(f, Buffer.from(await shot(Math.round(t * config.fps)), 'base64'));
    console.log(`OVERLAY ${id}: ${f.replace(rel(''), '')}`);
  }
} else {
  const out = A.opt('out', rel(`out/shorts/.overlay-${id}.mov`)), t0 = Date.now();
  fs.mkdirSync(rel('out/shorts'), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(config.fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'qtrle', '-pix_fmt', 'argb', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    if (!ff.stdin.write(Buffer.from(await shot(i), 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log(`OVERLAY ${id}: ${n} frames → ${out.replace(rel(''), '')} in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}
await browser.close();
fs.rmSync(html, { force: true });
