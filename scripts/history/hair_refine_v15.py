import bpy,numpy as np,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_全部星饰圆润统一_v14_20261021';D=B/'3D重建_v6基础_发束细雕_v15_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6全部星饰圆润统一.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));m=body.data;nv=len(m.vertices);co=np.empty(nv*3,np.float32);m.vertices.foreach_get('co',co);co=co.reshape(-1,3);before=co.copy();norm=np.empty(nv*3,np.float32);m.vertices.foreach_get('normal',norm);norm=norm.reshape(-1,3);im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);votes=np.zeros(nv);counts=np.zeros(nv);hairfaces=[]
for f in m.polygons:
 x,y,z=f.center
 if not(.026<z<.092 and (y>.003 or (abs(x)>.016 and z>.060) or z>.081 or (x<-.016 and y>-.014) or (abs(x)>.024 and y>-.005))):continue
 if y<-.009 and abs(x)<.017 and z<.081:continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);r,g,b=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3];hair=(.07<r<.58 and .23<g/max(r,.001)<.69 and .30<b/max(g,.001)<.96)
 ids=np.array(f.vertices);counts[ids]+=1
 if hair:votes[ids]+=1;hairfaces.append(f.index)
mask=(counts>0)&(votes/np.maximum(counts,1)>.94)
# Tighten the mask at color boundaries so the sculpt cannot creep into skin or clothes.
edges=np.empty(len(m.edges)*2,np.int32);m.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2);weight=mask.astype(float)
for _ in range(3):
 accum=np.zeros(nv);num=np.zeros(nv);np.add.at(accum,edges[:,0],weight[edges[:,1]]);np.add.at(accum,edges[:,1],weight[edges[:,0]]);np.add.at(num,edges[:,0],1);np.add.at(num,edges[:,1],1);weight=np.minimum(weight,accum/np.maximum(num,1))
# Preserve the support surfaces beneath attached stars and flowers.
pv=[];pf=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ('Hair star' in ob.name or 'hair clip' in ob.name or 'daisy' in ob.name.lower() or 'flower' in ob.name.lower()):
  base=len(pv);pv.extend([ob.matrix_world@v.co for v in ob.data.vertices]);pf.extend([tuple(base+k for k in f.vertices) for f in ob.data.polygons])
prot=BVHTree.FromPolygons(pv,pf) if pv else None
if prot:
 for i in np.flatnonzero(weight>.001):weight[i]*=float(np.clip((prot.find_nearest(Vector(co[i]))[3]-.0005)/.0015,0,1))
# Subtle normal-only relaxation keeps silhouettes and broad curls in place.
a=np.zeros_like(co);num=np.zeros(nv);np.add.at(a,edges[:,0],co[edges[:,1]]);np.add.at(a,edges[:,1],co[edges[:,0]]);np.add.at(num,edges[:,0],1);np.add.at(num,edges[:,1],1);lap=a/np.maximum(num[:,None],1)-co;normal_lap=(lap*norm).sum(1);smooth=np.clip(normal_lap*.15,-.000045,.000045)
x,y,z=co.T;flow=x+.00135*np.sin(z*100+x*40)+.00045*np.sin(z*235+x*70);phase=flow*(2*math.pi/.00092)+.28*np.sin(z*390);groove=((1+np.cos(phase))/2)**7;detail=-.000075*groove+.000018*(1-groove);taper=np.clip((z-.026)/.007,0,1)*np.clip((.092-z)/.006,0,1);displacement=weight*taper*(smooth+detail);co+=norm*displacement[:,None];m.vertices.foreach_set('co',co.ravel());m.update()
# A separate textured hair material controls highlights without touching skin or clothes.
original=m.materials[0];hairmat=original.copy();hairmat.name='Refined chestnut sculpted hair';bs=hairmat.node_tree.nodes.get('Principled BSDF')
if bs:
 bs.inputs['Roughness'].default_value=.43;bs.inputs['Metallic'].default_value=0;bs.inputs['Coat Weight'].default_value=.10;bs.inputs['Coat Roughness'].default_value=.35
m.materials.append(hairmat);slot=len(m.materials)-1
for j in hairfaces:
 f=m.polygons[j]
 if all(mask[k] for k in f.vertices) and f.material_index==0:f.material_index=slot
assert np.array_equal(co[~mask],before[~mask]);r={'hair_vertices_refined':int((abs(displacement)>1e-9).sum()),'max_sculpt_displacement_mm':float(abs(displacement).max()*1000),'non_hair_vertices_exactly_preserved':True,'hair_groove_pitch_mm':.92,'accessory_contact_fade_mm':1.5};(D/'头发细雕校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6发束细雕.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6发束细雕.glb'),use_selection=True,export_format='GLB');print(json.dumps(r))
