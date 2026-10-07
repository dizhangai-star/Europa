window.CLIP = {
  id: '07-breakthrough',
  duration: 14,
  shot: 's07_breakthrough.py',  // Sprint 3.7: glow → break (3.5 s) → the 0.134 g drop → the black well → level
  spf: 40,                    // Sprint 5.0: s/frame at 64 spp, full res, measured (tools/ab.mjs: glow 50 · break 47 · 38 · end 26); batch.mjs: cheapest first
  caps: [[8.0, 13.4, 'NO SUNLIGHT HAS EVER REACHED IT', '从没有阳光到过这里']],
  sfx: [[1.6, 'cluster', { d: 1.4, k: 3, v: 0.7 }]],   // Sprint 4.1: the base ice settling over the glow, before the break
};
