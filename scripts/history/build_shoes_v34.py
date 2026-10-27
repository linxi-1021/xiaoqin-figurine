import bpy, bmesh, math, json, os
from mathutils import Vector, Matrix

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_背包鞋镜框重建_v34_20261025\小秦_v6背包鞋镜框重建.blend'
OUT_DIR = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34\shoes'
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world

mat_upper = bpy.data.materials['Cream leather shoes soft satin finish']

# ---------- 1. 删除旧鞋面（奶白皮革材质）与薄底（PBR，z<0.0124 的脚部区域） ----------
upper_idx = None
for i, m in enumerate(me.materials):
    if m and m.name == 'Cream leather shoes soft satin finish':
        upper_idx = i
assert upper_idx is not None

bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
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
print('REMAIN_FACES', len(me.polygons))

# ---------- 2. 参数（单位米） ----------
Z_BOT = 0.0088      # 底座顶面
SOLE_OUT = 0.0019
SOLE_MID = 0.0015
Z_SOLE_TOP = Z_BOT + SOLE_OUT + SOLE_MID   # 0.0122

SIDES = {
    'L': {'cx': -0.00615, 'a': 0.00630, 'b': 0.00990, 'toe': -0.01000, 'heel': 0.00900},
    'R': {'cx': 0.00675, 'a': 0.00655, 'b': 0.00960, 'toe': -0.01000, 'heel': 0.00880},
}


def sup(v, p):
    return math.copysign(abs(v) ** (2.0 / p), v)


def make_obj(name, verts, faces, mat, smooth=True):
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], faces)
    m.validate()
    m.update()
    ob = bpy.data.objects.new(name, m)
    scene.collection.objects.link(ob)
    m.materials.append(mat)
    if smooth:
        for p in m.polygons:
            p.use_smooth = True
    return ob


def rounded_slab(name, cx, cy, a, b, z0, z1, p=3.2, inset_bottom=0.00045, inset_top=0.00035, n=64):
    """超椭圆平面 + 上下收边的一层底"""
    verts, faces = [], []
    levels = [(z0, inset_bottom), (z0 + (z1 - z0) * 0.45, 0.0), (z1, inset_top)]
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
    # 底、顶封口
    faces.append(tuple(range(n - 1, -1, -1)))
    top = (len(levels) - 1) * n
    faces.append(tuple(range(top, top + n)))
    return verts, faces


def upper_body(name, cx, toe, heel, mat):
    """鞋身放样：沿 y 的截面是超椭圆，底边落在鞋底顶面"""
    stations = [
        (toe, 0.0030, 0.0133),
        (toe + 0.0012, 0.0048, 0.0150),
        (toe + 0.0034, 0.0058, 0.0169),
        (toe + 0.0056, 0.0061, 0.0181),
        (toe + 0.0080, 0.0061, 0.0189),
        (toe + 0.0105, 0.0059, 0.0194),
        (toe + 0.0130, 0.0056, 0.0196),
        (toe + 0.0152, 0.0053, 0.0196),
        (heel - 0.0012, 0.0051, 0.0195),
        (heel, 0.0042, 0.0192),
    ]
    K = 32
    p = 2.7
    verts, faces = [], []
    for (y, w, zt) in stations:
        h = zt - Z_SOLE_TOP
        zc = Z_SOLE_TOP + h / 2
        for i in range(K):
            t = 2 * math.pi * i / K
            x = cx + w * sup(math.cos(t), p)
            z = zc + (h / 2) * sup(math.sin(t), p)
            verts.append((x, y, z))
    for s in range(len(stations) - 1):
        a0 = s * K
        a1 = (s + 1) * K
        for i in range(K):
            j = (i + 1) % K
            faces.append((a0 + i, a0 + j, a1 + j, a1 + i))
    faces.append(tuple(range(K - 1, -1, -1)))
    last = (len(stations) - 1) * K
    faces.append(tuple(range(last, last + K)))
    return verts, faces


