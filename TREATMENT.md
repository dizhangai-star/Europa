# Europa · 深渊 (Abyss): Treatment (clip list locked 2026-10-04)

Episode 3 of the planet series (恐惧 / Fear), after *巨物* and *Io · 永恒*. Standalone film. Clip list, 9:16 climax,
⚠ items and cryobot power locked by the user 2026-10-04 (§8); shot details still change in each shot's animatic.

## 1. Brief
- About 2 min (length set from §5), 24 fps, 1920×1080 with a 2.39:1 letterbox (picture 1920×804), delivered 4K, grade
  matched to 巨物 / Io (AgX, grain, vignette). Picture: Blender 5.2 Cycles from Python; Workbench/EEVEE animatics.
- A 9:16 cut of the climax (§6), with its own portrait cameras.
- No narration; captions EN (Cinzel caps) over 简中 (Noto Serif SC), as Io. Counters added at compile.
- **Shot rule (user 2026-10-04): within real physics, as spectacular as possible, above all what Earth can't show.**
  Every number from `python3 tools/physics.py`. Tentative or lab-predicted phenomena carry a ⚠ and need a yes.

## 2. What only Europa shows (the spectacle list, from `physics.py`)
Surface: Conamara Chaos (9.7° N, 273.7° W), where Jupiter sits on the horizon for ever.
| # | phenomenon | numbers | status |
|---|---|---|---|
| A | **Three-quarters of Jupiter fixed on the horizon** (the lowest quarter below the ice), due west; its axis near horizontal, so **the bands stand vertical** and the clouds roll *down* into the ice, one turn per 11.23 h | centre 3.5° up, 12.3° wide; pole +80° from up | real |
| B | **The Sun never sets: it sinks into Jupiter.** It descends almost vertically onto the top limb and goes out 9.5° above the ice in ~1.5 min; it would come back out below the horizon. Sunset = eclipse, every 85.3 h. Then a black disc with a **red refraction arch standing on the ice**, and the stars flood in | first contact 8.2–9.6° up (by season), ingress 1–2 min | real (ring colour as Io) |
| C | **Io sets into the ice in front of Jupiter.** It enters the top limb and slides down across the bands for 1.35 h, then the horizon swallows it while it is still on the disc. At full Jupiter it is a bright 0.84° disc (1.6× our Moon) | 135 mm: Jupiter 1,543 px, Io 105 px; but the visible ¾ (top limb 9.6° up) is 1,215 px, taller than the 804 px frame, so Io's entry at the top limb falls outside it; 85 mm fits the whole visible disc (765 px, Io 66 px): **02 = 75 mm (user 2026-10-05, Sprint 3.2)**: Io visible above the disc before it enters | real; needs Jupiter ≥ 90 % lit and the Sun down: 14 transits in a row, once every 438 d |
| C2 | **Two shadows on the bands: Io's, and our own.** During the same night transit Io's black shadow crosses the clouds beside it (the Sun–Io line meets the cloud tops), and Europa's own shadow sits on Jupiter at the anti-solar point: it is on the disc for 2.9 h (= the eclipse), mostly in the last hours of the night | Io's shadow 1.85° from Io (Sun 178°), 0.68° (Sun 180°); Europa's umbra 0.16° in a 0.37° penumbra (135 mm: 21 / 46 px); `physics.io_cast_shadow`, `own_shadow` | real (geometry: shadow transits, Hubble 2015; seen from Europa itself never photographed) — user 2026-10-05 |
| D | **Three worlds in one sky.** On every other Io transit (Laplace 1:2:4), Ganymede hangs 60° up, 0.24° wide, 84 % lit | — | real |
| E | **Giant-lamp lighting.** Full-Jupiter light comes from 3.5° up: ice faces turned to Jupiter get 13× the light of the flat plain; chaos blocks glow on one side, the plain is near black, shadows run for kilometres | wall 259 mW/m², plain 20 mW/m² (Sun 50 W/m²) | real |
| F | Black sky, stars by day, the Sun a 0.10° point at 1/27 of Earth's light | — | real |
| G | **Water boils and freezes at once** where the cryobot first melts into the ice under vacuum: a spray of vapour and ice crystals in Jupiter-light | — | real (behaviour); exact look by reference |
| H | Radiation: a ~50 %-lethal dose in 20 h at the surface | 5.4 Sv/day | real (caption) |
| I | Lightning flashes on Jupiter's night side while it is black (seen by Voyager, Galileo, Juno) | brightness to check | real; was in 04 (user 2026-10-04); **dropped 2026-10-05** after the animatic: odd inside the eclipse (true flashes are 1-px points; enlarged ones looked like moons) |
| J | ✗ (not used) Water plume, 200 km, vented at 683 m/s, 20 min flight, sunlit ice crystals, ballistic umbrella | — | tentative (Hubble 2012/2016) |
| K | ✗ (not used) Faint glow of the night-side ice under Jupiter's radiation | — | lab prediction (Gudipati et al. 2020) |

