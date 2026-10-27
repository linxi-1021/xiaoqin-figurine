import bpy,bmesh,numpy as np,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_两侧粗绒衔接_v9_20261021';D=B/'3D重建_v6基础_帽檐上部补绒_v10_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6两侧粗绒衔接.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data;body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co);assert len(old.polygons)==ns*142

from mathutils.kdtree import KDTree
centers=co.mean(1);mi=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32);rings=co.reshape(-1,15,10,3);lines=rings.mean(2);radii=np.linalg.norm(rings-lines[:,:,None,:],axis=3).mean((1,2));target=float(np.median(radii[(centers[:,1]>.012)&(mi<5)]));ivory=np.flatnonzero((mi>=5)&(mi<10)&(radii>target*.75));kt=KDTree(len(ivory))
for j,i in enumerate(ivory):kt.insert(Vector(centers[i]),j)
kt.balance();fur=BVHTree.FromObject(yarn,bpy.context.evaluated_depsgraph_get());U=Vector((.94,0,-.342));V=Vector((.342,0,.94));origin=Vector((.00666,0,.10105));cells={};added=[];addedm=[];m=body.data;im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4)
for f in m.polygons:
 c=f.center;n=f.normal;q=(c-origin).dot(V)
 if not(c.y<-.018 and -.019<q<.001 and n.dot(V)>.15):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);r,g,b=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3]
 if not(r>.58 and g/max(r,.001)>.72 and b/max(g,.001)>.62):continue
 # Exclude the nose and its clearance halo in three dimensions.
 if (c-Vector((.0054,-.0152,.1009))).length<.0042:continue
 key=tuple(np.floor(np.array(c)/.00165).astype(int))
 if key not in cells:cells[key]=(c.copy(),n.copy())
for c,n in cells.values():
 hit=fur.ray_cast(c+n*.006,-n,.0055)
 if hit[0] is not None and (hit[0]-c).dot(n)>.0016:continue
 _,j,_=kt.find(c);i=int(ivory[j]);source=tree.find_nearest(Vector(centers[i]));rotation=source[1].rotation_difference(n).to_matrix();rel=co[i]-centers[i];v=np.array([tuple(rotation@Vector(a)) for a in rel]);added.append(v+np.array(c+n*.00075));addedm.append(int(mi[i]))
out=np.concatenate([co,np.array(added,dtype=np.float32)],axis=0) if added else co.copy();mi=np.concatenate([mi,np.array(addedm,np.int32)]);assert np.array_equal(out[:ns],co)
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
new=bpy.data.meshes.new('Matched front and rear thick yarn');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new

r={'added_brim_strands':len(added),'existing_vertices_exactly_preserved':True,'surface_candidates':len(cells),'nose_clearance_mm':4.2}
(D/'帽檐补绒校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6帽檐上部补绒.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6帽檐上部补绒.glb'),use_selection=True,export_format='GLB');print(json.dumps(r))
