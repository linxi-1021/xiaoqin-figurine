import bpy,hashlib,numpy as np,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');s=B/'3D重建_v6基础_前星星发夹修正_20261020/小秦_v6前星星发夹修正.blend';d=B/'3D重建_v6基础_熊帽绒线细化_20261020'
def hashes(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));r={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  m=o.data;co=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',co);ids=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',ids);r[o.name]=hashlib.sha256(co.tobytes()+ids.tobytes()).hexdigest()
 return r
src=hashes(s);dst=hashes(d/'小秦_v6熊帽绒线细化.blend');r={'original_mesh_count':len(src),'unchanged_original_objects':all(dst.get(k)==v for k,v in src.items()),'added_objects':[k for k in dst if k not in src]};(d/'原模型保留校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(r)
