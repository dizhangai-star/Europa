// The film's layout, shared by compile.mjs (picture) and audio/music.mjs (score + foley), so both put every clip at
// the same film second. The kit's film() can't: it lays clips end to end, without the head or dissolves.
// Copied from Io (Sprint 0.3): head kept; Europa's joints and fades are chosen in the whole-film animatic (Sprint 4),
// hard cuts until then. Io's were one dissolve (04 → 05, ring match) and a fade to black before the title card.
import { config, clipIds, loadClip } from '../../../_kit/lib/film.mjs';

export const HEAD = { black: 1.0, fade: 0.5 };               // s: black (sound first), then 01 fades up
export const JOINTS = {                                      // the joint after each clip; d in frames (24 fps)
  // e.g. '04-sunfall': { kind: 'dissolve', d: 36 },
};
export const FADE_OUT = {};                                  // s at the clip's end, to black, e.g. { '08-abyss': 1.0 }

// → { clips: [{ id, start, duration, joint_out, A }], total }: the dissolve overlaps real frames, so
// total = Σ clips − dissolves + head.
export function layout() {
  const ids = clipIds(), fps = config.fps;
  let at = HEAD.black;
  const clips = ids.map((id, k) => {
    const A = loadClip(id), j = JOINTS[id];
    const c = { id, start: +at.toFixed(4), duration: A.duration, joint_out: j?.kind ?? (k < ids.length - 1 ? 'cut' : 'end'), A };
    at += A.duration - (j?.kind === 'dissolve' ? j.d / fps : 0);
    return c;
  });
  return { clips, total: +at.toFixed(4), at: (id) => clips.find((c) => c.id === id).start };
}
