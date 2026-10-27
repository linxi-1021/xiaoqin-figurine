import bpy, bmesh, math, json, os
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

# ---------- 1. 从原鞋面采样一块奶白 UV ----------
uv_layer = me.uv_layers['UVMap']
img = None
for n in mat_upper.node_tree.nodes:
    if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'Front clip carrier cleaned atlas':
        img = n.image
w, h = img.size
px = np.empty(w * h * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)

cands = []
for p in me.polygons:
    if p.material_index != upper_idx:
        continue
    c = mw @ p.center
    if not (0.0088 <= c.z <= 0.020 and abs(c.x) < 0.014 and -0.012 < c.y < 0.014):
        continue
    u = sum(uv_layer.data[li].uv[0] for li in p.loop_indices) / p.loop_total
    v = sum(uv_layer.data[li].uv[1] for li in p.loop_indices) / p.loop_total
    xi = int(u * w) % w
    yi = int(v * h) % h
    r, g, b = float(px[yi, xi, 0]), float(px[yi, xi, 1]), float(px[yi, xi, 2])
    cands.append((min(r, g, b), max(r, g, b), abs(max(r, g, b) - min(r, g, b)), u, v, r, g, b))

cands.sort(key=lambda t: (-t[0], t[2]))
pick = cands[0]
CREAM_UV = (pick[3], pick[4])
print('UV_CANDIDATES', len(cands), 'PICK', [round(x, 4) for x in pick])

# ---------- 2. 删除旧鞋面 + 薄底 ----------
bm = bmesh.new()
bm.from_mesh(me)
deleting = []
for f in bm.faces:
    c = mw @ f.calc_center_median()
    if f.material_index == upper_idx:
        deleting.append(f)
    elif c.z < 0.0124 and abs(c.x) < 0.0175 and -0.015 < c.y < 0.016:
        deleting.append(f)
print('DELETE_FACES', len(deleting))
bmesh.ops.delete(bm, geom=deleting, context='FACES')
bm.to_mesh(me)
bm.free()
me.update()

# ---------- 3. 参数 ----------
Z_BOT = 0.0088
SOLE_OUT = 0.0019
SOLE_MID = 0.0015
Z_SOLE_TOP = Z_BOT + SOLE_OUT + SOLE_MID
Z_UP_BOT = Z_SOLE_TOP - 0.0004  # 鞋身略嵌入鞋底，消缝

SIDES = {
    'L': {'cx': -0.00615, 'a': 0.00630, 'b': 0.01000, 'toe': -0.01010, 'heel': 0.00900},
    'R': {'cx': 0.00675, 'a': 0.00655, 'b': 0.00970, 'toe': -0.01010, 'heel': 0.00880},
}


def sup(v, p):
    return math.copysign(abs(v) ** (2.0 / p), v)


def set_uv(ob, uv=(0.5, 0.5)):
    m = ob.data
    layer = m.uv_layers.new(name='UVMap')
    for d in layer.data:
        d.uv = uv


def make_obj(name, verts, faces, mat, uv=CREAM_UV, smooth=True):
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], faces)
    m.validate()
    m.update()
    ob = bpy.data.objects.new(name, m)
    scene.collection.objects.link(ob)
    m.materials.append(mat)
    set_uv(ob, uv)
    if smooth:
        for p in m.polygons:
            p.use_smooth = True
    return ob


def rounded_slab(name, cx, cy, a, b, z0, z1, mat, p=3.4, inset_bottom=0.00050, inset_top=0.00040, n=72):
    verts, faces = [], []
    levels = [(z0, inset_bottom), (z0 + (z1 - z0) * 0.5, 0.0), (z1, inset_top)]
    for z, inset in levels:
        for i in range(n):
            t = 2 * math.pi * i / n
            x = cx + (a - inset) * sup(math.cos(t), p)
            y = cy + (b - inset) * sup(math.sin(t), p)
            verts.append((x, y, z))
    for L in range(len(levels) - 1):
        base = L * n
        for i in range(n):
            j = (i + 1) % n
            faces.append((base + i, base + j, base + n + j, base + n + i))
    faces.append(tuple(range(n - 1, -1, -1)))
    top = (len(levels) - 1) * n
    faces.append(tuple(range(top, top + n)))
    return make_obj(name, verts, faces, mat)


