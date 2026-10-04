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

## Wanted (2026-10-04)
Who fetches: **user** = needs a login (Mixamo, Freesound downloads) or a choice of look; **Claude** = public, no login.
| # | what | for | where to look | who | priority |
|---|---|---|---|---|---|
| W1 | Mixamo clip(s): astronaut crouching/kneeling at the probe, then standing to watch it sink (in place, FBX, without skin, 30 fps; start/end poses that join Breathing Idle) | 03 | mixamo.com ("kneel", "crouch", "stand up") | user | high |
| W2 | Ice sounds: lake/sea ice cracking and "singing" (deep booms, pew-pew), recorded | 05–06 | Freesound, CC0 first | user | high |
| W3 | Under-ice hydrophone ambience | 07–08 | Freesound, CC0 first | user | medium |
| W4 | Cryobot model (optional: the plan is code-built, plain, no logos) | 03, 05–08 | NASA 3D Resources (public domain), Sketchfab CC-BY ("cryobot", "ice melt probe", "Europa lander") | user, optional | low |
| W5 | USGS Europa global mosaic (Galileo SSI + Voyager) + Galileo Conamara close-ups (PIA photojournal) | 01–04 ground colour and block shapes | astrogeology.usgs.gov, photojournal.jpl.nasa.gov | Claude (0.4) | high |
| W6 | Close-up frost/ice PBR textures | 01, 03 foreground | Poly Haven, ambientCG (CC0) | Claude | medium |
| W7 | Look references only (not in the picture): Icefin under-ice footage, Juno/Galileo night-side lightning images, Jupiter eclipse images, cryobot concept art | 04, 05–08 | NASA/JPL, Georgia Tech/Cornell Icefin | Claude | medium |
