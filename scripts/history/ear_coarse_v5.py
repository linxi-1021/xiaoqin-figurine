import bpy,numpy as np,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020';D=B/'3D重建_v6基础_熊耳分色粗绒_v5_20261020';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6后帽粗绒浮贴蝴蝶结_v4.blend'))
yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data
# Hash every other mesh and its transform before the localized edit.
def hashes():
 r={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o==yarn:continue
  a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);r[o.name]=hashlib.sha256(a.tobytes()+np.array(o.matrix_world).tobytes()).hexdigest()
 return r
before=hashes();co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);cent=co.mean(1);ns=len(co);mi=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32)
body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
# Ear disks tilt with the hat rather than following a world-horizontal stripe.
U=np.array([.94,0,-.342]);V=np.array([.342,0,.94]);earcent=[np.array([-.0103,.001,.1122]),np.array([.0236,.002,.1019])]
earid=np.full(ns,-1);rho=np.zeros(ns)
for j,e in enumerate(earcent):
 q=cent-e;rr=np.sqrt((q@U/.0095)**2+(q@V/.0090)**2);mask=(rr<1.13)&((q@V)>-.0053);earid[mask]=j;rho[mask]=rr[mask]
keep=np.ones(ns,bool);cells={};out=co.copy();ear_before=int((earid>=0).sum())
for i,c in enumerate(cent):
 ear=earid[i]>=0
 # Keep the already approved rear/bow region exact; simplify ear fibers on both sides.
 if not ear and c[1]>.003:continue
 hit=tree.find_nearest(Vector(c));a=np.array(hit[0]);n=np.array(hit[1]);spacing=.00165 if ear else .00142;key=(int(earid[i]) if ear else -2,*np.floor(a/spacing).astype(int));limit=2 if ear else 3
 if cells.get(key,0)>=limit:keep[i]=False;continue
 cells[key]=cells.get(key,0)+1
 v=co[i].reshape(15,10,3);line=v.mean(1);vec=line-a;vert=(vec@n)[:,None]*n;tan=vec-vert
 scale=1.43 if ear else 1.17;rise=1.20 if ear else 1.08
 new=line+(rise-1)*vert
 out[i]=(new[:,None,:]+(v-line[:,None,:])*scale).reshape(150,3)
 if ear:
  # Front: recessed cocoa center, peach ring, cocoa outer edge. Back stays cocoa.
  r=rho[i];front=c[1]<.0038
  kind=0 if (not front or r>.88) else (2 if r<.48 else 1)
  mi[i]=len(old.materials)+kind*3+(i%3)
ids=np.flatnonzero(keep);out=out[ids];mi=mi[ids]
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);template=np.array([old.loops[i].vertex_index for i in range(580)],np.int32)
new=bpy.data.meshes.new('Chunky yarn with layered bear ear colors');N=len(out);new.vertices.add(N*150);new.vertices.foreach_set('co',out.ravel());new.loops.add(N*580);new.loops.foreach_set('vertex_index',(np.arange(N,dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(N*142);new.polygons.foreach_set('loop_start',(np.arange(N,dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,N));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(N*142,bool))
for m in old.materials:new.materials.append(m)
for label,color in [('Warm cocoa ear rim',(.63,.37,.25)),('Peach cream ear ring',(.87,.66,.53)),('Deep cocoa ear hollow',(.43,.23,.14))]:
 for variation in [.98,1,1.02]:
  m=bpy.data.materials.new(label+str(variation));m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*[((v*variation+.055)/1.055)**2.4 for v in color],1);p.inputs['Roughness'].default_value=.86;p.inputs['Specular IOR Level'].default_value=.14;p.inputs['Sheen Weight'].default_value=.16;new.materials.append(m)
new.update(calc_edges=True);yarn.data=new
assert before==hashes()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6熊耳分色粗绒_v5.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6熊耳分色粗绒_v5.glb'),use_selection=True,export_format='GLB')
r={'other_objects_exactly_preserved':before==hashes(),'ear_strands_before':ear_before,'ear_strands_after':int(((earid>=0)&keep).sum()),'ear_thickness_scale':1.43,'ear_rise_scale':1.20,'total_strands_before':ns,'total_strands_after':N,'colors':['warm cocoa rim','peach cream ring','deep cocoa hollow']};(D/'熊耳修正校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
