import bpy, math, os
from mathutils import Vector

# 单位：1 Blender 单位 = 1 mm
V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025'
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(V35, 'steps'), exist_ok=True)

# 清空场景
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

MAT = {}


def mat(name, color, rough=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    MAT[name] = m
    return m


CLAY = mat('Clay gray', (0.72, 0.71, 0.70), 0.65)
SKIN = mat('Skin', (0.94, 0.80, 0.70), 0.55)
HAIR = mat('Hair', (0.35, 0.22, 0.15), 0.45)
HAT = mat('Hat', (0.62, 0.46, 0.38), 0.8)
CREAM = mat('Cream', (0.93, 0.90, 0.84), 0.6)
PLAID = mat('Plaid', (0.45, 0.50, 0.60), 0.7)


def sphere(name, loc, radius, scale=(1, 1, 1), mat=CLAY, seg=48, ring=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=seg, ring_count=ring, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    bpy.ops.object.transform_apply(scale=True)
    return ob


def capsule(name, p1, p2, r1, r2=None, mat=CLAY):
    """两球 + 圆柱的简单胶囊"""
    p1, p2 = Vector(p1), Vector(p2)
    r2 = r1 if r2 is None else r2
    d = p2 - p1
    L = d.length
    mid = (p1 + p2) / 2
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r1, radius2=r2, depth=L, location=mid)
    ob = bpy.context.object
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    ob.data.materials.append(mat)
    bpy.ops.object.transform_apply(rotation=True)
    parts = [ob]
    parts.append(sphere(name + '_a', p1, r1, mat=mat))
    parts.append(sphere(name + '_b', p2, r2, mat=mat))
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    parts[0].name = name
    return parts[0]


def cyl(name, loc, r, h, verts=64, mat=CLAY, bevel=0.6):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    if bevel > 0:
        b = ob.modifiers.new('bev', 'BEVEL')
        b.width = bevel
        b.segments = 3
        bpy.ops.object.modifier_apply(modifier=b.name)
    return ob


def shade(ob):
    for p in ob.data.polygons:
        p.use_smooth = True


# ---------------- 比例基准（mm，底座底 = 0） ----------------
Z_BASE = 6            # 底座厚
Z_SOLE = Z_BASE       # 鞋底
Z_SHOE_TOP = 16
Z_KNEE = 22
Z_HEM = 30
Z_WAIST = 43
Z_SHOULDER = 59
Z_CHIN = 65
Z_EYE = 76
Z_BRIM = 95
Z_TOP = 120

parts = []
# 底座
base = cyl('P_Base', (0, 0, Z_BASE / 2), 24.5, Z_BASE, bevel=0.8, mat=CREAM)
parts.append(base)

# 鞋（两团）
for sx in (-6.0, 6.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, -1.0, Z_SOLE + 5.0))
    shoe = bpy.context.object
    shoe.name = f'P_Shoe_{"L" if sx < 0 else "R"}'
    shoe.scale = (10.0, 19.0, 10.0)
    bpy.ops.object.transform_apply(scale=True)
    b = shoe.modifiers.new('bev', 'BEVEL')
    b.width = 3.4
    b.segments = 4
    shoe.data.materials.append(CREAM)
    bpy.ops.object.modifier_apply(modifier=b.name)
    parts.append(shoe)

# 腿
for sx in (-5.4, 5.4):
    parts.append(capsule(f'P_Leg_{"L" if sx < 0 else "R"}', (sx, 0, Z_SHOE_TOP - 1), (sx, 0, Z_WAIST - 4), 4.6, 5.0, SKIN))

# 裙（圆台）
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=15.5, radius2=10.5, depth=Z_WAIST - Z_HEM,
                                location=(0, 0, (Z_WAIST + Z_HEM) / 2))
skirt = bpy.context.object
skirt.name = 'P_Skirt'
skirt.data.materials.append(PLAID)
parts.append(skirt)

# 躯干（从腰到肩）
parts.append(capsule('P_Torso', (0, 0, Z_WAIST), (0, 0, Z_SHOULDER), 10.5, 11.5, CREAM))
# 颈
parts.append(capsule('P_Neck', (0, 0, Z_SHOULDER - 2), (0, 0, Z_CHIN - 2), 4.6, 4.4, SKIN))

# 头
head = sphere('P_Head', (0, 0, Z_CHIN + 17), 13.0, (1.0, 0.98, 1.16), SKIN)
parts.append(head)

# 手臂：左手挥手（画面右 = +X），右手下垂
parts.append(capsule('P_ArmWave', (12.0, 0, Z_SHOULDER - 1), (20.0, -6, Z_SHOULDER + 2), 4.4, 3.9, CREAM))
parts.append(capsule('P_ArmDown', (-12.0, 0, Z_SHOULDER - 1), (-14.5, -4, Z_WAIST - 2), 4.4, 3.8, CREAM))
# 手（示意球）
parts.append(sphere('P_HandWave', (21.0, -7.0, Z_SHOULDER + 4), 4.6, (1, 0.7, 1.1), SKIN))
parts.append(sphere('P_HandDown', (-15.0, -5.0, Z_WAIST - 4), 4.4, (1, 0.8, 1.1), SKIN))

# 熊帽（球壳裁半）
hat = sphere('P_HatShell', (0, 1.0, Z_BRIM + 12), 24.5, (1.0, 0.86, 0.66), HAT)
parts.append(hat)
# 熊耳（两个球）
parts.append(sphere('P_Ear_L', (-19.0, 2.0, Z_TOP - 4), 7.6, (1, 0.8, 1.05), HAT))
parts.append(sphere('P_Ear_R', (19.0, 2.0, Z_TOP - 4), 7.6, (1, 0.8, 1.05), HAT))
# 帽檐（压扁的圆盘，前伸）
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=17.0, depth=3.0, location=(0, -8.0, Z_BRIM - 3.0))
brim = bpy.context.object
brim.name = 'P_Brim'
brim.scale = (1.25, 1.0, 1.0)
brim.rotation_euler = (math.radians(-14), 0, 0)
brim.data.materials.append(CREAM)
bpy.ops.object.transform_apply(scale=True, rotation=True)
parts.append(brim)

# 头发（后发大体块）
parts.append(sphere('P_HairBack', (0, 6.0, Z_CHIN + 8), 20.0, (0.92, 0.70, 1.25), HAIR))

for p in parts:
    shade(p)

# ---------------- 相机与灯光 ----------------
world = bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.6


def add_area(name, loc, energy, size, target=(0, 0, 60)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ob = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area('Key', (150, -180, 220), 900000, 120)
add_area('Fill', (-160, -120, 90), 350000, 150)
add_area('Rim', (0, 200, 170), 500000, 120)

cam_data = bpy.data.cameras.new('CAM')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 150
cam = bpy.data.objects.new('CAM', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 720
scene.render.resolution_y = 1400
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 32
scene.view_settings.view_transform = 'Standard'
scene.view_settings.exposure = 0.0


def shoot(name, pos, target=(0, 0, 60)):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


shoot('blockout-front', (0, -300, 60))
shoot('blockout-side', (300, 0, 60))
shoot('blockout-back', (0, 300, 60))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step01_blockout.blend'))
print('SAVED')
