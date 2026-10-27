import bpy,json,numpy as np
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_柔褶蝴蝶结圆润星_v13_20261021/小秦_v6柔褶蝴蝶结圆润星.blend')
for o in bpy.context.scene.objects:
 if o.type=='MESH' and 'star' in o.name.lower():
  p=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);print(o.name,len(p),p.mean(0),np.ptp(p,axis=0))
