import bpy, math, os
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
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r1, radius2=r2, depth=d.length,
                                    location=(p1 + p2) / 2)
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


# ---------------- 比例基准（mm） ----------------
H = 114.0            # 人物高
Z_TOP = 120.0        # 帽顶（含耳顶）
Z_BRIM = 96.0        # 帽檐线
Z_EYE = 77.0
Z_CHIN = 66.0
Z_SHOULDER = 63.0
Z_WAIST = 47.0
Z_HEM = 34.0
Z_KNEE = 25.0
Z_SHOE_TOP = 16.0
Z_BASE = 6.0
HEAD_R = 11.0
HEAD_CZ = 83.0

parts = []
parts.append(cyl('P_Base', (0, 0, Z_BASE / 2), 24.5, Z_BASE, CREAM, bevel=0.9))

# 鞋
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

# 腿
for sx in (-5.6, 5.6):
    parts.append(capsule(f'P_Leg_{"L" if sx < 0 else "R"}', (sx, 0, Z_SHOE_TOP - 2), (sx, 0, Z_WAIST - 2), 4.7, 5.2, SKIN))

# 裙
bpy.ops.mesh.primitive_cone_add(vertices=72, radius1=15.6, radius2=10.8,
                                depth=Z_WAIST - Z_HEM, location=(0, 0.5, (Z_WAIST + Z_HEM) / 2))
skirt = bpy.context.object
skirt.name = 'P_Skirt'
skirt.data.materials.append(PLAID)
parts.append(smooth(skirt))

# 躯干 / 颈 / 头
parts.append(capsule('P_Torso', (0, 0.5, Z_WAIST), (0, 0.5, Z_SHOULDER), 10.6, 11.6, CREAM))
parts.append(capsule('P_Neck', (0, 0.5, Z_SHOULDER - 3), (0, 0.5, Z_CHIN - 2), 4.6, 4.4, SKIN))
parts.append(sphere('P_Head', (0, 0.5, HEAD_CZ), HEAD_R, (1.0, 0.96, 1.12), SKIN))

# 手臂：画面右 = +X 挥手；左侧下垂
parts.append(capsule('P_ArmWave', (12.6, 0.5, Z_SHOULDER - 1), (20.5, -4.0, 60.0), 4.5, 3.9, CREAM))
parts.append(capsule('P_ArmDown', (-12.6, 0.5, Z_SHOULDER - 1), (-14.8, -3.0, Z_WAIST - 1), 4.5, 3.8, CREAM))
parts.append(sphere('P_HandWave', (21.6, -5.0, 61.5), 4.7, (1.0, 0.62, 1.15), SKIN))
parts.append(sphere('P_HandDown', (-15.4, -4.0, Z_WAIST - 4), 4.4, (1.0, 0.7, 1.1), SKIN))

# 熊帽：半球壳（下沿到帽檐线）
hat = sphere('P_HatShell', (0, 1.5, Z_BRIM + 10.5), 24.6, (1.0, 0.74, 0.60), HAT)
parts.append(hat)
# 熊耳
parts.append(sphere('P_Ear_L', (-19.5, 2.5, Z_TOP - 6.5), 7.4, (1.0, 0.72, 1.0), HAT))
parts.append(sphere('P_Ear_R', (19.5, 2.5, Z_TOP - 6.5), 7.4, (1.0, 0.72, 1.0), HAT))
# 帽檐：前伸的薄板（压扁圆柱，前缘下压）
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=15.5, depth=2.6, location=(0, -11.0, Z_BRIM - 1.0))
brim = bpy.context.object
brim.name = 'P_Brim'
brim.scale = (1.35, 0.86, 1.0)
brim.rotation_euler = (math.radians(-10), 0, 0)
brim.data.materials.append(CREAM)
bpy.ops.object.transform_apply(scale=True, rotation=True)
parts.append(smooth(brim))

# 后发（限制在下巴以下到肩，不穿过躯干）
parts.append(sphere('P_HairBack', (0, 8.0, Z_CHIN - 2), 17.0, (1.0, 0.62, 1.35), HAIR))

# ---------------- 灯光 / 相机 ----------------
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
scene.eevee.taa_render_samples = 32
scene.view_settings.view_transform = 'Standard'


def shoot(name, pos, target=(0, 0, 61)):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)


shoot('bo2-front', (0, -300, 61))
shoot('bo2-side', (300, 0, 61))
shoot('bo2-back', (0, 300, 61))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V35, 'steps', 'step02_blockout.blend'))
print('SAVED')
