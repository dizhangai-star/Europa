window.CLIP = {
  id: '03-probe',
  duration: 9 + 20 / 24,        // trimmed 12 → 9 s (user 2026-10-05, Sprint 3.3); + the whip's 20 frames (physics.WHIP34.out, Sprint 4.0c)
  shot: 's03_probe.py',         // Sprint 3.3: dawn (Sun 2.3° up behind the camera), the probe's vapour blows the frost out at 1.0 s; tilt up to Ganymede 3.0–8.0 s, 1 s hold; 4.0c: then the whip down toward Jupiter (cut to 04 at its peak)
  caps: [],
  sfx: [[1.0, 'shimmer'], [1.05, 'in', { take: 'catch', v: 0.8 }], [3.2, 'out', { take: 'armOut' }]],   // Sprint 4.1: the frost burst glitters, a breath catches
};
