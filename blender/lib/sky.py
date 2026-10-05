"""Europa's sky: the Sun lamp (true size, true irradiance, place from its elongation), a black world with stars, exposure.
Copied from ../Io/blender/lib/sky.py (Sprint 0.3); the Sun may carry a declination (physics.DEC_SUN: ±3.1°).

No air: the world is black apart from stars; no sky light, no haze, shadows razor-sharp (the Sun is 0.10° wide).
Ground light besides the Sun comes from the scene itself (Jupiter's lit disc, a lamp): Cycles traces it, no fill lamps.
Units: the Sun lamp's strength is its irradiance, E_SUN = 50.3 W/m², so a surface of albedo a facing it has
radiance a·E/π ≈ 10 for frost (Europa's ice, albedo ≈ 0.6–0.7, a little more). Shots set the film exposure (EV) to suit: ≈ −4.5 for sunlit ground and Jupiter,
≈ +2 for the eclipse (Jupiter-shine alone is 6 stops below sunlight).
"""
import math

import bpy
from mathutils import Vector
import physics as P
from . import nodes


def sun(sc, elong, strength=None, dec=0.0):
    """Sun lamp at signed elongation `elong` and declination `dec` (deg, physics.sun_local). Returns the object."""
    L = bpy.data.lights.new('Sun', 'SUN')
    L.energy = P.E_SUN if strength is None else strength
    L.angle = math.radians(2 * P.R_SUN_DEG)
    L.color = (1.0, 1.0, 1.0)                     # white: the grade's warmth comes later, not from the lamp
    ob = bpy.data.objects.new('Sun', L)
    sc.collection.objects.link(ob)
    ob.rotation_euler = (-Vector(P.sun_local(elong, dec))).to_track_quat('-Z', 'Y').to_euler()
    return ob


