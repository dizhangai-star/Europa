// Kit config for this film (see ../../_kit/README.md). Picture comes from Blender (blender/), not engine.html:
// clips/NN-*.js hold timing + captions so the kit's audio, compile and QC tools work unchanged.
// Format: 1920×1080, 24 fps; the picture is rendered 1920×804 (2.39:1, blender/lib/shot.py RES), render.mjs letterboxes.
export default {
  title: 'Europa · 深渊',
  style: 'blender',
  clipDir: 'clips', global: 'CLIP', param: 'clip',
  film: 'out/europa.mp4',
  fps: 24,
  crf: 16,
  samples: 64,          // Cycles samples per frame (+ OIDN denoise); render.mjs --samples overrides
  blackGround: true,    // black sky, the eclipse, the black ocean: check.mjs reports black frames without failing
  soundtrack: 'none',   // no narration; a film-local score (audio/music.mjs, Sprint 4) is laid on the compiled film
  // caps (drawn by tools/overlay.mjs) + srt-only cues (`srt: [[a, b, text]]`: 09's sound credit, drawn on the card itself)
  subtitles: (A) => [...(A.caps || []).map(([a, b, en, zh]) => [a, b, `${en}\n${zh}`]), ...(A.srt || [])],
  narration: null,
};
