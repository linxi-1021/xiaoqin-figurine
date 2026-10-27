import bpy,bmesh,numpy as np,json,hashlib,shutil
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_鞋履收敛_v35_20261025';D=B/'3D重建_v6基础_五处局部收口_v36_20261025';D.mkdir(exist_ok=True);(D/'对照图').mkdir(exist_ok=True);(D/'过程备份').mkdir(exist_ok=True)
src=S/'小秦_v6鞋履收敛.blend';shutil.copy2(src,D/'过程备份'/'v35修改前.blend');bpy.ops.wm.open_mainfile(filepath=str(src))
report=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 co=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);report.append({'name':o.name,'vertices':len(co),'lo_mm':(co.min(0)*1000).tolist(),'hi_mm':(co.max(0)*1000).tolist(),'hash':hashlib.sha256(co.tobytes()).hexdigest()})
body=bpy.data.objects['textured_mesh.obj'];bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bound=[e for e in bm.edges if e.is_boundary];print('BODY_BOUNDARIES',len(bound),'NONMANIFOLD',sum(not e.is_manifold for e in bm.edges));print('BOUND_Z',sorted([round(e.verts[0].co.z*1000,1) for e in bound])[:30]);bm.free()
(D/'baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
