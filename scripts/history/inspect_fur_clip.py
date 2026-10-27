import bpy,json
from pathlib import Path
p=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_柔和圆角底座_v31_20261022/小秦_v6柔和圆角底座.blend');bpy.ops.wm.open_mainfile(filepath=str(p))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  print('OBJ',o.name,len(o.data.vertices),[round(x,5) for x in o.dimensions])
