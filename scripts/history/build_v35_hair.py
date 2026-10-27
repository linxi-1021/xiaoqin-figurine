import bpy, math, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'
BLEND = os.path.join(V35, 'steps', 'step06_blockout.blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene

# 删除占位头发
for n in ('P_HairBack', 'P_HairSide_L', 'P_HairSide_R'):
    ob = bpy.data.objects.get(n)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)

HAIR = bpy.data.materials['Hair']
Z_BRIM = 96.0


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


def lock(name, pts, radii, m, bevel=2.0):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 10
    cu.bevel_depth = bevel
    cu.bevel_resolution = 4
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
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return smooth(bpy.context.object)


made = []

# 发帽壳体（不露头皮）
cap = ellipsoid('P_HairCap', (0, 4.0, 79.0), 16.5, (1.02, 0.92, 1.12), HAIR, cut=55.0)
made.append(cap)

# 刘海（5 束，从帽檐下沿垂到眉上）
for i, x in enumerate((-14, -7, 0, 7, 14)):
    made.append(lock(f'P_Bang_{i}',
                     [(x, -11.5, 95), (x * 1.06, -14.5, 88), (x * 1.12, -15.2, 82), (x * 1.2, -13.5, 78.5)],
                     [1.35, 1.5, 1.1, 0.25], HAIR, bevel=2.4))

# 侧发（每侧 3 束）
for s in (-1, 1):
    made.append(lock(f'P_SideA_{s}',
                     [(s * 16, -6, 94), (s * 24, -3, 82), (s * 27, 0, 66), (s * 24, 2, 50), (s * 20.5, 3.5, 43)],
                     [1.8, 2.0, 1.7, 1.0, 0.2], HAIR, bevel=2.8))
    made.append(lock(f'P_SideB_{s}',
                     [(s * 19, 3, 92), (s * 26, 7, 77), (s * 25, 11, 60), (s * 21, 13, 46)],
                     [1.7, 1.9, 1.3, 0.25], HAIR, bevel=2.6))
    made.append(lock(f'P_SideC_{s}',
                     [(s * 11, -10, 92), (s * 17, -11, 83), (s * 20, -7, 71), (s * 19, -3, 58)],
                     [1.3, 1.5, 1.1, 0.25], HAIR, bevel=2.2))

# 后发（6 束）
for i, x in enumerate((-18, -11, -4, 4, 11, 18)):
    made.append(lock(f'P_Back_{i}',
                     [(x, 8, 94), (x * 1.1, 14, 80), (x * 1.14, 16, 62), (x * 1.05, 15, 46)],
                     [1.7, 1.9, 1.5, 0.3], HAIR, bevel=3.0))

# 合并为一个头发对象（保留分件信息在名字里）
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


shoot('hair-front', (0, -300, 60))
shoot('hair-side', (300, 0, 60))
shoot('hair-back', (0, 300, 60))
shoot('hair-34', (200, -220, 90))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step07_hair.blend'))
print('SAVED', len(hair.data.polygons))
