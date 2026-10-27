import bpy, bmesh, math, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025'
BLEND = os.path.join(V35, '小秦_v6鞋履收敛.blend')
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world

# ---- 1) 删除旧手（袖口以上） ----
bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
deleting = []
for f in bm.faces:
    c = mw @ f.calc_center_median()
    if 0.0190 < c.x < 0.0285 and 0.0502 < c.z < 0.0590 and -0.008 < c.y < 0.006:
        deleting.append(f)
print('DELETE_HAND_FACES', len(deleting))
bmesh.ops.delete(bm, geom=deleting, context='FACES')
bm.to_mesh(me)
bm.free()
me.update()

# ---- 2) 材质 ----
skin = bpy.data.materials.get('Skin hand rebuild')
if not skin:
    skin = bpy.data.materials.new('Skin hand rebuild')
    skin.use_nodes = True
    b = skin.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.98, 0.80, 0.72, 1)
    b.inputs['Roughness'].default_value = 0.48


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def blob(name, loc, r, scale, m=skin):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=32, ring_count=20, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(m)
    bpy.ops.object.transform_apply(scale=True)
    return smooth(ob)


def finger(name, p1, p2, r1, r2, m=skin):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2, depth=d.length,
                                    location=(p1 + p2) / 2)
    ob = bpy.context.object
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    ob.data.materials.append(m)
    bpy.ops.object.transform_apply(rotation=True)
    return smooth(ob)


parts = []
# 手掌：扁椭球
parts.append(blob('Palm', (0.0234, -0.0008, 0.0530), 1.0, (0.00260, 0.00145, 0.00270)))
# 四指（画面从左到右 = 食指→小指），略呈扇形，长短不一
FINGERS = [
    ((0.0214, -0.0012, 0.0546), (0.0210, -0.0022, 0.0593), 0.00062, 0.00052),
    ((0.0229, -0.0012, 0.0550), (0.0227, -0.0022, 0.0602), 0.00064, 0.00054),
    ((0.0244, -0.0011, 0.0550), (0.0244, -0.0021, 0.0600), 0.00062, 0.00052),
    ((0.0259, -0.0010, 0.0546), (0.0262, -0.0020, 0.0588), 0.00058, 0.00048),
]
for i, (a, b, r1, r2) in enumerate(FINGERS):
    parts.append(finger(f'Finger{i}', a, b, r1, r2))
# 拇指：从掌左侧伸出，略朝前下
parts.append(finger('Thumb', (0.0212, -0.0018, 0.0522), (0.0196, -0.0032, 0.0552), 0.00072, 0.00058))

bpy.ops.object.select_all(action='DESELECT')
for ob in parts:
    ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
hand = bpy.context.view_layer.objects.active
hand.name = 'GEO-Rebuilt hand wave'
hand.data.name = 'Rebuilt hand wave'
m = hand.modifiers.new('smooth', 'SUBSURF')
m.levels = 1
bpy.ops.object.modifier_apply(modifier=m.name)
print('HAND_POLYS', len(hand.data.polygons))

# 轻微融合：用 voxel remesh 把手指与掌连成一体（保留指缝）
hand.data.remesh_voxel_size = 0.00018
bpy.context.view_layer.objects.active = hand
bpy.ops.object.voxel_remesh()
for p in hand.data.polygons:
    p.use_smooth = True
print('AFTER_REMESH_POLYS', len(hand.data.polygons))

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
print('SAVED_EXPORTED')
