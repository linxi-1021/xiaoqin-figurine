import bpy, os
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_背包鞋镜框重建_v34_20261025\小秦_v6背包鞋镜框重建.blend'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34\shoes'
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.eevee.taa_render_samples = 128
scene.view_settings.view_transform = 'Standard'
scene.view_settings.exposure = -1.15

world = scene.world or bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.09, 0.09, 0.10, 1)

for o in list(scene.objects):
    if o.type == 'LIGHT':
        bpy.data.objects.remove(o, do_unlink=True)


def add_area(name, loc, energy, size, target=(0, 0, 0.015)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ob = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area('Key', (0.16, -0.15, 0.20), 9.0, 0.10)
add_area('Fill', (-0.15, -0.09, 0.10), 4.0, 0.14)
add_area('Rim', (0.0, 0.16, 0.16), 5.0, 0.10)

cam_data = bpy.data.cameras.new('CMP')
cam = bpy.data.objects.new('CMP', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def shoot(name, pos, target, lens=85):
    cam.data.lens = lens
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


T = (0, 0, 0.0146)
shoot('r2-side', (0.20, 0.002, 0.020), T)
shoot('r2-front', (0.0, -0.20, 0.018), T)
shoot('r2-34', (0.13, -0.13, 0.050), T)
shoot('r2-side-close', (0.115, 0.001, 0.018), (-0.0058, 0.0, 0.0146), lens=85)
shoot('r2-front-close', (0.0, -0.115, 0.017), (0.0, 0.0, 0.0146), lens=85)
shoot('r2-below', (0.06, -0.06, -0.02), (0, 0, 0.012))
print('DONE')
