import bpy, json

o = bpy.data.objects['textured_mesh.obj']
me = o.data
mw = o.matrix_world
stats = {}
for p in me.polygons:
    mi = p.material_index
    name = me.materials[mi].name if mi < len(me.materials) and me.materials[mi] else f'<{mi}>'
    s = stats.setdefault(name, {'polys': 0, 'verts': set(), 'min': [1e9, 1e9, 1e9], 'max': [-1e9, -1e9, -1e9]})
    s['polys'] += 1
    for vi in p.vertices:
        s['verts'].add(vi)
        co = mw @ me.vertices[vi].co
        for k in range(3):
            s['min'][k] = min(s['min'][k], co[k])
            s['max'][k] = max(s['max'][k], co[k])

out = {}
for name, s in stats.items():
    out[name] = {
        'polys': s['polys'],
        'verts': len(s['verts']),
        'min': [round(v, 4) for v in s['min']],
        'max': [round(v, 4) for v in s['max']],
        'size': [round(s['max'][k] - s['min'][k], 4) for k in range(3)],
    }
with open(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v33-material-bounds.json', 'w', encoding='utf8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('MAT_BOUNDS_OK', len(out))
