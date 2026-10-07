window.CLIP = {
  id: '05-lid',
  duration: 3 + 10,             // + the descending head (physics.TILT45.head, Sprint 4.0d): the old 0 s is at 3 s; trim candidate: into 06
  shot: 's05_lid.py',           // Sprint 3.5: cutaway, 35 mm, camera stays in the ice with puck 1 (30 m); the probe sinks, the front comes down onto the puck at 5 s (×2,900)
  spf: 80,                    // Sprint 5.0: s/frame at 64 spp, full res, measured (tools/ab.mjs: 99 · 77 · 76 · 70); batch.mjs: cheapest first
  caps: [[3 + 5.0, 3 + 9.4, 'THERE IS NO WAY BACK', '没有回头路']],
  counter: 'counter05',         // physics.counter05: hours since the drop · depth of the probe's nose
  counter_in: 3,                // the clock fades in as the descent lands (physics.TILT45.head), not over the black dissolve
  counter_out: 12.5,            // gone 6 frames into the 18-frame dissolve to 06 (Sprint 4.0e): 06's readout fades in after it, never on top
  sfx: [[4.2, 'crack', { size: 0.35, pan: 0.3 }], [6.6, 'cluster', { d: 1.6, k: 4 }], [10.4, 'crack', { size: 0.6, pan: -0.4 }], [11.8, 'crack', { size: 0.25, pan: 0.5 }]],   // Sprint 4.1: the brittle lid flexing with the tide
};
