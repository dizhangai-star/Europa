# Europa · 木卫二 · 深渊: progress

## State (2026-10-04)
**Sprint 0 (brainstorm → treatment) in progress.** Folder opened; `tools/physics.py` adapted from Io's (Jupiter 12.3°, Io
transits, Io's shadow, horizon sites Conamara / Pwyll, ice + ocean pressure, lens table). Ideas, three directions and
the reuse map in `BRAINSTORM.md`. Git: `github.com/dizhangai-star/Europa` (`main`), `.gitignore` from Io.
Direction, descent, format and title picked by the user 2026-10-04 (Decisions).

## Next
0.2 Physics rows the treatment needs (below), then `TREATMENT.md` with a draft clip list for ~2 min; the user sets
the final length from the clip list. 0.3 Copy the scaffold from `../Io`.

## Sprints (plan, 2026-10-04)
0. Treatment, physics, scaffold. 0.1 ✅ brainstorm + repo · 0.2 physics rows + `TREATMENT.md` (clip list, beat sheet
   of the key clip, sound plan) → user picks length and the 9:16 climax · 0.3 scaffold copy from Io (`blender/lib`
   rig/shot/nodes/jupiter/sky/globe/astronaut/retarget/prints/lander, `render.mjs` `preview.mjs` `compile.mjs`,
   `tools/card.mjs` `overlay.mjs` `timeline.mjs` `maps.py`, `audio/`) · 0.4 maps: USGS Europa global mosaic +
   Galileo Conamara close-ups (public domain) into `../../_assets/textures/europa/`.
1. Look spike (3 stills, Cycles): Conamara horizon with half-Jupiter (Jupiter-lit ice) · Io on the disc at 135 mm ·
   cryobot lamp in black water under the ice ceiling (time the water volume: the one unknown cost).
2. Builds: `europa_world.py` (ice plain, double ridges, lineae, chaos blocks, colour from the mosaic), the cryobot
   (code-built), ice-shell interior (melt channel, refrozen ice, bubbles), under-ice ocean (ceiling, particles).
   Astronaut and Mixamo idle reused from `../../_assets`.
3. Shots: action + animatic + 3-still Cycles check → locked, one shot per session.
4. Whole-film animatic (2.39:1) + joints + captions/counter; score + sound cut to it.
5. Batch render (overnight, resume) → 4K compile, srt, poster; then the 9:16 climax cut (own portrait cameras).

## Decisions (locked)
- Fear (user 2026-10-04): **深渊**, with the horizon and Io as the surface half. Horizon (half-Jupiter fixed on the
  Conamara horizon) → Io crosses Jupiter's face (callback to ep. 2) → down through the ice → the dark ocean; end on the
  ocean numbers.
- Descent and people (user 2026-10-04): a small astronaut on the surface (Io's EMU #12622 + Mixamo, reused); below the
  surface a **code-built cryobot** (melt probe) goes down, time-lapse with a counter (depth / pressure / days), then its
  one lamp in the black water. No open 20 km crack (not real), no human under the ice. Real physics throughout.
- Title (user 2026-10-04): **木卫二 · 深渊 / Europa · Abyss**.
- Format (user 2026-10-04): landscape 2.39:1 (1920×804 picture, letterboxed, 4K delivery, as Io), **about 2 min**,
  final length set after the clip list. A **9:16 climax cut** as well: 804 px of height can't be cropped to portrait,
  so the climax shots get their own portrait cameras/renders (planned in the treatment, rendered last).

## To decide in the treatment (recommendations)
- Surface light: Io visible on the disc only when Jupiter is nearly full (it is lit like Jupiter; on a crescent it is
  a dark dot on the dark side). Full Jupiter at Conamara = Sun ~3.5° below the opposite horizon: **ice lit by Jupiter
  alone** (≈ 113× full moonlight), black sky, stars. Rec.: the whole surface half at that hour.
- Ice thickness for the counter and the cards: 20 km (estimates 15–25 km); ice base 242 bar, sea floor 1,596 bar.
- Cryobot: plain design, no agency logos; descent shown as time-lapse (real melt rates make 20 km months-long: the
  counter in days is part of the fear). Rate and heat numbers from `physics.py`, not typed.
- In the ocean: nothing is shown alive (no invented life); the lamp lights only drifting particles and the ice ceiling,
  then the black below it. The fear is what the lamp doesn't reach.
- Which shots form the 9:16 climax (rec.: the lamp switching on in the ocean + the final numbers).
- No narration; EN (Cinzel) + 简中 captions, as Io. Sound: Io's breath on the surface; below, ice creaks, sub-bass
  pressure, a hydrophone hum; silence in the ocean.

## Physics rows still to add to `tools/physics.py` (0.2)
- Sun elevation/azimuth at Conamara against elongation (when is Jupiter full, how long the Sun stays down).
- Io transit timing within the Europa day; its phase on the disc; the shadow's place.
- Light in ice: sunlight gone within ~metres; what the lamp reaches in ice and in water.
- Cryobot: melt rate for a given power → days to 20 km; ice temperature profile (≈ 100 K at the top, 273 K at the base).
- Ocean: pressure and temperature at the ice base, depth to the sea floor.

## Notes / lessons
(none yet)
