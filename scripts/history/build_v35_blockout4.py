import bpy, bmesh, math, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(V35, 'steps'), exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

MATS = {}


def mat(name, color, rough=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    MATS[name] = m
    return m


CLAY = mat('Clay', (0.70, 0.68, 0.66), 0.7)
SKIN = mat('Skin', (0.95, 0.82, 0.72), 0.5)
HAIR = mat('Hair', (0.33, 0.20, 0.13), 0.4)
HAT = mat('Hat', (0.64, 0.48, 0.40), 0.85)
CREAM = mat('Cream', (0.94, 0.91, 0.85), 0.6)
PLAID = mat('Plaid', (0.42, 0.47, 0.58), 0.75)


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def sphere(name, loc, radius, scale=(1, 1, 1), m=CLAY):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=56, ring_count=36, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(m)
    bpy.ops.object.transform_apply(scale=True)
    return smooth(ob)


def capsule(name, p1, p2, r1, r2=None, m=CLAY):
    p1, p2 = Vector(p1), Vector(p2)
    r2 = r1 if r2 is None else r2
    d = p2 - p1
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r1, radius2=r2, depth=d.length, location=(p1 + p2) / 2)
    ob = bpy.context.object
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    ob.data.materials.append(m)
    bpy.ops.object.transform_apply(rotation=True)
    a = sphere(name + '_a', p1, r1, m=m)
    b = sphere(name + '_b', p2, r2, m=m)
    bpy.ops.object.select_all(action='DESELECT')
    for o in (ob, a, b):
        o.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.join()
    ob.name = name
    return ob


def cyl(name, loc, r, h, m=CLAY, bevel=0.8, verts=72, scale=(1, 1, 1), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.rotation_euler = rot
    ob.data.materials.append(m)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    if bevel > 0:
        bm = ob.modifiers.new('bev', 'BEVEL')
        bm.width = bevel
        bm.segments = 4
        bpy.ops.object.modifier_apply(modifier=bm.name)
    return smooth(ob)


def cut_below(ob, z, fill=True):
    """把对象在 z 平面以下切掉"""
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, z), plane_no=(0, 0, 1), clear_inner=True, use_fill=fill)
    bpy.ops.object.mode_set(mode='OBJECT')


# ---------------- 比例基准（mm） ----------------
Z_TOP = 120.0
Z_BRIM = 96.0
Z_CHIN = 66.0
Z_SHOULDER = 63.0
Z_WAIST = 47.0
Z_HEM = 34.0
Z_SHOE_TOP = 16.0
Z_BASE = 6.0

parts = []
parts.append(cyl('P_Base', (0, 0, Z_BASE / 2), 24.5, Z_BASE, CREAM, bevel=0.9))

for sx in (-5.8, 5.8):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, -1.2, Z_BASE + 5.2))
    shoe = bpy.context.object
    shoe.name = f'P_Shoe_{"L" if sx < 0 else "R"}'
    shoe.scale = (10.4, 20.0, 10.4)
    bpy.ops.object.transform_apply(scale=True)
    bv = shoe.modifiers.new('b', 'BEVEL')
    bv.width = 3.6
    bv.segments = 5
    shoe.data.materials.append(CREAM)
    bpy.ops.object.modifier_apply(modifier=bv.name)
    parts.append(smooth(shoe))

for sx in (-5.6, 5.6):
    parts.append(capsule(f'P_Leg_{"L" if sx < 0 else "R"}', (sx, 0, Z_SHOE_TOP - 2), (sx, 0, Z_WAIST - 2), 4.7, 5.2, SKIN))

bpy.ops.mesh.primitive_cone_add(vertices=72, radius1=15.6, radius2=10.8,
                                depth=Z_WAIST - Z_HEM, location=(0, 0.5, (Z_WAIST + Z_HEM) / 2))
skirt = bpy.context.object
skirt.name = 'P_Skirt'
skirt.data.materials.append(PLAID)
parts.append(smooth(skirt))

