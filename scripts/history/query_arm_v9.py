import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'))
b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
for z in [.034,.038,.042,.046]:
 ps=[v.co for v in b.data.vertices if abs(v.co.z-z)<.0002 and -.026<v.co.x<-.016]
 print(z,[(min(p[i] for p in ps),max(p[i] for p in ps)) for i in range(3)])
