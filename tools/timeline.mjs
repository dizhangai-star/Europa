// The film's layout, shared by compile.mjs (picture) and audio/music.mjs (score + foley), so both put every clip at
// the same film second. The kit's film() can't: it lays clips end to end, without the head or dissolves.
// Copied from Io (Sprint 0.3). Europa's joints (Sprint 4.0, user 2026-10-06: three blocks, surface 01–04 · ice 05–06 ·
// ocean 07–08, smooth joints inside them): edit-level joints here; the shot-level ones (01→02 zoom, 03→04 whip,
// 04→05 tilt into the ice) live in the shot scripts and meet here as dissolves or cuts.
import { config, clipIds, loadClip } from '../../../_kit/lib/film.mjs';

export const HEAD = { black: 1.0, fade: 0.5 };               // s: black (sound first), then 01 fades up
export const JOINTS = {                                      // the joint after each clip; d in frames (24 fps)
  '02-neighbour': { kind: 'dissolve', d: 24 },              // 02's tail lands on 03's frame and dawn: only the probe and astronaut fade in (ends on 03's frost burst, 1.0 s)
  '05-lid': { kind: 'dissolve', d: 18 },                    // the same cutaway, 34 m in both; counters cross in place
  '06-descent': { kind: 'dissolve', d: 24 },                // the same lamp: in the ice (06) → its glow from below (07)
};
export const TRIM_IN = {                                     // frames cut from a clip's head (its clock is unchanged)
  '08-abyss': 19,                                           // 07 → 08 cut on the action: 0.2 s before the brake lets go (1.0 s)
};
export const FADE_OUT = {};                                  // s at the clip's end, to black, e.g. { '08-abyss': 1.0 }

// → { clips: [{ id, start, in, trim, duration, joint_out, A }], total }: `start` = the film second of the clip's own
// t = 0 (captions, counters, sound cues add their clip times to it); `in` = where its first shown frame sits
// (start + trim). The dissolve overlaps real frames, so total = Σ clips − trims − dissolves + head.
export function layout() {
  const ids = clipIds(), fps = config.fps;
  let at = HEAD.black;
  const clips = ids.map((id, k) => {
    const A = loadClip(id), j = JOINTS[id], trim = (TRIM_IN[id] ?? 0) / fps;
    const c = { id, start: +(at - trim).toFixed(4), in: +at.toFixed(4), trim, duration: A.duration, joint_out: j?.kind ?? (k < ids.length - 1 ? 'cut' : 'end'), A };
    at += A.duration - trim - (j?.kind === 'dissolve' ? j.d / fps : 0);
    return c;
  });
  return { clips, total: +at.toFixed(4), at: (id) => clips.find((c) => c.id === id).start };
}
