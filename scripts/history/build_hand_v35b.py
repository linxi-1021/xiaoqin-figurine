import bpy, bmesh, math, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025'
BLEND = os.path.join(V35, '小秦_v6鞋履收敛.blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world

bm = bmesh.new()
bm.from_mesh(me)
bm.normal_update()

X0, X1 = 0.0180, 0.0330
Z0, Z1 = 0.0530, 0.0630
Y0, Y1 = -0.012, 0.014

GAPS = (0.0229, 0.0255, 0.0281)
GROOVE_HALF = 0.00070
GROOVE_DEPTH = 0.00045
Z_FINGER = 0.0555
STRETCH = 0.08
moved = 0
for v in bm.verts:
    p = mw @ v.co
    if not (X0 < p.x < X1 and Z0 < p.z < Z1 and Y0 < p.y < Y1):
        continue
    # 只处理朝前的面，避免前后壳互穿
    n = (mw.to_3x3() @ v.normal).normalized()
    if n.y > -0.25:
        continue
    d = Vector((0, 0, 0))
    if p.z > Z_FINGER:
        d.z += (p.z - Z_FINGER) * STRETCH
    for gx in GAPS:
        dg = abs(p.x - gx)
        if dg < GROOVE_HALF:
            t = dg / GROOVE_HALF
            w = 0.5 * (1 + math.cos(math.pi * t))
            hz = min(1.0, max(0.0, (p.z - Z_FINGER) / 0.0030))
            d.y += GROOVE_DEPTH * w * hz
    v.co = v.co + d
    moved += 1
print('MOVED', moved)
bm.to_mesh(me)
bm.free()
me.update()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')
