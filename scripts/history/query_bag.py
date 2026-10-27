import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'detail-v5/小秦_重建模型.blend'))
o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())
result=[]
for x,z in [(-.011,.037),(-.011,.038),(-.012,.037),(-.013,.039),(-.009,.039),(-.01,.035),(-.014,.035)]:
 h=tree.ray_cast(Vector((x,-.15,z)),Vector((0,1,0)));result.append({'xz':[x,z],'hit':list(h[0]) if h[0] else None,'normal':list(h[1]) if h[1] else None})
(r/'bag-v6/surface-query.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
