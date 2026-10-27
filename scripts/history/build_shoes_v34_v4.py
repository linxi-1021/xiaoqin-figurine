import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_背包鞋镜框重建_v34_20261025\小秦_v6背包鞋镜框重建.blend'
OUT_DIR = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34\shoes'
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world

mat_upper = bpy.data.materials['Cream leather shoes soft satin finish']
upper_idx = [i for i, m in enumerate(me.materials) if m and m.name == mat_upper.name][0]

# ---------- 1. 采样奶白 UV ----------
uv_layer = me.uv_layers['UVMap']
img = None
for n in mat_upper.node_tree.nodes:
    if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'Front clip carrier cleaned atlas':
        img = n.image
w_img, h_img = img.size
px = np.empty(w_img * h_img * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h_img, w_img, 4)

cands = []
for p in me.polygons:
    if p.material_index != upper_idx:
        continue
    c = mw @ p.center
    if not (0.0088 <= c.z <= 0.020 and abs(c.x) < 0.014 and -0.012 < c.y < 0.014):
        continue
    u = sum(uv_layer.data[li].uv[0] for li in p.loop_indices) / p.loop_total
    v = sum(uv_layer.data[li].uv[1] for li in p.loop_indices) / p.loop_total
    r, g, b = (float(px[int(v * h_img) % h_img, int(u * w_img) % w_img, k]) for k in range(3))
    cands.append((min(r, g, b), abs(max(r, g, b) - min(r, g, b)), u, v))
cands.sort(key=lambda t: (-t[0], t[1]))
CREAM_UV = (cands[0][2], cands[0][3])
print('CREAM_UV', [round(x, 4) for x in CREAM_UV])

# ---------- 2. 只删“薄底”面，保留原鞋面 ----------
bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
deleting = []
for f in bm.faces:
    c = mw @ f.calc_center_median()
    if c.z < 0.0116 and abs(c.x) < 0.0175 and -0.016 < c.y < 0.017:
        deleting.append(f)
print('DELETE_THIN_SOLE_FACES', len(deleting))
bmesh.ops.delete(bm, geom=deleting, context='FACES')
bm.to_mesh(me)
bm.free()
me.update()

# ---------- 3. 量原鞋外形（按 y 分箱） ----------
Z_BOT = 0.0088
SOLE_H = 0.0036
Z_SOLE_TOP = Z_BOT + SOLE_H
SIDES = {
    'L': {'cx': -0.00615, 'a': 0.00645, 'b': 0.01040, 'toe': -0.01010, 'heel': 0.00900},
    'R': {'cx': 0.00675, 'a': 0.00665, 'b': 0.01010, 'toe': -0.01010, 'heel': 0.00880},
}


def sup(v, p):
    return math.copysign(abs(v) ** (2.0 / p), v)


def set_uv(ob, uv):
    layer = ob.data.uv_layers.new(name='UVMap')
    for d in layer.data:
        d.uv = uv


def make_obj(name, verts, faces, mat, smooth=True):
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], faces)
    m.validate()
    m.update()
    ob = bpy.data.objects.new(name, m)
    scene.collection.objects.link(ob)
    m.materials.append(mat)
    set_uv(ob, CREAM_UV)
    if smooth:
        for p in m.polygons:
            p.use_smooth = True
    return ob


def bumper(name, cx, cy, a, b, mat, n=72, p=3.4):
    """分层鞋底：底部外扩、腰线凹槽、上沿收边"""
    levels = [
        (0.0000, 0.00060),
        (0.0009, 0.00000),
        (0.0011, 0.00035),
        (0.0013, 0.00000),
        (0.0026, 0.00000),
        (SOLE_H, 0.00045),
    ]
    verts, faces = [], []
    for dz, inset in levels:
        for i in range(n):
            t = 2 * math.pi * i / n
            verts.append((cx + (a - inset) * sup(math.cos(t), p),
                          cy + (b - inset) * sup(math.sin(t), p),
                          Z_BOT + dz))
    for L in range(len(levels) - 1):
        base = L * n
        for i in range(n):
            j = (i + 1) % n
            faces.append((base + i, base + j, base + n + j, base + n + i))
    faces.append(tuple(range(n - 1, -1, -1)))
    top = (len(levels) - 1) * n
    faces.append(tuple(range(top, top + n)))
    return make_obj(name, verts, faces, mat)


