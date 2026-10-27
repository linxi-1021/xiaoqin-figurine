import bpy, json
objs = []
for o in bpy.context.scene.objects:
    d = {"name": o.name, "type": o.type, "parent": o.parent.name if o.parent else None}
    if o.type == 'MESH':
        me = o.data
        d.update({
            "verts": len(me.vertices),
            "polys": len(me.polygons),
            "materials": [m.name for m in me.materials if m],
            "dims": [round(v, 4) for v in o.dimensions],
            "loc": [round(v, 4) for v in o.location],
            "modifiers": [m.type for m in o.modifiers],
        })
    objs.append(d)
out = {"file": bpy.data.filepath, "object_count": len(objs), "objects": objs}
with open(r"C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v33-objects.json", "w", encoding="utf8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OBJECTS_JSON_OK", len(objs))
