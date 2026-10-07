window.CLIP = {
  id: '02-neighbour',
  duration: 15.25,              // 12 → 15.25 s (Sprint 4.0b): + the tail onto 03's framing and dawn (3.45 s, slow sunrise) before the 24-frame dissolve
  shot: 's02_neighbour.py',     // Sprint 3.2: 75 mm locked (4.0b: head zooms in from 01's end, tail out to 03's start), time-lapse ×512: Io enters 1.0 s, Europa's shadow on it ~2.4–7.3 s, sets 10.5 s
  spf: 5.8,                   // Sprint 5.0: s/frame at 64 spp, full res, measured (tools/ab.mjs: 8.0 · 4.0 · 5.5); batch.mjs: cheapest first
  caps: [[6.5, 11.4, 'IO. WE STOOD THERE.', '我们曾站在那里']],
  sfx: [[5.2, 'in', { take: 'armIn', v: 0.9 }], [7.6, 'out', { take: 'sigh' }]],   // Sprint 4.1: watching Europa's shadow on Io; a sigh under the caption
};
