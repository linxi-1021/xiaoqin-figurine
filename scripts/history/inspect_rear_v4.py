import bpy,json
from pathlib import Path
p=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_熊帽檐下包绒_v3_20261020/小秦_v6熊帽檐下包绒_v3.blend');bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if o.name.startswith('Ribbon') or 'plush tufts' in o.name:
  co=[o.matrix_world@v.co for v in o.data.vertices] if o.name.startswith('Ribbon') else []
  rows.append({'name':o.name,'v':len(o.data.vertices),'f':len(o.data.polygons),'bounds':[[min(v[i] for v in co),max(v[i] for v in co)] for i in range(3)] if co else None})
print(json.dumps(rows))
