import bpy,numpy as np,hashlib,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_按人物侧面校正包脸_20261019'
def snapshot(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256()
  for data,prop,dt,n in [(o.data.vertices,'co',np.float32,3),(o.data.loops,'vertex_index',np.int32,1)]:
   a=np.empty(len(data)*n,dt);data.foreach_get(prop,a);h.update(a.tobytes())
  h.update(np.array(o.matrix_world).tobytes());out[o.name]=h.hexdigest()
 return out
original=B/'3D重建_小熊包图案优化_v6/小秦_重建模型.blend';sha=hashlib.sha256(original.read_bytes()).hexdigest();a=snapshot(original);b=snapshot(D/'小秦_v6侧面包脸校正.blend');assert a==b;assert sha==hashlib.sha256(original.read_bytes()).hexdigest();j=json.loads((D/'表面坐标与投影校验.json').read_text(encoding='utf-8'));assert j['normal'][0]<-.9;assert j['surface_position_check']=='PASS';j.update({'all_v6_mesh_geometry_hashes_match':True,'mesh_count':len(a),'source_v6_unchanged':True,'source_v6_sha256':sha});(D/'表面坐标与投影校验.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');print('ALL_V6_GEOMETRY_PRESERVED',len(a))
