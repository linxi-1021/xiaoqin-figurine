import bpy,json,struct,hashlib,collections
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'bag-v12';s=(r/'export_no_bag_v10.py').read_text(encoding='utf-8');exec(s[s.index('def fingerprint'):s.index('bpy.ops.wm.open_mainfile')])
results={}
for tag,file in [('before',r/'bag-v11/小秦_圆柱小熊斜挎包.blend'),('after',out/'小秦_贴衣圆柱小熊包.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));results[tag]={kind:fingerprint(b,kind) for kind in ['legs','outside_strap']}
report={k:{'unchanged':results['before'][k]==results['after'][k],'faces':sum(results['after'][k].values())} for k in results['before']};assert all(v['unchanged'] for v in report.values());(out/'character-preservation-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PRESERVED',json.dumps(report))
