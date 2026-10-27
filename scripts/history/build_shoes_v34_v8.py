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

# 量脚部轮廓（低处整圈）
low_pts = {'L': [], 'R': []}
for p in me.polygons:
    c = mw @ p.center
    if abs(c.x) > 0.0175 or not (-0.017 < c.y < 0.018):
        continue
    if 0.0126 <= c.z <= 0.0148:
        low_pts['L' if c.x < 0 else 'R'].append((c.x, c.y, c.z))

# 删旧薄底
bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
deleting = []
for f in bm.faces:
    c = mw @ f.calc_center_median()
    if c.z < 0.0116 and abs(c.x) < 0.0175 and -0.016 < c.y < 0.017:
        deleting.append(f)
print('DELETE', len(deleting))
bmesh.ops.delete(bm, geom=deleting, context='FACES')

# 在鞋面上挤出两条搭带（继承 UV / 材质）
bm.normal_update()
for side, sign in (('L', -1), ('R', 1)):
    for y0 in (-0.0016, 0.0017):
        faces = []
        for f in bm.faces:
            c = mw @ f.calc_center_median()
            if f.material_index != upper_idx:
                continue
            if (c.x < 0) != (side == 'L'):
                continue
            if abs(c.y - y0) < 0.00155 and c.z > 0.0142 and abs(c.x) < 0.016:
                faces.append(f)
        if not faces:
            print('NO_FACES', side, y0)
            continue
        dup = bmesh.ops.duplicate(bm, geom=faces)
        new_faces = [g for g in dup['geom'] if isinstance(g, bmesh.types.BMFace)]
        ext = bmesh.ops.extrude_face_region(bm, geom=new_faces)
        new_verts = [g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)]
        for v in new_verts:
            v.co = v.co + v.normal * 0.00085
        for g in ext['geom']:
            if isinstance(g, bmesh.types.BMFace):
                g.material_index = upper_idx
        print('STRAP', side, y0, len(faces), 'faces')

bm.to_mesh(me)
bm.free()
me.update()

Z_BOT = 0.0088
SOLE_H = 0.0032


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


def bumper(name, cx, cy, a, b, mat, n=72, p=3.4):
    levels = [(0.0000, 0.00055), (0.0008, 0.0), (0.0010, 0.00025),
              (0.0012, 0.0), (0.0023, 0.0), (SOLE_H, 0.00035)]
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


def torus(name, loc, major, minor, mat, seg=24, ring=10):
    verts, faces = [], []
    for i in range(seg):
        u = 2 * math.pi * i / seg
        cu, su = math.cos(u), math.sin(u)
        for j in range(ring):
            v = 2 * math.pi * j / ring
            r = major + minor * math.cos(v)
            zz = minor * math.sin(v)
            verts.append((loc[0] + zz, loc[1] + r * cu, loc[2] + r * su))
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(ring):
            j2 = (j + 1) % ring
            faces.append((i * ring + j, i2 * ring + j, i2 * ring + j2, i * ring + j2))
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
for side, sign in (('L', -1), ('R', 1)):
    xs = [p[0] for p in low_pts[side]]; ys = [p[1] for p in low_pts[side]]
    cx = (min(xs) + max(xs)) / 2
    a = (max(xs) - min(xs)) / 2 + 0.00015
    if side == 'L':
        a = min(a, -0.00030 - cx)
    else:
        a = min(a, cx - 0.00030)
    cy = (min(ys) + max(ys)) / 2
    b = (max(ys) - min(ys)) / 2 + 0.00015
    sole = bumper(f'Sole details {side}', cx, cy, a, b, mat_sole)
    parts = [sole]

    # 扣：放在两条带的外侧端
    strap_pts = [(p.co.x, p.co.y, p.co.z) for p in
                 [v for v in me.vertices if 0.0140 < (mw @ v.co).z < 0.0198 and abs((mw @ v.co).x) < 0.016]]
    for y0 in (-0.0016, 0.0017):
        cand = [p for p in strap_pts if abs(p[1] - y0) < 0.0016 and (p[0] < 0) == (side == 'L')]
        if not cand:
            continue
        edge = max(cand, key=lambda p: p[0] * sign)
        zc = sum(p[2] for p in cand) / len(cand)
        parts.append(torus(f'Buckle{side}{y0}', (edge[0] + 0.00055 * sign, y0, min(zc, 0.0172)),
                           0.00095, 0.00028, mat_upper))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = f'GEO-Sneaker details {side}'
    ob.data.name = f'Sneaker details {side}'
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    made.append(ob)

print('BUILT', [(o.name, len(o.data.polygons)) for o in made])
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')
