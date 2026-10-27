import bpy, bmesh, json
from mathutils import Vector

src = bpy.data.objects['textured_mesh.obj']
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True)
bpy.context.view_layer.objects.active = src
bpy.ops.object.duplicate()
dup = bpy.context.view_layer.objects.active
dup.name = 'ISLAND_PROBE'
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')

parts = []
for o in [x for x in bpy.context.scene.objects if x.name.startswith('ISLAND_PROBE')]:
    if o.type != 'MESH':
        continue
    me = o.data
    ws = [o.matrix_world @ v.co for v in me.vertices]
    if not ws:
        continue
    xs = [p.x for p in ws]; ys = [p.y for p in ws]; zs = [p.z for p in ws]
    mats = sorted({me.materials[p.material_index].name for p in me.polygons if me.materials[p.material_index]})
    parts.append({
        'name': o.name,
        'verts': len(me.vertices),
        'polys': len(me.polygons),
        'min': [round(min(xs), 4), round(min(ys), 4), round(min(zs), 4)],
        'max': [round(max(xs), 4), round(max(ys), 4), round(max(zs), 4)],
        'center': [round(sum(xs) / len(xs), 4), round(sum(ys) / len(ys), 4), round(sum(zs) / len(zs), 4)],
        'materials': mats,
    })

parts.sort(key=lambda p: -p['verts'])
out = {'source': src.name, 'island_count': len(parts), 'islands': parts[:80]}
with open(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v33-islands.json', 'w', encoding='utf8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('ISLANDS_OK', len(parts))
