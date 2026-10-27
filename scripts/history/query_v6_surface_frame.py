import bpy,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_小熊包图案优化_v6/小秦_重建模型.blend')
o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));mi=next(i for i,m in enumerate(o.data.materials) if 'Bear bag' in m.name);p=np.array([tuple(f.center) for f in o.data.polygons if f.material_index==mi]);print('PATCH',mi,len(p),p.min(0),p.max(0),p.mean(0))
t=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());rows=[]
for z in [.033,.034,.035,.036,.037,.038,.039]:
 row=[]
 for x in [-.014,-.012,-.01,-.008,-.006]:
  h,n,idx,dist=t.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)));row.append([round(x*1000),round(h.y*1000,2),[round(v,2) for v in n]])
 rows.append({'z':z*1000,'row':row})
print('GRID',json.dumps(rows))
