import bpy, json
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()

# 手区域：x 19..33mm, z 49..63mm；从前方向 +y 打射线，记录表面 y
xs = [0.019 + i * 0.0004 for i in range(36)]
zs = [0.049 + i * 0.0004 for i in range(36)]
grid = []
for z in zs:
    row = []
    for x in xs:
        h, loc, n, _i, _o, _m = scene.ray_cast(deps, Vector((x, -0.12, z)), Vector((0, 1, 0)), distance=0.25)
        row.append(loc.y if h else None)
    grid.append(row)

# 以 mm 输出一个粗略的“深度图”，越深(越靠后)数值越大
print('    ' + ''.join(f'{int(round(x*1000))%10}' for x in xs))
for zi, z in enumerate(zs):
    if int(round(z * 10000)) % 4:
        continue
    line = ''
    for yi, y in enumerate(grid[zi]):
        if y is None:
            line += ' '
        else:
            line += str(int(round(y * 10000)) % 10)
    print(f'{z*1000:5.1f} {line}')

# 找每一行的局部“谷”（y 较大处＝手指之间的凹槽）
print('GAPS')
for zi, z in enumerate(zs):
    if not (0.054 <= z <= 0.062):
        continue
    row = grid[zi]
    for yi in range(1, len(row) - 1):
        a, b, c = row[yi - 1], row[yi], row[yi + 1]
        if None in (a, b, c):
            continue
        if b > a + 0.00015 and b > c + 0.00015:
            print(f'  z={z*1000:.1f} x={xs[yi]*1000:.1f} depth={b*1000:.1f}')
