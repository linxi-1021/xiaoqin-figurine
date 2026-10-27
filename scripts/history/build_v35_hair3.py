import bpy, math, os, random
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'
BLEND = os.path.join(V35, 'steps', 'step06_blockout.blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
for n in ('P_HairBack', 'P_HairSide_L', 'P_HairSide_R'):
    ob = bpy.data.objects.get(n)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)

HAIR = bpy.data.materials['Hair']
random.seed(7)


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def ellipsoid(name, loc, r, scale, m, cut=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=48, ring_count=32, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(m)
    bpy.ops.object.transform_apply(scale=True)
    if cut is not None:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0, 0, cut), plane_no=(0, 0, 1), clear_inner=True, use_fill=True)
        bpy.ops.object.mode_set(mode='OBJECT')
    return smooth(ob)


def lock(name, pts, radii, m, bevel):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    cu.fill_mode = 'FULL'
    sp = cu.splines.new('NURBS')
    sp.points.add(len(pts) - 1)
    for i, (p, r) in enumerate(zip(pts, radii)):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
        sp.points[i].radius = r
    sp.order_u = 4
    sp.use_endpoint_u = True
    sp.resolution_u = 12
    ob = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    return smooth(bpy.context.object)


made = []
made.append(ellipsoid('P_HairCap', (0, 3.0, 78.0), 15.2, (1.06, 0.98, 1.12), HAIR, cut=54.0))

# ---- 刘海 9 束：短、斜扫、参差 ----
for i in range(9):
    x0 = -22 + i * 5.5
    side = 1 if x0 >= 0 else -1
    tip_z = 83.5 + random.uniform(-1.6, 2.2)
    made.append(lock(f'P_Bang_{i}',
                     [(x0, -10.5, 95.5),
                      (x0 * 1.05 + side * 1.2, -14.2, 90.0),
                      (x0 * 1.12 + side * 2.4, -14.8, 86.5),
                      (x0 * 1.16 + side * 3.2, -13.2, tip_z)],
                     [0.85, 1.0, 0.9, 0.22], HAIR, bevel=2.1))

# ---- 侧发：每侧 6 束（含 2 束外层轮廓） ----
for s in (-1, 1):
    for k in range(4):
        x0 = 13 + k * 4.2
        z_end = 47 + k * 3 + random.uniform(-2, 2)
        bulge = 1.30 + 0.05 * k
        made.append(lock(f'P_Side_{s}_{k}',
                         [(s * x0, -8 + k * 3, 94),
                          (s * x0 * bulge, -5 + k * 4, 84),
                          (s * x0 * (bulge + 0.08), 0 + k * 4, 70),
                          (s * x0 * (bulge - 0.05), 3 + k * 3, 58),
                          (s * x0 * (bulge - 0.22), 4 + k * 3, z_end)],
                         [0.9, 1.05, 1.0, 0.75, 0.2], HAIR, bevel=2.3))
    # 外层轮廓束：更粗，位置在外侧，制造 50 mm+ 的宽度
    for k, (zz, xx) in enumerate(((86, 23.5), (74, 26.5), (62, 26.0))):
        made.append(lock(f'P_Outer_{s}_{k}',
                         [(s * (xx - 3), -4 + k * 4, zz + 8),
                          (s * xx, -2 + k * 5, zz + 2),
                          (s * (xx + 1.0), 1 + k * 5, zz - 4),
                          (s * (xx - 2.5), 3 + k * 5, zz - 12)],
                         [1.0, 1.15, 1.0, 0.25], HAIR, bevel=2.8))

# ---- 后发 12 束 ----
for i in range(12):
    x0 = -22 + i * 4.0
    z_end = 44 + random.uniform(-3, 4)
    made.append(lock(f'P_Back_{i}',
                     [(x0 * 0.92, 9, 94),
                      (x0 * 1.10, 15, 82),
                      (x0 * 1.16, 17, 66),
                      (x0 * 1.08, 16, 54),
                      (x0 * 0.98, 15, z_end)],
                     [0.95, 1.1, 1.0, 0.7, 0.2], HAIR, bevel=2.5))

bpy.ops.object.select_all(action='DESELECT')
for ob in made:
    ob.select_set(True)
bpy.context.view_layer.objects.active = made[0]
bpy.ops.object.join()
hair = bpy.context.view_layer.objects.active
hair.name = 'P_Hair'
hair.data.name = 'Hair'

cam = bpy.data.objects['CAM']
scene.render.resolution_x = 700
scene.render.resolution_y = 1300


def shoot(name, pos, target=(0, 0, 60)):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


shoot('hair3-front', (0, -300, 60))
shoot('hair3-34', (200, -220, 90))
shoot('hair3-side', (300, 0, 60))
shoot('hair3-back', (0, 300, 60))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step09_hair3.blend'))
print('SAVED', len(hair.data.polygons))