def strap(name, cx, y0, w, zt, half_y, thick, arc=(-78, 78), n=20):
    """跨过鞋面的搭带：沿截面弧线扫掠一个薄带"""
    verts, faces = [], []
    p = 2.7
    h = zt - Z_SOLE_TOP
    zc = Z_SOLE_TOP + h / 2
    pts = []
    for i in range(n + 1):
        t = math.radians(arc[0] + (arc[1] - arc[0]) * i / n)
        x = cx + (w + 0.0005) * sup(math.cos(t), p)
        z = zc + (h / 2 + 0.0005) * sup(math.sin(t), p)
        nx = math.cos(t)
        nz = math.sin(t)
        ln = math.hypot(nx, nz) or 1.0
        pts.append((x, z, nx / ln, nz / ln))
    for (x, z, nx, nz) in pts:
        for dy, dn in ((-half_y, 0.0), (half_y, 0.0), (half_y, thick), (-half_y, thick)):
            verts.append((x + nx * dn, y0 + dy, z + nz * dn))
    for i in range(n):
        b0 = i * 4
        b1 = (i + 1) * 4
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((b0 + k, b0 + k2, b1 + k2, b1 + k))
    faces.append((0, 1, 2, 3))
    b = n * 4
    faces.append((b + 3, b + 2, b + 1, b + 0))
    return verts, faces


def torus(name, loc, major, minor, mat, axis='X', seg=24, ring=10):
    verts, faces = [], []
    for i in range(seg):
        u = 2 * math.pi * i / seg
        cu, su = math.cos(u), math.sin(u)
        for j in range(ring):
            v = 2 * math.pi * j / ring
            r = major + minor * math.cos(v)
            z = minor * math.sin(v)
            if axis == 'X':
                p = Vector((z, r * cu, r * su))
            else:
                p = Vector((r * cu, r * su, z))
            verts.append((loc[0] + p.x, loc[1] + p.y, loc[2] + p.z))
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(ring):
            j2 = (j + 1) % ring
            faces.append((i * ring + j, i2 * ring + j, i2 * ring + j2, i * ring + j2))
    return make_obj(name, verts, faces, mat)


# 鞋底材质：原皮革材质的略暗副本
if 'Cream sole soft matte' in bpy.data.materials:
    mat_sole = bpy.data.materials['Cream sole soft matte']
else:
    mat_sole = mat_upper.copy()
    mat_sole.name = 'Cream sole soft matte'
    if mat_sole.use_nodes:
        for n in mat_sole.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                c = n.inputs['Base Color'].default_value
                n.inputs['Base Color'].default_value = (c[0] * 0.93, c[1] * 0.90, c[2] * 0.84, 1)
                n.inputs['Roughness'].default_value = 0.62

parent = bpy.data.objects.get('Character_120mm')
made = []
for side, cfg in SIDES.items():
    cx = cfg['cx']
    cy = (cfg['toe'] + cfg['heel']) / 2
    parts = []
    v, f = rounded_slab(f'Outsole_{side}', cx, cy, cfg['a'], cfg['b'], Z_BOT, Z_BOT + SOLE_OUT)
    parts.append(make_obj(f'Outsole_{side}', v, f, mat_sole))
    v, f = rounded_slab(f'Midsole_{side}', cx, cy, cfg['a'] - 0.0003, cfg['b'] - 0.0003,
                        Z_BOT + SOLE_OUT, Z_SOLE_TOP)
    parts.append(make_obj(f'Midsole_{side}', v, f, mat_sole))
    v, f = upper_body(f'Upper_{side}', cx, cfg['toe'], cfg['heel'], mat_upper)
    up = make_obj(f'Upper_{side}', v, f, mat_upper)
    parts.append(up)

    # 两条搭带：按鞋面在该 y 处的高度放
    for k, (yy, hw) in enumerate([(-0.0022, 0.0016), (0.0030, 0.0016)]):
        frac = (yy - cfg['toe']) / (cfg['heel'] - cfg['toe'])
        w = 0.0061 - 0.0008 * abs(frac - 0.5) * 2
        zt = 0.0188 + 0.0006 * min(1.0, max(0.0, frac))
        v, f = strap(f'Strap{side}{k}', cx, yy, w, zt, hw, 0.0011)
        parts.append(make_obj(f'Strap{side}{k}', v, f, mat_upper))

    # 外侧扣
    bx = cx + (cfg['a'] + 0.0011) * (1 if side == 'R' else -1)
    parts.append(torus(f'Buckle_{side}', (bx, -0.0022, 0.0172), 0.0016, 0.00040, mat_upper))

    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    shoe = bpy.context.view_layer.objects.active
    shoe.name = f'GEO-Rebuilt sneaker {side}'
    shoe.data.name = f'Rebuilt sneaker {side}'
    mod = shoe.modifiers.new('Smooth', 'SUBSURF')
    mod.levels = 1
    mod.render_levels = 1
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if parent:
        shoe.parent = parent
        shoe.matrix_parent_inverse = parent.matrix_world.inverted()
    made.append(shoe)

print('BUILT', [ (o.name, len(o.data.polygons)) for o in made])

# ---------- 3. 保存 ----------
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED', BLEND)
