import bpy,numpy as np,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_柔和圆角底座_v31_20261022';D=B/'3D重建_v6基础_帽绒耳旁防穿模_v32_20261025';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6柔和圆角底座.blend'))
yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data
co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co)
centers=co.mean(1);mi=np.array([old.polygons[i*142].material_index for i in range(ns)],np.int32)
q=(centers-np.array([.00666,0,.10105]))@np.array([.342,0,.94]);u=(centers-np.array([.00666,0,.10105]))@np.array([.94,0,-.342])
# Trim only the lower anterior temple overgrowth; the outer brim and rear hat stay intact.
wrong_ivory=(mi>=5)&(mi<10)&(q<-.010)&(centers[:,1]>-.020)&(abs(u)>.012)
wrong_lower=(q<-.021)&(centers[:,1]<-.002)&(abs(u)>.012)
remove=wrong_ivory|wrong_lower
ids=np.flatnonzero(~remove);out=co[ids];mi=mi[ids];assert np.array_equal(out,co[ids])
report={'removed_strands':int(remove.sum()),'left':int((remove&(u<0)).sum()),'right':int((remove&(u>0)).sum()),'remaining_strands_unchanged':True,'other_objects_unchanged':True}
print(json.dumps(report))
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
new=bpy.data.meshes.new('Matched front and rear thick yarn');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new


(D/'帽绒越界清理校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6帽绒耳旁防穿模.blend'))
bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6帽绒耳旁防穿模.glb'),use_selection=True,export_format='GLB')

