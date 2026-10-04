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

Clip list locked by the user the same day (Decisions).

## Next
0.3 scaffold copy from `../Io`; 0.4 Europa maps (USGS mosaic, Galileo Conamara close-ups). Asset hunt by the user in
parallel (list in REFERENCES.md "Wanted").

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
- Clip list (user 2026-10-04): TREATMENT §5, 9 clips ≈ 1:58 (horizon · neighbour · the probe · the fall of the Sun ·
  the lid · descent · breakthrough · abyss · title). 9:16 climax = 02 + 04. Jupiter lightning in 04 yes; plume and
  ice glow no. Cryobot 10 kW (1,044 days to 20 km). Radiation fact on the end card, not in 03.
- Title (user 2026-10-04): **木卫二 · 深渊 / Europa · Abyss**.
- Format (user 2026-10-04): landscape 2.39:1 (1920×804 picture, letterboxed, 4K delivery, as Io), **about 2 min**,
  final length set after the clip list. A **9:16 climax cut** as well: 804 px of height can't be cropped to portrait,
  so the climax shots get their own portrait cameras/renders (planned in the treatment, rendered last).

## Notes / lessons
(none yet)
