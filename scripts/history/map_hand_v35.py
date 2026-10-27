import bpy, json
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()

xs = [0.017 + i * 0.001 for i in range(17)]   # 17..33 mm
zs = [0.049 + i * 0.001 for i in range(15)]   # 49..63 mm
print('     ' + ' '.join(f'{x*1000:4.0f}' for x in xs))
for z in zs:
    row = []
    for x in xs:
        h, loc, n, _i, _o, _m = scene.ray_cast(deps, Vector((x, -0.15, z)), Vector((0, 1, 0)), distance=0.3)
        row.append(f'{loc.y*1000:4.1f}' if h else '   -')
    print(f'{z*1000:4.0f} ' + ' '.join(row))
