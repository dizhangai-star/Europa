# Europa · 木卫二: brainstorm (2026-10-04)

Episode 3 of the planet series (恐惧 / Fear), after *巨物* (`../imagnation`) and *Io · 永恒* (`../Io`).
Numbers: `python3 tools/physics.py` (adapted from Io's). Nothing below is locked.

## What the physics gives us (vs Io)
| | Io | Europa |
|---|---|---|
| Jupiter in the sky | 19.6°, fixed | **12.3°, fixed** (rocks ±1.1° over 3.55 d: invisible in any shot) |
| Day = eclipse period | 42.5 h | 85.3 h; eclipse 2.9 h |
| Full-Jupiter shine | 0.78 W/m² | 0.31 W/m² (39 % of Io's, still ≈ 110× full moonlight) |
| Ground | sulfur, lava, brown-yellow | water ice, white-blue, red-brown lineae and chaos. Albedo about the same (~0.6–0.7); the difference is colour, not brightness |
| Gravity | 0.18 g | 0.13 g |
| Under the ground | rock and magma | **ice 10–30 km, then ~100 km of ocean**: 2.1× all of Earth's seawater; sea floor ~1,600 bar = 15.8 km down in Earth's sea (Mariana: 10.9 km) |

New sky events, none of them in the Io film:
- **Io crosses Jupiter's face.** At every Io–Europa conjunction (84.6 h) Io, 0.84° wide (1.6× our Moon), drifts across
  the disc in 1.7 h. Long lens: 135 mm → Io 105 px against a 1,546 px Jupiter. The callback to episode 2: *we stood there*.
- **Io's shadow on Jupiter.** A black dot at the sub-solar point, every Io day. Io and its own shadow on the disc
  together only when Jupiter is nearly full (Sun almost behind us, our night).
- **Jupiter on the horizon, for ever.** At Conamara Chaos (9.7° N, 273.7° W) Jupiter's centre is 3.5° up, its lower limb
  2.6° below the horizon: half a giant planet sitting on the ice, permanently, a sunrise that never finishes.
  Pwyll crater: 1.1° up, almost all of the lower half hidden. (The ±1.1° libration makes it rise and sink a little over 3.5 days.)
- Ganymede, 0.76° at its nearest, sits on the other side of the sky (it never crosses Jupiter).

## Fear: three directions
1. **冰下 · BELOW (thalassophobia, the abyss).** The surface is the lid. A crack, down through 20 km of ice, into an
   ocean no light has ever reached. Strongest fear, most new work (ice walls, under-ice darkness).
2. **邻居 · THE NEIGHBOUR (渺小, again).** Io crosses Jupiter's face as a small bright disc; a whole world we
   just made a film about is a dot. Almost all reuse, but the emotion repeats Io's.
3. **地平线 · THE HORIZON (永恒 → 停滞).** Conamara: ¾ of Jupiter fixed on the horizon, chaos-terrain ice blocks
   in front. Never rises, never sets: the one image only Europa has.

**Recommended: 3 + 1 (+ 2 as a beat).** Open on the horizon (new image), Io crosses as the one thing that moves
(callback), then the lid opens: down into the dark. Ending sentence on black: the ocean numbers.

## Rough clip idea (~60 s, not locked)
| # | beat | picture | caption idea |
|---|---|---|---|
| 01 | horizon | Conamara ice blocks, low eye; ¾ of Jupiter on the horizon, white-blue ice catching its light | EUROPA · 木卫二 |
| 02 | neighbour | 135 mm: Io's small bright disc creeps across the bands (sped up) | IO. WE STOOD THERE. / 我们曾站在那里 |
| 03 | the lid | from above (drone rise like Io 05): a double ridge / dark lineae splits the plain; push into the crack | — |
| 04 | down | descent through blue → black ice, depth counter 0 → 20 km (Io's 03 counter style), sound of ice | — |
| 05 | the ocean | black water; one light (a probe lamp) and nothing else; counter keeps going: 242 bar … 1,596 bar | NO SUNLIGHT HAS EVER REACHED IT / 从没有阳光到过这里 |
| 06 | title | card: 2.1× EARTH'S OCEANS · 100 km DEEP · 木卫二 · 深渊 | — |

Who is in it? Io had the astronaut. Here: astronaut on the surface (01/03), then a code-built probe lamp underwater
(we can't honestly put a person 20 km under ice). Or no human at all after 03: the camera alone is scarier.

## Reuse from Io (`../Io`)
| Io piece | Europa | work |
|---|---|---|
| `blender/lib/jupiter.py` (true angle/place, 14K map, eclipse ring) | as is | new distance + site only |
| `sky.py` (Sun lamp, stars, exposure) | as is | — |
| `astronaut.py`, `retarget.py`, `rig.py`, EMU suit + Mixamo idle in `../../_assets` | as is | — |
| `lander.py`, `prints.py` | as is (prints in frost) | optional |
| `globe.py` (curved surface) | as is | — |
| `io_world.py` (terrain, palette, lava, plumes) | → `europa_world.py` | **new**: ice plain, double ridges, lineae, chaos blocks; USGS Europa mosaic for colour |
| 05 rise/pull-back camera, 03 time-lapse + counter overlay | 03 / 04 | retune |
| `render.mjs`, `preview.mjs`, `compile.mjs`, `tools/card.mjs`, `overlay.mjs`, `timeline.mjs` | copy | — |
| audio (`music.mjs`, CC0 breath + heartbeat) | copy | new cues: ice creak, sub-bass pressure |
| 巨物's FFT ocean (three.js) | **little use**: under ice there are no waves | — |

New work: Europa ground; the crack interior (ice walls, translucency, blue → black); under-ice water (darkness,
particles, a single lamp); maybe a probe.

## Open questions for the user
1. Which fear: 深渊 (1, recommended with 3), 渺小 (2), or 停滞 (3)?
2. People: astronaut on the surface, then alone below? Or a probe from the start?
3. Length and format: ~60 s 2.39:1 like Io, plus a 9:16 Shorts cut planned from the start?
4. Title: 木卫二 · 深渊 / Europa · Abyss? (series pattern: 巨物, 永恒, …)
