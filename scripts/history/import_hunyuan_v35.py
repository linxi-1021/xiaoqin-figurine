import bpy, glob, os, json
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'
GEN = os.path.join(V35, 'generated')

glbs = sorted(glob.glob(os.path.join(GEN, '**', '*.glb'), recursive=True), key=os.path.getmtime)
if not glbs:
    raise SystemExit('NO_GLB_FOUND')
glb = glbs[-1]
print('IMPORT', glb)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not objs:
    raise SystemExit('NO_MESH')

# 计算世界包围盒
mn = Vector((1e9, 1e9, 1e9))
mx = Vector((-1e9, -1e9, -1e9))
for o in objs:
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], p[i])
            mx[i] = max(mx[i], p[i])
size = mx - mn
print('RAW_BBOX', [round(v, 4) for v in size])

scale = 120.0 / size.z
for o in objs:
    o.scale = (o.scale.x * scale, o.scale.y * scale, o.scale.z * scale)
    o.location = (o.location.x * scale, o.location.y * scale, o.location.z * scale)
bpy.context.view_layer.update()

# 重新计算并归位：底面 z=0，中心 x=y=0
mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
for o in objs:
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], p[i]); mx[i] = max(mx[i], p[i])
cx = (mn.x + mx.x) / 2
cy = (mn.y + mx.y) / 2
for o in objs:
    o.location.x -= cx
    o.location.y -= cy
    o.location.z -= mn.z
bpy.context.view_layer.update()
print('FINAL_BBOX', [round(v, 3) for v in (mx - mn)], 'at z0')

# 材质：保留原贴图；补一盏灯与相机
scene = bpy.context.scene
world = bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.45, 0.45, 0.47, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.7


def add_area(name, loc, energy, size, target=(0, 0, 60)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ob = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area('Key', (160, -180, 240), 1200000, 140)
add_area('Fill', (-170, -130, 100), 420000, 160)
add_area('Rim', (0, 210, 190), 600000, 130)

cam_data = bpy.data.cameras.new('CAM')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 127.6
cam = bpy.data.objects.new('CAM', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 700
scene.render.resolution_y = 1300
scene.eevee.taa_render_samples = 48
scene.view_settings.view_transform = 'Standard'


def shoot(name, pos, target=(0, 0, 60)):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


shoot('gen-front', (0, -300, 60))
shoot('gen-side', (300, 0, 60))
shoot('gen-back', (0, 300, 60))
shoot('gen-34', (200, -220, 90))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step10_generated.blend'))
print('SAVED')