def stars(sc, px_rad, gain=1.0, density=0.35, cell=0.012, seed=0.0, axis=None, taps=1, camera_only=False, orient=None):
    """Black world + procedural stars: one per Voronoi cell (cell ≈ `cell` rad) kept with probability `density`,
    a round spot `px_rad` radians in radius (≈ 1 px at the shot's lens and resolution), brightness heavy-tailed
    (rand⁸: a few bright, many faint), colour 3500–11000 K. `gain` = the brightest star's radiance.
    `axis` (local unit vector: Europa's pole, physics.jupiter_local()[4]) makes the sky turnable: returns (world, turn,
    smear), two Value nodes a shot keys: turn = the stars' rotation about the pole so far (rad, + = the way they move,
    east → west), smear = their rotation during the shutter (rad), spread over `taps` lookups (star trails; the
    trail's light is shared out, as on film). Without `axis`: returns the world (the static sky of 01/02/04).
    `camera_only`: the stars light nothing (as world light their mean radiance, ∝ the spot area, lit 05's eclipsed
    Jupiter at preview resolutions). `orient` (axis, angle rad): turn the star lattice; a 3D Voronoi sliced by the sky
    sphere shows concentric rings where a lattice axis points (az 0°, el 0° by default: 05 frames it)."""
    w = bpy.data.worlds.new(sc.name + '_Sky')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    g = nodes.Graph.__new__(nodes.Graph)
    g.nt = nt
    out = g.add('ShaderNodeOutputWorld')
    tc = g.add('ShaderNodeTexCoord')
    turn = smear = None
    if axis is None:
        dirs = [g.o(tc, 'Generated')]
    else:
        turn, smear = g.add('ShaderNodeValue'), g.add('ShaderNodeValue')
        turn.name, smear.name = 'StarTurn', 'StarSmear'
        turn.outputs[0].default_value = smear.outputs[0].default_value = 0.0
        dirs = []
        for k in range(taps):
            f = k / (taps - 1) - 0.5 if taps > 1 else 0.0
            ang = g.math('ADD', g.o(turn, 0), g.math('MULTIPLY', g.o(smear, 0), f))
            rot = g.add('ShaderNodeVectorRotate', rotation_type='AXIS_ANGLE')
            g.set(rot, 'Vector', g.o(tc, 'Generated'))
            g.set(rot, 'Axis', tuple(axis))
            g.set(rot, 'Angle', ang)        # view direction → the inertial sky: undo the turn (stars drift + about the pole)
            dirs.append(g.o(rot, 0))
    if orient is not None:
        rd = []
        for vec in dirs:
            ro = g.add('ShaderNodeVectorRotate', rotation_type='AXIS_ANGLE')
            g.set(ro, 'Vector', vec)
            g.set(ro, 'Axis', tuple(orient[0]))
            g.set(ro, 'Angle', orient[1])
            rd.append(g.o(ro, 0))
        dirs = rd
    total = None
    for vec in dirs:
        nrm = g.add('ShaderNodeVectorMath', operation='NORMALIZE')
        g.set(nrm, 0, vec)
        sc_ = g.add('ShaderNodeVectorMath', operation='SCALE', Scale=1.0 / cell)
        g.set(sc_, 0, g.o(nrm, 0))
        v = g.add('ShaderNodeTexVoronoi', feature='F1', Randomness=1.0, W=seed)
        v.voronoi_dimensions = '3D'
        g.set(v, 'Vector', g.o(sc_, 0))
        dist = g.math('MULTIPLY', g.o(v, 'Distance'), cell)                 # radians from the cell's star
        spot = g.math('POWER', g.maprange(dist, px_rad * 1.6, 0.0), 2.0)
        r, gg, b = g.xyz(g.o(v, 'Color'))
        keep = g.math('GREATER_THAN', r, 1.0 - density)
        bright = g.math('POWER', gg, 8.0)
        k = g.math('MULTIPLY', g.math('MULTIPLY', spot, keep), g.math('MULTIPLY', bright, gain))
        if total is None:
            total, temp = k, b                                              # colour: the first lookup's star
        else:
            total = g.math('ADD', total, k)
    if len(dirs) > 1:
        total = g.math('DIVIDE', total, float(len(dirs)))
    bb = g.add('ShaderNodeBlackbody')
    g.set(bb, 'Temperature', g.maprange(temp, 0.0, 1.0, 3500.0, 11000.0))
    bg = g.add('ShaderNodeBackground')
    g.set(bg, 'Color', g.o(bb, 0))
    if camera_only:
        lp = g.add('ShaderNodeLightPath')
        total = g.math('MULTIPLY', total, g.o(lp, 'Is Camera Ray'))
    g.set(bg, 'Strength', total)
    g.link(bg, 0, out, 'Surface')
    return w if axis is None else (w, turn, smear)


def sun_disc(sc, elong, dist=1.5e6):
    """The Sun's disc for the camera only (a Sun lamp is invisible to camera rays): an emitter of true angular size
    and true radiance (E / solid angle) beyond Jupiter, so Jupiter hides it. Returns the object; shots move it with
    `place_sun`."""
    import bmesh
    r = dist * math.tan(math.radians(P.R_SUN_DEG))
    me = bpy.data.meshes.new('SunDisc')
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('SunDisc', me)
    sc.collection.objects.link(ob)
    for k in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(ob, k, False)
    m = bpy.data.materials.new('SunDisc')
    g = nodes.Graph(m)
    em = g.add('ShaderNodeEmission')
    g.set(em, 'Color', (1.0, 1.0, 1.0))
    g.set(em, 'Strength', P.E_SUN / (math.pi * math.sin(math.radians(P.R_SUN_DEG)) ** 2))
    g.output(g.o(em, 0))
    me.materials.append(m)
    ob['dist'] = dist
    place_sun(None, ob, elong)
    return ob


