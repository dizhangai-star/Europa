// Shorts layout + spec loader (Sprint 6.0), shared by shorts.mjs and tools/short-overlay.mjs.
// Square-in-portrait (user 2026-10-09): a SRC×SRC square of the 2.39:1 render (the full picture height; Jupiter's disc,
// ≈ 800 px at 50 mm, stays whole) scaled to 1080×1080 at y = SQ_Y on a black 1080×1920 frame; the hook above it, the
// captions under it. Text stays inside the Shorts safe area: clear of the top bar (~150 px), the right-hand buttons and
// the title/channel band at the bottom (~1600 down).
import { pathToFileURL } from 'node:url';
import { rel } from '../../../_kit/lib/film.mjs';

export const SRC = { w: 1920, h: 804 };           // blender/lib/shot.py RES
export const LAYOUT = {
  W: 1080, H: 1920, SQ: 1080, SQ_Y: 360,
  max: 940,                                        // text width (px)
  hook: { y: 236, lh: 76, font: '600 64px "Cinzel"', track: 6 },
  sub: { y: 306, font: '400 24px "JetBrains Mono"', track: 4 },
  cap: { y: 1500, lh: 50, font: '600 36px "Cinzel"', track: 3 },
};

export async function loadShort(id) {
  const S = (await import(pathToFileURL(rel(`shorts/${id}.js`)).href)).default;
  S.duration = S.segments.reduce((d, s) => d + s.out - s.in, 0);
  return S;
}
