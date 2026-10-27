import bpy, json
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
o = bpy.data.objects['textured_mesh.obj']
mw = o.matrix_world

pts = []
for v in o.data.vertices:
    p = mw @ v.co
    if 0.016 < p.x < 0.038 and -0.014 < p.y < 0.010 and 0.045 < p.z < 0.068:
        pts.append(p)
xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
print('N', len(pts))
print('BBOX', [round(min(xs), 4), round(min(ys), 4), round(min(zs), 4)],
      [round(max(xs), 4), round(max(ys), 4), round(max(zs), 4)])
print('SIZE_MM', [round((max(xs) - min(xs)) * 1000, 1), round((max(ys) - min(ys)) * 1000, 1),
                  round((max(zs) - min(zs)) * 1000, 1)])

top = sorted(pts, key=lambda p: -p.z)[:40]
print('TOP_Z')
for p in top[:20]:
    print('  ', round(p.x * 1000, 1), round(p.y * 1000, 1), round(p.z * 1000, 1))
