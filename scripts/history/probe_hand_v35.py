import bpy, bmesh, math, os
from mathutils import Vector

V35 = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025'
BLEND = os.path.join(V35, '小秦_v6鞋履收敛.blend')
OUT = r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35'

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
body = bpy.data.objects['textured_mesh.obj']
mw = body.matrix_world
deps = bpy.context.evaluated_depsgraph_get()

# 从正前方打一条射线，找挥手手掌表面
origin = Vector((0.0255, -0.120, 0.0575))
hit, loc, nor, idx, ob, mat = scene.ray_cast(deps, origin, Vector((0, 1, 0)), distance=0.2)
print('RAY_HIT', hit, [round(v, 4) for v in loc] if hit else None)
if not hit:
    raise SystemExit('NO_HIT')

anchor = loc.copy()
print('ANCHOR', [round(v, 4) for v in anchor])

# 采样手掌区域，估算手宽/手高
pts = []
for dx in [i * 0.0005 for i in range(-24, 25)]:
    for dz in [i * 0.0005 for i in range(-8, 26)]:
        o2 = Vector((anchor.x + dx, -0.12, anchor.z + dz))
        h, l, n, _i, _o, _m = scene.ray_cast(deps, o2, Vector((0, 1, 0)), distance=0.2)
        if h:
            pts.append((dx, dz, l.y))
print('SAMPLES', len(pts))
if pts:
    print('DX_RANGE', round(min(p[0] for p in pts) * 1000, 2), round(max(p[0] for p in pts) * 1000, 2))
    print('DZ_RANGE', round(min(p[1] for p in pts) * 1000, 2), round(max(p[1] for p in pts) * 1000, 2))
