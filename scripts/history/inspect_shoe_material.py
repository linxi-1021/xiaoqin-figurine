import bpy, json
o = bpy.data.objects['textured_mesh.obj']
me = o.data
out = {'uv_layers': [l.name for l in me.uv_layers], 'color_attrs': [a.name for a in me.color_attributes]}
m = bpy.data.materials['Cream leather shoes soft satin finish']
info = {'name': m.name, 'use_nodes': m.use_nodes, 'nodes': []}
if m.use_nodes:
    for n in m.node_tree.nodes:
        d = {'type': n.type, 'name': n.name}
        if n.type == 'TEX_IMAGE' and n.image:
            d['image'] = n.image.name
            d['size'] = list(n.image.size)
        if n.type == 'BSDF_PRINCIPLED':
            d['base_color'] = [round(v, 3) for v in n.inputs['Base Color'].default_value]
            d['roughness'] = round(n.inputs['Roughness'].default_value, 3)
        info['nodes'].append(d)
out['material'] = info
with open(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34-shoe-material.json', 'w', encoding='utf8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('MAT_OK')
