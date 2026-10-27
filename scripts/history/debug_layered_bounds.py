import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/全新分层重建_20261019/milestones/08_assembled.blend')
rows=[]
for o in bpy.context.scene.objects:
 if o.type not in {'MESH','CURVE'}:continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=min(v.z for v in ps);hi=max(v.z for v in ps);rows.append((hi-lo,lo,hi,o.name,list(o.location),list(o.scale)))
for row in sorted(rows,reverse=True)[:10]:print(row)
