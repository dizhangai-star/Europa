// Film-local title card (09; copied from Io's 06, Sprint 0.3): text on black, drawn in headless Chrome with 巨物's title type (Cinzel 600 caps tracked,
// 中文 Noto Serif SC spaced, a two-line physics readout in JetBrains Mono) so the series' cards match. No Blender:
// the card is all type, and the same canvas route carries the captions + counter at compile (tools/overlay.mjs).
// Usage: node tools/card.mjs <id> [--variant europa|io] [--out out/<id>.mp4] [--stills t1,t2,… (→ frames/<id>-tNN.png)]
//   Numbers come from `python3 tools/physics.py --card`. Frames are full 1920×1080 (black bars are black anyway).
//   Logical units are 巨物's 640×360 overlay grid, drawn ×3.
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { loadClip, rel, config, argv, chrome, kitRoot } from '../../../_kit/lib/film.mjs';

const puppeteer = createRequire(`${kitRoot}/package.json`)('puppeteer-core');
const A = argv(undefined, ['4k']);
const K = A.has('4k') ? 2 : 1, W = 1920 * K, H = 1080 * K;   // --4k: the same layout drawn ×6 for the 4K delivery (sharp type)
const [id] = A.positional();
const C = loadClip(id);
const P = JSON.parse(execFileSync('python3', [rel('tools/physics.py'), '--card'], { encoding: 'utf8' }));
const variant = A.opt('variant', C.card?.variant ?? 'europa');

const TITLE = {
  europa: { en: 'EUROPA', zh: '深 渊', enPx: 30, enSp: 12, zhPx: 13, zhSp: 6, y: 153 },   // title 木卫二 · 深渊 / Europa · Abyss; Sprint 3.9 (user): no kicker, the block re-centred (title 162 → 153)
  io: { en: 'IO', zh: '永 恒', enPx: 30, enSp: 18, zhPx: 13, zhSp: 6, kicker: ['木 卫 一', 'A MOON OF JUPITER'] },   // ep. 2's card, for comparison
}[variant];
const LINES = [
  `冰下的海，地球海洋的 ${P.oceans} 倍  ·  海底 ${P.floor_bar.toLocaleString('en')} 巴  ·  地表辐射 ${P.lethal_h} 小时致死`,
  `${P.oceans}× EARTH'S OCEANS · ${P.floor_bar.toLocaleString('en')} BAR AT THE SEA FLOOR · A LETHAL DOSE IN ${P.lethal_h} HOURS ON THE ICE`,   // 'on the ice' = 地表 (user 3.9)
];
const T = { title: [0.4, 5.5, 0.8, 1.6], lines: [1.1, 5.5, 0.8, 1.6] };   // [in, out, fade in, fade out] s: black 0–0.4, both gone by 5.5, black tail; slow 1.6 s fade out (user 2026-10-03: the end was too quick; 3.9: held 1 s longer, clip 7 s)

const page_ = `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=JetBrains+Mono:wght@400&family=Noto+Serif+SC:wght@400&display=block" rel="stylesheet">
<style>html,body{margin:0;background:#000}</style><canvas id="cv" width="${W}" height="${H}"></canvas>
<script>
const S = ${JSON.stringify({ TITLE, LINES, T })};
const EN = '"Cinzel", serif', ZH = '"Noto Serif SC", serif', MONO = '"JetBrains Mono", "Noto Serif SC", monospace';
const x = document.getElementById('cv').getContext('2d');
const ss = (a, b, t) => { const u = Math.min(1, Math.max(0, (t - a) / (b - a))); return u * u * (3 - 2 * u); };
const alphaIn = (t, [a, b, fi, fo]) => ss(a, a + fi, t) * (1 - ss(b - fo, b, t));
function text(s, px, py, font, color, a, spacing = 0) {
  if (a <= 0) return;
  x.save(); x.globalAlpha = a; x.font = font; x.fillStyle = color; x.textAlign = 'center'; x.textBaseline = 'middle';
  if (spacing) x.letterSpacing = spacing + 'px';
  x.fillText(s, px + spacing / 2, py); x.restore();      // letterSpacing trails the last glyph: shift half back to centre
}
window.renderAt = (t) => {
  x.setTransform(1, 0, 0, 1, 0, 0); x.fillStyle = '#000'; x.fillRect(0, 0, ${W}, ${H}); x.setTransform(${3 * K}, 0, 0, ${3 * K}, 0, 0);
  const a = alphaIn(t, S.T.title), b = alphaIn(t, S.T.lines), M = S.TITLE, y = M.y ?? 162, dy = y - 162;
  if (M.kicker) {                                    // small label above the title: what Europa is
    text(M.kicker[0], 320, 119, '400 7px ' + ZH, '#b9b2a2', a * 0.9, 3);
    text(M.kicker[1], 320, 129, '600 5.5px ' + EN, '#8a8f96', a * 0.9, 2.5);
  }
  text(M.en, 320, y, '600 ' + M.enPx + 'px ' + EN, '#e9e2d0', a, M.enSp);
  text(M.zh, 320, y + M.enPx * 0.5 + 12, '400 ' + M.zhPx + 'px ' + ZH, '#d8d0bf', a, M.zhSp);
  text(S.LINES[0], 320, 210 + dy, '400 6px ' + MONO, '#b9b2a2', b, 1);
  text(S.LINES[1], 320, 219 + dy, '400 6px ' + MONO, '#8a8f96', b * 0.9, 1);
};
window.ready = (async () => {
  const fonts = ['600 30px "Cinzel"', '400 13px "Noto Serif SC"', '400 6px "JetBrains Mono"'];
  await Promise.all(fonts.map((f) => document.fonts.load(f, S.TITLE.en + S.TITLE.zh + (S.TITLE.kicker || []).join('') + S.LINES.join(''))));
  await document.fonts.ready;
  return fonts.filter((f) => !document.fonts.check(f, S.TITLE.zh + S.LINES[0]));
})();
</script>`;

const html = rel(`frames/.card-${id}.html`);
fs.mkdirSync(rel('frames'), { recursive: true });
fs.writeFileSync(html, page_);
const browser = await puppeteer.launch({ executablePath: chrome(), headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.setViewport({ width: W, height: H });
await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
const missing = await page.evaluate(() => window.ready);
if (missing.length) { console.error(`fonts missing: ${missing.join(', ')}`); await browser.close(); process.exit(1); }
const shot = (t) => page.evaluate((tt) => { window.renderAt(tt); return document.getElementById('cv').toDataURL('image/png').split(',')[1]; }, t);

const stills = A.opt('stills');
if (stills) {
  for (const t of stills.split(',').map(Number)) {
    const f = rel(`frames/${id}-t${t.toFixed(2)}.png`);
    fs.writeFileSync(f, Buffer.from(await shot(t), 'base64'));
    console.log(`CARD ${id} ${variant}: ${f.replace(rel(''), '')}`);
  }
} else {
  const out = A.opt('out', rel(`out/${id}.mp4`)), n = Math.round(C.duration * config.fps), t0 = Date.now();
  fs.mkdirSync(rel('out'), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(config.fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(config.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
  { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    if (!ff.stdin.write(Buffer.from(await shot(i / config.fps), 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log(`CARD ${id} ${variant}: ${n} frames → ${out.replace(rel(''), '')} in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}
await browser.close();
fs.rmSync(html, { force: true });
