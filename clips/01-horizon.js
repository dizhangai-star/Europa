window.CLIP = {
  id: '01-horizon',
  duration: 12,                 // TREATMENT §5 (locked 2026-10-04); the whole-film animatic may still trim
  shot: 's01_horizon.py',       // the turn (user 2026-10-05): lit mesa → disc, 24 → 35 mm, +1.5 → −3.5 EV (Sprint 3.1)
  caps: [[8.2, 11.6, 'EUROPA', '木卫二']],  // Sprint 3.1: the pan settles on the disc by 8.1 s
  sfx: [[-0.9, 'in', { take: 'headIn' }], [1.0, 'out', { take: 'headOut' }],   // Sprint 4.1: calm before the turn
         [6.4, 'in', { take: 'catch' }], [8.7, 'out', { take: 'shaky' }]],     // the disc swings in: a catch, held, a shaky release
};
