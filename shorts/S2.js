// S2 · "Io and Europa's shadow" (Sprint 6.1): 02-neighbour from the start of its zoom (Io already above the disc) to
// just after Io sets behind the ice, before the tail swings onto 03's dawn. 01's tail is left out: it's the same still
// disc 02 opens on. The square follows the zoom (disc centre 765 at 35 mm → 960 at 75 mm, measured on the frames). Ends
// with Io gone and both shadows still on the bands → loops back to Io entering. 02's clock = clip seconds; the Short's
// = clip − 0.5. Eclipse on Io (physics.sound()['02']['eclipse']): 2.97 · 4.95 deepest · 6.91 clip s.
export default {
  id: 'S2',
  title: "Io and Europa's shadow",
  segments: [{ clip: '02-neighbour', in: 0.5, out: 11.0, x: [[0, 765], [2.0, 960]] }],
  hook: ['IO FROM EUROPA', 'REAL PHYSICS · NOT AI'],
  caps: [
    [0.3, 2.3, "IO CROSSES JUPITER\n{lapse(site(*SITE[1:]), LAPSE_E_END[1], 0.0)['dur'] * 60:.0f} MINUTES IN {lapse02_start.__defaults__[1] - lapse02_start.__defaults__[0]:.1f} SECONDS"],
    [2.6, 5.4, "IO GOES BLACK:\nIT IS IN EUROPA'S SHADOW"],
    [5.7, 8.0, "TWO DOTS ON JUPITER:\nIO'S SHADOW AND OURS"],
    [8.3, 10.4, 'IO. WE STOOD THERE.'],
  ],
};
