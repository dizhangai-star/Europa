// S1 · "Sunset on Europa" (Sprint 6.0): 04-sunfall from its first settled frame to the tilt into 05, square-cropped
// on Jupiter. Opens on the full Jupiter over the ice (the strongest still in the first second), ends on the red ring
// (loops back to the lit disc). Caption text in {braces} is a Python f-string evaluated in tools/physics.py's namespace
// (tools/short-overlay.mjs), so every number on screen comes from the script. 04's clock (physics.lapse04, SHOT04) is
// the old one: clip second − 14/24 (the whip's frames in front, physics.WHIP34.inn).
export default {
  id: 'S1',
  title: 'Sunset on Europa',
  // segments, in order: clip id, in/out (clip seconds), x = the square's centre in the 1920-wide render (a number, or
  // [[segment second, x], …] eased between keys)
  segments: [{ clip: '04-sunfall', in: 1.0, out: 17.4 + 14 / 24, x: 960 }],   // out = the tilt into 05 starts (physics.TILT45.t0, old clock)
  hook: ['SUNSET ON EUROPA', 'REAL PHYSICS · NOT AI'],
  // [from, to (Short seconds), text]
  caps: [
    [0.3, 4.5, "JUPITER NEVER MOVES IN EUROPA'S SKY"],
    [4.8, 9.3, "{-lapse04(1 - 14/24) / 3600:.0f} HOURS OF SUNLIGHT IN {SHOT04['contact'] - (1 - 14/24):.0f} SECONDS"],
    [10.0 + 14 / 24 - 1.0, 16.8, 'THE SUN NEVER SETS HERE.\nIT FALLS INTO JUPITER.'],
  ],
};