# 采样原鞋表面（top z / 半宽）
surf = {}
for side, cfg in SIDES.items():
    bins = {}
    for v in me.vertices:
        co = mw @ v.co
        if not (Z_SOLE_TOP - 0.0005 <= co.z <= 0.0215):
            continue
        if abs(co.x) > 0.016 or not (cfg['toe'] - 0.002 < co.y < cfg['heel'] + 0.002):
            continue
        if (co.x < 0) != (side == 'L'):
            continue
        k = round((co.y - cfg['toe']) / (cfg['heel'] - cfg['toe']), 2)
        d = bins.setdefault(k, {'zt': -1e9, 'w': 0.0})
        d['zt'] = max(d['zt'], co.z)
        d['w'] = max(d['w'], abs(co.x - cfg['cx']))
    surf[side] = bins
    print('SURF', side, len(bins), 'zmax', round(max(b['zt'] for b in bins.values()), 4),
          'wmax', round(max(b['w'] for b in bins.values()), 4))


def surf_at(side, f):
    bins = surf[side]
    ks = sorted(bins)
    k = min(ks, key=lambda x: abs(x - f))
    return bins[k]['w'], bins[k]['zt']


def strap(name, cx, y0, w, zt, half_y, mat, arc=(22, 158), n=26):
    """贴着原鞋面拱起的搭带，只覆盖鞋面上半部分"""
    z0 = Z_SOLE_TOP
    h = zt - z0
    zc = z0 + h / 2
    p = 2.6
    pts = []
    for i in range(n + 1):
        t = math.radians(arc[0] + (arc[1] - arc[0]) * i / n)
        x = cx + (w + 0.00060) * sup(math.cos(t), p)
        z = zc + (h / 2 + 0.00060) * sup(math.sin(t), p)
        nx, nz = math.cos(t), math.sin(t)
        ln = math.hypot(nx, nz) or 1.0
        pts.append((x, z, nx / ln, nz / ln))
    verts, faces = [], []
    for (x, z, nx, nz) in pts:
        for dy, dn in ((-half_y, 0.0), (half_y, 0.0), (half_y, 0.00115), (-half_y, 0.00115)):
            verts.append((x + nx * dn, y0 + dy, z + nz * dn))
    for i in range(n):
        b0, b1 = i * 4, (i + 1) * 4
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((b0 + k, b0 + k2, b1 + k2, b1 + k))
    faces.append((0, 1, 2, 3))
    b = n * 4
    faces.append((b + 3, b + 2, b + 1, b + 0))
    return make_obj(name, verts, faces, mat)


def torus(name, loc, major, minor, mat, seg=28, ring=12):
    verts, faces = [], []
    for i in range(seg):
        u = 2 * math.pi * i / seg
        cu, su = math.cos(u), math.sin(u)
        for j in range(ring):
            v = 2 * math.pi * j / ring
            r = major + minor * math.cos(v)
            z = minor * math.sin(v)
            verts.append((loc[0] + z, loc[1] + r * cu, loc[2] + r * su))
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(ring):
            j2 = (j + 1) % ring
            faces.append((i * ring + j, i2 * ring + j, i2 * ring + j2, i * ring + j2))
    return make_obj(name, verts, faces, mat)


if 'Cream sole soft matte' in bpy.data.materials:
    mat_sole = bpy.data.materials['Cream sole soft matte']
else:
    mat_sole = mat_upper.copy()
    mat_sole.name = 'Cream sole soft matte'
    for nd in mat_sole.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Roughness'].default_value = 0.60

parent = bpy.data.objects.get('Character_120mm')
made = []
for side, cfg in SIDES.items():
    cx = cfg['cx']
    L = cfg['heel'] - cfg['toe']
    cy = (cfg['toe'] + cfg['heel']) / 2
    parts = [bumper(f'Sole_{side}', cx, cy, cfg['a'], cfg['b'], mat_sole)]
    for k, f in enumerate((0.46, 0.63)):
        w, zt = surf_at(side, f)
        y0 = cfg['toe'] + f * L
        parts.append(strap(f'Strap{side}{k}', cx, y0, w, zt, 0.00175, mat_upper))
    w, zt = surf_at(side, 0.63)
    bx = cx + (w + 0.00155) * (1 if side == 'R' else -1)
    parts.append(torus(f'Buckle_{side}', (bx, cfg['toe'] + 0.63 * L, Z_SOLE_TOP + (zt - Z_SOLE_TOP) * 0.45),
                       0.00140, 0.00033, mat_upper))

    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    shoe = bpy.context.view_layer.objects.active
    shoe.name = f'GEO-Sneaker details {side}'
    shoe.data.name = f'Sneaker details {side}'
    m = shoe.modifiers.new('Smooth', 'SUBSURF')
    m.levels = 1
    m.render_levels = 1
    bpy.ops.object.modifier_apply(modifier=m.name)
    if parent:
        shoe.parent = parent
        shoe.matrix_parent_inverse = parent.matrix_world.inverted()
    made.append(shoe)

print('BUILT', [(o.name, len(o.data.polygons)) for o in made])
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')
