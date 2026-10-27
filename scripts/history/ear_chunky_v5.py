import bpy,bmesh,numpy as np,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020';D=B/'3D重建_v6基础_熊耳分色粗绒_v5_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6后帽粗绒浮贴蝴蝶结_v4.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data;body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co);assert len(old.polygons)==ns*142

centers=co.mean(1);keep=np.ones(ns,bool);ear=np.zeros(ns,bool);mi0=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32);mi=mi0.copy();out=co.copy();cells={};zones=[0,0,0]
U=np.array([.94,0,-.342]);V=np.array([.342,0,.94]);ec=[np.array([-.010,0,.110]),np.array([.023,0,.100])]
# Follow each tilted ear rather than the world vertical.
for i,c in enumerate(centers):
 which=None
 for j,e in enumerate(ec):
  d=c-e;u=d@U;v=d@V;r=math.sqrt((u/.0094)**2+(v/.0096)**2)
  if r<1.12 and ((u<-.001 if j==0 else u>.001) or v>.0025):which=(j,u,v,r);break
 if which is None:continue
 ear[i]=True;hit=tree.find_nearest(Vector(c));a=np.array(hit[0]);n=np.array(hit[1]);key=tuple(np.floor(a/.00140).astype(int));count=cells.get(key,0)
 if count>=3:keep[i]=False;continue
 cells[key]=count+1
 vtx=co[i].astype(float).reshape(15,10,3);line=vtx.mean(1);vec=line-a;vertical=(vec@n)[:,None]*n;tangent=vec-vertical
 # Rear ear strands were already thickened in v4; avoid doubling them again.
 rear=c[1]>.006;rad=1.22 if rear else 1.65;rise=1.15 if rear else 1.45
 out[i]=((a+tangent*1.10+vertical*rise+n*.00008)[:,None,:]+(vtx-line[:,None,:])*rad).reshape(150,3)
 j,u,v,r=which
 zone=0 if r<.44 and n[1]<.35 else (1 if r<.82 and n[1]<.55 else 2)
 zones[zone]+=1;mi[i]=15+zone*3+(i%3)
ids=np.flatnonzero(keep);out=out[ids];mi=mi[ids]
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
new=bpy.data.meshes.new('Chunky three-tone bear ears');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new

for zone,(label,color) in enumerate([('Cocoa ear center',(.48,.27,.18)),('Pale rose ear ring',(.83,.63,.52)),('Warm brown ear rim',(.64,.36,.23))]):
 for k in range(3):
  mat=bpy.data.materials.new(label+str(k));mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');sr=np.array(color)*(.97+k*.03);bs.inputs['Base Color'].default_value=(*[((v+.055)/1.055)**2.4 for v in sr],1);bs.inputs['Roughness'].default_value=.88;bs.inputs['Specular IOR Level'].default_value=.14;new.materials.append(mat)
# Preserve and verify all non-ear strand coordinates exactly.
assert np.array_equal(out[~ear[ids]],co[ids[~ear[ids]]])
r={'ear_strands_before':int(ear.sum()),'ear_strands_after':int((ear&keep).sum()),'non_ear_vertices_exactly_preserved':True,'front_ear_strand_radius_scale':1.65,'front_ear_height_scale':1.45,'ear_color_zones':zones,'all_other_objects_unchanged':True}
(D/'熊耳分色粗绒校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6熊耳分色粗绒_v5.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6熊耳分色粗绒_v5.glb'),use_selection=True,export_format='GLB');print(json.dumps(r))

