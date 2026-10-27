import bpy,numpy as np,hashlib,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_熊帽檐下包绒_v3_20261020';D=B/'3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020'
def inspect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));r={};front=None
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co)
  if o.name=='GEO-Redesigned hat solid plush tufts':
   a=co.reshape(-1,150,3);a=a[a.mean(1)[:,1]<=.003];front=hashlib.sha256(a.tobytes()).hexdigest();continue
  loops=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',loops);r[o.name]={'mesh':hashlib.sha256(co.tobytes()+loops.tobytes()).hexdigest(),'loc':np.array(o.matrix_world).tolist()}
 return r,front
old,of=inspect(S/'小秦_v6熊帽檐下包绒_v3.blend');new,nf=inspect(D/'小秦_v6后帽粗绒浮贴蝴蝶结_v4.blend');others=[k for k in old if not k.startswith('Ribbon')];bows=[k for k in old if k.startswith('Ribbon')];r={'front_yarn_hash_equal':of==nf,'unchanged_other_objects':all(old[k]==new[k] for k in others),'bow_local_shape_unchanged':all(old[k]['mesh']==new[k]['mesh'] for k in bows),'bow_y_translation_mm':{k:(new[k]['loc'][1][3]-old[k]['loc'][1][3])*1000 for k in bows},'added_objects':[k for k in new if k not in old]};r['passed']=r['front_yarn_hash_equal'] and r['unchanged_other_objects'] and r['bow_local_shape_unchanged'];(D/'独立保留校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r));assert r['passed']
