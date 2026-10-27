import bpy, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025'
BLEND = os.path.join(V35, '小秦_v6鞋履收敛.blend')
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene

X0, X1 = 19.0, 27.5
Y0, Y1 = -6.0, 2.0
Z0, Z1 = 50.0, 59.0
cx = (X0 + X1) / 2000.0
cy = (Y0 + Y1) / 2000.0
cz = (Z0 + Z1) / 2000.0
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
box = bpy.context.object
box.scale = ((X1 - X0) / 1000.0, (Y1 - Y0) / 1000.0, (Z1 - Z0) / 1000.0)
bpy.ops.object.transform_apply(scale=True)
box.display_type = 'WIRE'
m = bpy.data.materials.new('BoxRed')
m.use_nodes = True
bsdf = m.node_tree.nodes['Principled BSDF']
bsdf.inputs['Emission Color'].default_value = (1, 0, 0, 1)
bsdf.inputs['Emission Strength'].default_value = 5
box.data.materials.append(m)

world = bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.25, 0.27, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.2


def add_area(name, loc, energy, size, target=(0.0, 0.0, 0.06)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ob = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area('Key', (0.16, -0.18, 0.24), 900, 0.12)
add_area('Fill', (-0.17, -0.13, 0.10), 300, 0.16)

cam_data = bpy.data.cameras.new('CAM')
cam_data.clip_start = 0.001
cam_data.clip_end = 10.0
cam = bpy.data.objects.new('CAM', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (0.030, 0.068, 0.065)
cam.rotation_euler = (Vector((0.024, 0.066, 0.018)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.view_settings.view_transform = 'Standard'
scene.render.filepath = os.path.join(OUT, 'hand-box-check.png')
bpy.ops.render.render(write_still=True)
print('RENDER_DONE')
