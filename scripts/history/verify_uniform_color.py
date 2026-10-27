import bpy,numpy as np,hashlib,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包脸上下居中_20261019';D=B/'3D重建_v6基础_小熊包统一底色_20261019'
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));r={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256()
  for coll,key,dt,k in [(o.data.vertices,'co',np.float32,3),(o.data.loops,'vertex_index',np.int32,1)]:
   a=np.empty(len(coll)*k,dt);coll.foreach_get(key,a);h.update(a.tobytes())
  for uv in o.data.uv_layers:
   a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  h.update(np.array(o.matrix_world).tobytes());r[o.name]=h.hexdigest()
 return r
a=read(S/'小秦_v6包脸上下居中.blend');b=read(D/'小秦_v6小熊包统一底色.blend');assert a==b
(D/'独立几何校验.json').write_text(json.dumps({'passed':True,'mesh_count':len(a),'coordinates_topology_all_uvs_transforms_identical':True},ensure_ascii=False,indent=2),encoding='utf8');print('VERIFIED 21 meshes geometry and UVs identical')
