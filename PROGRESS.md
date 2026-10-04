# Europa · 木卫二 · 深渊: progress

## State (2026-10-04)
**Sprint 0 (brainstorm → treatment → scaffold → maps) done 2026-10-04; next Sprint 1.** Folder opened; `tools/physics.py` adapted from Io's (Jupiter 12.3°, Io
transits, Io's shadow, horizon sites Conamara / Pwyll, ice + ocean pressure, lens table). Ideas, three directions and
the reuse map in `BRAINSTORM.md`. Git: `github.com/dizhangai-star/Europa` (`main`), `.gitignore` from Io.
Direction, descent, format and title picked by the user 2026-10-04 (Decisions).
**0.2 done 2026-10-04:** `physics.py` has the Conamara sky (Jupiter due west, bands vertical; the Sun sinks into
Jupiter 9.5° up: sunset = eclipse; Io sets into the ice in front of Jupiter; Ganymede 60° up on alternate transits;
wall vs plain light 13×), radiation, shell temperatures, cryobot times, light in water. `TREATMENT.md` draft: the
spectacle list (§2), a 9-clip list ≈ 1:58 (§5), 9:16 climax proposal (§6), questions (§8).

Clip list locked by the user the same day (Decisions).
**0.3 done 2026-10-04 (branch `sprint-0.3-scaffold`):** scaffold copied from `../Io` and retargeted to Europa.
- `tools/physics.py`: "Blender local frame" (+Y toward Jupiter along the ground, +X right of it ≈ north at Conamara,
  Z up; `jupiter_local`, `sun_local(elong, dec)`, `alt_az`, `to_local`, `lit_fraction`): the API Io's libs read.
  Checked against `altaz`: Jupiter centre 3.5° up, az 269.4° (due west), radius 6.12°, pole pointing right →
  bands vertical. `--card` → the 09 numbers (2.1× Earth's oceans, 242 / 1,596 bar, lethal in 20 h).
- `blender/lib`: rig, shot, nodes, retarget, prints, lander as is; `jupiter.py` (Europa distance, `europa_shadow`
  replaces `io_shadow`), `sky.py` (`sun(…, dec)`), `astronaut.py`, `globe.py` (still Io's relief/colour; only if a
  view from altitude is needed); `europa_world.py` from `io_world.py`: Europa radius, `europa_body`, lava removed,
  **surface material still Io's placeholder** until Sprint 2.
- `render.mjs`, `preview.mjs`, `compile.mjs` (→ `out/europa.mp4`, silent until `audio/music.mjs` exists),
  `film.config.mjs`, `package.json`, `timeline.js`; `tools/card.mjs` (variant `europa`: EUROPA / 深 渊 + readout),
  `overlay.mjs` (counter still Io's 03 clock → 06's days · depth · temperature · pressure in Sprint 3),
  `timeline.mjs` (head kept, joints empty = hard cuts until Sprint 4), `maps.py` (`jupiter` shared; `io`/`far` →
  `europa` in 0.4). `audio/music-io.mjs` = Io's score kept as a reference only.
- `clips/01…09` from TREATMENT §5 (118 s): durations locked, **caption times provisional** (set in the animatics),
  shot files named but not written (Sprint 3). 09 is the card.
- Smoke tests: `blender/shots/board_astronaut.py --facing jupiter --aimz 1.5` (Cycles, 5.5 s at 40 %): Jupiter on the
  western horizon, bands vertical, suit lit by the Sun behind the camera; `node preview.mjs 09-title 3` card OK.

**0.4 done 2026-10-04 (branch `sprint-0.4-maps`):** Europa maps in `../../_assets/textures/europa/` (index ids
`europa-usgs-mosaic-500m`, `europa-galileo-closeups`; REFERENCES.md "Downloaded for Europa").
- USGS 500 m global mosaic (greyscale only: no USGS colour product for Europa) + 8 Galileo photojournal images
  (Conamara: PIA01403 15 m/px mosaic, 01182 9 m/px cliffs, 00591 rafts; enhanced colour 01127 / 01296 / 26446;
  natural-colour global 19048; ridged plains 01178).
- `tools/maps.py`: `io`/`far` → **`europa`** (site reprojected to the local frame, top = toward Jupiter, right = +X ≈
  north: `blender/textures/src/europa_site_500m.png` 512 km, `europa_wide_1km.png` 2048 km) and **`colour`** (natural
  palette from PIA19048). Georef read from the GeoTIFF keys (centre meridian 180 → 0–360° E, R 1562.09 km).
  **Orientation checked**: Pwyll's ray centre lands on the predicted pixel (x −951 km = south, left); the site map shows
  Conamara's chaos patch beside the Asterius/Agave lineae X, as in PIA01296.
- Numbers for Sprint 2: Conamara ±50 km normalised reflectance 0.66 (p5 0.52, p95 0.88). Natural tints (linear,
  albedo-free, from PIA19048): clean ice (0.872, 0.973, 1.0) · blue polar/plains ice (0.577, 0.791, 1.0) · cream
  (1.0, 0.922, 0.826) · non-ice brown (1.0, 0.716, 0.539) · darkest lineae/chaos brown (1.0, 0.509, 0.324) at 0.77×
  brightness. Conamara itself is mostly the brown units (PIA26446/01127, enhanced, show where).
- Not yet switched: `europa_world.surface()` still tiles Io's PIA02507 (→ PIA01403 at ~15 m/px in Sprint 2);
  `globe.py` `FAR_MAP` still points at Io's `io_far_1km.png` (only if a view from altitude is needed; `europa_wide_1km`
  is the candidate, but its east side is smeared Voyager data).

