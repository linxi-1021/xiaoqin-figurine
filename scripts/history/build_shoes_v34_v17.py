import bpy, bmesh, math, os

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_背包鞋镜框重建_v34_20261025\小秦_v6背包鞋镜框重建.blend'
OUT_DIR = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34\shoes'
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world
mat_upper = bpy.data.materials['Cream leather shoes soft satin finish']
upper_idx = [i for i, m in enumerate(me.materials) if m and m.name == mat_upper.name][0]

# 脚部轮廓（低处整圈）
low_pts = {'L': [], 'R': []}
for p in me.polygons:
    c = mw @ p.center
    if abs(c.x) > 0.0175 or not (-0.017 < c.y < 0.018):
        continue
    if 0.0116 <= c.z <= 0.0150:
        low_pts['L' if c.x < 0 else 'R'].append((c.x, c.y, c.z))

# 删旧薄底
bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
deleting = []
print('DELETE', 0)

# 在鞋面上做出两条平滑凸带 + 外侧扣片
bm.normal_update()
BANDS = (-0.0016, 0.0017)
HALF = 0.00155
RISE = 0.00105
TOE_SEAM_Y = None
moved = 0
for v in bm.verts:
    co = mw @ v.co
    if not (0.0088 <= co.z <= 0.0198 and abs(co.x) < 0.017 and -0.016 < co.y < 0.017):
        continue
    zf = min(1.0, max(0.0, (co.z - 0.0146) / 0.0014))
    if zf <= 0:
        continue
    for y0 in BANDS:
        d = abs(co.y - y0)
        if d >= HALF:
            continue
        t = d / HALF
        # 平顶 + 陡边：读起来像带子而不是圆棱
        if t < 0.62:
            w = 1.0
        else:
            w = math.cos(math.pi * (t - 0.62) / 0.76) ** 2
        push = RISE * w * zf
        if y0 == BANDS[1] and abs(co.x) > 0.0102 and 0.0152 < co.z < 0.0182:
            u = min(1.0, max(0.0, (abs(co.x) - 0.0102) / 0.0016))
            push += 0.00070 * w * (u * u * (3 - 2 * u))
        v.co = v.co + v.normal * push
        moved += 1
print('MOVED_VERTS', moved)

# 鞋头围条：一条浅凹线（沿法线向内）
for v in bm.verts:
    co = mw @ v.co
    if not (0.0130 <= co.z <= 0.0195 and abs(co.x) < 0.016 and -0.014 < co.y < -0.003):
        continue
    yg = -0.0068
    d = abs(co.y - yg)
    if d > 0.0007:
        continue
    g = math.cos(math.pi * d / 0.0007) ** 2
    v.co = v.co - v.normal * (0.00028 * g)

bm.to_mesh(me)
bm.free()
me.update()

Z_BOT = 0.0088
SOLE_H = 0.0034


def sup(v, p):
    return math.copysign(abs(v) ** (2.0 / p), v)


def make_obj(name, verts, faces, mat, uv=(0.4, 0.3564)):
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], faces)
    m.validate(); m.update()
    ob = bpy.data.objects.new(name, m)
    scene.collection.objects.link(ob)
    m.materials.append(mat)
    lay = m.uv_layers.new(name='UVMap')
    for d in lay.data:
        d.uv = uv
    for p in m.polygons:
        p.use_smooth = True
    return ob


def bumper(name, cx, cy, a, b, mat, n=72, p=2.6):
    levels = [(0.0000, 0.00045), (0.0007, 0.0), (0.0009, 0.00020),
              (0.0011, 0.0), (0.0022, 0.0), (SOLE_H - 0.00030, -0.00018), (SOLE_H, 0.0)]
    verts, faces = [], []
    for dz, inset in levels:
        for i in range(n):
            t = 2 * math.pi * i / n
            verts.append((cx + (a - inset) * sup(math.cos(t), p),
                          cy + (b - inset) * sup(math.sin(t), p), Z_BOT + dz))
    for L in range(len(levels) - 1):
        base = L * n
        for i in range(n):
            j = (i + 1) % n
            faces.append((base + i, base + j, base + n + j, base + n + i))
    faces.append(tuple(range(n - 1, -1, -1)))
    top = (len(levels) - 1) * n
    faces.append(tuple(range(top, top + n)))
    return make_obj(name, verts, faces, mat)


mat_sole = bpy.data.materials.get('Cream sole soft matte')
if not mat_sole:
    mat_sole = mat_upper.copy()
    mat_sole.name = 'Cream sole soft matte'
    for nd in mat_sole.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Roughness'].default_value = 0.60

parent = bpy.data.objects.get('Character_120mm')
made = []
for side in ('L', 'R'):
    xs = [p[0] for p in low_pts[side]]; ys = [p[1] for p in low_pts[side]]
    cx = (min(xs) + max(xs)) / 2
    a = (max(xs) - min(xs)) / 2 + 0.00020
    if side == 'L':
        a = min(a, -0.00020 - cx)
    else:
        a = min(a, cx - 0.00020)
    cy = (min(ys) + max(ys)) / 2
    b = (max(ys) - min(ys)) / 2 + 0.00020
    ob = bumper(f'Sole details {side}', cx, cy, a, b, mat_sole)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    made.append(ob)
    print('SOLE', side, 'cx', round(cx, 5), 'a', round(a, 5), 'b', round(b, 5))

print('BUILT', [(o.name, len(o.data.polygons)) for o in made])
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')
