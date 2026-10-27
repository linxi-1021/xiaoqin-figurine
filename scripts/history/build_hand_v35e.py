import bpy, bmesh, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025'
BLEND = os.path.join(V35, '小秦_v6鞋履收敛.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world

# 已验证的删除框（Blender 坐标 mm）
BX0, BX1 = 11.0, 19.0
BY0, BY1 = -3.0, 5.0
BZ0, BZ1 = 59.5, 67.0

bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
deleting = []
for f in bm.faces:
    c = mw @ f.calc_center_median()
    if BX0 / 1000 < c.x < BX1 / 1000 and BY0 / 1000 < c.y < BY1 / 1000 and BZ0 / 1000 < c.z < BZ1 / 1000:
        deleting.append(f)
print('DELETE', len(deleting))
bmesh.ops.delete(bm, geom=deleting, context='FACES')
bm.to_mesh(me)
bm.free()
me.update()

skin = bpy.data.materials.get('Skin hand rebuild')
if not skin:
    skin = bpy.data.materials.new('Skin hand rebuild')
    skin.use_nodes = True
    b = skin.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.97, 0.80, 0.71, 1)
    b.inputs['Roughness'].default_value = 0.5


def mm(v):
    return v / 1000.0


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def blob(name, loc, r, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=mm(r), segments=32, ring_count=20,
                                        location=(mm(loc[0]), mm(loc[1]), mm(loc[2])))
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(skin)
    bpy.ops.object.transform_apply(scale=True)
    return smooth(ob)


def capsule(name, a, b, r1, r2):
    p1 = Vector((mm(a[0]), mm(a[1]), mm(a[2])))
    p2 = Vector((mm(b[0]), mm(b[1]), mm(b[2])))
    d = p2 - p1
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=mm(r1), radius2=mm(r2),
                                    depth=d.length, location=(p1 + p2) / 2)
    ob = bpy.context.object
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    ob.data.materials.append(skin)
    bpy.ops.object.transform_apply(rotation=True)
    return smooth(ob)


parts = [
    blob('BackFill', (14.5, 3.2, 61.2), 1.0, (mm(3.4), mm(2.6), mm(3.6))),
    capsule('Wrist', (14.5, 1.0, 57.0), (14.5, 1.0, 61.0), 2.95, 2.75),
    blob('Palm', (14.5, 1.0, 62.0), 1.0, (mm(3.3), mm(2.10), mm(3.3))),
]
FINGERS = [
    ((12.5, 0.5, 63.6), (12.3, -0.1, 66.9), 0.60, 0.48),
    ((13.8, 0.5, 63.8), (13.7, -0.1, 67.5), 0.62, 0.50),
    ((15.1, 0.5, 63.8), (15.1, -0.1, 67.3), 0.60, 0.48),
    ((16.4, 0.5, 63.5), (16.6, -0.1, 66.4), 0.56, 0.45),
]
for i, (a, b2, r1, r2) in enumerate(FINGERS):
    parts.append(capsule(f'F{i}', a, b2, r1, r2))
parts.append(capsule('Thumb', (12.2, 0.3, 61.0), (10.8, -0.4, 63.0), 0.70, 0.54))

bpy.ops.object.select_all(action='DESELECT')
for ob in parts:
    ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
hand = bpy.context.view_layer.objects.active
hand.name = 'GEO-Hand wave'
hand.data.name = 'Hand wave'
m = hand.modifiers.new('s', 'SUBSURF')
m.levels = 1
bpy.ops.object.modifier_apply(modifier=m.name)
hand.data.remesh_voxel_size = mm(0.10)
bpy.context.view_layer.objects.active = hand
bpy.ops.object.voxel_remesh()
for p in hand.data.polygons:
    p.use_smooth = True
print('HAND_POLYS', len(hand.data.polygons))

parent = bpy.data.objects.get('Character_120mm')
if parent:
    hand.parent = parent
    hand.matrix_parent_inverse = parent.matrix_world.inverted()

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
glb = os.path.join(V35, '小秦_v6鞋履收敛.glb')
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
    if o.type == 'MESH':
        o.select_set(True)
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format='GLB')
print('DONE')
