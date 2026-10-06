window.CLIP = {
  id: '05-lid',
  duration: 3 + 10,             // + the descending head (physics.TILT45.head, Sprint 4.0d): the old 0 s is at 3 s; trim candidate: into 06
  shot: 's05_lid.py',           // Sprint 3.5: cutaway, 35 mm, camera stays in the ice with puck 1 (30 m); the probe sinks, the front comes down onto the puck at 5 s (×2,900)
  caps: [[3 + 5.0, 3 + 9.4, 'THERE IS NO WAY BACK', '没有回头路']],
  counter: 'counter05',         // physics.counter05: hours since the drop · depth of the probe's nose
  counter_in: 3,                // the clock fades in as the descent lands (physics.TILT45.head), not over the black dissolve
  sfx: [],
};
