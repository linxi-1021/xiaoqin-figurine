import bpy,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_前星星发夹修正_20261020/小秦_v6前星星发夹修正.blend');o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());cam=Vector((.012,-.085,.053));target=Vector((.006,-.013,.094));fw=(target-cam).normalized();right=fw.cross(Vector((0,0,1))).normalized();up=right.cross(fw).normalized();V=Vector((.342,0,.94)).normalized();origin=Vector((.00666,0,.10105))
for px,py in [(475,350),(600,395),(325,350),(500,400),(425,570),(580,570),(490,480)]:
 direction=(fw+right*((2*px/1000-1)*math.tan(math.radians(16))*1000/850)+up*((1-2*py/850)*math.tan(math.radians(16)))).normalized();hit=tree.ray_cast(cam,direction)
 if hit[0]:print('PIXEL',px,py,'CO',list(hit[0]),'Q',(hit[0]-origin).dot(V),'NV',hit[1].dot(V))
