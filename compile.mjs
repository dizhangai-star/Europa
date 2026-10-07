// Film-local compile (copied from Io, Sprint 0.3): every clip in order → the film, with its captions + counter
// (tools/overlay.mjs) and the joints in tools/timeline.mjs, then the score (audio/music.mjs, Sprint 4) under it; no
// music.mjs yet → silent. The kit's compile (plain cuts, no overlay) and mix (clips end to end, loudnorm) are not used.
// Usage: node compile.mjs [--animatic] [--silent] [--out path]
//   --animatic: out/<id>-animatic.mp4 → out/europa-animatic.mp4 (EEVEE / Workbench drafts; 09 is the real card)
// Joints: tools/timeline.mjs (Sprint 4.0: dissolves overlap real frames; TRIM_IN cuts frames off a clip's head, its
// overlay with it; the film = Σ clips − trims − dissolves + head).
// Sound: audio/build/film.wav (the film's exact length) → one gain to −16 LUFS + a −2 dB peak limiter at 4× (192 kHz:
// it catches the intersample peaks, Sprint 4.1: at 48 kHz the AAC came out at −0.9 dBTP) (not
// loudnorm: the eclipse's near-silence gives a loudness range it would answer by switching to dynamic mode and
// lifting the silence). Clip start times (film seconds) → out/timeline.json, subtitles → out/europa.srt.
// Delivery (user 2026-10-03): the film is 3840×2160 — clips upscaled lanczos and kept 4:4:4 through joints and
// overlays, yuv420p only at the final encode (chroma then at the render's full resolution: the eclipse ring stays
// clean); captions, counter and the title card are drawn natively at 4K (--4k). The animatic stays 1920×1080.
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { root, config, clipIds, loadClip, argv } from '../../_kit/lib/film.mjs';
import { HEAD, JOINTS, FADE_OUT, TRIM_IN, layout } from './tools/timeline.mjs';

const A = argv(undefined, ['animatic', 'silent']);
const anim = A.has('animatic');
const out = path.resolve(root, A.opt('out', anim ? 'out/europa-animatic.mp4' : config.film));
const ids = clipIds();
const files = ids.map((id) => path.join(root, 'out', `${id}${anim ? '-animatic' : ''}.mp4`));
const missing = ids.filter((_, k) => !fs.existsSync(files[k]));
if (missing.length) { console.error(`missing: ${missing.join(', ')} (node render.mjs <id>${anim ? ' --animatic' : ''})`); process.exit(1); }
const fps = config.fps;
const C = ids.map((id) => loadClip(id));
const trim = ids.map((id) => TRIM_IN[id] ?? 0);              // frames cut from a clip's head (picture + its overlay)
const len = C.map((c, k) => c.duration - trim[k] / fps);    // the length each clip shows
const [W, H, PIX] = anim ? [1920, 1080, 'yuv420p'] : [3840, 2160, 'yuv444p'];
const k4 = anim ? [] : ['--4k'];
// title card(s): type only, so redrawn at the delivery size instead of upscaled (a few seconds)
const cards = ids.map((id, k) => {
  if (anim || !C[k].card) return null;
  const f = path.join(root, 'out', `.card-${id}.mp4`);
  execFileSync('node', [path.join(root, 'tools/card.mjs'), id, ...k4, '--out', f], { stdio: 'inherit' });
  return (files[k] = f);
});

// caption / counter layers, one per clip that has any (regenerated each time: a few seconds each)
const ov = ids.map((id, k) => {
  if (!(C[k].caps?.length || C[k].counter)) return null;
  const f = path.join(root, 'out', `.overlay-${id}.mov`);
  execFileSync('node', [path.join(root, 'tools/overlay.mjs'), id, ...k4, '--out', f], { stdio: 'inherit' });
  return f;
});
const inputs = [...files], ovIn = ov.map((f) => (f ? inputs.push(f) - 1 : -1));

