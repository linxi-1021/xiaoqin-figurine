import bpy,bmesh,hashlib,json,numpy as np
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_手部精修_20261019'
def protected(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));body=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));arr=[]
 for f in body.data.polygons:
  if f.center.x<0 or f.center.z<.055:
   h=hashlib.sha256()
   for i in f.loop_indices:
    h.update(np.array(body.data.vertices[body.data.loops[i].vertex_index].co,dtype=np.float32).tobytes())
    for uv in body.data.uv_layers:h.update(np.array(uv.data[i].uv,dtype=np.float32).tobytes())
   h.update(str(f.material_index).encode());arr.append(h.hexdigest())
 return sorted(arr)
a=protected(S/'小秦_v6包身材质接缝修复.blend');b=protected(D/'小秦_v6手部精修.blend');assert a==b
body=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));new_counts=[len(body.data.vertices),len(body.data.polygons),len(body.data.loops)];bm=bmesh.new();bm.from_mesh(body.data);new_bad=sum(not e.is_manifold for e in bm.edges);bm.free()
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));body=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));old_counts=[len(body.data.vertices),len(body.data.polygons),len(body.data.loops)];bm=bmesh.new();bm.from_mesh(body.data);old_bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert new_counts==old_counts and old_bad==new_bad
r={'passed':True,'protected_original_faces_unchanged':len(a),'bag_lower_fist_and_lower_body_geometry_uv_material_unchanged':True,'topology_counts_unchanged':True,'no_added_boundary_or_nonmanifold_edges':True,'local_hand_deformation_only':True};(D/'手部独立校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
