import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_帽檐上部补绒_v10_20261021/小秦_v6帽檐上部补绒.blend')
r=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('Ribbon' in o.name or 'attachment' in o.name):
  c=[o.matrix_world@v.co for v in o.data.vertices];r.append({'name':o.name,'min':list(map(min,zip(*c))),'max':list(map(max,zip(*c))),'center':list(sum(c,Vector())/len(c)),'vertices':len(c)})
Path('models/rebuild/bow_inventory.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