const f = [];
ids.forEach((id, k) => {
  const cut = trim[k] ? `trim=start_frame=${trim[k]},setpts=PTS-STARTPTS,` : '';
  let s = `[${k}:v]${cut}fps=${fps},scale=${W}:${H}:flags=lanczos,setsar=1,format=${PIX},settb=1/${fps}`;
  if (k === 0) s += `,tpad=start_duration=${HEAD.black}:start_mode=add:color=black,fade=t=in:st=${HEAD.black}:d=${HEAD.fade}`;
  if (FADE_OUT[id]) s += `,fade=t=out:st=${(len[k] - FADE_OUT[id]).toFixed(4)}:d=${FADE_OUT[id]}`;
  if (ovIn[k] >= 0) {                                         // the layer fades with its clip only where captions sit
    f.push(`${s}[p${k}]`);
    const pad = k === 0 ? `,tpad=start_duration=${HEAD.black}:start_mode=add:color=black@0` : '';
    f.push(`[${ovIn[k]}:v]${cut}format=rgba,settb=1/${fps}${pad}[o${k}]`, `[p${k}][o${k}]overlay=0:0:eof_action=pass:format=auto,format=${PIX},settb=1/${fps}[c${k}]`);
  } else f.push(`${s}[c${k}]`);
});
let cur = 'c0', curLen = len[0] + HEAD.black;
const starts = [HEAD.black];
for (let k = 1; k < ids.length; k++) {
  const j = JOINTS[ids[k - 1]] ?? { kind: 'cut' };
  if (j.kind === 'dissolve') {
    const off = curLen - j.d / fps;
    f.push(`[${cur}][c${k}]xfade=transition=fade:duration=${(j.d / fps).toFixed(4)}:offset=${off.toFixed(4)}[j${k}]`);
    starts.push(off);
    curLen = off + len[k];
  } else {
    f.push(`[${cur}][c${k}]concat=n=2:v=1:a=0,settb=1/${fps}[j${k}]`);   // concat resets the timebase; xfade wants equal ones
    starts.push(curLen);
    curLen += len[k];
  }
  cur = `j${k}`;
}

const tmp = path.join(path.dirname(out), `.${path.basename(out)}`);
execFileSync('ffmpeg', ['-y', '-v', 'error', ...inputs.flatMap((c) => ['-i', c]), '-filter_complex', f.join(';'),
  '-map', `[${cur}]`, '-c:v', 'libx264', '-preset', 'medium', '-crf', String(config.crf), '-pix_fmt', 'yuv420p',
  '-r', String(fps), '-movflags', '+faststart', tmp], { stdio: 'inherit' });
fs.renameSync(tmp, out);
[...ov, ...cards].forEach((o) => o && fs.rmSync(o, { force: true }));
let dur = +execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], { encoding: 'utf8' });
const L = layout();
L.clips.forEach((c, k) => { if (Math.abs(c.in - starts[k]) > 1e-3) throw new Error(`${c.id}: layout ${c.in} ≠ compile ${starts[k]}`); });
const t0 = starts.map((s, k) => s - trim[k] / fps);          // the film second of each clip's own t = 0
const timeline = ids.map((id, k) => ({ id, start: +t0[k].toFixed(3), in: +starts[k].toFixed(3), duration: C[k].duration, trim_in: trim[k], joint_out: JOINTS[id]?.kind ?? (k < ids.length - 1 ? 'cut' : 'end') }));
if (!A.opt('out')) fs.writeFileSync(path.join(root, 'out/timeline.json'), `${JSON.stringify({ head: HEAD, timeline, total: +dur.toFixed(3) }, null, 1)}\n`);
// subtitles from the real clip starts (the kit's srt.mjs lays clips end to end: no head, no dissolve → 1 s early)
if (!anim && !A.opt('out')) {
  const ts = (s) => { const ms = Math.round(s * 1000); return `${new Date(ms).toISOString().slice(11, 19)},${String(ms % 1000).padStart(3, '0')}`; };
  const cues = ids.flatMap((id, k) => (config.subtitles(C[k], C[k].timing) ?? []).map(([a, b, t]) => [t0[k] + a, t0[k] + b, t]));
  fs.writeFileSync(out.replace(/\.mp4$/, '.srt'), cues.map(([a, b, t], i) => `${i + 1}\n${ts(a)} --> ${ts(b)}\n${t}\n`).join('\n'));
}
console.log(timeline.map((c) => `${c.id} @ ${c.in.toFixed(2)} s`).join(' · '));
console.log(`${ids.length} clips → ${path.relative(root, out)}, ${dur.toFixed(2)} s`);

if (!A.has('silent') && fs.existsSync(path.join(root, 'audio/music.mjs'))) {
  const wav = path.join(root, 'audio/build/film.wav');
  execFileSync('node', [path.join(root, 'audio/music.mjs')], { cwd: root, stdio: 'inherit' });
  const e = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', wav, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], { encoding: 'utf8' }).stderr;
  const m = JSON.parse(e.slice(e.lastIndexOf('{'), e.lastIndexOf('}') + 1)), gain = -16 - +m.input_i;
  const tmpA = path.join(path.dirname(out), `.a-${path.basename(out)}`);
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', out, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-af', `volume=${gain.toFixed(2)}dB,aresample=192000,alimiter=limit=${(10 ** (-2 / 20)).toFixed(4)}:attack=2:release=60:level=0,aresample=48000`,
    '-c:a', 'aac', '-b:a', '192k', '-t', dur.toFixed(3), '-movflags', '+faststart', tmpA], { stdio: 'inherit' });
  fs.renameSync(tmpA, out);
  console.log(`sound: ${m.input_i} LUFS ${gain >= 0 ? '+' : ''}${gain.toFixed(1)} dB → −16, limited at −2 dB → ${path.relative(root, out)}`);
}
