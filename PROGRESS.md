# Europa · 木卫二 · 深渊: progress

## State (2026-10-05)
**Sprint 2.1 (the `europa_world` ground) done 2026-10-05 (branch `sprint-2.1-ground`), waiting for the user's look at
`frames/ground/ground-sheet.png`. Next: Sprint 2.2, the cryobot.** Sprint 2.0 (01 framing test) done 2026-10-05
(merged, PR #4): 01 = the turn. Sprint 1 (look spike) done 2026-10-05 (merged, PR #3). Sprint 0 (brainstorm → treatment → scaffold → maps) done 2026-10-04. Folder opened; `tools/physics.py` adapted from Io's (Jupiter 12.3°, Io
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

**Sprint 1 done 2026-10-05: look spike, three boards (not clips), Cycles 64 spp, contact sheet
`frames/look/sprint1-looks.png`.** All three work in real light; full-res cost per frame: horizon 14–16 s, Io 11 s,
lamp in water 23 s (the water volume costs little: one homogeneous volume, no ray marching). Film budget ≈ 2,830
frames × ~18 s ≈ 14 h before the cheaper-way ladder (02 locked camera → plate + border; 04 freeze tail).
- `blender/shots/look_horizon.py` (`--view jupiter | away | side | wide`): spike chaos plates (convex polygons,
  ragged cliffs, talus, tilted ridged tops; `physics.CHAOS` film picks) in a hummocky matrix, a lane toward
  Jupiter, the camera on a low knoll; Sun at 178° (down), the ground lit by Jupiter alone through **`jupiter.lamp`**
  (an emissive twin of the disc that only diffuse/glossy rays see, radiance = the Lambert radiance from the Sun's
  direction; the visible disc keeps the camera and the shadows). Without it a 12° lit sphere found by bounce rays
  would be all noise at night. New `europa_world.ice()` (first pass: PIA19048 tints at Conamara's albedos, clean
  blue-white streaked cliff faces, frost specular).
- `blender/shots/look_io.py`: 135 mm, Io (new **`lib/moons.py`**: Io at the same far-scale k as Jupiter and the
  scaled Europa, map `tools/maps.py io_globe` → `io_globe_2k.png`, albedo 1.5 × `P_GEOM_IO` clamped) mid-transit;
  it joins Jupiter's Sun's blocker collection, so **Io's shadow and Europa's own shadow fall on the clouds by
  geometry** (k-scaling about the camera keeps shadows exact).
- `blender/shots/look_lamp.py`: the ice-shell base (undulating, scalloped bump, SSS, specular ≈ 0 under water),
  probe Ø 0.25 m × 3 m on a tether, one 50 W spot, water = `physics.water_rgb()` absorption (R/G/B 0.39 / 0.090 /
  0.0135 per m) + `SEA_SCATTER` 0.02/m, g 0.85, marine-snow point cloud (GN Mesh to Points).
- physics.py new rows: `own_shadow` (Europa's shadow on Jupiter: at the anti-solar point, on the disc for 2.9 h,
  mostly the last hours of the night; umbra 0.16° in a 0.37° penumbra), `io_cast_shadow` (mid-transit, Sun 178°:
  1.85° from Io; Sun 180°: 0.68°), `water_rgb`, `P_GEOM_IO`, `CHAOS`, `SEA_SCATTER`/`SEA_G`/`CRYO_LAMP_W`.

**Findings for the user (Sprint 1):**
1. ⭐ New real spectacle for 02: at night with full Jupiter, **Io crosses the bands with its own black shadow beside
   it, and Europa's shadow (our own) sits on Jupiter too**: three dots of two worlds' making. 02's time-lapse could
   carry all three. **Yes (user 2026-10-05): TREATMENT §2 C2, 02's row.** **Checked online 2026-10-05:** the geometry is the
   everyday shadow transit (Io + Europa shadows together every ~3.5 d; Hubble's 2015 triple transit shows moons with
   their shadows strung out beside them); from Earth a moon and its shadow coincide at opposition and part as the
   phase angle grows, as `io_cast_shadow` gives (seen from Europa they also part as Io leaves the disc centre,
   because Io is 2.7× nearer than Jupiter). ESA's JUICE NavCam simulation (Airbus 2019) shows Europa in front of
   Jupiter with its shadow as a black disc. Nobody has seen Europa's own shadow *from Europa* (no one there), so it
   rests on that geometry, not on a photo: status **real (geometry)**, no ⚠ needed.
   Sources: earthsky.org/astronomy-essentials/transits-of-jupiters-moons-shadow ·
   science.nasa.gov/asset/hubble/jupiter-moon-transit-january-24-2015-0710-ut-annotated ·
   sci.esa.int/web/juice/-/61515-simulated-navcam-view-of-jupiter-and-europa
2. 01: the disc and the walls it lights can't share one frame: a wall faces Jupiter only when the camera looks
   away from it (`--view wide` 14 mm proved it: backs of blocks, a stretched disc). Lit walls need raking light
   (`side`, heading ~125°); facing Jupiter the blocks are silhouettes and the plain is black under a glint path.
   → 01's move must turn (lit walls → the disc) or cut. **User 2026-10-05: decide in Sprint 2, from several more
   test frames (headings, lenses, a turn).**
3. 02 at 135 mm: the 2 km ice horizon is a ruler-straight line (1 px = 0.26 m there): Sprint 2's ground needs
   knobs/ridges on the horizon silhouette (**yes, user 2026-10-05**). Visible disc: Io sits ~5° up mid-transit, the frame shows 6.4° of it.
4. Lamp: looking into the beam = one forward-scatter blob (g 0.85); across the beam reads (probe silhouette with a
   rim, cyan cone, ice ceiling lit blue). Red is gone within metres as physics says. Snow flecks only read inside
   the beam (place them there in 07). Exposure ≈ +4 EV vs 0 for the sunlit-ice scale.
5. Stars (Io's `sky.stars`) look too dense and even at 24 mm night exposures: thin them in Sprint 2.
   (4 and 5: **yes, user 2026-10-05**.)

**Sprint 2.0 (01 framing test) done 2026-10-05, branch `sprint-2.0-framing`: user picked A, the turn.**
`blender/lib/chaos.py` = the spike ground factored out of `look_horizon.py` (same draw order; `extra=` hand-placed
plates). `blender/shots/test01_framing.py`: one ground over az −70..200°, `--views h:lens:ev[:tilt],…` (one still
per view) or `--turn h0:l0:ev0,h1:l1:ev1 --frames N --hold0 --hold1` (eased pan + zoom + exposure ride), `--hero 1`
(a lit mesa at az 150°/600 m, its face 30° off Jupiter; a mesa at az −7°/2.4 km biting the disc's lower-left limb;
one flanking at 27°), stars `--star-density` 0.06 (was 0.35). Frames in `frames/test01/` (git-ignored):
`sweep-sheet.png` (24 mm, headings 170→18), `ends-sheet.png`, `turn.mp4` / `turn-reverse.mp4` / `turn-strip.png`
(150°/24 mm/+1.5 EV → 6°/35 mm/−2.5 EV, 12 s, 25 %, 16 spp: 2.7 s/frame).
- Walls glow only from heading ≳ 125°; with the disc in frame every block is a silhouette and the plain is black.
- Silhouettes beside the disc vanish (black on black); a block **biting the disc's limb** reads, and gives scale.
- The turn passes ~3 s of black between heading 90° and 40° (nothing seen from there faces Jupiter).
- Options shown: A turn walls → disc · B reverse · C cut (01a walls, 01b disc) · D disc only. **A picked** (Decisions).
  For Sprint 3: pan faster through the dark middle (hold ~3 s on the mesa, pan ~5 s, hold ~4 s on the disc), add a slow
  forward drift; the caption lands on the disc.

**Sprint 2.1 (the ground) done 2026-10-05, branch `sprint-2.1-ground`.** `lib/chaos.py` promoted into
**`europa_world.Ground`** (same plate draws, so 2.0's framing and hero plates hold; `look_horizon`, `test01_framing`
switched to it). Board: `blender/shots/board_ground.py` (`--views h:lens:ev[:tilt]`, `--elong`, `--band a:b:s` for a
long lens, `--az0/--az1/--nseg-deg/--rmax`, `--hero 1`); sheet `frames/ground/ground-sheet.png` (01 start / end at night,
02 at 135 mm, 125° night, 04 at 50 mm with the Sun 6° up behind, 90° day). Height field ≈ 3 µs/vertex (7.6 M verts:
~23 s), Cycles stills 3–5 s at 50 %/32 spp.
- **Plates** carry the ridged plains as one field turned (±15°) and shifted with each plate (they fit back together):
  three ridge sets fading along their length + double-ridge fragments (two crests, a trough, 20–70 m): skylines notch.
  Hand-placed plates (`extra`) keep their plains at 30 % (`plains`), so 01's limb-biting mesa keeps its 2.0 skyline.
- **Matrix**: billowy hummocks + a jumble of blocks in three bands (`blocks()`: 300 m cells → 30–200 m blocks 6–30 m
  tall; 60 m → 6–40 m house-size; 8 m → 0.8–5 m boulders), three overlapping grids per band, irregular 7-gons, shards,
  each face its own slope (~80° sheer … ~30° talus), ragged outlines, lumpy tilted tops, 15 % tilted rafts; talus
  aprons are rubble slopes on the matrix (debris ×2.5 there). A **clearing** round the camera (`clear`: no 300-m-band
  blocks within ~400 m, no house-size ones within ~30 m) so the knoll isn't walled in.
- **Lane toward Jupiter**: no plates; matrix and rubble capped under a skyline that rises from −0.3° near the camera to
  +0.6° beyond ~3 km (`lane_cap_deg`), so **02's horizon is a ragged line of far blocks and small mesas** (finding 3)
  and ≤ 21 % of the disc is hidden (16 % at the bare horizon): "¾ above the ice" holds. Day shots toward Jupiter (04)
  see the capped near ground as a flat plain: 04 sets its own cap or foreground plates.
- **Far plates** 6–18 km (own draws) out to a 20 km sector.
- **Masks** → mesh attributes (`plate ridge margin block talus`), read by **`ice()`**: matrix brown ↔ cream laid out by
  a km noise + **PIA01403** (15 m/px, mask only), block tops and talus fresher; plate tops cream ↔ clean ↔ blue-white,
  bright crests, dark brown double-ridge margins; steep faces clean blue-white, streaked (as Sprint 1). Io's placeholder
  `surface()` removed (`board_astronaut` uses `ice()`).
- physics.py `CHAOS` rows: `ridge_sets`, `plate_spin_deg`, `double_az/gap/w/h`, `debris` bands (film picks inside the
  published ranges, comments cite PIA01182/01403, Spaun 1998).
- **Bug found and fixed: MetalRT drops triangles in one 7.6 M-vertex mesh** (holes near the camera showing the sky:
  the "stars in the ground" also in Sprint 2.0's frames). CPU and MetalRT off were clean; `terrain()` now splits into
  ≤ 1 M-vertex ring bands (`max_verts`) and MetalRT renders clean. Lesson in the skill's REALISM.md.
- Open for look-dev in the shots: day exposure (clean cliffs clip at EV 0 with the Sun 6° up), 04's foreground.

## Next
Finding 1 (Io + two shadows in 02): verified, in TREATMENT as C2 and in 02's row (user 2026-10-05).
01's framing test done (2.0, the turn); the ground done (2.1). Next, Sprint 2 builds, one per session: the cryobot
(code-built) · ice-shell interior · under-ice ocean. Asset hunt by the user in parallel
(REFERENCES.md "Wanted": W1 Mixamo kneel/stand, W2–W3 ice sounds and hydrophone).

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
- 02 carries Io's shadow + Europa's own shadow on the bands (user 2026-10-05, TREATMENT C2).
- 01 = **the turn** (user 2026-10-05, finding 2): glowing mesa (~150° from Jupiter) → pan left ~145°, 24 → 35 mm,
  exposure ride −4 EV, slow drift; ends on the disc with a mesa biting its lower limb (scale). TREATMENT 01 row.
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
- MetalRT (Blender 5.2, M4 Pro) lost triangles in one 7.6 M-vertex terrain: split big meshes (≤ 1 M verts per object).
  Test for holes with the ground as a flat emitter over a starfield.
- A skyline cap at one elevation makes the near ground the skyline (a smooth line, then crenellated equal tops): let
  the cap rise with distance so the far rubble forms it.
- Night ground lit by a lit planet: make the planet a light (an emissive twin, `jupiter.lamp`); bounce rays alone
  find a 12° object too rarely. Far bodies (Jupiter, Io, Europa for the shadows) all at one scale k about the camera
  → angles and shadows exact.
- zsh doesn't word-split `$VAR` in a command line: a flags string in a variable runs Blender with one bad argument
  and prints nothing; write the flags out (or use an array).
- USGS GeoTIFFs: read the projection centre (GeoKey 3088) — Europa's mosaic is centred on 180°, so its x origin is
  lon 0 E, not −180 (Io's was −180..180). Verify any reprojection on a landmark (here Pwyll's rays), not by eye.
- Photojournal catalog pages are JS-heavy; the description text sits after ">Description<" in the raw HTML. TIFFs:
  `assets.science.nasa.gov/content/dam/science/psd/photojournal/pia/piaNN/piaNNNNN/PIANNNNN.tif` (browser UA).
