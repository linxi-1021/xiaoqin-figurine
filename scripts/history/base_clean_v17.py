import bpy,numpy as np,json,hashlib
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_鞋履细节精修_v16_20261021';D=B/'3D重建_v6基础_底座净色_v17_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6鞋履细节精修.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));m=body.data;before=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',before)
# Outer upward faces identify the pedestal crown independently of the shoes.
fit=[]
for f in m.polygons:
 x,y,z=f.center
 if x*x+y*y>.019**2 and z<.0095 and f.normal.z>.80:fit.append((x,y,z))
a=np.array(fit);coef=np.linalg.lstsq(np.column_stack([a[:,0],a[:,1],np.ones(len(a))]),a[:,2],rcond=None)[0];res=a[:,2]-(coef[0]*a[:,0]+coef[1]*a[:,1]+coef[2]);margin=max(.00012,float(np.percentile(res,99))+.00005)
mat=bpy.data.materials.new('Pedestal clean warm ivory satin');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');srgb=[.86,.79,.69];bs.inputs['Base Color'].default_value=(*[((v+.055)/1.055)**2.4 for v in srgb],1);bs.inputs['Roughness'].default_value=.64;bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.28;m.materials.append(mat);slot=len(m.materials)-1;selected=[]
for f in m.polygons:
 x,y,z=f.center;limit=coef[0]*x+coef[1]*y+coef[2]+margin
 if z<min(limit,.0093):f.material_index=slot;selected.append(f.index)
after=np.empty_like(before);m.vertices.foreach_get('co',after);assert np.array_equal(before,after)
r={'base_faces_recolored':len(selected),'pedestal_top_plane':coef.tolist(),'surface_margin_mm':margin*1000,'all_geometry_unchanged':True,'base_material':'warm ivory satin, no baked texture','source_version':'v16'};(D/'底座净色校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底座净色.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底座净色.glb'),use_selection=True,export_format='GLB')