PROFILE = [
    (0.00, 0.0022, 0.0136),
    (0.04, 0.0036, 0.0146),
    (0.10, 0.0048, 0.0158),
    (0.18, 0.0057, 0.0168),
    (0.28, 0.0060, 0.0176),
    (0.40, 0.0061, 0.0184),
    (0.52, 0.0060, 0.0188),
    (0.64, 0.0058, 0.0191),
    (0.76, 0.0055, 0.0193),
    (0.88, 0.0050, 0.0194),
    (1.00, 0.0042, 0.0193),
]


def upper_body(name, cx, toe, heel, mat):
    L = heel - toe
    K = 36
    p = 2.6
    verts, faces = [], []
    for (f, w, zt) in PROFILE:
        y = toe + f * L
        hgt = zt - Z_UP_BOT
        zc = Z_UP_BOT + hgt / 2
        for i in range(K):
            t = 2 * math.pi * i / K
            x = cx + w * sup(math.cos(t), p)
            z = zc + (hgt / 2) * sup(math.sin(t), p)
            verts.append((x, y, z))
    for s in range(len(PROFILE) - 1):
        a0 = s * K
        a1 = (s + 1) * K
        for i in range(K):
            j = (i + 1) % K
            faces.append((a0 + i, a0 + j, a1 + j, a1 + i))
    faces.append(tuple(range(K - 1, -1, -1)))
    last = (len(PROFILE) - 1) * K
    faces.append(tuple(range(last, last + K)))
    return make_obj(name, verts, faces, mat)


def interp_profile(f):
    for i in range(len(PROFILE) - 1):
        f0, w0, z0 = PROFILE[i]
        f1, w1, z1 = PROFILE[i + 1]
        if f0 <= f <= f1:
            k = (f - f0) / (f1 - f0)
            return w0 + (w1 - w0) * k, z0 + (z1 - z0) * k
    return PROFILE[-1][1], PROFILE[-1][2]


def strap(name, cx, f, L, toe, half_y, thick, mat, arc=(-84, 84), n=24):
    w, zt = interp_profile(f)
    y0 = toe + f * L
    p = 2.6
    hgt = zt - Z_UP_BOT
    zc = Z_UP_BOT + hgt / 2
    verts, faces = [], []
    pts = []
    for i in range(n + 1):
        t = math.radians(arc[0] + (arc[1] - arc[0]) * i / n)
        x = cx + (w + 0.00055) * sup(math.cos(t), p)
        z = zc + (hgt / 2 + 0.00055) * sup(math.sin(t), p)
        nx, nz = math.cos(t), math.sin(t)
        ln = math.hypot(nx, nz) or 1.0
        pts.append((x, z, nx / ln, nz / ln))
    for (x, z, nx, nz) in pts:
        for dy, dn in ((-half_y, 0.0), (half_y, 0.0), (half_y, thick), (-half_y, thick)):
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
    parts = [
        rounded_slab(f'Outsole_{side}', cx, cy, cfg['a'], cfg['b'], Z_BOT, Z_BOT + SOLE_OUT, mat_sole),
        rounded_slab(f'Midsole_{side}', cx, cy, cfg['a'] - 0.00035, cfg['b'] - 0.00035,
                     Z_BOT + SOLE_OUT, Z_SOLE_TOP, mat_sole),
        upper_body(f'Upper_{side}', cx, cfg['toe'], cfg['heel'], mat_upper),
    ]
    for k, f in enumerate((0.42, 0.62)):
        parts.append(strap(f'Strap{side}{k}', cx, f, L, cfg['toe'], 0.00140, 0.00105, mat_upper))
    w_s, zt_s = interp_profile(0.62)
    bx = cx + (w_s + 0.0021) * (1 if side == 'R' else -1)
    parts.append(torus(f'Buckle_{side}', (bx, cfg['toe'] + 0.62 * L, Z_UP_BOT + (zt_s - Z_UP_BOT) * 0.62),
                       0.00145, 0.00034, mat_upper))

    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    shoe = bpy.context.view_layer.objects.active
    shoe.name = f'GEO-Rebuilt sneaker {side}'
    shoe.data.name = f'Rebuilt sneaker {side}'
    m = shoe.modifiers.new('Smooth', 'SUBSURF')
    m.levels = 1
    m.render_levels = 1
    bpy.ops.object.modifier_apply(modifier=m.name)
    if parent:
        shoe.parent = parent
        shoe.matrix_parent_inverse = parent.matrix_world.inverted()
    made.append(shoe)

print('BUILT', [(o.name, len(o.data.polygons)) for o in made])
print('CREAM_UV', [round(x, 4) for x in CREAM_UV])
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')
