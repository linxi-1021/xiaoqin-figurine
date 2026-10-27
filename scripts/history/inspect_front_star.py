import bpy,json
from pathlib import Path
p=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_四指并拢保留长短_20261020/小秦_v6四指并拢.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
a=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  co=[o.matrix_world@v.co for v in o.data.vertices];a.append({'name':o.name,'verts':len(co),'min':[min(v[i] for v in co) for i in range(3)],'max':[max(v[i] for v in co) for i in range(3)]})
Path('models/rebuild/star_scene.json').write_text(json.dumps(a,indent=2),encoding='utf8')
