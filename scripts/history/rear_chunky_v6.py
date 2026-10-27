import bpy,bmesh,numpy as np,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_熊耳分色粗绒_v5_20261021';D=B/'3D重建_v6基础_后帽再加粗减密_v6_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6熊耳分色粗绒_v5.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data;body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co);assert len(old.polygons)==ns*142

centers=co.mean(1);keep=np.ones(ns,bool);out=co.copy();mi=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32);rear=(centers[:,1]>.004)&(mi<5);cells={};pv=[];pf=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and (ob.name.startswith('Ribbon') or 'attachment' in ob.name):
  base=len(pv);pv.extend([ob.matrix_world@v.co for v in ob.data.vertices]);pf.extend([tuple(base+k for k in f.vertices) for f in ob.data.polygons])
protect=BVHTree.FromPolygons(pv,pf)
for i in np.flatnonzero(rear):
 c=centers[i];hit=tree.find_nearest(Vector(c));a=np.array(hit[0]);n=np.array(hit[1]);distance=protect.find_nearest(Vector(c))[3];alpha=float(np.clip((distance-.0015)/.0025,0,1))*float(np.clip((c[1]-.004)/.004,0,1));key=tuple(np.floor(a/.00205).astype(int));count=cells.get(key,0)
 if alpha>.8 and count>=3:keep[i]=False;continue
 cells[key]=count+1
 v=co[i].astype(float).reshape(15,10,3);line=v.mean(1);vec=line-a;vertical=(vec@n)[:,None]*n;tangent=vec-vertical
 out[i]=((a+tangent*(1+.10*alpha)+vertical*(1+.24*alpha))[:,None,:]+(v-line[:,None,:])*(1+.35*alpha)).reshape(150,3)
ids=np.flatnonzero(keep);out=out[ids];mi=mi[ids]
assert np.array_equal(out[~rear[ids]],co[ids[~rear[ids]]])
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
new=bpy.data.meshes.new('Coarser spaced rear yarn');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new

r={'rear_strands_before':int(rear.sum()),'rear_strands_after':int((rear&keep).sum()),'rear_radius_scale_max':1.35,'rear_height_scale_max':1.24,'non_rear_vertices_exactly_preserved':True,'bear_ear_colors_preserved':True,'bow_clearance_zone_preserved':True}
(D/'后帽粗绒校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6后帽再加粗减密.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6后帽再加粗减密.glb'),use_selection=True,export_format='GLB');print(json.dumps(r))
