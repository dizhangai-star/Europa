window.CLIP = {
  id: '04-sunfall',
  duration: 19 + 8 / 24 + 14 / 24,   // + the whip's 14 frames in front (physics.WHIP34.inn, Sprint 4.0c): the old 0 s is at 0.58 s; + the tilt tail (physics.TILT45, Sprint 4.0d): clock 18 → 19.33 s
  shot: 's04_sunfall.py',       // Sprint 3.4: 50 mm locked; 03's dawn → ×25,000 day → the Sun touches the top limb 10 s, gone 13.5 s (×31 ingress), night in real time: arch, corona, stars, lightning
  spf: 5.9,                   // Sprint 5.0: s/frame at 64 spp, full res, measured (tools/ab.mjs: 7.8 · 5.3 · 5.2 · 5.2 · 5.8); batch.mjs: cheapest first
  caps: [[11.0 + 14 / 24, 17.4 + 14 / 24, 'THE SUN NEVER SETS HERE. IT FALLS INTO JUPITER.', '这里的太阳从不落下，它坠入木星']],
  sfx: [[8.9, 'in', { take: 'holdIn' }], [15.2, 'heartbeat'], [17.2, 'out', { take: 'farOut', far: 0.3 }]],   // Sprint 4.1: held through the Sun's fall (contact 10.58); one beat as the arch comes up; the last breath
};
