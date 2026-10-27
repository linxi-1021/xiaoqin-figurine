import bpy,numpy as np,json
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_祝福语微右移_v29_20261021/小秦_v6祝福语微右移.blend')
for o in bpy.context.scene.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ['pedestal','inset','collar','recessed','qr']):
  a=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);print(o.name,len(a),a.min(0).tolist(),a.max(0).tolist())