def corona(sc, elong, dist=1.6e6, r_max=20.0):
    """The solar corona for the camera only (04: it shows once Jupiter hides the Sun's disc, as at a total eclipse
    on Earth; its surface brightness doesn't depend on distance, so from Europa it is as bright as from Earth but
    5.2× smaller). Baumbach (1937) K+F profile, physics.CORONA / corona(r), r in solar radii (1 … `r_max`), relative
    to the disc centre's radiance (the mean disc radiance / physics.LIMB_DARK). A flat camera-facing disc beyond Jupiter (Jupiter hides it) and the Sun's disc
    (`sun_disc`, 1.5e6 m); white (scattered sunlight). Returns the object; shots move it with `place_sun`-style keys
    (`ob['dist']`) and keep it facing the camera with its Track To constraint (`track`)."""
    import bmesh
    rs = dist * math.tan(math.radians(P.R_SUN_DEG))
    me = bpy.data.meshes.new('Corona')
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=rs * r_max)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('Corona', me)
    sc.collection.objects.link(ob)
    for k in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(ob, k, False)
    m = bpy.data.materials.new('Corona')
    m.surface_render_method = 'BLENDED'
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    ln = g.add('ShaderNodeVectorMath', operation='LENGTH')
    g.set(ln, 0, g.o(tc, 'Object'))
    r = g.math('MAXIMUM', g.math('DIVIDE', g.o(ln, 'Value'), rs), 1.0)
    prof = None
    for a, n in P.CORONA:
        t = g.math('MULTIPLY', g.math('POWER', r, -n), a)
        prof = t if prof is None else g.math('ADD', prof, t)
    b0 = P.E_SUN / (math.pi * math.sin(math.radians(P.R_SUN_DEG)) ** 2) / P.LIMB_DARK
    em = g.add('ShaderNodeEmission')
    g.set(em, 'Color', (1.0, 1.0, 1.0))
    g.set(em, 'Strength', g.math('MULTIPLY', prof, 1e-6 * b0))
    tr = g.add('ShaderNodeBsdfTransparent')
    add = g.add('ShaderNodeAddShader')
    g.link(tr, 0, add, 0)
    g.link(em, 0, add, 1)
    g.output(g.o(add, 0))
    me.materials.append(m)
    ob['dist'] = dist
    place_sun(None, ob, elong)
    return ob


def track(ob, cam):
    """Keep a flat camera-only disc (the corona) facing the camera."""
    c = ob.constraints.new('TRACK_TO')
    c.target, c.track_axis, c.up_axis = cam, 'TRACK_Z', 'UP_Y'
    return c


def place_sun(lamp, disc, elong, origin=(0.0, 0.0, 0.0)):
    """Point the Sun lamp and move its disc to elongation `elong` (either may be None)."""
    u = Vector(P.sun_local(elong))
    if lamp is not None:
        lamp.rotation_euler = (-u).to_track_quat('-Z', 'Y').to_euler()
    if disc is not None:
        disc.location = Vector(origin) + u * disc['dist']


def glare(sc, threshold=500.0, maximum=3000.0, size=7, strength=1.0, kind='Fog Glow'):
    """Lens glow around the Sun's disc (compositor; only light above `threshold`, i.e. the Sun's ~2e7, glows;
    `maximum` clamps it so the glow stays a camera's, not a white-out)."""
    g = bpy.data.node_groups.new(sc.name + '_Comp', 'CompositorNodeTree')
    g.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = g.nodes.new('CompositorNodeRLayers')
    rl.scene = sc
    gl = g.nodes.new('CompositorNodeGlare')
    for k, v in (('Type', kind), ('Threshold', threshold), ('Clamp', True), ('Maximum', maximum), ('Size', size),
                 ('Strength', strength), ('Quality', 'High')):
        gl.inputs[k].default_value = v
    out = g.nodes.new('NodeGroupOutput')
    g.links.new(rl.outputs['Image'], gl.inputs['Image'])
    g.links.new(gl.outputs['Image'], out.inputs[0])
    sc.compositing_node_group = g
    sc.render.use_compositing = True
    return gl


def exposure(sc, ev):
    sc.view_settings.exposure = ev


def px_angle(lens, pct=100, width=1920):
    """Angle (rad) of one pixel at the centre of the frame for a 36 mm-wide sensor."""
    return 36.0 / lens / (width * pct / 100.0)
