import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_包耳基准对齐_20261019';bpy.ops.wm.open_mainfile(filepath=str(B/'3D重建_v6基础_小熊包图案细修_20261019/小秦_v6包面细修.blend'));o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());r=[]
for name,px,py in [('ear_left',540,52),('ear_right',742,156)]:
 x=-.014+(px-450)*.024/900;z=.032+(450-py)*.024/900;p,n,idx,dist=tree.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)));r.append({'name':name,'source_pixel':[px,py],'surface_center':list(p),'normal':list(n),'polygon':idx})
(D/'ear_landmarks.json').write_text(json.dumps({'source':'v6/bag-after.png, 900x900, calibrated front orthographic camera','method':'manually annotated visible inner-ear centres, raycast to original mesh; not hidden-volume centres','ears':r},indent=2),encoding='utf-8');print(json.dumps(r))
