import bpy,numpy as np,hashlib,json,bmesh
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_蝴蝶结吊星结构精修_v11_20261021'
def hashes():
 r={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.name.startswith('Ribbon') or 'attachment' in o.name:continue
  a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);r[o.name]=hashlib.sha256(a.tobytes()+np.array(o.matrix_world).tobytes()).hexdigest()
 return r
bpy.ops.wm.open_mainfile(filepath=str(B/'3D重建_v6基础_帽檐上部补绒_v10_20261021/小秦_v6帽檐上部补绒.blend'));before=hashes();bpy.ops.wm.open_mainfile(filepath=str(D/'小秦_v6蝴蝶结吊星结构精修.blend'));after=hashes();assert before==after
r={'unchanged_meshes_verified':len(before),'all_non_accessory_meshes_exact':before==after,'accessories':{}}
for o in bpy.context.scene.objects:
 if o.type=='MESH' and (o.name.startswith('Ribbon') or 'attachment' in o.name):
  bm=bmesh.new();bm.from_mesh(o.data);r['accessories'][o.name]={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free()
assert all(v['nonmanifold_edges']==0 for v in r['accessories'].values());(D/'独立网格校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
