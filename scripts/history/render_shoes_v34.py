import bpy, math, os
from mathutils import Vector

BLEND = r'D:\Desktop\鐩稿唽\浜岀淮IP鍒朵綔_20261012\鎵嬪姙璁捐\3D閲嶅缓_v6鍩虹_鑳屽寘闉嬮暅妗嗛噸寤篲v34_20261025\灏忕Е_v6鑳屽寘闉嬮暅妗嗛噸寤?blend'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34\shoes'
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 96
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'

world = scene.world or bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.10, 0.10, 0.11, 1)
    bg.inputs[1].default_value = 1.0

# 娓呮帀鏃х伅锛岄噸寤轰笁鐐瑰厜
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
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area('Key', (0.18, -0.16, 0.22), 6.5, 0.12)
add_area('Fill', (-0.16, -0.10, 0.12), 3.2, 0.14)
add_area('Rim', (0.0, 0.18, 0.18), 4.5, 0.12)

cam_data = bpy.data.cameras.new('CMP')
cam_data.lens = 85
cam = bpy.data.objects.new('CMP', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def shoot(name, pos, target, lens=85):
    cam.data.lens = lens
    cam.location = pos
    d = Vector(target) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


T = (0, 0.001, 0.0148)
shoot('r1-side', (0.20, 0.004, 0.020), T)
shoot('r1-front', (0.0, -0.20, 0.018), T)
shoot('r1-34', (0.13, -0.13, 0.055), T)
shoot('r1-side-close', (0.115, 0.001, 0.019), (-0.0060, -0.001, 0.0148), lens=85)
shoot('r1-front-close', (0.0, -0.115, 0.017), (0.0, 0.0, 0.0148), lens=85)
shoot('r1-back', (0.0, 0.20, 0.020), (0, 0.001, 0.0148))
print('DONE')




