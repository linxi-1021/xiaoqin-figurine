import bpy,bmesh,json
from pathlib import Path
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_底面融合字槽修复_v23_20261021');bpy.ops.wm.open_mainfile(filepath=str(D/'小秦_v6底面融合字槽修复.blend'));r={}
for name in ['GEO-Flush inset underside engraving','GEO-Uniform recessed 小秦天天开心 fill','GEO-Scannable recessed QR code']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);r[name]={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'vertices':len(bm.verts)};bm.free()
(D/'底面网格校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r));assert all(v['boundary_edges']==0 and v['nonmanifold_edges']==0 for v in r.values())
