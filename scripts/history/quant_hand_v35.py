import bpy, json
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
o = bpy.data.objects['textured_mesh.obj']
mw = o.matrix_world

pts = []
for v in o.data.vertices:
    p = mw @ v.co
    if 0.012 < p.x < 0.034 and 0.045 < p.z < 0.066 and -0.02 < p.y < 0.012:
        pts.append(p)
print('N', len(pts))
xs = sorted(p.x for p in pts)
ys = sorted(p.y for p in pts)
zs = sorted(p.z for p in pts)
print('X_QUANT', [round(xs[int(len(xs) * q)] * 1000, 1) for q in (0.02, 0.1, 0.25, 0.5, 0.75, 0.9, 0.98)])
print('Y_QUANT', [round(ys[int(len(ys) * q)] * 1000, 1) for q in (0.02, 0.1, 0.25, 0.5, 0.75, 0.9, 0.98)])
print('Z_QUANT', [round(zs[int(len(zs) * q)] * 1000, 1) for q in (0.02, 0.1, 0.25, 0.5, 0.75, 0.9, 0.98)])

# 前表面（y 最小的一批）就是手掌
front = [p for p in pts if p.y < ys[int(len(ys) * 0.15)]]
fx = [p.x for p in front]; fz = [p.z for p in front]; fy = [p.y for p in front]
print('FRONT_BBOX x', round(min(fx) * 1000, 1), round(max(fx) * 1000, 1),
      'z', round(min(fz) * 1000, 1), round(max(fz) * 1000, 1),
      'y', round(min(fy) * 1000, 1), round(max(fy) * 1000, 1))
print('FRONT_CENTER', round(sum(fx) / len(fx) * 1000, 1), round(sum(fz) / len(fz) * 1000, 1))
