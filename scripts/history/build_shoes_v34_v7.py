import bpy, bmesh, math, os
import numpy as np

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_背包鞋镜框重建_v34_20261025\小秦_v6背包鞋镜框重建.blend'
OUT_DIR = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34\shoes'
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world
mat_upper = bpy.data.materials['Cream leather shoes soft satin finish']
upper_idx = [i for i, m in enumerate(me.materials) if m and m.name == mat_upper.name][0]

uv_layer = me.uv_layers['UVMap']
img = [n.image for n in mat_upper.node_tree.nodes
       if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'Front clip carrier cleaned atlas'][0]
wi, hi = img.size
px = np.empty(wi * hi * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(hi, wi, 4)
best = None
for p in me.polygons:
    if p.material_index != upper_idx:
        continue
    c = mw @ p.center
    if not (0.0090 <= c.z <= 0.019 and abs(c.x) < 0.013 and -0.011 < c.y < 0.013):
        continue
    u = sum(uv_layer.data[li].uv[0] for li in p.loop_indices) / p.loop_total
    v = sum(uv_layer.data[li].uv[1] for li in p.loop_indices) / p.loop_total
    r, g, b = (float(px[int(v * hi) % hi, int(u * wi) % wi, k]) for k in range(3))
    s = min(r, g, b) - abs(max(r, g, b) - min(r, g, b))
    if best is None or s > best[0]:
        best = (s, u, v)
CREAM_UV = (best[1], best[2])
print('CREAM_UV', [round(x, 4) for x in CREAM_UV])

shoe_pts = {'L': [], 'R': []}
low_pts = {'L': [], 'R': []}
for p in me.polygons:
    c = mw @ p.center
    if abs(c.x) > 0.0175 or not (-0.017 < c.y < 0.018) or c.z > 0.0215 or c.z < 0.0095:
        continue
    side = 'L' if c.x < 0 else 'R'
    if p.material_index == upper_idx:
        shoe_pts[side].append((c.x, c.y, c.z))
    if 0.0126 <= c.z <= 0.0148:
        low_pts[side].append((c.x, c.y, c.z))

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
bm.to_mesh(me)
bm.free()
me.update()

Z_BOT = 0.0088
SOLE_H = 0.0036
SIDES = {}
for side in ('L', 'R'):
    xs = [p[0] for p in low_pts[side]]; ys = [p[1] for p in low_pts[side]]
    cx = (min(xs) + max(xs)) / 2
    a = (max(xs) - min(xs)) / 2 + 0.00040
    # 两脚之间留 0.35mm 缝
    if side == 'L':
        a = min(a, -0.00035 - cx)
    else:
        a = min(a, cx - 0.00035)
    SIDES[side] = {'cx': cx, 'a': a,
                   'b': (max(ys) - min(ys)) / 2 + 0.00040,
                   'toe': min(ys), 'heel': max(ys)}
    print('SOLE', side, {k: round(v, 5) for k, v in SIDES[side].items()})


def sup(v, p):
    return math.copysign(abs(v) ** (2.0 / p), v)


def make_obj(name, verts, faces, mat, smooth=True):
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], faces)
    m.validate(); m.update()
    ob = bpy.data.objects.new(name, m)
    scene.collection.objects.link(ob)
    m.materials.append(mat)
    lay = m.uv_layers.new(name='UVMap')
    for d in lay.data:
        d.uv = CREAM_UV
    if smooth:
        for p in m.polygons:
            p.use_smooth = True
    return ob


def bumper(name, cx, cy, a, b, mat, n=72, p=3.4):
    levels = [(0.0000, 0.00055), (0.0009, 0.0), (0.0011, 0.00030),
              (0.0013, 0.0), (0.0026, 0.0), (SOLE_H, 0.00040)]
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


def hull2d(pts):
    pts = sorted(set((round(x, 6), round(z, 6)) for x, z in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def ray_near(poly, cx, cz, ang):
    dx, dz = math.cos(ang), math.sin(ang)
    hits = []
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        ex, ez = x2 - x1, z2 - z1
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        t = ((x1 - cx) * ez - (z1 - cz) * ex) / den
        s = ((x1 - cx) * dz - (z1 - cz) * dx) / den
        if t > 0 and -0.001 <= s <= 1.001:
            hits.append(t)
    return min(hits) if hits else 0.0


def strap(name, cx, y0, slab_pts, mat, r_off=0.00045, thick=0.00105, half_y=0.00165, n=24):
    poly = hull2d([(p[0], p[2]) for p in slab_pts])
    if len(poly) < 3:
        return None, None, None
    zmin = min(p[1] for p in poly); zmax = max(p[1] for p in poly)
    cz = (zmin + zmax) / 2
    pts = []
    for i in range(n + 1):
        ang = math.radians(198 - 216 * i / n)
        r = ray_near(poly, cx, cz, ang)
        if r <= 0:
            continue
        x = cx + (r + r_off) * math.cos(ang)
        z = cz + (r + r_off) * math.sin(ang)
        pts.append((x, z, math.cos(ang), math.sin(ang)))
    if len(pts) < 2:
        return None, None, None
    verts, faces = [], []
    for (x, z, nx, nz) in pts:
        for dy, dn in ((-half_y, 0.0), (half_y, 0.0), (half_y, thick), (-half_y, thick)):
            verts.append((x + nx * dn, y0 + dy, z + nz * dn))
    for i in range(len(pts) - 1):
        b0, b1 = i * 4, (i + 1) * 4
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((b0 + k, b0 + k2, b1 + k2, b1 + k))
    faces.append((0, 1, 2, 3))
    b = (len(pts) - 1) * 4
    faces.append((b + 3, b + 2, b + 1, b + 0))
    return make_obj(name, verts, faces, mat), pts[0], pts[-1]


def torus(name, loc, major, minor, mat, seg=28, ring=12):
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
for side, cfg in SIDES.items():
    cx = cfg['cx']
    L = cfg['heel'] - cfg['toe']
    cy = (cfg['toe'] + cfg['heel']) / 2
    parts = [bumper(f'Sole_{side}', cx, cy, cfg['a'], cfg['b'], mat_sole)]
    ends = []
    for k, f in enumerate((0.45, 0.62)):
        y0 = cfg['toe'] + f * L
        slab = [p for p in shoe_pts[side] if abs(p[1] - y0) < 0.0007]
        st, p0, p1 = strap(f'Strap{side}{k}', cx, y0, slab, mat_upper)
        if st:
            parts.append(st)
            ends.append((max((p0, p1), key=lambda q: abs(q[0] - cx)), y0))
    for k, (p, y0) in enumerate(ends):
        off = 0.00045 * (1 if side == 'R' else -1)
        parts.append(torus(f'Buckle{side}{k}', (p[0] + off, y0, p[1]), 0.00105, 0.00028, mat_upper))
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
