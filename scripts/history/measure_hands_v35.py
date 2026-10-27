import bpy, json
from mathutils import Vector

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
o = bpy.data.objects['textured_mesh.obj']
mw = o.matrix_world

regions = {
    'wave': lambda p: p.x > 0.012 and -0.03 < p.y < 0.01 and 0.040 < p.z < 0.075,
    'hang': lambda p: p.x < -0.008 and -0.03 < p.y < 0.01 and 0.030 < p.z < 0.060,
}
out = {}
for name, fn in regions.items():
    pts = []
    for v in o.data.vertices:
        p = mw @ v.co
        if fn(p):
            pts.append(p)
    if not pts:
        out[name] = None
        continue
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    out[name] = {
        'n': len(pts),
        'min': [round(min(xs), 4), round(min(ys), 4), round(min(zs), 4)],
        'max': [round(max(xs), 4), round(max(ys), 4), round(max(zs), 4)],
        'size_mm': [round((max(xs) - min(xs)) * 1000, 1),
                    round((max(ys) - min(ys)) * 1000, 1),
                    round((max(zs) - min(zs)) * 1000, 1)],
    }
print(json.dumps(out, ensure_ascii=False, indent=1))
