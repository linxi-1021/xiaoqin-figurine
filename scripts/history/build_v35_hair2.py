import bpy, math, os
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
    sp.resolution_u = 10
    ob = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    return smooth(bpy.context.object)


made = []
# 发帽壳体：贴合头，不露头皮
made.append(ellipsoid('P_HairCap', (0, 3.5, 79.0), 14.6, (1.03, 0.95, 1.10), HAIR, cut=56.0))

# 刘海：7 束，短、斜扫，绕开额头中心
BANGS = [
    (-16, -10.5, 94, -20, -13.0, 88, -22, -12.0, 83.5, 1.05, 0.35),
    (-10, -11.5, 95, -13, -14.0, 89, -16, -13.0, 84.0, 1.00, 0.30),
    (-4, -12.0, 95, -5, -14.5, 89.5, -7, -13.5, 85.0, 0.95, 0.30),
    (2, -12.0, 95, 1, -14.5, 89.5, -1, -13.5, 85.0, 0.95, 0.30),
    (8, -11.5, 95, 11, -14.0, 89, 13, -13.0, 84.5, 1.00, 0.30),
    (14, -10.5, 94, 18, -13.0, 88.5, 21, -12.0, 84.0, 1.05, 0.35),
    (18, -8.5, 93, 22, -11.0, 87, 24, -10.0, 82.5, 1.00, 0.35),
]
for i, (x1, y1, z1, x2, y2, z2, x3, y3, z3, r1, r3) in enumerate(BANGS):
    made.append(lock(f'P_Bang_{i}',
                     [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3)],
                     [r1, 1.0, r3], HAIR, bevel=2.0))

# 侧发：每侧 4 束，S 弯垂到腰
for s in (-1, 1):
    made.append(lock(f'P_SideTemple_{s}',
                     [(s * 15, -9, 93), (s * 21, -7, 84), (s * 24, -2, 72), (s * 23, 2, 58)],
                     [0.9, 1.0, 0.95, 0.3], HAIR, bevel=2.2))
    made.append(lock(f'P_SideMid_{s}',
                     [(s * 18, 1, 92), (s * 25, 3, 80), (s * 26, 6, 64), (s * 22, 8, 48)],
                     [0.95, 1.05, 0.9, 0.28], HAIR, bevel=2.2))
    made.append(lock(f'P_SideBack_{s}',
                     [(s * 14, 8, 92), (s * 22, 12, 78), (s * 24, 14, 60), (s * 20, 14, 45)],
                     [0.9, 1.0, 0.85, 0.25], HAIR, bevel=2.0))
    made.append(lock(f'P_SideLow_{s}',
                     [(s * 20, -4, 84), (s * 26, 0, 70), (s * 25, 3, 56), (s * 21, 5, 44)],
                     [0.8, 0.95, 0.8, 0.22], HAIR, bevel=2.0))

# 后发：8 束
for i, x in enumerate((-20, -14, -8, -3, 3, 8, 14, 20)):
    made.append(lock(f'P_Back_{i}',
                     [(x * 0.9, 9, 93), (x * 1.12, 15, 78), (x * 1.16, 16, 60), (x * 1.05, 15, 44)],
                     [0.95, 1.05, 0.85, 0.25], HAIR, bevel=2.4))

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


def shoot(name, pos, target=(0, 0, 60), lens=None):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


shoot('hair2-front', (0, -300, 60))
shoot('hair2-34', (200, -220, 90))
shoot('hair2-side', (300, 0, 60))
shoot('hair2-back', (0, 300, 60))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step08_hair2.blend'))
print('SAVED', len(hair.data.polygons))
