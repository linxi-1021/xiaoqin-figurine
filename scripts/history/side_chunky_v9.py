import bpy,bmesh,numpy as np,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_前后帽统一粗绒_v8_20261021';D=B/'3D重建_v6基础_两侧粗绒衔接_v9_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6前后统一粗绒.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data;body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co);assert len(old.polygons)==ns*142

centers=co.mean(1);keep=np.ones(ns,bool);out=co.copy();mi=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32)
rings=co.reshape(-1,15,10,3);lines=rings.mean(2);radii=np.linalg.norm(rings-lines[:,:,None,:],axis=3).mean((1,2));target=float(np.median(radii[(centers[:,1]>.012)&(mi<5)]));side=(abs(centers[:,0])>.011)&(centers[:,1]>-.006)&(centers[:,1]<.016)&(mi<5)&(radii<target*.94);cells={};scales=[]
# Use actual cross-section size, not front/back Y masks, to close the transition gap.
for i in np.flatnonzero(side):
 c=centers[i];hit=tree.find_nearest(Vector(c));a=np.array(hit[0]);n=np.array(hit[1]);key=tuple(np.floor(a/.00205).astype(int));count=cells.get(key,0)
 if count>=3:keep[i]=False;continue
 cells[key]=count+1
 v=co[i].astype(float).reshape(15,10,3);line=v.mean(1);vec=line-a;vertical=(vec@n)[:,None]*n;tangent=vec-vertical;scale=min(target/max(radii[i],1e-8),4.5);scales.append(scale);height=max(float(np.max(vec@n)),.0001);rise=max(1,min(.00125/height,1.8))
 out[i]=((a+tangent+vertical*rise)[:,None,:]+(v-line[:,None,:])*scale).reshape(150,3)
ids=np.flatnonzero(keep);out=out[ids];mi=mi[ids];assert np.array_equal(out[~side[ids]],co[ids[~side[ids]]])
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
new=bpy.data.meshes.new('Matched front and rear thick yarn');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new

r={'side_strands_before':int(side.sum()),'side_strands_after':int((side&keep).sum()),'reference_mean_radius_mm':target*1000,'other_strands_vertices_preserved_exactly':True,'left_changed':int((side&(centers[:,0]<0)).sum()),'right_changed':int((side&(centers[:,0]>0)).sum())}
(D/'两侧厚度衔接校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6两侧粗绒衔接.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6两侧粗绒衔接.glb'),use_selection=True,export_format='GLB');print(json.dumps(r))
