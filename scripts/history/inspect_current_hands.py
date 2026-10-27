import bpy,math
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_手部精修_20261019';D.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));s=bpy.context.scene;s.render.resolution_x=900;s.render.resolution_y=900;s.cycles.samples=16;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
cam=s.camera
for name,target,pos,scale in [('raised-front-before',(.018,0,.065),(.018,-.2,.065),.020),('raised-side-before',(.018,0,.065),(.18,-.10,.065),.021),('lower-front-before',(-.022,-.01,.032),(-.022,-.2,.032),.019)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