parts.append(capsule('P_Torso', (0, 0.5, Z_WAIST), (0, 0.5, Z_SHOULDER), 10.6, 11.6, CREAM))
parts.append(capsule('P_Neck', (0, 0.5, Z_SHOULDER - 3), (0, 0.5, Z_CHIN - 1), 4.6, 4.4, SKIN))

# 头：脸高 30 mm（66→96），宽 22
head = sphere('P_Head', (0, 0.6, 81.0), 11.0, (1.0, 0.98, 1.36), SKIN)
parts.append(head)

parts.append(capsule('P_ArmWave', (12.6, 0.5, Z_SHOULDER - 1), (20.5, -4.0, 60.0), 4.5, 3.9, CREAM))
parts.append(capsule('P_ArmDown', (-12.6, 0.5, Z_SHOULDER - 1), (-14.8, -3.0, Z_WAIST - 1), 4.5, 3.8, CREAM))
parts.append(sphere('P_HandWave', (21.6, -5.0, 61.5), 4.7, (1.0, 0.62, 1.15), SKIN))
parts.append(sphere('P_HandDown', (-15.4, -4.0, Z_WAIST - 4), 4.4, (1.0, 0.7, 1.1), SKIN))

# 熊帽：半球（切平底在帽檐线）
hat = sphere('P_HatShell', (0, 0.5, Z_BRIM), 24.5, (1.0, 0.80, 0.98), HAT)
cut_below(hat, Z_BRIM - 0.001)
parts.append(hat)
parts.append(sphere('P_Ear_L', (-19.8, 2.0, Z_TOP - 7.0), 7.6, (1.0, 0.70, 1.0), HAT))
parts.append(sphere('P_Ear_R', (19.8, 2.0, Z_TOP - 7.0), 7.6, (1.0, 0.70, 1.0), HAT))

# 帽檐：压扁球壳切出前伸弧形板（贴合头型）
brim = sphere('P_Brim', (0, 1.0, Z_BRIM + 0.4), 26.0, (1.0, 0.95, 0.055), CREAM)
bpy.context.view_layer.objects.active = brim
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(0, 2.0, 0), plane_no=(0, -1, 0), clear_inner=True, use_fill=True)
bpy.ops.object.mode_set(mode='OBJECT')
brim.rotation_euler = (math.radians(-8), 0, 0)
bpy.ops.object.transform_apply(rotation=True)
parts.append(smooth(brim))

# 头发：后发大束 + 两侧发量（轮廓关键）
hair = sphere('P_HairBack', (0, 9.0, 72.0), 23.0, (1.0, 0.62, 1.30), HAIR)
cut_below(hair, 38.0)
parts.append(hair)
parts.append(sphere('P_HairSide_L', (-20.0, 3.0, 70.0), 12.5, (0.62, 0.95, 1.65), HAIR))
parts.append(sphere('P_HairSide_R', (20.0, 3.0, 70.0), 12.5, (0.62, 0.95, 1.65), HAIR))

# 后发：从下巴到肩膀，包住后脑
hair = sphere('P_HairBack', (0, 7.5, 80.0), 16.0, (1.0, 0.72, 1.35), HAIR)
cut_below(hair, Z_CHIN - 1)
parts.append(hair)

world = bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.42, 0.42, 0.44, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.55


def add_area(name, loc, energy, size, target=(0, 0, 62)):
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
cam_data.ortho_scale = 140
cam = bpy.data.objects.new('CAM', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 700
scene.render.resolution_y = 1300
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 32
scene.view_settings.view_transform = 'Standard'


def shoot(name, pos, target=(0, 0, 61)):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


shoot('bo4-front', (0, -300, 61))
shoot('bo4-side', (300, 0, 61))
shoot('bo4-back', (0, 300, 61))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step04_blockout.blend'))
print('SAVED')
