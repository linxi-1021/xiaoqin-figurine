import bpy,json,bmesh,numpy as np
from mathutils import Vector
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'no-bag-v9'
bpy.ops.wm.open_mainfile(filepath=str(out/'working.blend'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];body=max(objs,key=lambda o:len(o.data.vertices))
# Remove the remaining ivory bag attachment below the sleeve; retain skin-colored fingers.
img=next(nd.image for nd in body.data.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image)
pix=np.empty(img.size[0]*img.size[1]*4,dtype=np.float32);img.pixels.foreach_get(pix);pix=pix.reshape(img.size[1],img.size[0],4);uv=body.data.uv_layers[0].data;ids=[]
for f in body.data.polygons:
 p=f.center
 if not(-.019<p.x<-.013 and .028<p.z<.0335 and p.y<-.001):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[1]>rgb[0]*.78 and rgb[2]>rgb[0]*.57:ids.append(f.index)
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[j] for j in ids],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(body.data);bm.free();print('REMNANTS_REMOVED',len(ids))
assert not any('Bag round' in o.name or 'Bear bag ear' in o.name or 'Bag circular' in o.name for o in objs)
report={'source':'v6 uncompressed body; no v7 bag objects imported','removed_original_bag_region_faces':10489,'removed_strap_faces':6512,'new_cylinder_bag_objects':0,'reconstruction':['mirrored intact skirt panel','inner sleeve wall','knit torso'],'status':'visual model; garment assembly requires fusion and print validation','objects':[{'name':o.name,'faces':len(o.data.polygons)} for o in objs]}
(out/'removal-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_去除斜挎包.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('Web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
patch=next(o for o in objs if o.name=='Reconstructed skirt panel');bpy.context.view_layer.objects.active=patch;mod=patch.modifiers.new('Web optimization','DECIMATE');mod.ratio=.4;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_去除斜挎包.glb'),use_selection=True,export_format='GLB');print('NO_BAG_EXPORTED')
