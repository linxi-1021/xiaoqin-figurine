import bpy,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_小熊包统一底色_20261019');bpy.ops.wm.open_mainfile(filepath=str(B/'小秦_v6小熊包统一底色.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));print([(i,m.name) for i,m in enumerate(o.data.materials)]);print(json.loads((B/'表面坐标与投影校验.json').read_text(encoding='utf8'))['center_surface_m'])
