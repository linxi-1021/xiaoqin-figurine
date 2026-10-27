import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v8/小秦_重建模型.blend'))
o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();loc=c+n*.012+u*.15;rot=(c-loc).to_track_quat('-Z','Y');right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));direction=(c-loc).normalized()
report=[]
for px,py in [(450,280),(430,320),(410,370),(432,230),(450,400)]:
 origin=loc+right*((px-300)*.024/600)+up*((300-py)*.024/600);h=tree.ray_cast(origin,direction)
 if h[0] is not None:
  face=o.data.polygons[h[2]];q=h[0]-c;report.append({'pixel':[px,py],'hit':list(h[0]),'material':o.data.materials[face.material_index].name,'face_index':h[2],'local':[q.dot(u),q.dot(n)],'poly_center':list(face.center)})
print(json.dumps(report))
