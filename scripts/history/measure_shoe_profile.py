import bpy, json
from collections import defaultdict

o = bpy.data.objects['textured_mesh.obj']
me = o.data
mw = o.matrix_world

bands = defaultdict(lambda: defaultdict(lambda: {'xmin': 1e9, 'xmax': -1e9, 'ymin': 1e9, 'ymax': -1e9, 'n': 0}))
for v in me.vertices:
    co = mw @ v.co
    if not (0.0085 <= co.z <= 0.0200 and abs(co.x) < 0.018 and -0.016 < co.y < 0.018):
        continue
    side = 'L' if co.x < 0 else 'R'
    zb = round(co.z, 3)
    b = bands[side][zb]
    b['xmin'] = min(b['xmin'], co.x); b['xmax'] = max(b['xmax'], co.x)
    b['ymin'] = min(b['ymin'], co.y); b['ymax'] = max(b['ymax'], co.y)
    b['n'] += 1

out = {}
for side, zs in bands.items():
    out[side] = {str(z): {k: (round(v, 4) if isinstance(v, float) else v) for k, v in b.items()} for z, b in sorted(zs.items())}
with open(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34-shoe-profile.json', 'w', encoding='utf8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('PROFILE_OK')
