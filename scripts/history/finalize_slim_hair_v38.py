import bpy,numpy as np,json
from pathlib import Path
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_后背粗发束收细_v38_20261026');S=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_五处局部收口_v36_20261025')
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v36五处局部收口_待验收.blend'));before=np.array([v.co[:] for v in bpy.data.objects['textured_mesh.obj'].data.vertices])
bpy.ops.wm.open_mainfile(filepath=str(D/'小秦_v38后背粗发束收细.blend'));body=bpy.data.objects['textured_mesh.obj'];m=body.data;after=np.array([v.co[:] for v in m.vertices]);restored=set()
for attempt in range(100):
 m.vertices.foreach_set('co',after.astype(np.float32).ravel());m.update();m.calc_loop_triangles();after=np.array([v.co[:] for v in m.vertices]);tri=np.empty(len(m.loop_triangles)*3,np.int32);m.loop_triangles.foreach_get('vertices',tri);tri=tri.reshape(-1,3)
 a=np.cross(before[tri[:,1]]-before[tri[:,0]],before[tri[:,2]]-before[tri[:,0]]);b=np.cross(after[tri[:,1]]-after[tri[:,0]],after[tri[:,2]]-after[tri[:,0]]);bad=(a*b).sum(1)<-1e-24
 if not bad.any():break
 pi=np.empty(len(m.loop_triangles),np.int32);m.loop_triangles.foreach_get('polygon_index',pi);ids=set()
 for fi in np.unique(pi[bad]):ids.update(m.polygons[int(fi)].vertices)
 restored.update(ids);ids=list(ids);after[ids]=before[ids]
assert not bad.any(),'Unable to remove face reversals'
print('FINAL_REVERSALS',int(bad.sum()),'RESTORED',len(restored),'PASSES',attempt)
# Recompute only changed hair normals after the final coordinate check.
changed=np.linalg.norm(after-before,axis=1)>1e-9;vn=np.zeros_like(after);cross=np.cross(after[tri[:,1]]-after[tri[:,0]],after[tri[:,2]]-after[tri[:,0]])
for j in range(3):np.add.at(vn,tri[:,j],cross)
vn/=np.maximum(np.linalg.norm(vn,axis=1)[:,None],1e-20);cn=np.empty(len(m.loops)*3,np.float32);m.corner_normals.foreach_get('vector',cn);cn=cn.reshape(-1,3);lv=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',lv);cm=changed[lv];cn[cm]=vn[lv[cm]];m.normals_split_custom_set(cn.tolist());m.update()
r=json.loads((D/'实际发束收细校验.json').read_text(encoding='utf8'));r['reversed_triangles_diagnostic']=0;r['local_vertices_restored_for_orientation']=len(restored);r['changed_hair_vertices']=int(changed.sum());(D/'实际发束收细校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');np.savez_compressed(D/'发束位移记录.npz',ids=np.flatnonzero(changed),before=before[changed],after=after[changed])
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v38后背粗发束收细.blend'));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v38后背粗发束收细.glb'),use_selection=True,export_format='GLB')
