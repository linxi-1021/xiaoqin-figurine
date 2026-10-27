import bpy,numpy as np,math,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_五处局部收口_v36_20261025';D=B/'3D重建_v6基础_后背波浪细发束_v37_20261025';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v36五处局部收口_待验收.blend'))
body=bpy.data.objects['textured_mesh.obj'];m=body.data;nv=len(m.vertices);co=np.empty(nv*3,np.float32);m.vertices.foreach_get('co',co);co=co.reshape(-1,3);before=co.copy();norm=np.empty(nv*3,np.float32);m.vertices.foreach_get('normal',norm);norm=norm.reshape(-1,3);im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);votes=np.zeros(nv);counts=np.zeros(nv)
for f in m.polygons:
 x,y,z=f.center
 if not(.036<z<.088 and y>.007 and abs(x)<.029):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);r,g,b=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3]
 hair=(.04<r<.64 and .20<g/max(r,.001)<.71 and .25<b/max(g,.001)<.97)
 ids=np.array(f.vertices);counts[ids]+=1
 if hair:votes[ids]+=1
mask=(counts>0)&(votes/np.maximum(counts,1)>.94)&(co[:,1]>.007)&(co[:,2]>.036)&(co[:,2]<.088)&(norm[:,1]>.20)
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
# Keep every previously repaired body vertex and its immediate support zone fixed.
protected_ids=set()
for stage in range(2,6):
 data=np.load(S/'过程备份'/f'stage{stage}_displacement.npz');protected_ids.update(data['ids'].tolist())
kt=KDTree(len(protected_ids))
for j,i in enumerate(sorted(protected_ids)):kt.insert(Vector(co[i]),j)
kt.balance()
source_tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());thin_skips=0
for i in np.flatnonzero(weight>.001):
 distance=kt.find(Vector(co[i]))[2];weight[i]*=float(np.clip((distance-.0003)/.0010,0,1))
 if weight[i]<.001:continue
 near=source_tree.find_nearest(Vector(co[i]));face=m.polygons[near[2]];n=face.normal;hit=source_tree.ray_cast(face.center-n*.00003,-n,.060)
 if hit[0] is not None and hit[3]<.00135:weight[i]=0;thin_skips+=1
x,y,z=co.T
flow=x+.0020*np.sin(z*170+x*24)+.00060*np.sin(z*330+x*35)
phase=flow*(2*math.pi/.0018)+.24*np.sin(z*230+x*120)
groove=((1+np.cos(phase))/2)**3
edgefade=np.clip((z-.036)/.008,0,1)*np.clip((.088-z)/.006,0,1)*np.clip((y-.007)/.004,0,1)*np.clip((.029-abs(x))/.003,0,1)
# Incised rounded flow grooves split the existing broad waves; no independent floating fibers.
displacement=-.00040*groove*weight*edgefade
co+=norm*displacement[:,None]
old_corner=np.empty(len(m.loops)*3,np.float32);m.corner_normals.foreach_get('vector',old_corner);old_corner=old_corner.reshape(-1,3)
m.vertices.foreach_set('co',co.ravel());m.update();m.calc_loop_triangles()
tri=np.empty(len(m.loop_triangles)*3,np.int32);m.loop_triangles.foreach_get('vertices',tri);tri=tri.reshape(-1,3);vn=np.zeros((nv,3),np.float64);cross=np.cross(co[tri[:,1]]-co[tri[:,0]],co[tri[:,2]]-co[tri[:,0]])
for j in range(3):np.add.at(vn,tri[:,j],cross)
vn/=np.maximum(np.linalg.norm(vn,axis=1)[:,None],1e-20)
loopids=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',loopids);edited=(abs(displacement)>1e-9);cm=edited[loopids];new_corner=old_corner.copy();new_corner[cm]=vn[loopids[cm]];m.normals_split_custom_set(new_corner.tolist());m.update()

assert np.array_equal(co[~mask],before[~mask]);assert np.array_equal(co[list(protected_ids)],before[list(protected_ids)])
bm=bmesh.new();bm.from_mesh(m);boundary=sum(e.is_boundary for e in bm.edges);bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert boundary==308 and bad==308
report={'source':'v36 candidate','changed_hair_vertices':int((abs(displacement)>1e-9).sum()),'maximum_groove_depth_mm':float(abs(displacement).max()*1000),'nominal_groove_pitch_mm':1.8,'thin_surface_candidates_skipped':thin_skips,'outside_hair_vertices_exactly_preserved':True,'v36_repair_vertices_exactly_preserved':True,'source_boundary_edges_preserved':boundary,'source_nonmanifold_edges_preserved':bad,'new_floating_fibers':0,'source_materials_and_textures_unchanged':True,'inherited_v36_production_acceptance':False}
(D/'后发细化校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v37后背波浪细发束.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v37后背波浪细发束.glb'),use_selection=True,export_format='GLB');print(json.dumps(report))
