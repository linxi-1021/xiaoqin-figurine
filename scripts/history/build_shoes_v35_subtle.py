import bpy, bmesh, math
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
me = body.data
mw = body.matrix_world

# 只在鞋面上做两条很浅的搭带起伏：不加深、不改鞋底、不加扣
BANDS = (-0.0016, 0.0017)
HALF = 0.00170
RISE = 0.00038
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.context.view_layer.objects.active = body
bm = bmesh.new()
bm.from_mesh(me)
bm.normal_update()
moved = 0
for v in bm.verts:
    co = mw @ v.co
    if not (0.0142 <= co.z <= 0.0198 and abs(co.x) < 0.016 and -0.016 < co.y < 0.016):
        continue
    zf = min(1.0, max(0.0, (co.z - 0.0142) / 0.0016))
    for y0 in BANDS:
        d = abs(co.y - y0)
        if d >= HALF:
            continue
        t = d / HALF
        w = 0.5 * (1 + math.cos(math.pi * t))
        v.co = v.co + v.normal * (RISE * w * zf)
        moved += 1
print('MOVED', moved)
bm.to_mesh(me)
bm.free()
me.update()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED')
