window.CLIP = {
  id: '08-abyss',
  duration: 12,                 // 14 → 12 s (Sprint 4.0e, user 2026-10-07): the light is out by ~11 s, then 1 s of black
  shot: 's08_abyss.py',         // Sprint 3.8: locked, looking down the tether; brake off at 1 s, free fall, ×1 → ×3: the light goes out
  caps: [[7.0, 11.6, '100 KM OF WATER BELOW', '下面还有一百公里的海']],
  counter: 'counter08',         // physics.counter08: real s since the breakthrough · depth below the surface · pressure
  counter_out: 12,              // fades out over the last 0.25 s, not cut off by the card (Sprint 4.0e)
  sfx: [],
};
