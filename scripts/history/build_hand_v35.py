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

bm = bmesh.new()
bm.from_mesh(me)
bm.normal_update()

# 手部工作区（世界坐标 mm → m）
X0, X1 = 0.0175, 0.0335
Z0, Z1 = 0.0525, 0.0635
Y0, Y1 = -0.012, 0.014

GAPS = (0.0227, 0.0254, 0.0281)   # 四指之间
GROOVE_HALF = 0.00075
GROOVE_DEPTH = 0.00095
Z_FINGER = 0.0550                 # 手指起点
STRETCH = 0.14                    # 手指拉长比例

n_groove = n_stretch = 0
for v in bm.verts:
    p = mw @ v.co
    if not (X0 < p.x < X1 and Z0 < p.z < Z1 and Y0 < p.y < Y1):
        continue
    d = Vector((0, 0, 0))
    # 1) 手指拉长（越高拉得越多）
    if p.z > Z_FINGER:
        d.z += (p.z - Z_FINGER) * STRETCH
        n_stretch += 1
    # 2) 指缝：沿法线向内压出 V 形槽
    for gx in GAPS:
        dg = abs(p.x - gx)
        if dg < GROOVE_HALF:
            t = dg / GROOVE_HALF
            w = 0.5 * (1 + math.cos(math.pi * t))
            # 只在手指段生效，越靠近指尖越深
            hz = min(1.0, max(0.0, (p.z - Z_FINGER) / 0.0035))
            d -= v.normal * (GROOVE_DEPTH * w * hz)
            n_groove += 1
    v.co = v.co + d

print('groove_verts', n_groove, 'stretch_verts', n_stretch)
bm.to_mesh(me)
bm.free()
me.update()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')

# 导出 glb
glb = os.path.join(V35, '小秦_v6鞋履收敛.glb')
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
    if o.type == 'MESH':
        o.select_set(True)
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format='GLB')
print('EXPORTED', glb)
