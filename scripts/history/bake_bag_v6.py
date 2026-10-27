import bpy,bmesh
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'bag-v6'
bpy.ops.wm.open_mainfile(filepath=str(out/'小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
material=bpy.data.materials['Bear bag clean face paint'];mi=list(body.data.materials).index(material)
copy=body.copy();copy.data=body.data.copy();bpy.context.collection.objects.link(copy);copy.name='Temporary bag color bake'
bm=bmesh.new();bm.from_mesh(copy.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=mi],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(copy.data);bm.free()
bakemat=material.copy();copy.data.materials.clear();copy.data.materials.append(bakemat)
for p in copy.data.polygons:p.material_index=0
uv=copy.data.uv_layers.get('BearBagFaceUV');copy.data.uv_layers.active=uv;uv.active_render=True
image=bpy.data.images.new('Bear bag final baked color 1024',width=1024,height=1024,alpha=False);image.generated_color=(.85,.7,.55,1)
target=bakemat.node_tree.nodes.new('ShaderNodeTexImage');target.image=image;bakemat.node_tree.nodes.active=target
bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},use_clear=False,margin=12)
image.filepath_raw=str(out/'小熊包_曲面合成贴图.png');image.file_format='PNG';image.save();image.pack()
bpy.data.objects.remove(copy,do_unlink=True)
nodes=material.node_tree.nodes;links=material.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='BearBagFaceUV';links.new(uvnode.outputs['UV'],tex.inputs['Vector']);links.new(tex.outputs['Color'],bs.inputs['Base Color'])
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;full=body.data.copy();mod=body.modifiers.new('Web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB');body.data=full
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'));print('BAKED_TEXTURE_EXPORT_DONE')