## Next
Sprint 1 look spike (3 Cycles stills, previews free): Conamara horizon with ¾-Jupiter (Jupiter-lit ice) · Io on the
disc at 135 mm · cryobot lamp in black water (time the water volume). Asset hunt by the user in parallel (REFERENCES.md
"Wanted": W1 Mixamo kneel/stand, W2–W3 ice sounds and hydrophone).

## Sprints (plan, 2026-10-04)
0. Treatment, physics, scaffold. 0.1 ✅ brainstorm + repo · 0.2 physics rows + `TREATMENT.md` (clip list, beat sheet
   of the key clip, sound plan) → user picks length and the 9:16 climax · 0.3 scaffold copy from Io (`blender/lib`
   rig/shot/nodes/jupiter/sky/globe/astronaut/retarget/prints/lander, `render.mjs` `preview.mjs` `compile.mjs`,
   `tools/card.mjs` `overlay.mjs` `timeline.mjs` `maps.py`, `audio/`) · 0.4 maps: USGS Europa global mosaic +
   Galileo Conamara close-ups (public domain) into `../../_assets/textures/europa/`.
1. Look spike (3 stills, Cycles): Conamara horizon with ¾-Jupiter (Jupiter-lit ice) · Io on the disc at 135 mm ·
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
- Fear (user 2026-10-04): **深渊**, with the horizon and Io as the surface half. Horizon (¾-Jupiter fixed on the
  Conamara horizon) → Io crosses Jupiter's face (callback to ep. 2) → down through the ice → the dark ocean; end on the
  ocean numbers.
- Descent and people (user 2026-10-04): a small astronaut on the surface (Io's EMU #12622 + Mixamo, reused); below the
  surface a **code-built cryobot** (melt probe) goes down, time-lapse with a counter (depth / pressure / days), then its
  one lamp in the black water. No open 20 km crack (not real), no human under the ice. Real physics throughout.
- Clip list (user 2026-10-04): TREATMENT §5, 9 clips ≈ 1:58 (horizon · neighbour · the probe · the fall of the Sun ·
  the lid · descent · breakthrough · abyss · title). 9:16 climax = 02 + 04. Jupiter lightning in 04 yes; plume and
  ice glow no. Cryobot 10 kW (1,044 days to 20 km). Radiation fact on the end card, not in 03.
- Jupiter on the horizon (user 2026-10-04): keep Conamara; the text says ¾ of Jupiter, not half (centre 3.5° up,
  radius 6.1°: 16 % of the disc below the ice). Knock-on: at 135 mm the visible disc overflows the 804 px frame, so
  02's lens is open (TREATMENT row C), decided in Sprint 3.
- Title (user 2026-10-04): **木卫二 · 深渊 / Europa · Abyss**.
- Format (user 2026-10-04): landscape 2.39:1 (1920×804 picture, letterboxed, 4K delivery, as Io), **about 2 min**,
  final length set after the clip list. A **9:16 climax cut** as well: 804 px of height can't be cropped to portrait,
  so the climax shots get their own portrait cameras/renders (planned in the treatment, rendered last).

## Notes / lessons
- USGS GeoTIFFs: read the projection centre (GeoKey 3088) — Europa's mosaic is centred on 180°, so its x origin is
  lon 0 E, not −180 (Io's was −180..180). Verify any reprojection on a landmark (here Pwyll's rays), not by eye.
- Photojournal catalog pages are JS-heavy; the description text sits after ">Description<" in the raw HTML. TIFFs:
  `assets.science.nasa.gov/content/dam/science/psd/photojournal/pia/piaNN/piaNNNNN/PIANNNNN.tif` (browser UA).
