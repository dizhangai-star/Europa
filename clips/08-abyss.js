window.CLIP = {
  id: '08-abyss',
  duration: 2.5 + 12,           // 14 → 12 s (Sprint 4.0e, user: the light is out by ~11 s, then 1 s of black); + the head from 07's end pose (physics.SEAM78.head)
  shot: 's08_abyss.py',         // Sprint 3.8: locked, looking down the tether; brake off at 1 s, free fall, ×1 → ×3: the light goes out
  spf: 6.5,                   // Sprint 5.0: s/frame at 64 spp, full res, measured (tools/ab.mjs: head 13 · 9, fall ~6); batch.mjs: cheapest first
  caps: [[2.5 + 7.0, 2.5 + 11.6, '100 KM OF WATER BELOW', '下面还有一百公里的海']],
  counter: 'counter08',         // physics.counter08: real s since the breakthrough · depth below the surface · pressure
  counter_in: 3.5,              // in as the camera settles on the locked view (SEAM78.move), not over the dissolve from 07
  counter_out: 2.5 + 12,        // fades out over the last 0.25 s, not cut off by the card (Sprint 4.0e)
  sfx: [],
};