Below (ice 20 km over a 100 km ocean):
| # | phenomenon | numbers | status |
|---|---|---|---|
| L | **The hole closes behind the probe**: the melt water refreezes above it; there is no way back | 10 kW: 1,044 days to 20 km, 0.68 → 1.19 m/h | real (concept physics) |
| M | Ice from −173 °C to −2 °C on the way down; pressure 0 → 242 bar | conductive profile | real (model) |
| N | **Light dies by colour** in the water: red gone within 3 m, green ~18 m, blue ~100 m, then nothing | Pope & Fry 1997 | real (clearest case) |
| O | An ocean 2.1× all of Earth's, 100 km deep; sea floor 1,596 bar (= 15.8 km down in Earth's sea) | — | real (model ranges) |

## 3. Logline and arc
On Europa the Sun can't even set; it falls into Jupiter. And under the ice there is a sea no light has ever touched.
- **Act I, the surface (night before dawn → a day → the fall of the Sun):** the fixed ¾-Jupiter, Io sinking into
  the ice, a tiny astronaut and a probe that starts to melt its way down; one day in time-lapse ending with the Sun
  falling into Jupiter and the red arch.
- **Act II, the lid:** the probe in its bubble of melt water, 20 km of ice in time-lapse; the hole freezing shut above.
- **Act III, the abyss:** the ice ends; the lamp in black water; the light sinks away from us until it is gone.
- **Native move at the peak:** vertical. Everything in this film goes *down*: Jupiter's clouds, Io, the Sun, the probe,
  the light. (It also makes the 9:16 cut natural.)
- **Against Io:** there the giant was fixed overhead and nothing moved; here the giant is fixed on the floor of the
  sky and everything else falls toward it, then below it.

## 4. Benchmark
- Galileo's Conamara mosaics (the ground), Cassini/Juno Jupiter, Icefin under Antarctic ice shelves (under-ice light,
  the ice ceiling), NASA/JPL cryobot concepts (PRIME, SESAME), *2001* (stillness), Apollo hard light.
  **Learn:** scale by a small human, vacuum light, a single lamp in black water. **Don't take:** designs, logos,
  *Europa Report*'s life or plot. Nothing alive is shown.

