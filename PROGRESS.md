# Europa · 木卫二 · 深渊: progress

## State (2026-10-09)
**DONE 2026-10-09: *Europa · 木卫二 · 深渊* delivered, Sprint 5.3 (branch `sprint-5.3-deliver`), signed off by the
user, merged.** `out/europa.mp4` · `out/europa.srt` · `out/poster.png` (= candidate b, 02 at 6.5 s, Io + shadow on
the disc; user's pick). User 2026-10-09: film accepted as is; **`frames/` (≈ 4.3 GB) kept until Sprint 6's 9:16 cut is
done**; Sprint 6 (9:16) stays planned, start on the user's word. REFERENCES "Delivered" + root CLAUDE.md entry added.
- **5.2 renders done** (user, 2026-10-07 → 10-09): all 8 clips, frame counts = animatics (2,844). Measured s/frame:
  01 5.1 · 02 4.5 · 08 6.3 · 04 5.4 · 03 15.5 · 07 ≈ 44 then 26.8 · 06 ≈ 100 milky → 13.8 clear · 05 84.7.
  Three Metal **GPU out-of-memory** crashes (07 at f258, 06 at f339, 05 three times at frame 0 right after 06's crash,
  then fine on a fresh start); every one resumed cleanly. QC: per-frame mean luma of every clip vs its animatic; the
  only spikes (06 f74/75, f342) are in the animatic too (06's designed time-lapse flicker); no seam jump.
- `node compile.mjs` → `out/europa.mp4` 3840×2160, 24 fps, **122.75 s**, 157 MB, h264 yuv420p + AAC 48 k (2:41 min);
  starts as the animatic (01 @ 1.00 · 02 @ 13.00 · 03 @ 27.25 · 04 @ 37.08 · 05 @ 56.50 · 06 @ 68.75 · 07 @ 87.75 ·
  08 @ 101.25 · 09 @ 115.75); `out/europa.srt` 6 cues (as Sprint 4.0).
- `check.mjs`: **−16.4 LUFS, TP −1.7 dBTP**; silence 47.7 + 4.6 s (04: music dead at first contact, intended); black
  0–1.13 (head), 6.96–7.63 (01's dark pan mesa → disc, same in the animatic), 32.46–37.00 (03's tail + whip), 50.04–57.63
  (04 after the Sun is gone + tilt), 108.92–end (08's black + card): all intended. Only FAIL "duration −2.75 s" = the
  kit's end-to-end layout (no head, no dissolves), as in Io.
- Joints in the final film (−2 f / mid / +1 f after each): all as designed.
- Poster candidates (render frame ×2 lanczos, letterboxed, no caption) in `out/poster-candidates/`: a 04 17.5 s red
  ring · b 02 6.5 s Io + shadow (chosen) · c 04 12.5 s arch over the ice · d 07 3 s breakthrough.

**Sprint 5.1 (batch + 09 credit) done 2026-10-07, branch `sprint-5.1-batch`. Next: 5.2, the user starts the renders.**
- `batch.mjs` (from childhood-desktop's, film-local): default = every clip without `out/<id>.mp4`, **cheapest first by
  `spf` × frames** (09 card · 01 · 02 · 08 · 04 · 03 · 07 · 06 · 05); ids given (`08 2`, NN or bare numbers) render in
  that order. Per clip as `render.mjs`: `samples` (else 64), `freeze`, `--persist 1`, `--resume 1`, the letterbox pad,
  4:4:4 masters; 09 via `tools/card.mjs` (compile redraws it at 4K). Truncated PNGs (no IEND) deleted on start; a
  failed clip is logged and the batch goes on; `--until HH:MM` stops launching and kills the running Blender then;
  `caffeinate -is`; progress every 24 frames with s/frame and the clip's finish time; `out/batch-report.md` after
  every clip, `logs/batch-<stamp>.log` full output; frames kept (`--clean` deletes). `--dry` = the plan with
  estimated hours and finish times (`out/batch-report-dry.md`): **≈ 21 h from now** (01 ≈ 30 min … 05 ≈ 6.9 h).
- `shot.run`: a `FRAME n t` line per saved frame (`render_write` handler); `SHOT` now counts only frames rendered in
  this run (a resume skips the ones on disk).
- Test (real 08 settings, frames kept for 5.2): `batch.mjs 08 --until 17:40` → stopped at 16/348 in 3.1 min (head
  frames 10.4 s; 5.0 measured 13 · 9), `batch.mjs 8 --until 17:43` → resumed at frame 17, stopped at 33/348; no
  truncated frame, no errors; PSNR frame-to-frame across the seam 16→17 32.8 dB between its neighbours' 34.1 / 31.9
  (moving camera; no jump). Frames ≈ 1.5 MB → ≈ 4.3 GB for the film. `batch.mjs 09` → `out/09-title.mp4` (168 fr, 4 s).
- **09 credit: dropped (user 2026-10-07)**, replacing 5.0 plan ②: no credit on the card or in the srt; every credit
  (ice cracks CC BY 3.0, astronaut CC BY 4.0, Jupiter map, NASA/USGS, CC0 sounds) goes in the **YouTube description**,
  ready to paste in REFERENCES.md "Credits for the YouTube description". A credit line was tried on the card (`card.mjs`
  third line + an srt-only cue) and reverted; 09 is as locked in 3.9, `out/09-title.mp4` redrawn.
- 5.2 commands: `node batch.mjs --dry` · `node batch.mjs` · `node batch.mjs --until 08:00` · `node batch.mjs 08 02` ·
  `cat out/batch-report.md`. Rerun = resume. No previews while it renders.

**Sprint 5.0 (cost ladder) done 2026-10-07, branch `sprint-5.0-ladder`: nothing passes, every clip renders at 64 spp.**
`tools/ab.mjs` (new): full-res stills per variant, one Blender run each at `--persist 1` (as the batch), seconds per
still, PSNR vs the reference (whole + centre 960×402), **mean luma** of both, zooms ref | variant | |diff|×8
(`frames/ab/<id>-fNNNN.png`), report `frames/ab/<id>.md`. `shot.run` now sets persistent data before stills too and
prints `STILL f s`. Bar: ≥ ~48 dB and no visible change.

| clip | 32 spp vs 64 (dB, whole / inner) | verdict | s/frame at 64 (measured) | frames | time |
|---|---|---|---|---|---|
| 01 | mesa 43.4/40.4 · 45.8 · 55.2/49.5 | 64 | 6.2 | 288 | 30 min |
| 02 | disc 53.2/50.9 · 53.3 · tail 45.1/44.9 | 64 (32 only on the disc: −6 min) | 5.8 | 366 | 35 min |
| 08 | head 41.7/39.4 · 42.5 · fall 57.7 · 59.4 | 64 (32 after 2 s: −10 min) | 6.5 | 348 | 40 min |
| 04 | 48.4 · day 40.5/44.0 · 40.8 · 49.3 · 54.2 | 64 | 5.9 | 478 | 47 min |
| 03 | ground 42.6 · 42.2 · 41.8 · sky 54.7 · 74.0 | 64, motion blur kept | ground ~30, sky ~4 | 236 | 1.1 h |
| 07 | 44.1 · 44.1 · 49.4 · end 43.8/41.5 | 64 | 40 | 336 | 3.7 h |
| 06 | milky 38.2 · **28.6** · clear 44.9/40.6 | 64; vbounces 64 = same picture (54–66 dB), no faster | milky ~100, clear ~10 | 480 | 6.7 h |
| 05 | 40.0 · 37.5 · 38.6 · 31.9/30.8 | 64 | **80** (est. was 60) | 312 | 6.9 h |
| **all** | | | | 2,844 | **≈ 21 h** |

- 06 at 32 spp: whole frames brighten/darken (f145 mean luma 103.7 → 110.9; the neighbours 107.0/106.2 at 64): motion
  blur's time sampling (shutter 1.0, bands crossing the glow) is short, and the denoiser can't hide a level shift.
- 03 is far cheaper than estimated (2.6–3.9 h → 1.1 h): once the tilt leaves the ground it's ~4 s/frame. Motion blur
  off only matches before the burst (54.9/49.5 dB at 0.5 s): −6 min, not worth it.
- 08's black tail can't be frozen: the last blue speck is still there and moving at 14.4 s (YMAX 31).
- Measured s/frame now in each clip as `spf` (batch.mjs sorts by spf × frames: 01 · 02 · 08 · 04 · 03 · 07 · 06 · 05).
Next: **5.1** (batch.mjs + the 09 credit line): done, see above.

**Sprint 5 planned 2026-10-07 (user), branch `sprint-5.0-ladder`; next: 5.0.** User: ① cost ladder first; ② a small
credit line on the 09 card (Andrew5DMII, Freesound 146419, CC BY 3.0) + an srt cue; ③ render **cheapest clip first**;
④ the 9:16 cut → Sprint 6; renders started by the user any time (day or night) with the commands below. Budget before
the ladder ≈ 20–23 h at 64 spp (01 288 fr ≈ 40 min · 02 366 ≈ 40 min · 03 236 ≈ 2.6–3.9 h · 04 478 ≈ 50–55 min ·
05 312 ≈ 4.5–5 h · 06 480 ≈ 6.5–7 h · 07 336 ≈ 3.5–4 h · 08 348 ≈ 1 h · 09 card); disk 224 GB free.
- **5.0 ladder** (previews only): full-res A/B, PSNR whole + inner crop + side-by-side zoom (Io: 32 vs 64 spp = 54 dB;
  reject < ~48 dB or a visible change). 06: 32 spp, volume bounces 128 → 64 (milky ~4 s, 6 s; clear 19.5 s) · 05: same
  (0.5 · 5 · 9 s) · 07: 32 spp (2 · 3.6 s · end) · 03: 32 spp, motion blur only on frost/whip frames (1.2 · 5 · 9.5 s) ·
  01/02/04/08: 32 spp (02's test = Io's eclipse rim); 08 black tail `freeze` from ~13.6 s (04's tail moves: no freeze).
  05/06 at 32 spp also a 24-frame slice (`--start/--end`) for flicker. Results → `clips/*.js` (`samples`, `freeze`),
  re-timed s/frame → new budget table (+ a file batch can sort by).
- **5.1** `batch.mjs` from `../../childhood-desktop/batch.mjs` (per clip: `samples`, `--freeze`, `--persist 1`,
  `--resume 1`; 09 via `tools/card.mjs`; encode as `render.mjs`; order = cheapest first; `--dry`), `FRAME n t` in
  `shot.run`; 09 credit line (`tools/card.mjs` third line, mono ~4.5 px, dim, with the readout's fades; before/after
  still for the user) + srt cue; test `batch.mjs 08 --until` → resume.
- **5.2 render** (user runs, any time; rerun = resume): `node batch.mjs --dry` · `node batch.mjs` · `node batch.mjs
  --until 18:00` · `node batch.mjs 08 02` · `node render.mjs 08-abyss --resume --keep --silent` · `cat
  out/batch-report.md`. No previews while the GPU renders. After each batch: frame counts = animatic, 3-frame strips vs
  the animatic, 4 fps flicker look.
- **5.3 deliver**: `node compile.mjs` (4K, score, srt), `check.mjs`, loudness, joints, poster (candidates: 02 Io on the
  disc · 04 red arch · 07 breakthrough), REFERENCES/PROGRESS/root CLAUDE.md, merge on the user's sign-off.
**Sprint 4.1 (score + sound) done 2026-10-07, approved by the user, branch `sprint-4.1-score` (PR #24):** user: synth
only (no ice/hydrophone recordings; W1–W3 closed), CC0 + CC-BY allowed if recordings come later, the physics arc.
`audio/music.mjs` (engine from Io's: syn, takes, helmet; seed 20261007) + `physics.py --sound` (cue times in clip s:
02 Io in/set/eclipse, 04 contact/gone/tilt/black, 05 shut, 06 depth marks, 07 break/brake/stop, 08 release/blue/gone +
the fall for the hum's 1/r). Surface = vacuum: breath (Io's recorded takes, 9) + music in A (Io's chords quoted: Am9 on
EUROPA, the diamond glints as Io enters, A add9 under "WE STOOD THERE"); music dead at first contact, one heartbeat
(clip 15.2), back with the tilt into the ice as a D sub swell. Ice/water bus: probe hum on D2 (muffled when the front
shuts, receding at 1/r in 08), cracks, 06's crackle until the brittle lid ends (3 km) then silence, the break
(a crack slowed into a boom, the rush), the tether brake's groan + clank; all out with the light
(08 gone 13.59 s); 09 one held D4. Directed cues in the clips' `sfx`. `out/europa-animatic.mp4` 122.75 s: −16.7 LUFS,
TP −1.2 dBTP, silence 47.7–52.3 s (contact → heartbeat) and 114.95–116.2 s (black before the card) as intended.
**v2 (user 2026-10-07): the synth cracks' sine "pew" read as 80s/90s electronics ("biu biu") → recorded lake-ice
cracks** (Andrew5DMII, Freesound 146419, CC-BY 3.0, user-downloaded to `_assets/audio/ice/`; 24 onsets measured, its
16–22 Hz "booms" unusable): a random take per crack, size → playback rate (bigger = slower, lower), big ones + a ×0.3
copy for the body; creaks in 05/07 → small crack clusters; synth bubbles dropped; the synth crack stays as the fallback.
The brake's synth metal groan and the probe hum kept (user: "good enough"); no extra melt/jet layer under 05–07 (user).
compile's limiter now runs at 4× (192 kHz): the AAC's true peak −0.9 → −1.7 dBTP. Animatic −16.4 LUFS.
**Credit due at delivery: Andrew5DMII (Freesound 146419, CC-BY 3.0) on the end card / srt.** Next: merge; then
Sprint 5 (batch render).
**Sprint 4.0e (whole film v3) 2026-10-07, branch `sprint-4.0e-film`, waiting for the user's look:** 08 → 12 s (user:
the light out by ~11 s, 1 s of black, then the card; caption 7.0–11.6 s), 05→06 kept; counters swap inside the 05→06
dissolve (new `counter_out`) and 08's fades before the card. `out/europa-animatic.mp4` **122.75 s**. QC: layout =
compile, captions clear of the cuts. Next: user sign-off → merge; then 4.1 score. See the 4.0e section below.
**Sprint 4.0d (04→05 tilt into the ice) done 2026-10-07, approved by the user, branch `sprint-4.0d-tilt` (PR):**
after the caption 04 tilts down (physics.TILT45, up to 15°/s): the red arch and the stars slide up and out over the
black ice, the frame goes black at clock 19.03 s; a 12-frame dissolve on black; 05 opens 3 s early, 5 m up in black ice,
coming down at 04's screen speed into the lamp's glow and settling on its locked first frame. 04 18.58 → 19.92 s, 05 10 →
13 s, film **121.96 s**. Joint clip `out/04-05-tilt-joint.mp4`. See the 4.0d section below. Next: 4.0e.
**Sprint 4.0c (03→04 whip) done 2026-10-07, branch `sprint-4.0c-whip` (PR):** 03 holds on Ganymede to 9 s, then whips
down toward Jupiter (20 frames, accelerating to 143°/s; user: half v2's speed); the cut falls at the peak as the tripod
and the lit ground smear into frame; 04 opens on a smeared Jupiter that snaps and settles onto its locked frame in 14
frames (04's clock unchanged, from 0.58 s). 03 9 → 9.83 s, 04 18 → 18.58 s, film 118.13 s. Continuity: A (04 as locked). Next:
**4.0d** (04→05 tilt into the ice). See the 4.0c section below.
**Sprint 4.0b (shot 02's head + tail) done 2026-10-06 (merged, PR #20):** 01's sky re-timed to 02's
first frame (user: C; Io now above the disc in 01, the hard cut 01 → 02 differs by 0.06/255); 02 opens on 01's next
frame and zooms in; its tail zooms out, cranes to 03's spot and runs the clock to 03's dawn, slowing through the
sunrise, so the 24-frame 02→03 dissolve only brings in the probe and the astronaut. 02 is 12 → 15.25 s. Waiting for
the user's look at the whole-film animatic; then 4.0c (03→04 whip). See the 4.0b section below.
**Sprint 4.0 (whole-film animatic) in progress 2026-10-06, branch `sprint-4.0-animatic`.** Hard-cut baseline 117.0 s;
edit-level joints in → `out/europa-animatic.mp4` **113.2 s** (2,717 frames). Next: **4.0b = shot 02's new head + tail** (new
session), then 4.0c (03→04 whip), 4.0d (04→05 tilt into the ice). See the 4.0 section below.
**Sprint 3.9 (09, title card) done 2026-10-06, 09 locked by the user (branch `sprint-3.9-title`): kicker dropped
(title block re-centred, EUROPA at y 153 on the 640×360 grid), English readout ends "… IN 20 HOURS ON THE ICE" (= 地表),
held 1 s longer (both gone by 5.5 s, clip 6 → 7 s; film 116 s). No Blender: `out/09-title-animatic.mp4` is the real
card (168 frames in 1.4 s). All nine clips locked → next: Sprint 4 (whole-film animatic + joints + score).**
**Sprint 3.8 (shot 08, abyss) done 2026-10-06, 08 locked by the user (not rendered; branch `sprint-3.8-shot08`):
brake off, real time → ×3, the light goes out at ~11 s under the caption; counter time · depth · bar; ≈ 40–50 min at
64 spp. Next: 3.9 = 09 (title card), then Sprint 4 (whole-film animatic).**
**Sprint 3.7 (shot 07, breakthrough) done 2026-10-06, 07 locked by the user (not rendered; branch
`sprint-3.7-shot07`, merged, PR #16): physics (`tube07` 351 m, `drop07`), the tube board (black from below; user: black well), volume
base ice, `s07_breakthrough.py`, animatic v3, Cycles check, ≈ 3.5–4 h at 64 spp. Next: 3.8 = shot 08 (abyss).**
**Sprint 3.6 (shot 06, descent) done 2026-10-06, 06 locked by the user (not rendered; branch `sprint-3.6-shot06`).
The phone draft built and rendered as written; added an end exposure ride (+5 → +2 EV, 12–16 s), shutter 1.0 (the
user: soften the bands' flicker) and right-aligned counter columns. Next: 3.7 = shot 07 (breakthrough), now with the
open water tube above the probe (user: use it).** Sprint 3.5 (shot 05, the lid) done 2026-10-05, 05 locked by the user (not rendered; core as
built, EV ride +3 → +5.5, clock as built; merged, PR #13). Sprint 3.4 (shot 04, the fall of the Sun) done, 04 locked (merged,
PR #12). Sprint 3.3 (shot 03, the probe) done, 03 locked (merged,
PR #11). Sprint 3.2 (shot 02, Io sets) done, 02
locked (merged, PR #10). Sprint 3.1 (shot 01, the turn) done, 01 locked (merged, PR #9). Sprint 2.4 (the under-ice ocean) done, approved and merged (PR #8). Sprint 2.3 (the ice-shell interior) done, approved and merged (PR #7). Sprint 2.2 (the cryobot)
done, approved and merged (PR #6).
Sprint 2.1 (the ground) done and
merged 2026-10-05 (PR #5). Sprint 2.0 (01 framing test) done 2026-10-05
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

**Sprint 2.2 (the cryobot) done 2026-10-05, branch `sprint-2.2-cryobot`.** No ready-made model exists (asset index,
Blend Swap, NASA 3D, Sketchfab searched; REFERENCES W4 closed): code-built from the real concepts (REFERENCES "Cryobot
design sources"). **`blender/lib/cryobot.py`** `build(sc, P, loc, tether, pucks_above, open, lamp, lamp_cone)`: origin
at the nose tip, +Z up the probe, +X = lamp port. All sizes from **physics.py `CRYO_LEN`, `CRYO_SECTIONS`** (head 0.30 ·
bay 0.35 · swim 0.10 · heat 0.85 · vault 0.45 · tail 0.95 = 3.00 m), `CRYO_JETS`, `CRYO_TETHER_D`, `CRYO_PUCK(_KM)`,
`SWIM_*`; `physics.py` prints the layout row.
- One lathed hull (hard seams = duplicated rings): copper melt head 3 mm wider than the body, 6 + 1 jet nozzles, seam
  grooves with screw rings; brushed titanium (anisotropic round the axis), **heat section bead-blasted** (breaks the long
  tube); lamp port boss tilted 25° down with a sapphire window (emission = lamp W / port area when on: blinding at
  +4 EV, as it should be), camera dome, three sample-inlet slots. **No glow on the head** (it runs at ~0–100 °C).
- **Swimmers** (⚠ concept, user yes 2026-10-05): 2 tiers × 25 radial wedges whose backs are the hull at the package;
  pale satin paint, dark sensor tip at the inner end; each has `['rest']` (stowed matrix) for the shots to key.
- **Pucks**: Ø 0.20 × 0.07 m, threaded on the tether (film pick); the top one sits in the open top, dropped ones stay
  on the tether (they freeze into the hole: 05's payoff). Tether Ø 5 mm, Kevlar yellow.
- Boards: `blender/shots/board_cryobot.py` (dark studio, `--views full,nose,tail,open[,top]`, `--lampoff`, `--open`);
  `look_lamp.py` now uses the cryobot (`--lampaz` port azimuth, `--open`, `--cam`, `--aim`; `--lampdown` gone: the port
  tilt is the model's). Sheet `frames/cryobot/cryobot-sheet.png` (studio ×4 at 40 %/32 spp ≈ 1 s each; water wide and
  close at 40 %/64 spp ≈ 3 s).
- For the shots: in water the hull is nearly black except where the beam's scatter falls (07 will want the port
  turned partly toward the camera or the swimmers in the beam); looking at the port from ≲ 2 m blows out at +4 EV.

**Sprint 2.3 (the ice-shell interior) done 2026-10-05, branch `sprint-2.3-shell`.** **`blender/lib/shell.py`**
`build(sc, P, depth_m, cut, half, below, above, face, travel, sigma, similar)` + `key_depth(sh, P, frame, depth_m)`:
the probe's frame is the world (nose at z = 0); the ice hangs on `root` (z = nose depth, so ice-local z = −depth) and
slides past a following camera when 06 keys it. Board `blender/shots/board_shell.py` (`--depth`, views `probe lid nose
inside beam`, each with its own EV offset and port azimuth; `--cut --face --sigma --aniso --pucks`); sheet
`frames/shell/shell-sheet.png` (row 1: 30 m down probe · lid · inside · beam; row 2: 3 km inside · beam, 15 km inside ·
beam; row 3: full-res 30 m lid crop + nose).
- physics.py new rows (all printed): **pure-ice absorption** (Warren & Brandt 2008 table, downloaded: R/G/B
  0.29 / 0.058 / 0.0054 per m, e-fold 3 / 17 / 186 m), `N_ICE`/`N_WATER` (ice→water 1.017), **pores** `pore(z)`
  (film picks inside model ranges: φ 0.2 % under the regolith, e-fold 0.8 km, floor 2e-6; σs = 1.5 φ/r, g 0.75: σs
  5.8/m at 20 m, 1.7 at 1 km, 0.14 at 3 km, 0.006 at 10 km), `BRITTLE_KM` 3 (open cracks above), veins/sills of
  refrozen salty water (`VEIN_*`), porosity bands (`BAND_*`), `CRACKS_PER_M3`; **`refreeze(z)`**: radial enthalpy
  conduction (k = 651/T) of the melt column → the hole shuts 2.0 h ≈ 1.3 m above the probe near the top, 2.2 h / 1.6 m
  at 3 km, 6.8 h / 6 m at 15 km, ~98 h / ~110 m at 19.5 km (walls not pre-warmed: lower bounds). `cryo_speed(z)` split
  out of `cryobot()` (its rows unchanged).
- Look: all **homogeneous volumes** (a textured volume cost 4×): the ice (σs a keyable value per depth), lens-shaped
  sheets that add scatter (flat porosity bands → strata on the cut face and layers in the glow; steep veins / flat
  sills → deep down the only thing the beam finds), the hole bored out of all of them by one world-fixed cylinder (live
  Boolean), melt water (pocket + open column narrowing as `refreeze` says), clear refrozen column with the tether and a
  line of gas/brine beads on its axis (shown only above the front), open cracks (air films, TIR) above 3 km. Only
  light: the probe's lamp. Near-surface shots are a **cutaway**: the box's −y face is a polished ice face `cut` m in
  front of the axis (in 6/m ice a camera sees centimetres); deep shots put the camera inside (clear ice).
- **Cost**: 30 m down, full res 64 spp: **66 s/frame** (05's 240 frames ≈ 4.4 h before the cheaper-way ladder);
  3 km ≈ 4 s, 15 km ≈ 3 s per still at 40 %/32 spp (≈ 6× that at full res). Scene build ≈ 6 s (`refreeze` ≈ 3 s).
- Cycles warns "Maximum number of closures exceeded: 66 > 64" with the shell (not with the cryobot boards): it sizes
  closures for overlapping volumes; frames are clean. Watch for it if many sheets overlap.

**Findings for the user (Sprint 2.3):**
1. Near the surface the ice is **milky**: the probe is a lantern buried in it. White core at the lamp, then a cyan-blue
   halo metres wide (red is absorbed over the long scattered paths); the probe's body shows as a dark rod against its own
   glow, the strata of the cut face cross it (sheet row 1). At ~3 km it clears into a beam in dark ice; at 15 km it is
   black, the beam finding only refrozen veins (row 2). 06's time-lapse could ride exactly that: glow → beam → dark.
2. **The freezing itself is nearly invisible** (ice and water differ by 1.7 % in index; the front is only 1.3 m behind
   the probe near the top). What reads in 05: the clear refrozen column above the probe (a dark rod in the glow) with the
   tether locked in it; a dropped puck frozen into it would make "no way back" concrete (Tunnelbot drops pucks: real).
   **Proposal for 05: show a puck release and the column closing over it.** **Yes (user 2026-10-05).**
3. Porosity is unknown; the film pick (0.2 %) decides milky vs glassy. Lower φ = see the probe through metres of ice
   (less glow, more "glass"); higher = only the glow. **Keep 0.2 % (user 2026-10-05).**

**Sprint 2.4 (the under-ice ocean) done 2026-10-05, branch `sprint-2.4-ocean`.** Water reuse checked first: the
three.js water upgrade (imagnation `clips/aegean.js`, session "Three.js 水质感对比", 2026-10-04) is a sunlit-surface
shader (sky reflection, Sun glint, caustics on sand); nothing of it applies under 20 km of ice (no sky, no Sun, no free
surface). The under-ice water stays Sprint 1's homogeneous volume (`look_lamp`), now in a lib.
**`blender/lib/ocean.py`** `build(sc, P, kind, half, deep, n)`: world z = 0 = the ice base at the probe's exit hole,
+z into the ice, the current along +x. `oc['ice']` = a closed slab whose underside is the ceiling (random-walk
subsurface; the hole bored by a live Boolean), `oc['water']` = one box volume from 400 m down up into the slab (fills
the hole), `ceiling_z(oc, x, y)`, `motes()` / `frazil()` = point clouds that drift by themselves with the scene time
(GN Scene Time: current OCEAN_U, frazil rising at `rise_speed()`, fluttering). Grid 801² on a sinh axis (≈ 5 cm at
the hole, 0.5 m at ±60 m). Board **`blender/shots/board_ocean.py`** (`--views emerge,up,level,wide,down --sinks
10,40,100 --kind melt|freeze --motes 1 --frazil 1 --cloud x,y,z,r --lampaz`), sheets `frames/ocean/melt-sheet.png`
(emerge · up · level · wide / down 10 · 40 · 100 m) and `freeze-sheet.png`. **Cost**: build 1–3 s; 40 %/64 spp
≈ 8 s per still (full res ≈ 6× that: the cheapest Cycles environment of the film so far).
- physics.py new rows (all printed): current `OCEAN_U` 3 cm/s (film pick in model ranges) → **melt scallops 1.35 m**
  (Curl's Re 22,500); **terraces** risers 0.4–2.5 m at 65°, treads 3–14 m (Icefin under Thwaites, Schmidt et al.
  2023); **base ice** reduced scattering 3/m (film pick: brine-bearing accreted ice, as sea ice from below) → diffuse
  albedo R/G/B 0.41 / 0.67 / 0.88, mean free path 0.3 m (`base_ice()`, Jensen diffusion; no tint chosen by eye);
  ⚠ **frazil** 2 mm discs rising edge-on, `rise_speed()` calibrated on Gosink & Osterkamp's measured 10 mm/s →
  **3.1 mm/s on Europa** (4 cm in a 14 s shot; the current moves it 42 cm); **lamp seen from d m** (`lamp_seen`):
  blue −2 EV at 10 m, −8 at 40 m, −12 at 80 m, −17 at 150 m vs 5 m; red gone by 20 m, green by ~60 m.
- Ceilings: `melt` (terraces with scallops all over them; where the base melts) and ⚠ `freeze` (smooth accreted
  marine ice with a fringe of loose platelets; where it grows, model: Wolfenbarger et al. 2022, Lawrence et al. 2024).

**Findings for the user (Sprint 2.4):**
1. The **melt ceiling reads**: the lamp lights a stepped, cupped blue-white base above the probe (emerge, up), the
   terraces climb away into the dark (wide). With the port facing the camera the frame is one forward-scatter blob
   (Sprint 1 finding 4 again): 07 keeps the port across or away from the lens.
2. **08 times itself**: from the ceiling the probe's glow is a blue point by 40 m and gone by ~100 m (down100 is black
   at +4 EV), as `lamp_seen` says. 08's sink speed (tether pay-out) decides when; ~60–80 m in 14 s would end it on
   "gone". Open for 08's sprint.
3. **Particles don't read yet**: motes (0.2–1 mm) are sub-pixel at a 30 mm lens beyond ~1 m and the denoiser eats them;
   frazil discs are ice in water (relative index 0.983): nearly invisible, as they would be. To show "snow" in 07 the
   shot needs particles within ~1 m of the lens inside the beam (or a macro insert). Decide in 07's sprint.
4. **⚠ Frazil / freeze ceiling (model, not seen on Europa)**: real physics says the flakes rise 3 mm/s (weak gravity),
   so they hang nearly still and drift with the current: "snow that barely rises". The platelet fringe doesn't read
   either (same index problem). Proposal: keep `melt` for the film; frazil only if 07 wants it, marked ⚠.
   **Yes (user 2026-10-05): melt ceiling; frazil only if 07 asks for it, ⚠.**

**Sprint 3.1 (shot 01, the turn) done 2026-10-05, branch `sprint-3.1-shot01`.** **`blender/shots/s01_horizon.py`**
(from `test01_framing.py`, the 2.1 ground + 2.0's three hero plates; 12 s = 288 frames). Animatics:
`out/01-horizon-animatic.mp4` (Cycles 25 %/16 spp, 2.5 s/frame, 12 min; the motion check here, since the shot is
about light) and `out/01-horizon-animatic-wb.mp4` (Workbench, 0.5 s/frame, first timing). Cycles check
`frames/01-check.png` (50 %/64 spp: 1.0 s mesa · 4.2 s leaving it · 7.0 s disc entering · 11.5 s end).
- Heading 150° → 6° over 2.3–8.8 s; time per degree ∝ w(h) (`--dark` 0.75 between 40° and 95°) under Io's
  ramp-cruise-ramp ease (a 0.3, b 0.45): **peak 42°/s** (39 px/frame at 24 mm), dark stretch 5.0–6.3 s, disc limb
  enters at 6.5 s, within 1° of the end by 8.1 s, ~4 s on the disc. First try (dark 0.4, pan 2.8–8.0) was a 75°/s
  whip with 0.7 s of dark: rejected.
- Lens 24 → 35 mm on the plain eased time; exposure keyed by heading, +1.5 → **−3.5 EV** (smoothstep 60° → 20°; at the
  end −2.5 left the bands pale, −4.5 lost the faint plain under the disc). Push 0.3 m/s toward the end heading (3.6 m,
  over the knoll's top). Motion blur 0.5 shutter (the pan's stars streak).
- Limb mesa (az −7°, 2.4 km): full ridged plains on its top, tilt 2.5°, plate turned 40° (`--limb 1.0:2.5:40`); the
  2.0 version (plains 0.3) cut a flat rectangle out of the disc, plains 1.0 at rot 10° an 8-m sawtooth (ridges
  end-on). The animatic mp4 still shows the rectangle (motion unchanged).
- Europa's own shadow sits on the disc at the end (Sun 178°), as in 02: consistent.
- Caption EUROPA · 木卫二 moved to 8.2–11.6 s (on the settled disc).
- **Cost**: full res 64 spp ≈ **8–9 s/frame** (mesa 9.2, pan 8.3, disc 7.7) → ≈ **41 min**. Cheaper-way ladder: the
  camera moves every frame (no plate, no freeze); persistent data on in real renders; try 32 spp in the batch sprint
  (night, motion blur) with a PSNR A/B.
- Film-local fixes on the way: `shot.engine` mutes a keyed exposure in Workbench (else the ride darkened the draft);
  `render.mjs` prints `NOTE` lines too.

**Sprint 3.2 (shot 02, the neighbour) done 2026-10-05, branch `sprint-3.2-shot02`.** **`blender/shots/s02_neighbour.py`**:
01's knoll and ground (the 2.1 ground + 01's three hero plates: the limb-biting mesa is the same one), camera locked at
**75 mm** (hfov 27.0°, vfov 11.5°), aimed 5.44° up so the ice horizon sits 0.3° above the frame's foot (`--foot`).
One Io transit as a constant-rate time-lapse: **×512**, Io's centre on the top limb at 1.0 s, on the horizon at 10.5 s
(`--t-in --t-set`). Animatic `out/02-neighbour-animatic.mp4` (Cycles 50 %/16 spp, 2.7 s/frame, 13 min; Workbench can't
show shadows or the eclipse, so no Workbench pass). Cycles check `frames/02-check.png` (50 %/64 spp: 0.3 s Io above the
disc · 4.9 s Io eclipsed · 10.2 s Io setting); `02-check-ev45.png` = the same at −4.5 EV (disc mean 8 % darker; −4.0
kept: max 221/255, no clip, half a stop from 01's end).
- physics.py new rows (printed for `LAPSE_E_END` 180 / 179 / 178): **`lapse(fr, e_end, h)`** (Io's Δ, the Sun's
  elongation falling 4.22°/h, Jupiter's spin 360°/11.23 h → **43.3°** over the transit, the stars' turn 360°/85.2 h →
  **5.71°**), **`europa_on_io`** (Europa's shadow on Io: distance from the axis, umbra/penumbra radii) and
  **`eclipse_span`**. `io_track` cached in `lapse` (it scans 40,000 steps).
- Per frame (linear keys): Sun + Jupiter's Sun (quaternions), Jupiter's spin about its axis (clouds slide down with Io),
  Io (`moons.key_io`: place + locked face), stars (`StarTurn`, `StarSmear` over the 0.5 shutter, 3 taps). GRS at −40°
  at Io's entry: it slides down the left side behind the limb mesa.
- **Bug fixed (`lib/moons.py`)**: Io was lit by the main Sun, so the real-size Europa body shadowed the k-scaled Io
  (Io black for no reason in the first preview). Io is now lit by Jupiter's own Sun only (receiver collections), whose
  blockers are the scaled Europa + Io: Europa's shadow on Io falls true. `look_io.py` gets the fix too.
- Checked against physics per second: Io, Io's shadow and Europa's shadow (el/az) land where `io_cast_shadow` / the
  anti-solar point say; at the end Io's shadow (0.5° up) is behind the far rubble, Europa's (1.7° up) stays on the disc.
- **Cost**: full res 64 spp ≈ **6.4 s/frame** → ≈ **31 min**. Ladder: locked camera, but the whole disc changes every
  frame (spin, shadows): no plate; persistent data on; 32 spp A/B in the batch sprint (Io's eclipse rim is the test).

**Findings for the user (Sprint 3.2):**
1. ⭐ **Europa's shadow crosses Io (a mutual eclipse), real.** The film's Sun has declination 0 (Jupiter's equinox
   season, as 01); then Sun, Europa and Io line up during the transit and our shadow passes over Io's centre: Io goes
   black inside a thin lit ring (umbra r 1,337 km on Io's 1,822: 54 % of the face we see), then lights again with its
   own shadow and ours hanging above it on the bands like beads. Penumbra on Io for 34 min of the 1.35 h transit;
   with `--e-end 179` (the Sun 1° short of anti-Jupiter when Io sets) that is 2.4–7.3 s, deepest at 4.9 s; 178 puts it
   at 4.8–9.3 s. Status **real (geometry)**: mutual eclipses happen for months either side of each Jupiter equinox
   (twice per 12-y orbit; 2026–27 is one, BAA); it also needs Europa near its orbit's node (0.47° tilt), so not every
   transit. Sources: britastro.org/section_news_item/mutual-events-of-the-galilean-satellites-2026-27 ·
   arxiv.org/pdf/2310.00807. **Yes, mid-shot (e-end 179), user 2026-10-05.**
2. **Lens 75 mm** (TREATMENT said 135 locked, open since 0.2): 135 mm can't hold the visible disc (1,215 px in 804);
   85 mm cuts Io at the top edge when it enters; 75 mm shows Io in the black above the disc for ~1 s, the whole disc,
   Io ≈ 58 px. The limb mesa is bigger in frame than in 01 (same geometry). **75 mm locked, user 2026-10-05.**
3. Stars don't show at −4 EV beside the disc (density 0.06, as 01); they turn in the code, so a brighter star field
   would drift down with Io. Leave dark unless wanted.
4. Caption `IO. WE STOOD THERE.` 6.5–11.4 s lands as Io comes out of the shadow and sinks: kept.

**Sprint 3.3 (shot 03, the probe) done 2026-10-05, branch `sprint-3.3-shot03`.** User picks at the start (2026-10-05):
G = **blown frost + the vapour's wisp** (not a flash-boil burst), **35 mm tilt only** to Ganymede.
**`blender/shots/s03_probe.py`**: 01/02's ground (same plates; the camera stands 3 m right of 0,0, `--cam`, because
a 0.8 m boulder at 5 m filled the left of the frame; `Shifted` moves the ground so the camera's spot is the origin),
eye 0.4 m, 35 mm, azimuth = Ganymede's (−15°). Probe nose-down on the ice at 8 m (az −9°), hanging from a tripod;
astronaut 1.8 m left of it in profile (Breathing Idle + a 22° lean back 1.6–4.2 s: he watches the frost go up).
**Real time at dawn, 1.18 h after Io set** (Sun 174°, 2.3° up at az −179°: directly behind the camera; Jupiter 99.7 %
lit), −4.5 EV throughout. Burst at 1.0 s; tilt 5° → 55° over 3.0–8.0 s, 1 s hold (9 s clip after the review; first
cut 12 s, tilt to 9.0 s); Ganymede 57.7° up, 0.233°, 74 % lit, slightly above centre at the end. Animatics:
`out/03-probe-animatic.mp4` (Cycles 50 %/12 spp, the locked 9 s cut), `out/03-probe-animatic-wb.mp4` (Workbench,
first 12 s timing). Cycles check `frames/03-check.png` (50 %/64 spp:
0.5 s before · 2.6 s burst · 10.5 s Ganymede); full-res crops in `frames/03/`.
- physics.py new rows (all printed, "03: …"): **`vacuum_start`** (10 kW sublimates 1.6 g/s, head 0.13 m/h = 5.2×
  slower than melting; vapour choked at the triple point leaves at 409 m/s, ≤ 1,008 m/s expanded), **`jet_s0`/`jet_seen`**
  (condensed-grain lobe σs = S0·cos²θ/r², HG g 0.85: 4–8 stops under the lit plain 0.1–1 m up), **`flash`** (liquid
  meeting vacuum: 11.8 % boils, the rest freezes; not used), **`ballistic`** (0.134 g: 5 m/s at 75° → 8.9 m, 7.3 s),
  **`ganymede_pos`/`ganymede_seen`** (Laplace: −90° − Δ/2 from Europa), film picks `FROST_*` (5,000 flakes 2–15 mm from
  a 0.14–0.7 m ring, 0.3–6.5 m/s, e-fold 0.6 s; momentum check: 18 % of the vapour's over the burst), `TRIPOD_*`, `REEL`.
- New code: **`lib/vent.py`** (`frost`: each flake its own vacuum parabola by Geometry Nodes on the scene time,
  attributes vel/t0/t1/size/spin, landing solved on the real ground; `lobe`: the grain volume), **`cryobot.tripod`**
  (three legs, sheave, tether over it to a reel box), **`moons.ganymede`** (scale k, main Sun, mottled albedo round
  0.43: no map is resolved at 8 px).
- The vapour lobe is **off** (`--lobe 1` puts it back): A/B at 2.6 s = 47.9 dB, the difference is sampling noise only,
  and it costs 2.2× (physics said invisible; Cycles agrees).
- **Cost**: full res 64 spp ≈ **40–60 s/frame** (burst 63 s incl. sync; 26 s without motion blur: the 5,000 flake
  instances under blur double it) → ≈ **2.5–3 h** for the 9 s cut (216 frames). Ladder for the batch sprint: motion blur only where flakes stream
  (per-frame toggle), 32 spp A/B, persistent data (the ground is static).

**Findings for the user (Sprint 3.3):**
1. **Night → dawn (needs a yes).** At night (Sun 177°) everything in the shot is backlit by Jupiter: astronaut and
   probe black, Jupiter blown at an exposure that shows them (`frames/03/cy-grid.png`). At dawn the Sun rises exactly
   opposite Jupiter (az −179°), behind the camera: suit, probe, frost, Jupiter's full disc and Ganymede are all sunlit
   at one exposure (`frames/03/dawn-grid.png`, `03-check.png`), the shadows point at Jupiter, and 04 (the day) follows
   on. The TREATMENT row said "Jupiter-lit side". **Yes, dawn (user 2026-10-05).**
2. **The wisp is invisible, as physics says** (finding above): G on screen = the frost burst. It reads at 8 m:
   specks bursting out round the nose against the sky and Jupiter, landing in 1–10 s (`frames/03/f3-grid.png` 2.5 s).
3. **The last ~4 s are a near-empty black sky**: Ganymede is a 7.7 px gibbous disc (reads at full res,
   `frames/03/f3-sky.png`), only a few flakes get that high. Options: trim 03 to ~9 s (TREATMENT's trim candidate),
   slow the tilt to arrive at ~10.5 s, or keep the stillness. **Trim to 9 s (user 2026-10-05): tilt 3.0–8.0 s, 1 s
   hold on Ganymede.**
4. Astronaut idles (no kneel clip yet, W1); the lean back sells "watching it go up".

**Sprint 3.4 (shot 04, the fall of the Sun) done 2026-10-05, branch `sprint-3.4-shot04`; 04 locked (answers below).**
**`blender/shots/s04_sunfall.py`**: 01/02's knoll and ground (same HERO plates: the limb mesa at az −7° bites the disc's
lower left), eye 1.6 m, **50 mm locked**, Jupiter's top limb 3° under the frame top (frame −4.5° … 12.6°: the near ice
and blocks fill the lower third). Animatic `out/04-sunfall-animatic.mp4` (Cycles 25 %/16 spp), check
`frames/04-check.png` (50 %/64 spp: 0.5 dawn · 4 noon · 6.5 crescent · 9 Sun on the limb · 11.5 bead · 17 night).
- **Clock** (physics `SHOT04`, `fit04`, `lapse04*`): 0 s = 03's dawn (Sun 174°, 2.2° up behind, Jupiter 99.7 %), real
  time; log-rate eases up to **×25,373** by 1.5 s (the Sun 30°/s, Jupiter a turn every 1.6 s: its bands stream down
  into the ice; shadows swing from long-toward-Jupiter through noon, 80° up, to long-toward-us), eases down from 6 s;
  the Sun enters the frame top at 7.2 s and slows onto the limb; **first contact 10.0 s at ×31** (9.60° up), the rate
  held so the bead shrinks evenly (100/68/25/0 % at 10/11/12/13 s), real time from second contact 13.5 s (the
  ingress is 87 s real: "goes out in real time" can't fit 18 s; eased instead). Night 13.5–18 s in real time.
- **Ground light**: the Sun lamp keyed by `sun_visible`; Jupiter keeps its own Sun (europa_shadow, data copied so it
  is never dimmed). Jupiter's Lambert crescent 0.28 % at contact (sub-pixel under the ring).
- **Night** (exposure −4.5 → **+5 EV** over 13.0–15.5 s): stars at true brightness (brightest V −1.5, `--star-mag`;
  density 0.6), the black disc a starless hole; ring (Io's `_ring`, keyed by the Sun's limb distance; haze from first
  contact, arc from 1.5° out, dimmed ×16 / ×12 against Io's so it stays orange-red at +5 EV): **a red arch standing on
  the ice**; **the solar corona** (new `sky.corona`, Baumbach K+F profile, `physics.CORONA`/`corona(r)`, true surface
  brightness) as a pearly crown on the top limb: the Sun is only 0.05–0.06° behind it; **lightning** (new
  `jupiter.lightning`: 4 storm points, 9 flashes 14.6–17.8 s, 1e9–1.6e10 J, `physics.flash_seen`: V −0.2 … −3.2,
  0.4–0.6 px spots: points blinking inside the black disc).
- physics.py new rows ("04: …"): the day (39.8 h, highest 80.3°, Jupiter 99.7 → 0.28 %, 3.5 turns), ingress 87 s,
  clock, lightning by energy (Galileo SSI: up to 1.6e10 J, 45–80 km HWHM, Little et al. 1999; Juno SRU 1e5–1e8 J,
  pulses ms apart, Becker et al. 2020, Kolmašová et al. 2023), corona radiance at 1.05–5 R☉ (≈ 0.1 at 3 R☉ vs sunlit
  ice 10; 1 R☉ = 2.4 px at 50 mm).
- **Bug found and fixed**: at +5 EV Jupiter's night face showed its bands (≈ 5e-5 of the lit disc). Elimination: only
  `SunJupiter`, and only with bounces (direct-only black): its own lit far side leaking through the smooth-shaded
  sphere. Jupiter is now invisible to diffuse/glossy rays in 04 (`--jup-bounce 1` restores); it loses only its light
  on the ground by day (0.6 % of the Sun's).
- `render.mjs`: **persistent data for animatics too** (a Cycles animatic re-synced the 8 M-vertex ground every frame:
  ~40 s/frame → **0.5 s/frame**). Debug options in 04: `--hide A,B`, `--bounces N`, `--sj-angle DEG`.
- **Cost**: full res 64 spp ≈ **7 s/frame** (day stills, motion blur on; night frames cheaper) → ≈ **45–50 min**. Ladder: the night tail 13.5–18 s is static
  but for lightning and exposure → freeze tail (shot.freeze) + flashes pasted per frame (border renders), or render
  the tail at 32 spp; persistent data on.

**Findings for the user (Sprint 3.4):**
1. ⭐ **The solar corona on Jupiter's limb (real, new).** After second contact the Sun sits only 0.05° behind the top
   limb, so its corona (same surface brightness as at a total eclipse on Earth, 5.2× smaller) stands above the limb as
   a pearly crown next to the red arch. Status **real** (Baumbach profile). Keep?
2. **"Goes out in real time" → eased.** The real ingress is 87 s; it plays in 3.5 s at ×31 (the bead shrinks
   evenly), real time after. Alternative: a longer clip (the 87 s can't fit anyway).
3. **The ground turns grey-white once the Sun is ahead** (≈ 6–13 s): the frost's forward glint swamps the brown
   (`ice()` specular), a strong change from the sunlit brown at noon. Keep (it is the backlit look) or tone it down?
4. **Night exposure +5 EV, stars at true brightness**: ~hundreds of stars, the disc a starless hole, ring orange (not
   white). Lightning: 9 flashes, energies from Galileo; the rate (≈ 2/s from 4 storms) is a film pick (no published
 rate for flashes this big). At full res each flash is a 1-px white point for 1–2 frames (true size and
   brightness): subtle; a longer pulse train (3–5 frames, like Earth's in-cloud flashes) would read more.
5. Frame: the top limb 3° under the frame top (the Sun is in frame from 7.2 s); `--top` moves it.

**User's answers (2026-10-05):** 1. corona **off** (`--corona 0` default; the code and physics row stay). 2. eased
ingress as built. 3. keep the backlit grey-white ice. 4. lightning first "bigger, a bit exaggerated" (tried: a
1,500–3,000 km glow, ×6 energy, 3–5-frame trains: it read as a hard white dot, a moon, not lightning), then **dropped**:
flashes inside the eclipse looked odd (`--flashes 0` default; `jupiter.lightning` and `physics.flash_seen` stay for
true 1-px flashes). 5. framing OK. The animatic `out/04-sunfall-animatic.mp4` is re-rendered without them.

**Sprint 3.5 (shot 05, the lid) done 2026-10-05, branch `sprint-3.5-shot05`; 05 locked (answers below).** User picks at the start (2026-10-05):
**30 m, puck 1** (film pick `physics.CRYO_PUCK_FIRST`: dropped just under the regolith, then every 2 km), **camera
stays in the ice with the puck** (the probe sinks away), **a small clock**.
**`blender/shots/s05_lid.py`**: `shell.build` at 30 m (cutaway, as the 2.3 lid board) + the cryobot (port −40°); the
world is the probe's frame, so the ice (shell root), the dropped puck and the camera all move up by the descent d(t).
Clock (physics `SHOT05`, `fit05`, `lapse05`): real time at 0 s (the puck has just left the open top), log-rate eased
0.5 → 3.0 s up to **×2,890**, held; the freezing front (1.34 m above the probe's top, `refreeze`: 1.99 h at 0.68 m/h)
comes down after the probe and **reaches the puck's top at 5.0 s** (2.01 h, probe sunk 1.36 m), the caption's start;
6.02 h / 4.07 m by 10 s (34.1 m down). Camera 35 mm, f/4, 13° right of the cut's normal, push-in 4.0 → 2.6 m, aim the
puck (drop-frame 3.05 → 3.1 m), looking down 12° → 4° (sees into the open top), eased 0.5–9.6 s; focus on the puck.
Exposure +3 → +5.5 EV over 4–9.5 s (the eye follows the fading light: the lamp sinks away, red dies first).
- physics.py new rows ("05: …"): the drop (front, shut time, the 25 mm water ring round the puck shuts in ~5 min:
  invisible), the clock; **`HOLE_CORE`** (new, real on Earth): a refreezing hole freezes inward and pushes its gas/salt
  to the axis: IceCube's 55–60 cm holes have a ~16 cm milky **bubble column**, scattering length 2–30 cm (Rongen 2016,
  EPJ Web Conf. 116, 06011; arXiv:2307.15298). Film pick for Europa: 0.27 of the hole (Ø 6.8 cm), 5 cm, g 0.75.
- New code: **`shell.core`** (`build(..., with_core=True)`): the core as a homogeneous volume above the front (world-fixed
  like the front, a short cone at its tip), so in the ice's frame it comes down the column onto the puck. `counter05`
  + **`tools/overlay.mjs` counters generalised**: clip `counter: '<physics fn>'` → (hours, depth) per frame, READOUT
  holds label/format (Io's dead `lapse03` path removed); 05: `投放中继器后 SINCE THE RELAY WAS LEFT` `+2.7 h  31.8 m`.
- Tried and dropped: a wide pull-back to 11.6 m (puck + probe + glow in one frame): the puck was 24 px and the
  porosity bands owned the frame.
- **Bug (user spotted "a hard cut" at ~2 s)**: the sheets' live EXACT Booleans, re-run as the ice slides, dropped a whole
  band at 2.17 s (frames 52 → 53, Bands 922 → 821 faces; Veins changed too). Fix **`shell.fix_bore`**: the slide is
  along the hole's axis, so the sheets are bored once (cutter extended `travel` m below the nose, out of frame) and
  keep no live Boolean; face counts constant over the clip. (Same speed: 2.4 s/frame at 25 %/16 spp.) 06 will need
  its own answer (its ice slides 20 km). The ramp widened at the same time: 0.5 → 3.0 s (was 0.6 → 2.4: still to full
  speed in 0.8 s, just as the puck comes out).
- **Cost**: full res 64 spp ≈ **60 s/frame** (3 stills 188 s incl. build) → 240 frames ≈ **4 h**. The camera moves
  all clip long (no plate); ladder for the batch sprint: 32 spp A/B, fewer volume bounces A/B (128 now), persistent data.

- Animatic `out/05-lid-animatic.mp4` (Cycles 25 %/16 spp, 2.5 s/frame, 10 min; re-rendered after the band fix: no jump left, the largest frame-to-frame change is sampling noise in the dark tail) and `out/05-lid-animatic-ov.mp4` (with
  the clock and caption laid over); check `frames/05-check.png` (50 %/64 spp: 0.5 probe top · 2.5 the puck out of the
  top, the probe below · 6.5 the puck alone, fading blue).

**Findings for the user (Sprint 3.5):**
1. **The closing itself barely shows.** The milky core is real (IceCube) and in the scene, but in the probe's diffuse
   glow a pure scatterer is nearly invisible (it only redirects light that comes from every side): faint mottling in
   the column above the puck. What carries "no way back": the puck coming out of the top (~2 s), the probe sinking out
   of the frame (~3 s), the light leaving, the clock, the caption at 5 s. Keep the core (honest, subtle), drop it, or
   make it denser (scattering length 5 → 1–2 cm, still inside IceCube's 2–30 cm)?
2. **Exposure ride +3 → +5.5 EV (4–9.5 s)**: the puck stays readable at the end; the fade still shows. Less ride = darker
   end (the light truly leaving), more = flatter.
3. The puck is hidden in the open top for the first ~1.5 s (12° down isn't enough to see inside the rim at 4 m).
4. Clock label `投放中继器后 · SINCE THE RELAY WAS LEFT`, hours with one decimal + nose depth (30.0 → 34.1 m). Wording OK?
5. Cost ≈ 4 h at 64 spp (60 s/frame): the most expensive clip so far; 32 spp / fewer volume bounces to A/B in Sprint 5.

**User's answers (2026-10-05):** 1. the closing as built (the core stays, 5 cm). 2. exposure ride +3 → +5.5 EV
kept. 3. the puck hidden in the top for the first seconds: fine. 4. clock wording OK. 5. ≈ 4 h render accepted.
Before that the user spotted a "hard cut" at ~2 s: the band bug above, fixed (`shell.fix_bore`) with the softer ramp.

**Sprint 3.6 (shot 06, descent) DRAFTED 2026-10-05 (cloud session from the phone: no Blender, no `../../_kit`, no
`../../_assets`, download.blender.org blocked by the session's network policy).** Everything below is written and its
numbers printed by `physics.py`; **no frame has been rendered and the Blender code has never run.** User's go: "do
what can be done, open a PR, merge it, update the docs" (2026-10-05).
- **Clock (physics `SHOT06`, `fit06`, `z06`, `speed06`, `days_to`, `counter06`; new rows "06: …").** The clip is driven
  by depth, not time: the nose's depth moves in **ln z** (each second covers a factor of depth, so the milky top →
  clear ice change, 0.1 → 3 km, gets as long as 3 → 20 km); its rate eases (log-smoothstep, as 04/05) from 05's held
  **×2,890** (at 05's end, 34.1 m, day 2.1) up over 0–3 s to a peak **×27 M = 255 m of ice per frame at 11.6 s**, and
  down over 11–19 s to ×2,890 again, **20 m above the base** (19,980 m, day 1,043.4; 07 melts the last metres: day
  1,044.1). Depth marks: 0.1 km 3.8 s · 1 km 7.6 s · 3 km (the end of the cracked lid) 9.4 s · 10 km 11.3 s · 19 km
  13.4 s · 19.9 km 14.9 s; the last 5 s are the landing (×330 k → ×2,890, the ice −3 → −2 °C). Days = ∫ dz / v from
  the cryobot model (day 0 = the head first melts; 03's start in vacuum is left out).
- **Readout** `counter06` → `tools/overlay.mjs` (counters generalised: a READOUT entry is a label + one field per
  value; 05 draws exactly as before): `开始下潜后  SINCE THE DESCENT BEGAN` / `+2 d  34 m  −173 °C  0 bar` →
  `+1,043 d  19,980 m  −2 °C  242 bar` (the ice's temperature round the probe, `shell_T`; the pressure of the ice
  overhead).
- **`blender/shots/s06_descent.py`** (draft): `shell.build` at 05's end depth (cutaway, as 05) + the cryobot (port −40°,
  tether to the box top); camera **fixed to the probe**, 35 mm f/4, 13° right of the cut's normal, easing 1–17 s from
  the probe's top (aim 3.4 m, 3.2 m away, looking down 8°) to its head (aim 0.45 m, 2.4 m, 2°): 05 ends on the top, 07
  starts at the nose. Keyed from the true depth: σs (`physics.pore`: 5.7/m → 0.14 at 3 km → 0.006: **glow → beam → dark
  ice**, the 2.3 board's row 2), open cracks hidden below 3 km, the **open column** above the probe (`refreeze` on a
  depth grid: 1.3 m at the top, 6 m at 15 km; the melt-water lathe stretches by a shape key, the milky core and the
  beads' front move up with it; out of the frame below ~16.5 km), the seated puck (the magazine empties at 18 km: one
  dropped every 2 km after 05's), exposure **+3 → +5 EV over 0.3–3 km** (a guess until the animatic), motion blur 0.5.
- **The treadmill (new technique, untested):** 20 km of ice can't be built. The sheets (bands, veins, cracks, beads)
  are built for a 160 m window (+ 66 m blur margins either side, 292 m in all, ≈ 1,600 veins / 700 bands / 270 cracks)
  and bored once (`shell.fix_bore`); root z wraps inside the window **only while the ice moves ≥ 4 m per frame** (the
  frame is ~1.5 m tall at the axis; dry run: 106 wraps, the slowest at 5.1 m/frame). 05's handover (124 m) and the
  landing (61 m) each fit without a wrap. Root z is keyed at the frame and both shutter ends on one wrap branch,
  LINEAR, so the blur shows the true travel and never the wrap. The pure-Python part (clock, treadmill, column grid)
  was dry-run in the session: all positions stay inside the built window.
- `shell.py`: **`key_sigma`** (split out of `key_depth`): keys σs and, where the ice clears below `SIMILAR_MIN`, switches
  a material built in similarity mode back to the true σs and g (the beam's side-look depends on g); `_volume` names
  its scatter / multiply nodes (`SigmaScatter`, `SigmaSimilar`), the beads' front node is `Front` (keyable).
- `clips/06-descent.js`: `counter: 'counter06'`.

**First steps on the Mac (in order):**
1. `git pull`, then `python3 tools/physics.py | grep "06:"` (the three 06 rows) and
   `Blender -b --factory-startup -P blender/shots/s06_descent.py -- --frames 480 --stills 1 --pct 25 --samples 16`
   (scene build + one still; the log prints the clock, the treadmill and the wraps). Untried API: shape keys on the
   water lathe, keyed node sockets (`SigmaSimilar`, `SigmaScatter` Anisotropy, `Front`), keys at quarter frames,
   keyed `hide_render`, `keyframe_new_interpolation_type`, motion blur through volumes (if the sheets don't blur,
   `--shutter 0` and judge without it).
2. `node preview.mjs 06-descent 1 6 8.5 11.6 19.5 --pct 50`, then the animatic `node render.mjs 06-descent --animatic
   --engine cycles --pct 25 --samples 16` and `node tools/overlay.mjs 06-descent --stills 1,10,19.5`.

**Mac run (2026-10-06).** Build + one still 26 s (scene build dominates); the log's clock / treadmill / wraps match the
draft (106 wraps, cracks end 9.38 s, magazine empty 12.92 s). Every untried API worked (shape key, keyed sockets,
quarter-frame keys, keyed `hide_render`). Only warning: "closures 66 > 64" (known since 2.3, frames clean).
- Check `frames/06-descent-strip.png` (50 %/16 spp: 1 · 6 · 8.5 · 11.6 · 19.5 s): milky glow → veins streaking → black
  ice with the lamp's beam → the head. Glow → beam → dark ice reads as planned.
- **Motion blur through volumes works** (frame 120 with shutter 0 vs 0.5: the bands smear). The flicker at 5–7 s
  (frame-to-frame luma jumps up to ~30/255) is bands passing between the glow and the camera, several per frame:
  real time-lapse flicker, not the treadmill (no jump at the wrap boundaries 4.54 / 15.04 s beyond the rest).
- **Fix: the end blew out.** The port (−40°, as 05) faces the camera (−77°) once the camera reaches the head; at +5 EV
  the window was a white blob. New `--ev2 2 --evt 12,16`: EV +5 → +2 by time as the camera arrives. Tested at 19.5 s:
  port −40° / 0° × +5 / +2 EV; +2 keeps the window a readable source with its beam. Port 0° (beam side-on, more of a
  "beam") would break continuity with 05 and set 07's lamp direction: kept −40°.
- At ~18 s a porosity band drifts slowly up through the beam and lights as a sheet (the slow landing makes it visible).
- Counter: fields right-aligned per column (`overlay.mjs` field option `align`; 05 unchanged). The pressure reads
  `0 bar` for the first ~2 s (0.4 bar rounds down).
- Animatic: Cycles 25 %/16 spp, 480 frames ≈ 13 min (~1.6 s/frame); `out/06-descent-animatic-ov.mp4` = with counter.

**Questions for the user (Sprint 3.6, answer after the animatic):**
1. **The landing**: the last ~5 s are within 100 m of the base and slowing to ×2,890 (only the counter's last digits
   and the ice warming −3 → −2 °C move). Keep (a held breath before 07), or shorten it (`dn0`/`dn1` later, e.g.
   13 → 19.5 s) and give the dark deep ice more time?
2. **The middle is a blur by necessity**: 8–15 s the ice passes at 30–255 m per frame; what can show is the glow
   fading to a beam, veins streaking through it, the counter running. If it reads as noise, the alternative is
   "stations": the clock slows at two or three depths (1 km cracks, 3 km clear ice, 15 km dark veins) and jumps
   between them.
3. **Counter wording**: `开始下潜后 · SINCE THE DESCENT BEGAN`, `+1,043 d  19,980 m  −2 °C  242 bar` (the ice's
   temperature, not the probe's; the pressure of the ice overhead). OK?
4. **New physics fact, spectacle candidate for 07**: near the base the warm ice barely freezes the hole shut:
   open 12 days / **341 m** of water above the probe at 19.8 km, 27 days / **775 m** at 19.9 km, ~174 days / ~5 km
   at 19.98 km (conduction only, lower bounds; `refreeze`). The probe reaches the ocean at the bottom of a long
   water tube. Out of 06's frame; 07 could look up it (lit by the lamp) as the probe breaks through. Use it?
5. Puck drops (every 2 km) happen inside the blur, unseen; the seated puck is gone after 18 km. OK?
6. Cost unknown until run: 05 was 60 s/frame at 30 m (milky); the 2.3 board's deep stills were ~6× cheaper. Guess
   2–5 h for 480 frames at 64 spp. **Timed 2026-10-06** (full res, 64 spp, one still each): milky 6 s = **82 s/frame**
   (heavier than 05's 60), clear 19.5 s = **15 s/frame** → ≈ 216 milky frames (to ~9 s) + 264 clear ≈ **5.5–6 h**
   before the ladder (32 spp / fewer volume bounces A/B in Sprint 5: the milky half is the target).
7. (Mac run) The flicker at 5–7 s (bands crossing the glow): keep (reads as speed), or soften with a longer shutter
   (1.0: the blur doubles)?
8. (Mac run) End exposure +5 → +2 EV over 12–16 s, lamp port −40° kept (as 05). OK, or port 0° for a side-on beam?

**User's answers (2026-10-06):** 1. the slow landing kept. 2. the blurred middle OK. 3. counter wording OK (incl.
`0 bar` at the start). 4. **the water tube: use it in 07.** 5. pucks unseen, gone after 18 km: OK. 6. **soften the
flicker: shutter 0.5 → 1.0** (default now; treadmill margins grow with it). 7. EV +5 → +2 and port −40° OK.
→ Animatic re-rendered at shutter 1.0: frame-to-frame luma change at 4.5–7.5 s mean 8.7 → 5.5, peak 40 → 18.5
(whole clip peak 26 at 8.2 s = the milky → dark change itself). Treadmill margins 66 → 129 m (still 106 wraps);
full-res milky still 82 → **101 s/frame** → the clip ≈ **6.5–7 h** at 64 spp before the ladder. **06 locked.**

**Sprint 3.7 (shot 07, breakthrough) 2026-10-06, branch `sprint-3.7-shot07`.** User picks at the start: beats **glow →
break → tube → level**; the tube's look decided on a board (clear vs ⚠ mush); **marine snow near the lens**.
- **physics.py (rows "07: …")**: near the base the ice is within a few K of its melt, so the side heat (50 % of 10 kW)
  melts the walls: **`bore_wide`** 0.125 → 0.177 m (upper bound). **`tube07`**: at the moment of breakthrough the hole
  is water from the base up to where it has just frozen shut (bisection on `refreeze` age vs closing time): **351 m**
  (to 19.649 km; **256 m** with the head's bore), tapering 18 cm → 0 over its top ~150 m. *3.6's "341 m at 19.8 km /
  775 m at 19.9 km" were open time × speed (the probe only had 200 m left): corrected.* **`tir_half`** 10.4°: water
  (1.333) in ice (1.311) is an optical fibre. **`fit07` / `nose07`**: ×2,890 → real time over 0.3–3.4 s, the nose
  starts 0.88 m above the base and breaks through at 3.5 s (68 min real in 14 s). **`drop07`** (film picks
  `CRYO_MASS` 500 kg, `CRYO_CD` 0.9, `TETHER_BRAKE` 1 m/s², brake from `free` 4 m): weight in water 458 N →
  0.89 m/s² at 0.134 g, peak 2.45 m/s, stops 7.0 m down at 9.0 s. `MUSH` ⚠ (a skeletal brine-ice wall) kept as a
  constant only (unused: see the board).
- **`lib/ocean.py`**: `build(..., hole_r=)`; **`tube()`** (a lathe of the `tube07` profile above the slab: glass at
  N_WATER/N_ICE so TIR is real, pure melt-water absorption, transparent bottom cap; optional ⚠ mush skin);
  **`ice_volume_mat()`** (see the glow below).
- **Board `blender/shots/board_tube.py`** (`frames/tube/tube-board.png`, sent to the user): **the tube is black from
  below in every variant** — lamp as built; a test-only 10 W tail lamp aimed up the hole; + ⚠ mush σs 30/m; checked
  at +12 EV without the slab (only the tether and the water's own scatter show). Radiance is conserved along a
  light pipe: it carries the light up and away, and nothing sends it back down. **User: black well, lamp as built.**
- **`blender/shots/s07_breakthrough.py`**: ocean frame, the probe keyed by `nose07` (at the frame and the shutter's ends,
  shutter 0.5); until the break the bore is **plugged** below the nose (a base-ice cylinder whose bottom follows the
  ceiling, its top on the melt film by a shape key; hidden at 3.5 s: a moving Boolean cutter would re-bore 1.3 M
  vertices a frame). 24 mm, f/4. Camera: holds on the hole (2.2 m off the axis, 2 m down, gaze 40° up), then over
  8–13 s cranes down beside the port (0.7 m off the axis, 90° round from it, 0.25 m above it) and turns to look out
  along the beam (−3°). Port **40° off the line of sight, away** (at the lens it blew the frame white: 2.4 finding 1
  again), so the beam lights the ceiling *behind* the hole and silhouettes the head and the well. EV 0 (glow) → +4
  (3.5–8 s) → +5 (9–13 s). Motes: a 1.2 m cloud ahead of the end pose, in the beam's flank (bokeh specks at 13 s).
- **The glow needed a new ice**: with random-walk SSS (2.4's) the lamp inside the slab is only found by long walks that
  exit next to it → **dark blotches that survive 256 spp** (not the motes, not the bump: tested by elimination);
  Christensen-Burley is clean but carries light only a few mean free paths (a small spot). Ice → water reflects 7e-5,
  so the slab is now a **scattering volume behind a transparent surface** (`ocean.ice_volume_mat`, σs' 3/m, g 0,
  64 volume bounces): every scatter point sees the lamp → clean at 64 spp, and the head shows through the last
  centimetres (σs' 3/m: 3 cm is nearly clear). Compromise: the ocean box overlaps the slab, so the slab absorbs as
  water (R/G/B 0.39 / 0.090 / 0.0135 /m vs ice 0.29 / 0.058 / 0.0054: slightly bluer glow; printed). Terraces lit
  from outside read softer than with random walk (no surface at all).
- **Animatic** (Cycles 25 %/16 spp, 1.8 s/frame, 10.7 min): `out/07-breakthrough-animatic.mp4`. v1 (move 8–13 s) left
  7–9 s near-black (the probe below the frame, the hole unlit); **v2: move 6.5–12.5 s** (the camera follows it down):
  ~1 s darkish at 7 s, a dark frame at ~10 s as the camera passes the probe's top, snow from 11 s.
- (Captions/sound not checked against the animatic: Sprint 4, as for every shot.)

**Questions for the user (Sprint 3.7, after the animatic):**
1. Timing: the glow holds ~2–3.5 s with the head showing through the last cm (nothing moves: ×50 → ×1). Keep (the
   held breath before the drop), or break earlier (`SHOT07` brk/dn1)?
2. The black well reads only for a moment (~5–6 s, against the beam-lit ceiling behind it), as agreed. Enough?
3. The end: marine snow in a teal haze looking out along the beam (11–14 s); the probe itself is out of frame. Want
   the probe (its lit flank / the port's edge) in the end frame, or the beam pointing more down (`el1`, "nothing
   below")?
4. The volume ice (clean glow; slab absorbs as water: slightly bluer). OK?

**User's answers (2026-10-06):** 1. the hold kept. 2. the well's moment is enough. 3. **the probe in the last frame.**
4. volume ice OK.
→ End pose moved **behind and beside the probe** (`--back 1.6 --side 1.0 --up 0.25`, looking at a point `--reach 3` m
out along the beam; the side is the one nearer the start pose, so the crane no longer crosses round the probe: v2's dark
frame at ~10 s is gone): the head and the port's flank silhouetted against its own beam at the right of the frame,
snow in the beam ahead. Animatic **v3** (10.9 min) reads continuously. **Cycles check** (`node preview.mjs
07-breakthrough 2.5 5.5 13 --pct 50 --samples 64`, 16 s/still): clean glow with the head, the probe motion-blurred
against the lit terraces, the end frame. **Full res 64 spp: glow 54 s/frame, end 32 s/frame → ≈ 3.5–4 h** before the
ladder (Sprint 5 A/B: 32 volume bounces / fewer samples on the glow). **07 locked.**

**Sprint 3.8 (shot 08, abyss) 2026-10-06, branch `sprint-3.8-shot08`.** User picks at the start: **brake off, real
time → ×3** (gone under the caption; real time alone ends at 54 m on a faint point), **counter: time · depth · bar**.
- **physics.py (rows "08: …")**: `SHOT08` (dur 14, `rel` 1 s, ×1 → ×`rate` 3 over `up0`–`up1` 2.5–7 s), `drop08` (drop07's
  forces without the brake: the tether pays out from the probe's own spool and lies still behind it, no drag;
  0.89 m/s² → terminal 4.5 m/s, ~12 m/s on Earth), `lapse08`, `fit08`, `nose08`, `counter08`. Held 7.0 m below the base
  (07's stop) → 130 m at 14 s (31.9 s real). Lamp vs 5 m (blue): 4 s 11 m −3 EV · 7 s 36 m −7 · 10 s 76 m −11 ·
  12 s 103 m −13 · 14 s 130 m −15. Counter `破冰后 · SINCE THE BREAKTHROUGH` +10 s 20,007 m 242.0 bar → +42 s
  20,130 m 243.7 bar (`tools/overlay.mjs` counter08; t0 = 07's end, 10.5 s after the break).
- **`blender/shots/s08_abyss.py`**: ocean frame (no tube: out of view), camera **locked** 1.2 m off the hole's axis,
  0.6 m under the base, 35 mm f/4, gaze at the axis 60 m down, rolled so the offset lies across the frame: the probe
  starts at the left edge (tether in from the left, the probe foreshortened), slides into the vanishing point near the
  centre and goes out there. EV +4 fixed (the fade is honest); port 30° off straight-away; focus keyed on the port;
  shutter 0.5; no motes (sub-pixel at these distances; `--motes 1` to test).
- **Animatic** (Cycles 25 %/16 spp, **0.3 s/frame, 1.9 min**): `out/08-abyss-animatic.mp4`. Mean luma falls smoothly;
  a blue point from ~6 s, gone by ~11 s: ~2.5 s of black under the caption (7.0–13.4).
- **Cycles check** `frames/08-check.png` (50 %/64 spp: 0.5 · 6 · 10 s): silhouette with the lit underside and the
  beam's glow; a blue point with a small halo; a last speck. **Full res 64 spp ≈ 7–9 s/frame → ≈ 40–50 min** (the
  film's cheapest Cycles shot); ladder step 1 for Sprint 5: the black tail (~11–14 s) is one frame repeated.

**Questions for the user (Sprint 3.8, after the animatic):**
1. Composition: the probe starts at the left edge (tether from the left), foreshortened from above, and slides to the
   centre where it goes out. OK, or start nearer the centre (smaller `--r`)?
2. Timing: gone at ~11 s, ~2.5 s black under the caption. Keep, or hold the point longer (×2.5: gone ~12.5 s)?
3. Exposure fixed at +4 EV (honest), or a slow ride up (the eye follows the light, as 05)?

**User's answers (2026-10-06):** all three as drafted (composition from the left edge, gone at ~11 s, EV +4 fixed).
**08 locked.**

**Sprint 4.0 (whole-film animatic) 2026-10-06, branch `sprint-4.0-animatic`.** User at the start: hard cuts everywhere
would read as short videos strung together → **three blocks, smooth joints inside them**: surface 01–04 · ice 05–06 ·
ocean 07–08 (+ the card). **Mix level** (user): edit-level joints where the pictures already meet, shot-level ones
(new heads/tails on locked shots, each with an animatic + Cycles stills) for 01→02 (02 opens at 01's end framing and
zooms 35 → 75 mm while the clock ramps ×1 → ×512), 03→04 (whip from Ganymede to Jupiter, cut in the blur) and
**04→05: tilt down into the ice** (user's pick over a dip to black: after the caption 04 tilts from the black disc to
the ice at its foot, red arch and starlight only; 05 opens descending through the milky ice to its start pose; 0.5 s
dissolve near black on the downward motion).
- **Baseline** (`node compile.mjs --animatic --silent`, 51 s): hard cuts, 117.0 s. Joint sheet
  `frames/europa-animatic-joints.png` (last/first frame of each joint): 01 → 02 the same disc and mesa (zoom match
  works); **03 opens with Jupiter in frame behind the probe**; 06's lamp and 07's glow sit within ~1/6 frame of each
  other; 07 ends beside the probe, 08 opens above it, both held 7 m down.
- **Edit-level joints** (`tools/timeline.mjs`): dissolves 02→03 30 f (time dissolve, dawn 1.18 h after Io set), 05→06
  18 f (the same cutaway at 34 m; counters cross in place), 06→07 24 f (the same lamp from the other side); **`TRIM_IN`**
  (new, frames cut off a clip's head with its overlay; layout `start` stays the clip's own t = 0, `in` = first shown
  frame, compile asserts both): 08 −19 f → 07→08 cut on the action 0.2 s before the brake lets go. Film **113.2 s**
  (01 @ 1.00 · 02 @ 13.00 · 03 @ 23.75 · 04 @ 32.75 · 05 @ 50.75 · 06 @ 60.00 · 07 @ 79.00 · 08 @ 93.00 · 09 @ 106.21).
- **Finding: the 02→03 dissolve shows two Jupiters** (02's 75 mm disc centred, 03's 35 mm disc at the right).
  Proposal: 02's tail zooms back out 75 → 35 mm and turns so the disc lands where it sits in 03, then the dissolve
  changes only the ground (night → dawn) round a Jupiter that doesn't move (the film's one fixed thing). Shot-level,
  in 02 with the 01→02 head.
- **User (2026-10-06):** 02→03 → **02's tail zooms back out and aligns Jupiter** with 03's (proposal above); shot-level
  joints **one per session**: **4.0b** = 02 (head: 01's end framing → 75 mm with the clock ramp; tail: 75 → 35 mm onto
  03's disc position; dissolve kept), **4.0c** = 03→04 whip (03 tail + 04 head), **4.0d** = 04→05 tilt into the ice
  (04 tail + 05 head). Each: script → that shot's animatic → joint frames → Cycles stills of the new head/tail →
  recompile → user. Then 4.0e: whole film v3, trims (05 into 06? 08 → 10 s?), captions/counters, QC → merge; 4.1 score.

**Sprint 4.0b (shot 02: head + tail) 2026-10-06, branch `sprint-4.0b-shot02`.**
- **Head** (`s02_neighbour.py`): frame 1 = 01's t = 12.0 s (35 mm, heading 6°, tilt 4°, −3.5 EV, 01's 0.3 m/s push
  easing out over 2 s); zoom 35 → 75 mm (log, 01's ease) with the heading → 0° and the tilt → the locked aim over
  0–2.6 s; clock ×1 → ×512 over 0–1.5 s (smoothstep rate, joined to the locked clock: Io still enters ~1.0 s; the
  shadow window, the setting at 10.5 s and the caption are unchanged). Star spots keyed with the lens (01's 24 mm
  size at frame 1 → 75 mm → 03's 35 mm), so the stars stay ~1 px through both joints.
- **Finding 1: the 02→03 dissolve only holds Jupiter if 02's clock runs on to 03's time.** 03 is set 1.18 h after Io
  sets; Jupiter turns 38° more in that time, so a disc frozen at Io's setting would show the GRS twice in the
  dissolve. → **Tail** 10.8–13.25 s: zoom back out 75 → 35 mm, turn to 03's azimuth (Ganymede's, −15.1°) and tilt 5°,
  crane 3 m right and 1.6 → 0.4 m down onto 03's spot, EV −4 → −4.5, focus/f-stop onto 03's (8 m, f/8); the clock
  (quintic Hermite) goes ×512 → peak ×2,900 → real time and lands on 03's sky (Io set + 1.18 h). **The Sun rises
  behind the camera at 12.0 s** and lights the ice in the time-lapse: real, and a first sunrise for the film.
  From 13.25 s every frame is 03's first frame without the probe; the 30-frame dissolve brings in only the probe,
  tripod, astronaut and frost. 02 = **14.5 s** (was 12).
- The ground is built about 03's spot (03's `Shifted` ground, rings from 0.3 m, az −46…+37°, ~13.5 M verts, split
  ≤ 1 M): the 02 tail and 03 match rock for rock (`frames/02-joints-v1.png`, bottom row).
- **03 fix (stars):** 03's star field was at turn 0; at its time the stars have turned 10.7° about the pole, so they
  doubled in the dissolve. `s03_probe.py` now sets the turn to `S['turn']` (one line; nothing else in 03 changes).
- **Finding 2: 01's sky is not 02's.** 01 is lit at elongation 178° (0.24 h *after* Io sets in 02's clock); 02's first
  frame is 1.4 h before that (−174.7°): Io stands 1° above the disc (in 01's 35 mm frame, missing there), Europa's
  own-shadow dot sits 3.3° away and the clouds are turned 4.6°. On a hard cut Io pops in. Options: **(C)** re-time
  01's sky to 02's first frame (Sun, GRS, star turn, Io added above the disc; 01's light barely changes: the Sun is
  below the horizon either way, Jupiter ≥ 99 % lit) → one continuous shot across the cut; or **(B)** a 12-frame
  dissolve at the same framing (Io fades in; reads as the time-lapse starting). Recommended: C.
- **Animatic** (`node render.mjs 02-neighbour --animatic --engine cycles --pct 25 --samples 16`, 0.4 s/frame, 3.1 min):
  the head zoom reads as one move with Io coming onto the limb; in the tail the limb mesa (2.4 km, 120 m) catches the
  Sun first (11.7 s), the plain ~0.15 s later (no air: sunlight comes on almost at once), then the long shadows
  shorten to 13 s. 03's animatic re-rendered at the same settings (old one predated the star fix);
  `node compile.mjs --animatic --silent` → `out/europa-animatic.mp4` **115.71 s** (01 @ 1.00 · 02 @ 13.00 · 03 @
  26.25 · 04 @ 35.25 · 05 @ 53.25 · 06 @ 62.50 · 07 @ 81.50 · 08 @ 95.50 · 09 @ 108.71). Dissolve measured: ground,
  rocks and Jupiter within 1/255 between 02's last and 03's first frame; only the probe, tripod, astronaut, crate and
  frost ring fade in.
- Cycles stills (50 %, 32 spp: 0 · 1.3 · 11.8 · 13.3 s): Io and its shadow at the head, the lit mesa against the disc
  at sunrise, 03's frame at the end. Render cost: 02 grows 288 → 348 frames (≈ +20 %, ≈ 37 min at 64 spp).
- Open (minor): 03's frost burst (its 1.0 s) falls in the last 6 frames of the 30-frame dissolve (probe at ~80 %);
  a 24-frame dissolve would end on it (02 → 14.25 s). The sunrise could be slowed (hold the clock near ×500 round
  12 s) if the user wants the light to creep down the mesa.
- **User (2026-10-06): C** (the hard cut was odd: Io popped in), **24-frame dissolve**, **slow sunrise**. Done:
  - `physics.lapse02_start` = 02's first-frame hours (shared by both shots; 02 asserts its clock matches). `s01_horizon`
    is lit at that sky: Sun −174.7° (8.4° down), GRS = 02's, star turn = 02's, 02's lamp, **Io added** (1° above the
    top limb, its shadow on the bands; Jupiter's own Sun light-linked as in 02). `--elong DEG` keeps the old static sky.
    01 last frame vs 02 first frame (50 %, 32 spp): mean difference 0.06/255.
  - Dissolve 30 → 24 frames (`timeline.mjs`): it ends on 03's frost burst. `--tt1` = end − 24 frames.
  - Slow sunrise: the tail clock is Hermite → constant ×577 for `--rise-s` 1.2 s while the Sun climbs −1.1° → −0.3°
    (the limb mesa's top catching the light → the knoll's plain lit, measured in the first animatic) → Hermite to 03's
    sky at real time. Tail 10.8–14.25 s (3.45 s), **02 = 15.25 s**. Clock: ×512 → ×2,300 → ×577 (11.6–12.8 s) →
    ×2,600 → ×1 at 14.25 s. At 12.0 s only the mesa's top is lit.
  - Animatics (Cycles 25 %, 16 spp): 01 1.6 min, 02 3.1 min (366 frames); `compile.mjs --animatic --silent` →
    **116.71 s** (01 @ 1.00 · 02 @ 13.00 · 03 @ 27.25 · 04 @ 36.25 · 05 @ 54.25 · 06 @ 63.50 · 07 @ 82.50 · 08 @
    96.50 · 09 @ 109.71). In motion: Io holds through the 01→02 cut; the light creeps down the limb mesa ~1 s before
    the plain comes up. Render cost: 02 ≈ 366 frames (≈ 40 min at 64 spp); 01 unchanged (+ Io, a 0.8° sphere).

**Sprint 4.0c (03→04 whip) 2026-10-06, branch `sprint-4.0c-whip`.**
- **`physics.WHIP34` + `whip34_ends(aspect)` / `whip34(tau, aspect)`**: one path in (az, el) from 03's end aim
  (Ganymede's azimuth −15.1°, 55.2° up) to 04's (az 0, 4.06° up), 52.8° long, shared by both shots (each asserts its
  own end pose = the path's end). 03: after the held 9 s, `out` 10 frames with speed ∝ t² (leaves the hold smoothly)
  up to **278°/s** (≈ 11.6°/frame, half 03's frame height); the cut at the peak, 41° down the path; 04: `inn` 7 frames
  in front of its old first frame, speed ∝ (time left)⁴ (a snap, then a soft landing), the peak screen speed matched
  across the cut (angular speed × focal length: 35 → 50 mm). Whip frames keyed to **shutter 1.0** (the shots keep 0.5).
- **v1 (rejected by me before showing):** out 8 / inn 12, smooth S both sides, 147°/s: the cut fell in the black sky
  (03's whip all black, Jupiter only from 04's 3rd frame): 0.6 s of black, read as a dip, not a whip.
- `s03_probe.py` `--whip 0` / `s04_sunfall.py` `--whip 0` restore the locked shots (clips back to 9 / 18 s). 04's clock
  is unchanged: `t` = clip second − 7/24 (real time before 0); caption moved by the same 7 frames; flash frames too.
- `tools/timeline.mjs`: `'03-probe': { kind: 'cut' }` (documents the whip joint).
- **Bug found in the Cycles check, fixed:** 03's last frame came out nearly sharp and 04's first half-smeared: motion
  blur samples the camera ±½ frame and the f-curves stopped at the clip's ends. Both shots now key one extra camera
  pose on the path (03 at `frame_end + 1`, 04 at frame 0). Cycles check `frames/03-04-whip-check.png` (50 %, 32 spp;
  top 03 at 9.0 · 9.33 · 9.375 s, bottom 04 at 0 · 0.04 · 0.125 s): the cut is smear → smear, Jupiter low centre-right
  in both; the shutter key works (frames 225/226 fully smeared).
- **Animatics** (Cycles 25 %, 16 spp): 03 1.0 s/frame (4.5 min), 04 0.4 s/frame (3.7 min). Joint sheet
  `frames/03-04-whip-joint.png` (03's last 10 frames, 04's first 10): Ganymede leaves the top in ~5 frames, ~4 frames of
  streaked sky, the tripod and ground smear into 03's last two frames, 04's first frame is Jupiter smeared upward,
  settled by its 4th. `node compile.mjs --animatic --silent` → **117.42 s** (01 @ 1.00 · 02 @ 13.00 · 03 @ 27.25 · 04 @
  36.67 · 05 @ 54.96 · 06 @ 64.21 · 07 @ 83.21 · 08 @ 97.21 · 09 @ 110.42).
- **Finding (continuity, for the user):** 04's camera is on 01/02's knoll (0, 0), 03's is 3 m right of it; 03's tripod
  and astronaut are 8–9 m in front of 04's camera and inside its locked 50 mm frame (checked on the real
  ground): the tripod at az +12.5° (sheave 16.8° up, nose −12.3°: legs across the frame just right of the disc's right
  limb), the astronaut at az −1.6°, head 1.2° up (in front of the disc's lower centre). 04 shows neither. A hard cut
  hid this; a whip says "same place, same moment". Options: **A** keep 04 as locked (a whip-cut can jump place; the
  40 h time-lapse follows; recommended), **B** add the tripod (and the astronaut for the real-time start) to 04 where
  they stand (true, but a new foreground across the disc's right limb in a locked shot), **C** move 04's camera ~6 m
  left so both fall just outside its frame (true geometry, looks like A; the foreground ice changes).
- Render cost: 03 +10 frames (flakes under a 1.0 shutter, ≈ +10–15 min), 04 +7 frames (≈ +1 min).
- **User (2026-10-07):** the whip "a bit fast" → **half the speed**: `out` 20, `inn` 14 (same exponents, so the cut
  stays ~41° down the path), peak **143°/s** (≈ 6°/frame at 35 mm); 03 = 9.83 s, 04 = 18.58 s (caption + 14 frames).
  Continuity **A**: 04 stays as locked (no tripod, no astronaut; the whip-cut jumps place). Render cost now 03 +20
  frames (≈ +20–30 min), 04 +14 (≈ +2 min).
  Animatics re-rendered (03 1.1 s/frame, 04 0.5 s/frame); `compile.mjs --animatic --silent` → **118.13 s** (01 @ 1.00 ·
  02 @ 13.00 · 03 @ 27.25 · 04 @ 37.08 · 05 @ 55.67 · 06 @ 64.92 · 07 @ 83.92 · 08 @ 97.92 · 09 @ 111.13); joint clip
  `out/03-04-whip-joint.mp4`; Cycles check `frames/03-04-whip-check.png` (03 at 9.67 · 9.79 s, 04 at 0 · 0.08 s): smear
  → smear, Jupiter in the same place across the cut.
- **User (2026-10-07):** the probe on its tripod shows in 03's last 3 whip frames (234–236, 0.12 s: az −9°, sheave
  27° up, on the whip's path from Ganymede to Jupiter; the cut was put there to hide in bright smear) → **keep** (the
  camera leaves the probe for Jupiter). Not moving the cut earlier (black sky again) or bending the path round it.

**Sprint 4.0d (04→05 tilt into the ice) 2026-10-07, branch `sprint-4.0d-tilt`.**
- **`physics.TILT45` + `tilt04(t)` / `tilt04_dur(top0)` / `tilt05(tau)`** (film picks, one row in `physics.py`): 04's
  pitch speed rises ∝ t² from the caption's end (clock 17.4 s) over 1.5 s to 15°/s and holds; its frame top (12.63°)
  passes 3.2° (the limb mesa's top: the last stars and the arch leave) at 19.03 s; 04 ends 6 frames later (clock 19.333 s,
  was 18; clip 19.92 s), so the **12-frame dissolve is centred on the black**. 05 opens **3 s** before its old 0 s,
  **5 m higher** (tested: the lamp's glow is all but gone 4 m above the start, black at 6 m), moving down at 04's screen
  speed (15°/s × 50/35 × 4 m / cos 12° = 1.53 m/s), a cubic Hermite (peak 2.23 m/s) onto its start pose, at rest on the
  old first frame. Before 05's 0 s: real time, the puck still seated.
- `s04_sunfall.py` `--tilt 0` / `s05_lid.py` `--tilt 0` restore the locked shots. 04: one camera key past the end
  (motion blur). 05: motion blur only in the head (shutter 0.5, keyed to 0 from its 0 s: the locked 10 s unchanged),
  one key before frame 1. 05's caption + 3 s; `counter05` takes clip seconds (clock = − head); new clip field
  **`counter_in`** (`tools/overlay.mjs`, default 0): 05's clock readout fades in at 3 s, as the descent lands (it popped
  up over the black dissolve). `tools/timeline.mjs`: `'04-sunfall': dissolve 12`.
- **The ice at the camera's foot is black** (honest: starlight and the arch only; Jupiter's night side dark; the stars
  are camera-only in the scene): in 04 the "tilt into the ice" reads as the arch and the stars sliding up and out over
  the black ground; the ice itself is first seen in 05.
- Animatics (Cycles 25 %, 16 spp): 04 0.5 s/frame (4.1 min, 478 frames), 05 2.5 s/frame (13.3 min, 312 frames).
  `node compile.mjs --animatic --silent` → **121.96 s** (01 @ 1.00 · 02 @ 13.00 · 03 @ 27.25 · 04 @ 37.08 · 05 @ 56.50 ·
  06 @ 68.75 · 07 @ 87.75 · 08 @ 101.75 · 09 @ 114.96). Joint clip `out/04-05-tilt-joint.mp4` (film 53.5–61 s), sheet
  `frames/04-05-tilt-joint.png` (every 10 frames from 55 s); Cycles check `frames/04-05-tilt-check.png` (50 %, 32 spp:
  04 at 18.75 · 19.4 s, 05 at 1.25 · 2.25 s).
- Render cost: 04 +32 frames (≈ +4 min), 05 +72 frames (≈ +1 h at 60 s/frame; the dark early head is cheaper).
- **User (2026-10-07): approved as built** (black ice at the foot, 05's 3 s / 5 m head, the render cost).

**Sprint 4.0e (whole film v3: trims, captions/counters, QC) 2026-10-07, branch `sprint-4.0e-film`.**
- **Review** of `out/europa-animatic.mp4` (121.96 s): 1-fps contact sheet + per-second motion (frame difference) and
  luma of the picture area. Slow/dark stretches: 03's tilt through the star sky (film 32.6–37.0 s; stars and Ganymede
  are sub-threshold specks at 25 %), 04's night under the caption (50–57 s, the thin red arch), **08's tail** (the
  point's peak luma ≈ black from ~10.5 s clip; ~4 s of black under the caption before the card) and 06's slow landing
  (84–87 s, kept as locked). The 05→06 dissolve read as one move, but **its two counters overlapped** (05's
  `+5.8 h 33.9 m` printed over 06's `+2 d 34 m −173 °C 0 bar`, different columns).
- **User (2026-10-07): 08 → 12 s; 05→06 kept as is.**
  - `physics.SHOT08` dur 14 → 12 (`s08_abyss.py` asserts it): 103 m at 12 s (25.9 s real; blue −12 EV at 11 s, −13 at
    12 s); counter08 ends +36 s 20,103 m 243.3 bar. Caption 7.0 → 11.6 s (4.6 s; ~1 s over black). 08 animatic
    re-rendered (Cycles 25 %, 16 spp, 0.3 s/frame, 1.7 min).
  - New clip field **`counter_out`** (`tools/overlay.mjs`: the readout is gone at that clip second, 0.25 s fade):
    05 `counter_out` 12.5 (gone 6 frames into the 18-frame dissolve), 06 `counter_in` 0.5 (in by 0.75 s, the dissolve's
    end): the readouts swap inside the dissolve instead of overlapping. 08 `counter_out` 12 (no pop at the cut to the card).
- `node compile.mjs --animatic --silent` → **119.96 s**, 2,879 frames (01 @ 1.00 · 02 @ 13.00 · 03 @ 27.25 · 04 @ 37.08 ·
  05 @ 56.50 · 06 @ 68.75 · 07 @ 87.75 · 08 @ 101.75 · 09 @ 112.96). Captions (film s): EUROPA 9.20–12.60 · IO 19.50–24.40
  · SUN 48.67–55.07 · NO WAY BACK 64.50–68.90 · NO SUNLIGHT 95.75–101.15 · 100 KM 107.96–112.56; none crosses a cut; 05's
  ends 0.15 s into its dissolve (faded by then). Layout = compile (asserted).
- Render cost: 08 −48 frames (≈ −6 min).
- **User (2026-10-07), reversing 4.0c's "keep": no probe in the whip.** The tripod and probe smeared through 03's frames
  231–235. `s03_probe.py`: every object built for the probe, tripod, astronaut and frost (90) gets `hide_render` keyed
  on from the first whip frame (217); `--whip-hide 0` keeps them. The camera has left them since the tilt and 04 shows
  neither (continuity A), so the whip now lands on lit ground and Jupiter only. One high frost flake that showed in the
  whip frames went with them; no pop at 216 → 217 (frames 212–219 at 4× gain: stars only). 03 animatic re-rendered
  (4.5 min); joint clip `out/03-04-whip-joint.mp4` (film 34.5–39.5 s). Film unchanged, 119.96 s.
- **07→08: 08 opens on 07's last view (user 2026-10-07: tried, approved).** The old cut (07 beside the probe, level,
  the probe upright → 08 from above, the probe lying across the frame, bright → black) read as a new scene.
  `physics.SEAM78` (07's end-pose defaults copied; `s07_breakthrough.py` prints a NOTE if its pose drifts from them):
  08's head starts on 07's end pose (24 mm, beside/behind the port, el −3°, EV +5, 07's grain cloud) under a
  **12-frame dissolve**, holds 0.5 s, then one smoothstep move 0.5–3.5 s: crane up 5.7 m beside the hole, slerp onto the
  locked view (a ~90° roll on the way: the probe turns from upright to across the frame), 24 → 35 mm (log), EV +5 → +4.
  08's own clock starts at clip 2.5 s (`head`), so the brake lets go at 3.5 s as the camera settles. The port sits at
  07's 40° (08 had 30°: no twist at the seam). `TRIM_IN` 08 removed; `counter08` takes clip seconds; counter fades in
  at 3.5 s; caption 9.5–14.1 s. `--head 0` = 08 as locked in 3.8. 08 = 14.5 s.
  - Seam: 08's first frame matches 07's last (probe, beam, motes); only the ceiling's scallops show faintly at the top
    (07's base ice is the glowing volume, 08's the surface material); the dissolve hides it.
  - Animatic 0.4 s/frame (2.3 min); joint clip `out/07-08-seam-joint.mp4` (film 98.5–106.5 s); Cycles check
    `frames/07-08-seam-check.png` (50 %, 32 spp: 0 · 1.75 · 3.0 s).
  - `compile.mjs --animatic --silent` → **122.75 s** (… 07 @ 87.75 · 08 @ 101.25 · 09 @ 115.75). Render cost: 08 +60
    frames near the lamp (≈ +20–30 min).

## Next
Finding 1 (Io + two shadows in 02): verified, in TREATMENT as C2 and in 02's row (user 2026-10-05).
01's framing test done (2.0, the turn); the ground done (2.1); the cryobot done (2.2); the shell interior done (2.3,
approved: puck release in 05, porosity 0.2 %); the under-ice ocean done (2.4, approved: melt ceiling, frazil ⚠ only if
07 wants it; particles and 08's sink speed open for those shots). Sprint 2 builds are complete → Sprint 3, shots one per session: **01 locked (3.1); 02 locked (3.2); 03 locked (3.3); 04 locked (3.4); 05 locked (3.5); 06 locked (3.6); 07 locked (3.7); 08 locked (3.8); 09 locked (3.9, the card); Sprint 4 done; Sprint 5.0 ladder + 5.1 batch done; next 5.2 renders (user)**. W1–W3 closed (Sprint 4.1: 03 kept Breathing Idle; ice cracks recorded (Freesound 146419), water and hum synthesized, user 2026-10-07).

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
5. Batch render (resume) → 4K compile, srt, poster (re-planned 2026-10-07: 5.0 ladder · 5.1 batch + 09 credit ·
   5.2 renders, started by the user, cheapest clip first · 5.3 deliver; see State).
6. The 9:16 climax cut (02 + 04, own portrait cameras) (user 2026-10-07: split out of 5).

## Decisions (locked)
- Credits (user 2026-10-07, Sprint 5.1): none in the film (card, srt); all in the YouTube description (REFERENCES.md).
- Samples (Sprint 5.0, 2026-10-07): **64 spp for every clip**; 32 spp failed the full-res A/B on all eight (`tools/ab.mjs`,
  table in State); motion blur kept everywhere. Batch order = cheapest first by measured `spf`.
- Sound (user 2026-10-07, Sprint 4.1): ice sounds and hydrophone synthesized, then (v2, same day) the cracks recorded (Freesound 146419, CC-BY: credit); recorded sounds, if
  ever, CC0 or CC-BY (credited); the physics arc (vacuum → helmet only; the ice and then the water carry sound; out with
  the light; one held note under the title). Music in Io's synth family (A on the surface, D under the ice).
- Whole film v3 (user 2026-10-07, Sprint 4.0e): 08 → 12 s; 05→06 unchanged; readouts never overlap (`counter_out`);
  no probe/tripod/astronaut/frost in 03's whip frames (hidden from frame 217; replaces 4.0c's "keep").
- 07→08 (user 2026-10-07, Sprint 4.0e): `physics.SEAM78`: 08 opens on 07's end pose, 12-frame dissolve, crane up +
  turn down onto the locked view 0.5–3.5 s, brake at 3.5 s; port at 07's 40°; 08 = 14.5 s; film 122.75 s.
- 04→05 tilt (user 2026-10-07, Sprint 4.0d): `physics.TILT45`: 04 tilts down from the caption's end (clock 17.4 s, up
  to 15°/s) into the black ice, ends 6 frames after its frame goes black (clip 19.92 s); 12-frame dissolve centred on
  the black; 05 opens 3 s early, 5 m up, coming down at 04's screen speed into the lamp's glow (clip 13 s, motion blur
  in the head only); 05's counter fades in at 3 s (`counter_in`). Film 121.96 s.
- 03→04 whip (user 2026-10-07, Sprint 4.0c): `physics.WHIP34` out 20 / inn 14, speed ∝ t² then ∝ (time left)⁴, peak
  143°/s, cut at the peak ~41° down the path (tripod and lit ground smearing in), whip shutter 1.0; 03 = 9.83 s, 04 =
  18.58 s (clock from 0.58 s). Continuity A: 04 as locked, no tripod or astronaut in its frame.
- 08 locked (user 2026-10-06, Sprint 3.8): `s08_abyss.py` as checked: camera locked 1.2 m off the hole's axis,
  0.6 m under the base, 35 mm f/4, looking down the tether (gaze at 60 m on the axis); held 7.0 m down, brake off at
  1 s, free fall (`drop08`, terminal 4.5 m/s), clock ×1 → ×3 over 2.5–7 s → 130 m at 14 s (**4.0e, user 2026-10-07: 12 s, 103 m,
  caption 7.0–11.6 s**); EV +4 fixed; the light a
  blue point from ~6 s, gone ~11 s; counter `破冰后 · SINCE THE BREAKTHROUGH` s · m · bar. Renders in the Sprint 5 batch
  (≈ 40–50 min at 64 spp; the black tail one frame repeated).
- 07 locked (user 2026-10-06, Sprint 3.7): `s07_breakthrough.py` as checked: in the water, 24 mm, f/4; hold on the
  hole (gaze 40° up), crane down 6.5–12.5 s to behind/beside the probe looking out along its beam; clock ×2,890 → real
  time by 3.4 s, break 3.5 s, the 0.134 g drop stops 7 m down at 9.0 s (`drop07`); the glow hold kept; the tube a black
  well (light pipe, `tube07` 351 m; no tail lamp, no mush); port 40° off the line of sight, away; EV 0 → +4 → +5;
  motes ahead of the end pose; **base ice = scattering volume** (`ocean.ice_volume_mat`, slab absorbs as water);
  probe in the last frame. Renders in the Sprint 5 batch (≈ 3.5–4 h at 64 spp before the ladder).
- 06 locked (user 2026-10-06, Sprint 3.6): `s06_descent.py` as checked: cutaway 35 mm, the camera fixed to the probe
  (top → head over 1–17 s); depth in ln z, ×2,890 → ×27 M → ×2,890, 34 m → 19,980 m (day 2.1 → 1,043.4) in 20 s,
  the slow ~5 s landing kept; treadmill (106 wraps), **shutter 1.0**; EV +3 → +5 by depth (0.3–3 km), then → +2 by
  time (12–16 s), lamp port −40° (as 05); pucks dropped unseen, gone after 18 km; counter `开始下潜后 · SINCE THE
  DESCENT BEGAN` days · m · °C · bar. **07 uses the open water tube above the probe** (finding 4). Renders in the
  Sprint 5 batch (≈ 6.5–7 h at 64 spp before the ladder: the milky first half is the target).
- 05 locked (user 2026-10-05, Sprint 3.5): `s05_lid.py` as checked: 30 m, puck 1 (film pick `CRYO_PUCK_FIRST`),
  cutaway 35 mm, camera stays in the ice with the puck, push-in 4.0 → 2.6 m, looking down 12° → 4°; real time → ×2,890
  over 0.5–3.0 s, the front reaches the puck at 5.0 s (caption), 4.07 m sunk by 10 s; refrozen core (IceCube's bubble
  column, `HOLE_CORE`, subtle) kept; EV +3 → +5.5 (4–9.5 s); clock `投放中继器后 · SINCE THE RELAY WAS LEFT` + depth;
  sheets bored once (`shell.fix_bore`). Renders in the Sprint 5 batch (≈ 4 h at 64 spp before the ladder).
- 04 locked (user 2026-10-05, Sprint 3.4): `s04_sunfall.py` as checked: 50 mm, top limb 3° under the frame top,
  03's dawn → ×25,373 day → first contact 10 s, covered at ×31 by 13.5 s (87 s real; "real time" eased), real time
  after; exposure −4.5 → +5 EV (13.0–15.5 s), stars at true brightness, red arch on the ice; **no corona, no
  lightning**; backlit grey-white ice kept. Renders in the Sprint 5 batch (≈ 45–50 min at 64 spp).
- 03 locked (user 2026-10-05, Sprint 3.3): `s03_probe.py` as checked: **dawn** (1.18 h after Io set, Sun 2.3° up
  behind the camera, −4.5 EV), 35 mm, eye 0.4 m, camera 3 m right of 01/02's spot, probe on its tripod at 8 m, frost
  burst at 1.0 s (G = blown frost; the vapour lobe off: invisible), tilt 5° → 55° over 3.0–8.0 s to Ganymede, **9 s**
  (film ≈ 1:55). Renders in the Sprint 5 batch (≈ 2.5–3 h at 64 spp before the ladder).
- 02 locked (user 2026-10-05, Sprint 3.2): `s02_neighbour.py` as checked: 75 mm locked, horizon 0.3° above the foot,
  time-lapse ×512 (Io on the top limb 1.0 s, sets 10.5 s), −4.0 EV; **Europa's shadow crosses Io mid-shot** (mutual
  eclipse, real at Jupiter's equinox season; `--e-end 179`: 2.4–7.3 s, deepest 4.9 s). Renders in the Sprint 5 batch
  (≈ 31 min at 64 spp).
- 01 locked (user 2026-10-05, Sprint 3.1): `s01_horizon.py` as checked: pan 150° → 6° over 2.3–8.8 s (peak 42°/s),
  24 → 35 mm, +1.5 → −3.5 EV by heading, push 3.6 m, motion blur 0.5, limb mesa `1.0:2.5:40`, caption 8.2–11.6 s.
  Renders in the Sprint 5 batch (≈ 41 min at 64 spp).
- 05 (user 2026-10-05, Sprint 2.3 finding 2): the probe releases a relay puck and the clear column freezes over it
  ("no way back" made visible; the freezing front itself is nearly invisible). Near-surface porosity stays 0.2 %
  (milky: the probe is a lantern in the ice).
- Shot rule (user 2026-10-04): within real physics, as spectacular as possible, above all phenomena Earth can't show;
  tentative/lab-predicted ones only marked ⚠ and with a yes (also in CLAUDE.md).
- Fear (user 2026-10-04): **深渊**, with the horizon and Io as the surface half. Horizon (¾-Jupiter fixed on the
  Conamara horizon) → Io crosses Jupiter's face (callback to ep. 2) → down through the ice → the dark ocean; end on the
  ocean numbers.
- Descent and people (user 2026-10-04): a small astronaut on the surface (Io's EMU #12622 + Mixamo, reused); below the
  surface a **code-built cryobot** (melt probe) goes down, time-lapse with a counter (depth / pressure / days), then its
  one lamp in the black water. No open 20 km crack (not real), no human under the ice. Real physics throughout.
- Cryobot (user 2026-10-05): code-built from PRIME (size) + Tunnelbot (layout, pucks) + VALKYRIE (hot-water jets);
  PRIME's SWIM micro-swimmers in, marked ⚠ (concept).
- 02 carries Io's shadow + Europa's own shadow on the bands (user 2026-10-05, TREATMENT C2).
- 01 = **the turn** (user 2026-10-05, finding 2): glowing mesa (~150° from Jupiter) → pan left ~145°, 24 → 35 mm,
  exposure ride −4 EV, slow drift; ends on the disc with a mesa biting its lower limb (scale). TREATMENT 01 row.
- Under-ice ceiling (user 2026-10-05): **melt** (terraces + scallops); ⚠ frazil only if 07 asks for it.
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
- A/B a sample cut on mean luma as well as PSNR: with motion blur (06's shutter 1.0) 32 spp shifted whole frames by up
  to 7 levels, a flicker the denoiser can't hide. And test every distinct part of a clip: 08 passed at 57–59 dB in the
  fall, failed at 39–42 in its head (07's lamp-lit pose).
- Cycles animatics need persistent data: without it every frame re-syncs the whole ground (04: 40 s → 0.5 s/frame).
- A planet lit from behind (eclipse) at night exposure showed its own far side bounced onto the night face through a
  smooth-shaded sphere (~5e-5): make far bodies invisible to diffuse/glossy rays when nothing real lights them.
- Light diffusing through scattering ice needs many volume bounces (~(r/transport length)² × 1/(1 − g) events): 8
  left everything past 0.5 m black; 128 + the similarity relation (σs(1 − g), g = 0) carry it metres. Keep the true g
  where the medium is thin (single scattering: the beam's side-look depends on it).
- Textured (heterogeneous) volumes cost ~4× homogeneous ones: build structure from overlapping homogeneous sheets
  (volumes add) and Boolean holes, and key the one σs value.
- Sheets with polygon rims read as planks: taper them (lens), make them bigger than the frame, clip to the box.
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
