import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_底面留白收敛_v22_20261021/小秦_v6底面留白收敛.blend')
for name in ['GEO-Flush inset underside engraving','GEO-Recessed 小秦天天开心 dark fill']:
 o=bpy.data.objects[name];ps=[o.matrix_world@v.co for v in o.data.vertices];print(name, min(p.z for p in ps),max(p.z for p in ps),len(o.data.vertices),[(i,len([f for f in o.data.polygons if f.normal.z*i>.9])) for i in [-1,1]])
