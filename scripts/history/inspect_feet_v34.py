import bpy, json
from collections import defaultdict

o = bpy.data.objects['textured_mesh.obj']
me = o.data
mw = o.matrix_world

ZMAX = 0.028
stats = defaultdict(lambda: {'polys': 0, 'zmin': 1e9, 'zmax': -1e9, 'xmin': 1e9, 'xmax': -1e9})
side = {'L': {'polys': 0, 'zmin': 1e9, 'zmax': -1e9, 'xmin': 1e9, 'xmax': -1e9, 'ymin': 1e9, 'ymax': -1e9},
        'R': {'polys': 0, 'zmin': 1e9, 'zmax': -1e9, 'xmin': 1e9, 'xmax': -1e9, 'ymin': 1e9, 'ymax': -1e9}}
hist = defaultdict(int)

for p in me.polygons:
    c = mw @ p.center
    if c.z > ZMAX:
        continue
    name = me.materials[p.material_index].name if me.materials[p.material_index] else '?'
    s = stats[name]
    s['polys'] += 1
    s['zmin'] = min(s['zmin'], c.z); s['zmax'] = max(s['zmax'], c.z)
    s['xmin'] = min(s['xmin'], c.x); s['xmax'] = max(s['xmax'], c.x)
    k = 'L' if c.x < 0 else 'R'
    d = side[k]
    d['polys'] += 1
    d['zmin'] = min(d['zmin'], c.z); d['zmax'] = max(d['zmax'], c.z)
    d['xmin'] = min(d['xmin'], c.x); d['xmax'] = max(d['xmax'], c.x)
    d['ymin'] = min(d['ymin'], c.y); d['ymax'] = max(d['ymax'], c.y)
    if c.z < 0.020 and abs(c.x) < 0.020:
        hist[round(c.z, 3)] += 1

out = {
    'material_stats': {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in stats.items()},
    'side_stats': {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in side.items()},
    'z_histogram': {str(k): v for k, v in sorted(hist.items())},
}
with open(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34-feet-stats.json', 'w', encoding='utf8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('FEET_OK')
