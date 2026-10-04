# Europa · 木卫二 · 深渊: progress

## State (2026-10-04)
**Sprint 0 (brainstorm → treatment) in progress.** Folder opened; `tools/physics.py` adapted from Io's (Jupiter 12.3°, Io
transits, Io's shadow, horizon sites Conamara / Pwyll, ice + ocean pressure, lens table). Ideas, three directions and
the reuse map in `BRAINSTORM.md`. Git: `github.com/dizhangai-star/Europa` (`main`), `.gitignore` from Io.
Direction, descent, format and title picked by the user 2026-10-04 (Decisions).
**0.2 done 2026-10-04:** `physics.py` has the Conamara sky (Jupiter due west, bands vertical; the Sun sinks into
Jupiter 9.5° up: sunset = eclipse; Io sets into the ice in front of Jupiter; Ganymede 60° up on alternate transits;
wall vs plain light 13×), radiation, shell temperatures, cryobot times, light in water. `TREATMENT.md` draft: the
spectacle list (§2), a 9-clip list ≈ 1:58 (§5), 9:16 climax proposal (§6), questions (§8).

## Next
User answers TREATMENT §8 (length, 9:16 climax, ⚠ items, cryobot power) → lock the clip list. Then 0.3 scaffold copy
from `../Io`, 0.4 Europa maps.

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
- Shot rule (user 2026-10-04): within real physics, as spectacular as possible, above all phenomena Earth can't show;
  tentative/lab-predicted ones only marked ⚠ and with a yes (also in CLAUDE.md).
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
  a dark dot on the dark side). Full Jupiter at Conamara = Sun 3.6° below the east horizon: **ice lit by Jupiter
  alone**, black sky, stars. Drafted: 01–03 at that hour, 04 the following day.
- Ice thickness for the counter and the cards: 20 km (estimates 15–25 km); ice base 242 bar, sea floor 1,596 bar.
- Cryobot: plain design, no agency logos; descent shown as time-lapse (real melt rates make 20 km months-long: the
  counter in days is part of the fear). Rate and heat numbers from `physics.py`, not typed.
- In the ocean: nothing is shown alive (no invented life); the lamp lights only drifting particles and the ice ceiling,
  then the black below it. The fear is what the lamp doesn't reach.
- Which shots form the 9:16 climax (rec.: the lamp switching on in the ocean + the final numbers).
- No narration; EN (Cinzel) + 简中 captions, as Io. Sound: Io's breath on the surface; below, ice creaks, sub-bass
  pressure, a hydrophone hum; silence in the ocean.

## Notes / lessons
(none yet)
