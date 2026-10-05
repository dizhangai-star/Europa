"""03 · the probe starts in vacuum (Sprint 3.3): the loose frost its vapour blows out, and the vapour's grain lobe.
1 BU = 1 m, world frame (Z up). Everything from physics.py (FROST_*, jet_s0, JET_G, vacuum_start); see its 03 rows.

    vent.frost(sc, P, nose, ground, t_fire, fps)   loose flakes lying round the nose; from t_fire (shot seconds) the
                                                   vapour throws them out, each on its own vacuum parabola (Europa's g,
                                                   no drag), landing on the ground and staying there
    vent.lobe(sc, P, nose, t_fire, fps)             the condensed-grain lobe, σs = S0·cos²θ/r² (physics: 4–8 stops under
                                                   the lit plain, i.e. practically invisible: modelled, not boosted)

The flakes move by Geometry Nodes on the scene time (per-point attributes p0 = the vertex, vel, t0, t1), so any frame
renders on its own and motion blur sees sub-frames. `ground(x, y)` → z arrays (europa_world height + curvature).
"""
import math

import bpy
import numpy as np

from . import nodes


def _flake_mesh(name, seed=2):
    """One frost flake: a squashed, lumpy icosphere 1 BU across (the instance scale sets its size)."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.5)
    ob = bpy.context.object
    ob.name = name
    rng = np.random.default_rng(seed)
    for v in ob.data.vertices:
        v.co.x *= 1.0 * (0.8 + 0.4 * rng.random())
        v.co.y *= 0.7 * (0.8 + 0.4 * rng.random())
        v.co.z *= 0.3 * (0.8 + 0.4 * rng.random())
    ob.hide_render = ob.hide_viewport = True
    return ob


def flake_mat():
    """Frost: white, many grains → diffuse with some diffuse transmission (backlit flakes glow, as snow does)."""
    m = bpy.data.materials.get('Frost') or bpy.data.materials.new('Frost')
    g = nodes.Graph(m)
    b = g.add('ShaderNodeBsdfPrincipled')
    g.set(b, 'Base Color', (0.92, 0.94, 0.97))
    g.set(b, 'Roughness', 0.45)
    t = g.add('ShaderNodeBsdfTranslucent')
    g.set(t, 'Color', (0.85, 0.9, 0.95))
    mx = g.add('ShaderNodeMixShader')
    g.set(mx, 'Fac', 0.2)
    g.link(b, 0, mx, 1)
    g.link(t, 0, mx, 2)
    g.output(g.o(mx, 0))
    m.diffuse_color = (0.92, 0.94, 0.97, 1.0)
    return m


def launch(P, nose, ground, t_fire, seed=11):
    """Per flake: start point, velocity, launch and landing time (shot s), size, spin (rad/s per axis)."""
    rng = np.random.default_rng(seed)
    N = P.FROST_N
    r0, r1 = P.FROST_RING
    r = np.sqrt(r0 ** 2 + (r1 ** 2 - r0 ** 2) * rng.random(N))                  # uniform over the ring's area
    a = 2 * math.pi * rng.random(N)
    x, y = nose[0] + r * np.cos(a), nose[1] + r * np.sin(a)
    size = P.FROST_SIZE[0] * (P.FROST_SIZE[1] / P.FROST_SIZE[0]) ** rng.random(N)
    z = ground(x, y) + 0.3 * size
    u = (r - r0) / (r1 - r0)
    el = np.radians(P.FROST_EL[1] + (P.FROST_EL[0] - P.FROST_EL[1]) * u + rng.normal(0, 6, N))   # steep near the nose
    el = np.clip(el, math.radians(P.FROST_EL[0]), math.radians(P.FROST_EL[1]))
    v = P.FROST_V[0] + (P.FROST_V[1] - P.FROST_V[0]) * rng.random(N) ** P.FROST_V_POW
    v *= 1.0 - 0.4 * u                                                            # the gas is strongest at the nose
    a += rng.normal(0, 0.15, N)
    vel = np.stack([v * np.cos(el) * np.cos(a), v * np.cos(el) * np.sin(a), v * np.sin(el)], -1)
    t0 = t_fire + np.minimum(rng.exponential(P.FROST_TAU, N), 5 * P.FROST_TAU)
    g = P.g_at()
    t = 2 * vel[:, 2] / g                                                         # flight, refined on the ground
    for _ in range(4):
        zg = ground(x + vel[:, 0] * t, y + vel[:, 1] * t)
        dz = z - zg
        t = (vel[:, 2] + np.sqrt(np.maximum(vel[:, 2] ** 2 + 2 * g * dz, 0.0))) / g
    spin = rng.normal(0, 6.0, (N, 3)) * (v[:, None] / P.FROST_V[1] + 0.2)          # rad/s, tumbling (film pick)
    return np.stack([x, y, z], -1), vel, t0, t0 + t, size, spin


def _attr(me, name, kind, data):
    at = me.attributes.new(name, kind, 'POINT')
    at.data.foreach_set('vector' if kind == 'FLOAT_VECTOR' else 'value', data.astype(np.float32).ravel())


def _flight_nodes(P, proto, fps):
    gn = bpy.data.node_groups.new('FrostFlight', 'GeometryNodeTree')
    gn.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    gn.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = gn.nodes, gn.links.new
    gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput')

    def attr(name, kind='FLOAT'):
        n = N.new('GeometryNodeInputNamedAttribute')
        n.data_type = kind
        n.inputs['Name'].default_value = name
        return n.outputs['Attribute']

    def math_(op, a, b):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, s in enumerate((a, b)):
            if isinstance(s, (int, float)):
                n.inputs[i].default_value = s
            else:
                L(s, n.inputs[i])
        return n.outputs[0]

    def vmath(op, a, b=None, scale=None):
        n = N.new('ShaderNodeVectorMath')
        n.operation = op
        L(a, n.inputs[0])
        if b is not None:
            L(b, n.inputs[1])
        if scale is not None:
            L(scale, n.inputs['Scale'])
        return n.outputs[0]

    m2p = N.new('GeometryNodeMeshToPoints')
    L(gi.outputs[0], m2p.inputs['Mesh'])
    st = N.new('GeometryNodeInputSceneTime')
    t = math_('SUBTRACT', st.outputs['Seconds'], 1.0 / fps)                # shot seconds (frame 1 = 0 s)
    tc = math_('MINIMUM', math_('MAXIMUM', t, attr('t0')), attr('t1'))
    dt = math_('SUBTRACT', tc, attr('t0'))
    fall = N.new('ShaderNodeCombineXYZ')
    L(math_('MULTIPLY', math_('MULTIPLY', dt, dt), -0.5 * P.g_at()), fall.inputs['Z'])
    off = vmath('ADD', vmath('SCALE', attr('vel', 'FLOAT_VECTOR'), scale=dt), fall.outputs[0])
    sp = N.new('GeometryNodeSetPosition')
    L(m2p.outputs['Points'], sp.inputs['Geometry'])
    L(off, sp.inputs['Offset'])
    oi = N.new('GeometryNodeObjectInfo')
    oi.inputs['Object'].default_value = proto
    iop = N.new('GeometryNodeInstanceOnPoints')
    L(sp.outputs['Geometry'], iop.inputs['Points'])
    L(oi.outputs['Geometry'], iop.inputs['Instance'])
    r0 = N.new('FunctionNodeRandomValue')
    r0.data_type = 'FLOAT_VECTOR'
    r0.inputs['Max'].default_value = (6.2832, 6.2832, 6.2832)
    L(r0.outputs['Value'], iop.inputs['Rotation'])
    L(attr('size'), iop.inputs['Scale'])
    rot = N.new('GeometryNodeRotateInstances')
    L(iop.outputs['Instances'], rot.inputs['Instances'])
    L(vmath('SCALE', attr('spin', 'FLOAT_VECTOR'), scale=dt), rot.inputs['Rotation'])
    rot.inputs['Local Space'].default_value = True
    L(rot.outputs['Instances'], go.inputs[0])
    return gn


def frost(sc, P, nose, ground, t_fire, fps=24, seed=11):
    """The loose frost round the nose, thrown out from t_fire. Returns (object, launch arrays)."""
    p0, vel, t0, t1, size, spin = launch(P, nose, ground, t_fire, seed)
    proto = _flake_mesh('FrostFlake')
    proto.data.materials.append(flake_mat())
    me = bpy.data.meshes.new('Frost')
    me.vertices.add(len(p0))
    me.vertices.foreach_set('co', p0.astype(np.float32).ravel())
    _attr(me, 'vel', 'FLOAT_VECTOR', vel)
    _attr(me, 'spin', 'FLOAT_VECTOR', spin)
    for k, d in (('t0', t0), ('t1', t1), ('size', size)):
        _attr(me, k, 'FLOAT', d)
    ob = bpy.data.objects.new('Frost', me)
    sc.collection.objects.link(ob)
    ob.modifiers.new('Flight', 'NODES').node_group = _flight_nodes(P, proto, fps)
    return ob, (p0, vel, t0, t1, size)


def lobe(sc, P, nose, t_fire, fps=24, radius=2.0, ramp=0.5):
    """The vapour's condensed grains: a half-ball volume on the nose, σs = S0·z²/r⁴ (object space), HG g = JET_G,
    switched on over `ramp` s from t_fire."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius)
    ob = bpy.context.object
    ob.name = 'VapourLobe'
    bm_ = ob.data
    for v in bm_.vertices:
        v.co.z = abs(v.co.z)
    ob.location = nose
    m = bpy.data.materials.new('VapourLobe')
    g = nodes.Graph(m)
    tc = g.add('ShaderNodeTexCoord')
    x, y, z = g.xyz(g.o(tc, 'Object'))
    r2 = g.math('MAXIMUM', g.math('ADD', g.math('ADD', g.math('MULTIPLY', x, x), g.math('MULTIPLY', y, y)),
                                  g.math('MULTIPLY', z, z)), 0.03 ** 2)
    on = g.add('ShaderNodeValue', label='on')
    dens = g.math('MULTIPLY', g.math('DIVIDE', g.math('MULTIPLY', z, z), g.math('MULTIPLY', r2, r2)),
                  g.math('MULTIPLY', g.o(on, 0), P.jet_s0(P.CRYO_P[2])))
    vs = g.add('ShaderNodeVolumeScatter')
    g.set(vs, 'Color', (1.0, 1.0, 1.0))
    g.set(vs, 'Density', dens)
    g.set(vs, 'Anisotropy', P.JET_G)
    g.nt.links.new(g.o(vs, 0), g.out.inputs['Volume'])
    ob.data.materials.append(m)
    sw = on.outputs[0]
    for f, val in ((1, 0.0), (int(round(t_fire * fps)) + 1, 0.0), (int(round((t_fire + ramp) * fps)) + 1, 1.0)):
        sw.default_value = val
        sw.keyframe_insert('default_value', frame=f)
    return ob
