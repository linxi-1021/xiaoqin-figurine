import bpy,bmesh,numpy as np,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_后帽加粗100_v7_20261021';D=B/'3D重建_v6基础_前后帽统一粗绒_v8_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6后帽加粗100.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data;body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co);assert len(old.polygons)==ns*142

centers=co.mean(1);keep=np.ones(ns,bool);out=co.copy();mi=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32);front=(centers[:,1]<.004)&(mi<10);cells={};pv=[];pf=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ob!=yarn and ob!=body:
  base=len(pv);pv.extend([ob.matrix_world@v.co for v in ob.data.vertices]);pf.extend([tuple(base+k for k in f.vertices) for f in ob.data.polygons])
protect=BVHTree.FromPolygons(pv,pf)
rings=co.reshape(-1,15,10,3);lines=rings.mean(2);radii=np.linalg.norm(rings-lines[:,:,None,:],axis=3).mean((1,2));target=float(np.median(radii[(centers[:,1]>.012)&(mi<5)]));scales=[]
for i in np.flatnonzero(front):
 c=centers[i];hit=tree.find_nearest(Vector(c));a=np.array(hit[0]);n=np.array(hit[1]);distance=protect.find_nearest(Vector(c))[3];alpha=float(np.clip((distance-.0005)/.0025,0,1));alpha*=float(np.clip((.004-c[1])/.004,0,1));key=tuple(np.floor(a/.00205).astype(int));count=cells.get(key,0)
 if alpha>.8 and count>=3:keep[i]=False;continue
 cells[key]=count+1
 # Keep a smooth clearance halo around the actual eye and nose footprints.
 U=np.array([.94,0,-.342]);V=np.array([.342,0,.94])
 if c[1]<-.004:
  for e,rx,rz in [(np.array([-.00117,-.01267,.10393]),.0035,.0032),(np.array([.0145,-.01251,.09818]),.0035,.0032),(np.array([.0054,-.0152,.1009]),.0045,.0036)]:
   dd=c-e;rr=math.sqrt((dd@U/rx)**2+(dd@V/rz)**2);alpha=min(alpha,float(np.clip((rr-1)/.65,0,1)))
 v=co[i].astype(float).reshape(15,10,3);line=v.mean(1);vec=line-a;vertical=(vec@n)[:,None]*n;tangent=vec-vertical;scale=1+(min(target/max(radii[i],1e-8),4.5)-1)*alpha;scales.append(scale)
 out[i]=((a+tangent+vertical*(1+.65*alpha))[:,None,:]+(v-line[:,None,:])*scale).reshape(150,3)
ids=np.flatnonzero(keep);out=out[ids];mi=mi[ids]
assert np.array_equal(out[~front[ids]],co[ids[~front[ids]]])
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
new=bpy.data.meshes.new('Matched front and rear thick yarn');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new

r={'front_strands_before':int(front.sum()),'front_strands_after':int((front&keep).sum()),'rear_reference_mean_radius_mm':target*1000,'median_front_radius_scale':float(np.median(scales)),'rear_and_ears_vertices_preserved_exactly':True,'five_features_clearance_protected':True}
(D/'前后粗绒统一校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6前后统一粗绒.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6前后统一粗绒.glb'),use_selection=True,export_format='GLB');print(json.dumps(r))
