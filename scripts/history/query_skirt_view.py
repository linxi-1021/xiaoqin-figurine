import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_鞋履收敛_v35_20261025/小秦_v6鞋履收敛.blend');body=bpy.data.objects['textured_mesh.obj'];tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());pos=Vector((.065,-.018,.018));tar=Vector((0,0,.037));f=(tar-pos).normalized();r=f.cross(Vector((0,0,1))).normalized();u=r.cross(f).normalized()
for x,y in [(500,450),(400,440),(300,530),(650,450),(700,500),(500,520)]:
 d=(f+r*((x/1000*2-1)*math.tan(math.radians(16))*1000/900)+u*((1-y/900*2)*math.tan(math.radians(16)))).normalized();hit=tree.ray_cast(pos,d);print(x,y,tuple(round(v*1000,3) for v in hit[0]),hit[2])
