# References and downloaded assets

Every downloaded file: URL, author, licence, local path (shared library `../../_assets/`, index in its `index.json`),
which shot uses it.

## Reused from Io (already in `../../_assets/`)
| asset | licence | path | used in |
|---|---|---|---|
| Jupiter 14K map (Björn Jónsson, Cassini + Juno) | credit; private non-commercial | `textures/jupiter/jupiter_map_css_plus_juno_bj.png` | 01–04 |
| Astronaut, NASA EMU, rigged (Blend Swap #12622, jgilhutton) | CC-BY 4.0: credit in the end card | `models/astronaut-emu-12622/emu_clean.blend` | 03 |
| Mixamo "Breathing Idle" | Mixamo terms | `mocap/Breathing Idle.fbx` | 03 |
| Breaths (Freesound 387620, 682884), heartbeat (332819) | CC0 | `audio/breath/` | 01–04 |
| Ice cracks: Andrew5DMII, "Frozen Lake Ice and Water Sounds Shotgun Ice Cracking" (Freesound 146419) | CC-BY 3.0: credit in the end card / srt | `audio/ice/` | 05–08 |

## Downloaded for Europa (0.4, 2026-10-04)
All public domain (NASA / USGS). Index ids `europa-usgs-mosaic-500m`, `europa-galileo-closeups`; previews in
`../../_assets/previews/europa-*.jpg`. Derived maps (git-ignored, rebuilt by `python3 tools/maps.py europa`) in
`blender/textures/src/`.
| asset | what it is | path | used for |
|---|---|---|---|
| USGS Europa Voyager–Galileo SSI global mosaic 500 m ([page](https://astrogeology.usgs.gov/search/map/Europa/Voyager-Galileo/Europa_Voyager_GalileoSSI_global_mosaic_500m)) | greyscale, 19631×9816, 0–360° E, R 1562.09 km | `textures/europa/Europa_Voyager_GalileoSSI_global_mosaic_500m.tif` | site albedo map (512 km) + wide check (2048 km, Pwyll) |
| PIA01403 "A Closer Look at Chaos" | Conamara mosaic 35×50 km, ~15 m/px, 20 m insets, north up, Sun from the east | `textures/europa/galileo/PIA01403.*` | block/raft shapes; candidate detail tile (Sprint 2) |
| PIA01182 "Icy Cliffs" | Conamara 1.7×4 km, 9 m/px, north top-right: 100 m+ cliffs, house-size debris | `…/galileo/PIA01182.*` | the foreground scale (01, 03) |
| PIA00591 "Ice Rafts" | Conamara 34×42 km, 54 m/px | `…/galileo/PIA00591.*` | raft layout, 02 / 04 middle distance |
| PIA01127, PIA01296, PIA26446 | Conamara in **enhanced** colour (70×30, 250×200 km; close-up) | `…/galileo/` | *where* the colour sits only (brown on the chaos matrix and ridges, white = Pwyll ray frost, blue-white = old plains) |
| PIA19048 "Europa's Stunning Surface" | global view in approximately natural colour (2014 reprocessing), north at right | `…/galileo/PIA19048.*` | the palette (`maps.py colour`) |
| PIA01178 | ridged plains elsewhere (14° S 194° W, 26 m/px) | `…/galileo/PIA01178.*` | double-ridge shapes |

## Cryobot design sources (Sprint 2.2, 2026-10-05; look and layout only, all numbers in `physics.py` CRYO_*)
| source | what we took |
|---|---|
| JPL PRIME, Hand et al. 2022 (ui.adsabs.harvard.edu/abs/2022absc.conf50204H) | Ø 0.25 m, radioisotope heat, relays left in the ice; SWIM package 10 cm × Ø 25 cm, up to 50 wedge swimmers (⚠ concept) |
| NASA Compass "Europa Tunnelbot" 2019 (ntrs.nasa.gov/search.jsp?R=20190026714) | sections: heat source, electronics vault, tether paid out from the probe, repeater pucks every few km |
| Stone Aerospace VALKYRIE / PROMETHEUS (astrobiology.nasa.gov/news/warm-nosed-robot-breaks-the-ice) | hot-water jets from the melt head |
| centauri-dreams.org/2022/07/01/drilling-into-icy-moon-oceans · universetoday.com (signal through the ice) | puck relays, fibre tether in three layers |

## Wanted (2026-10-04)
Who fetches: **user** = needs a login (Mixamo, Freesound downloads) or a choice of look; **Claude** = public, no login.
| # | what | for | where to look | who | priority |
|---|---|---|---|---|---|
| W1 | Mixamo clip(s): astronaut crouching/kneeling at the probe, then standing to watch it sink (in place, FBX, without skin, 30 fps; start/end poses that join Breathing Idle) | 03 | mixamo.com ("kneel", "crouch", "stand up") | ✅ closed: 03 locked on Breathing Idle (Sprint 3.3) | — |
| W2 | Ice sounds: lake/sea ice cracking and "singing" (deep booms, pew-pew), recorded | 05–06 | Freesound, CC0 first | ✅ closed: recorded cracks, Freesound 146419 (user-downloaded 2026-10-07; the synth "pew" read as 80s/90s electronics) | — |
| W3 | Under-ice hydrophone ambience | 07–08 | Freesound, CC0 first | ✅ closed: synthesized (`audio/music.mjs` water/hum/bubbles, user 2026-10-07) | — |
| W4 | Cryobot model | 03, 05–08 | searched 2026-10-05: asset index, Blend Swap ("cryobot", "melt probe", "ice probe", "europa lander"), NASA 3D Resources, Sketchfab: **none exists** | ✅ closed: code-built (`blender/lib/cryobot.py`, Sprint 2.2) | — |
| W5 | USGS Europa global mosaic (Galileo SSI + Voyager) + Galileo Conamara close-ups (PIA photojournal) | 01–04 ground colour and block shapes | astrogeology.usgs.gov, photojournal.jpl.nasa.gov | ✅ done 0.4 (above) | high |
| W6 | Close-up frost/ice PBR textures | 01, 03 foreground | Poly Haven, ambientCG (CC0) | Claude | medium |
| W7 | Look references only (not in the picture): Icefin under-ice footage, Juno/Galileo night-side lightning images, Jupiter eclipse images, cryobot concept art | 04, 05–08 | NASA/JPL, Georgia Tech/Cornell Icefin | Claude | medium |
