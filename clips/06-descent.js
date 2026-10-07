window.CLIP = {
  id: '06-descent',
  duration: 20,
  shot: 's06_descent.py',       // Sprint 3.6, locked 2026-10-06: cutaway, 35 mm, the camera fixed to the probe; depth in ln z, ×2,890 → ×27 M → ×2,890: 34 m → 19,980 m
  spf: 50,                    // Sprint 5.0: s/frame at 64 spp, full res, measured (tools/ab.mjs: milky ~100 to ~9 s, clear ~10 after); batch.mjs: cheapest first
  caps: [],
  counter: 'counter06',         // physics.counter06: days since the head first melted · depth · ice temperature · pressure
  counter_in: 0.5,              // fades in 0.5–0.75 s, as 05's dissolve ends (05's readout gone at 0.25 s; Sprint 4.0e)
  sfx: [],
};