## 5. Clip list (≈ 1:58, locked 2026-10-04; the whole-film animatic may still trim)
| # | clip | dur | lens / camera | action | caption |
|---|---|---:|---|---|---|
| 01 | horizon | 12 s | 24 → 35 mm, eye 1.6 m, **the turn** (user 2026-10-05): hold on a glowing mesa (~150° from Jupiter), pan left ~145° (fast through the dark middle) while zooming 24 → 35 mm and riding exposure −4 EV, slow forward drift; end on the disc with a mesa biting its lower limb | night, full Jupiter: block faces glow on the Jupiter side, the plain dark (E); ¾ of Jupiter above the ice, bands vertical (A) | EUROPA · 木卫二 |
| 02 | neighbour | 12 s | 75 mm, locked; the ice horizon cuts the frame's foot | time-lapse 1.35 h (×512): Io enters at the top limb, slides down the bands with the clouds, its black shadow travelling beside it, Europa's own shadow on the disc too (C2); **mid-way Europa's shadow crosses Io** (mutual eclipse at Jupiter's equinox: Io black in a lit ring, user 2026-10-05); it sets into the ice in front of Jupiter (C) | IO. WE STOOD THERE. / 我们曾站在那里 |
| 03 | the probe | 9 s | 35 mm, low, then tilt up | **dawn** (user 2026-10-05: the Sun rises opposite Jupiter, behind the camera; all sunlit at one exposure): the astronaut beside the cryobot on its tripod as it starts: its vapour (invisible) blows the loose frost out, flakes fly vacuum parabolas at 0.134 g (G); tilt up to Ganymede 58° up (D) | — (the radiation fact moved to the end card) |
| 04 | the fall of the Sun | 18 s | 50 mm, locked on Jupiter (top limb 3° under the frame top), foreground blocks | time-lapse of the 40 h day (×25,000), eased: sunrise light sweeps in from behind, Jupiter wanes to a crescent, the Sun descends vertically onto the top limb (10 s) and is covered at an even ×31 (87 s real in 3.5 s), real time after (B); the ice turns grey-white while backlit; black disc, red arch on the ice, stars flood (no lightning, no corona: user 2026-10-05) | THE SUN NEVER SETS HERE. IT FALLS INTO JUPITER. / 这里的太阳从不落下，它坠入木星 |
| 05 | the lid | 10 s | cutaway, 35 mm, the camera stays in the ice with the puck, slow push-in 4 → 2.6 m | 30 m down (user 2026-10-05): the probe leaves relay puck 1 on its tether and sinks away (×2,900, clock top-left); the refrozen column's milky core (IceCube's bubble column) comes down onto the puck at 5 s: the hole has closed over it (L); the glow leaves, red first | THERE IS NO WAY BACK / 没有回头路 |
| 06 | descent | 20 s | inside the ice, following | 1,044 days in time-lapse, eased; ice layers, cracks and old refrozen bands pass up; counter: days · depth · temperature · pressure (M) | — (counter only) |
| 07 | breakthrough | 14 s | under the ice ceiling, looking up then level | the last metres melt; the probe drops into the water; the lamp: red dies first, cyan, particles, the ice ceiling above lit, nothing below (N) | NO SUNLIGHT HAS EVER REACHED IT / 从没有阳光到过这里 |
| 08 | abyss | 14 s | locked, looking down | the probe sinks away on its tether; its light shrinks to a blue point and goes out; counter 242 → … bar | 100 KM OF WATER BELOW / 下面还有一百公里的海 |
| 09 | title | 6 s | card (`tools/card.mjs`) | 木卫二 · 深渊 / EUROPA · ABYSS + readout: 2.1× EARTH'S OCEANS · 1,596 BAR · A LETHAL DOSE IN 20 HOURS (H) | — |

Trim candidates if the animatic drags: 03 → 8 s, 05 into 06, 08 → 10 s.

## 6. 9:16 climax (locked 2026-10-04: 02 + 04)
The film's motion is vertical, so portrait suits it: **02 (Io sinks into the ice) → 04 (the Sun falls into Jupiter)**,
≈ 30 s, own portrait cameras (vertical fov fits the disc + the falling Sun + the ice), rendered after the 2.39:1
film. Captions re-set for portrait.

## 7. Physics (`python3 tools/physics.py`, rows used above)
Site, Jupiter place and axis, Sun track by season, sunset = eclipse, Io's transit path, transit windows, Ganymede,
full-Jupiter light on walls vs plain, radiation, the shell's temperature profile, ice-base melting point, cryobot
times (1 / 5 / 10 kW), light in pure water, ocean pressure and volume.

## 8. Decisions on this draft (user 2026-10-04)
1. Length ≈ 1:58 as §5. 2. 9:16 climax = 02 + 04. 3. Lightning (I) in 04: yes (dropped 2026-10-05 after 04's animatic); plume (J) and ice glow (K): no.
4. Cryobot 10 kW: counter 0 → 1,044 days. 5. The radiation fact goes on the end card (09), not in 03.
6. (2026-10-05, after the Sprint 1 look spike) 02 carries Io's shadow and Europa's own shadow on the bands (C2).

## 9. Assets (log every download in REFERENCES.md; files in `../../_assets/`)
- Jupiter 14K map (have, Io). Astronaut EMU #12622 + Mixamo Breathing Idle (have, Io).
- USGS Europa global mosaic (Galileo SSI + Voyager), Galileo Conamara close-ups (public domain): to download (Sprint 0.4).
- Under-ice references (Icefin, public footage) for look only.

## 10. Sound (sketch)
Surface: Io's recorded breath, no suit sounds; a sub drone under 01–02; 04 near-silence at the Sun's fall, one
heartbeat at the arch. Ice: creaks and deep cracks (the shell flexes with the tide), the probe's hum muffled.
Ocean: a hydrophone hum, then silence as the light goes out. Title: one held note.
