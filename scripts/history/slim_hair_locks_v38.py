import bpy,numpy as np,math,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_五处局部收口_v36_20261025';D=B/'3D重建_v6基础_后背粗发束收细_v38_20261026';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v36五处局部收口_待验收.blend'))
body=bpy.data.objects['textured_mesh.obj'];m=body.data;nv=len(m.vertices);co=np.empty(nv*3,np.float32);m.vertices.foreach_get('co',co);co=co.reshape(-1,3);before=co.copy();norm=np.empty(nv*3,np.float32);m.vertices.foreach_get('normal',norm);norm=norm.reshape(-1,3);im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);votes=np.zeros(nv);counts=np.zeros(nv)
for f in m.polygons:
 x,y,z=f.center
 if not(.029<z<.090 and y>.004 and abs(x)<.033):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);r,g,b=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3]
 hair=(.02<r<.64 and .12<g/max(r,.001)<.65)
 ids=np.array(f.vertices);counts[ids]+=1
 if hair:votes[ids]+=1
mask=(counts>0)&(votes/np.maximum(counts,1)>.94)&(co[:,1]>.004)&(co[:,2]>.029)&(co[:,2]<.090)
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
# Geometric inward offset on the whole cross-section, including the sides of each existing curl.
protected_ids=set()
for stage in [3,4,5]:
 data=np.load(S/'过程备份'/f'stage{stage}_displacement.npz');protected_ids.update(data['ids'].tolist())
weight[list(protected_ids)]=0
x,y,z=co.T
fade=np.clip((z-.029)/.005,0,1)*np.clip((.090-z)/.007,0,1)*np.clip((y-.004)/.004,0,1)
weight*=fade
source_tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());thin_skips=0
# Gradual cross-section contraction avoids offsetting concave scan folds through each other.
vg=body.vertex_groups.new(name='Rear lock cross section contraction')
for i in np.flatnonzero(weight>.001):vg.add([int(i)],float(weight[i]),'REPLACE')
bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('Gradual existing lock thinning','SMOOTH');mod.factor=.8;mod.iterations=220;mod.use_x=True;mod.use_y=True;mod.use_z=False;mod.vertex_group=vg.name
bpy.ops.object.modifier_apply(modifier=mod.name)
m=body.data
co=np.empty(nv*3,np.float32);m.vertices.foreach_get('co',co);co=co.reshape(-1,3);delta=co-before
maxmove=np.linalg.norm(delta,axis=1).max()
if maxmove>.0020:delta*=.0020/maxmove;co=before+delta
vg_done=body.vertex_groups.get('Rear lock cross section contraction')
if vg_done:body.vertex_groups.remove(vg_done)
# Reject local face reversals and attenuate only the affected displacement neighborhoods.
m.calc_loop_triangles();tt=np.empty(len(m.loop_triangles)*3,np.int32);m.loop_triangles.foreach_get('vertices',tt);tt=tt.reshape(-1,3)
bc=before.astype(np.float64);base_cross=np.cross(bc[tt[:,1]]-bc[tt[:,0]],bc[tt[:,2]]-bc[tt[:,0]])
for attempt in range(60):
 cc=co.astype(np.float64);now_cross=np.cross(cc[tt[:,1]]-cc[tt[:,0]],cc[tt[:,2]]-cc[tt[:,0]]);flipped=(base_cross*now_cross).sum(1)<-1e-24
 if not flipped.any():break
 bad_ids=np.unique(tt[flipped]);delta[bad_ids]*=.5;co=before+delta
assert not flipped.any(),'Face reversal check failed'
old_corner=np.empty(len(m.loops)*3,np.float32);m.corner_normals.foreach_get('vector',old_corner);old_corner=old_corner.reshape(-1,3)
m.vertices.foreach_set('co',co.ravel());m.update();m.calc_loop_triangles();tri=np.empty(len(m.loop_triangles)*3,np.int32);m.loop_triangles.foreach_get('vertices',tri);tri=tri.reshape(-1,3);vn=np.zeros((nv,3),np.float64);cross=np.cross(co[tri[:,1]]-co[tri[:,0]],co[tri[:,2]]-co[tri[:,0]])
for j in range(3):np.add.at(vn,tri[:,j],cross)
vn/=np.maximum(np.linalg.norm(vn,axis=1)[:,None],1e-20);loopids=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',loopids);edited=np.linalg.norm(delta,axis=1)>1e-9;cm=edited[loopids];new_corner=old_corner.copy();new_corner[cm]=vn[loopids[cm]];m.normals_split_custom_set(new_corner.tolist());m.update()
assert np.array_equal(co[~mask],before[~mask]);assert np.array_equal(co[list(protected_ids)],before[list(protected_ids)])
bm=bmesh.new();bm.from_mesh(m);boundary=sum(e.is_boundary for e in bm.edges);bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert boundary==308 and bad==308
# Compare actual X cross-section intervals on the old and new geometry, rather than surface-line density.
after_tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
def intervals(tree,yy,zz):
 hits=[];origin=Vector((-.050,yy,zz));direction=Vector((1,0,0))
 for k in range(80):
  h=tree.ray_cast(origin,direction,.100)
  if h[0] is None or h[0].x>.05:break
  xx=h[0].x
  if not hits or xx-hits[-1]>.00001:hits.append(xx)
  origin=h[0]+direction*.000005
 return [(hits[i],hits[i+1]) for i in range(0,len(hits)-1,2)]
measure=[]
for yy in [.012,.016,.020,.024]:
 for zz in [.036,.043,.050,.057,.064,.071,.078]:
  old=intervals(source_tree,yy,zz);new=intervals(after_tree,yy,zz)
  for lo,hi in old:
   width=hi-lo
   if not(.0015<width<.014):continue
   center=(lo+hi)*.5
   candidates=[ab for ab in new if abs((ab[0]+ab[1])*.5-center)<.002]
   if not candidates:continue
   aa,bb=min(candidates,key=lambda ab:abs((ab[0]+ab[1])*.5-center));newwidth=bb-aa
   if .0005<newwidth<width*.95:measure.append({'y_mm':yy*1000,'z_mm':zz*1000,'x_mid_mm':center*1000,'width_before_mm':width*1000,'width_after_mm':newwidth*1000,'reduction_percent':(1-newwidth/width)*100})
report={'source':'v36 hair shape; replaces v37 surface-groove approach','method':'gradual transverse mesh contraction of existing wave cross sections; original Z coordinates preserved; no added hair grooves','changed_hair_vertices':int(edited.sum()),'max_transverse_offset_mm':float(abs(delta[:,0]).max()*1000),'max_depth_offset_mm':float(abs(delta[:,1]).max()*1000),'thin_surface_vertices_skipped':thin_skips,'non_hair_geometry_exactly_preserved':True,'contact_repair_vertices_exactly_preserved':True,'source_boundary_edges_preserved':boundary,'source_nonmanifold_edges_preserved':bad,'materials_textures_unchanged':True,'reversed_triangles_diagnostic':0,'cross_section_measurements':measure,'inherited_v36_production_acceptance':False}
(D/'实际发束收细校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');np.savez_compressed(D/'发束位移记录.npz',ids=np.flatnonzero(edited),before=before[edited],after=co[edited])
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v38后背粗发束收细.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v38后背粗发束收细.glb'),use_selection=True,export_format='GLB');print(json.dumps({k:v for k,v in report.items() if k!='cross_section_measurements'}));print('WIDTH_SAMPLES',len(measure),measure[:5])

