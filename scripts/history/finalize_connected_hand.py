import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_手部精修_20261019';bpy.ops.wm.open_mainfile(filepath=str(D/'hand-connected-work.blend'));s=bpy.context.scene;o=max((x for x in s.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));m=o.data.materials[0]
for nod,file,space in [('Image Texture','hand-clean-skin-atlas.png','sRGB'),('Image Texture.001','hand-matte-orm-atlas.png','Non-Color')]:
 im=bpy.data.images.load(str(D/file));im.colorspace_settings.name=space;im.pack();m.node_tree.nodes[nod].image=im
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
for name,target,pos,scale in [('raised-front-after',(.018,0,.065),(.018,-.2,.065),.020),('raised-side-after',(.018,-.009,.064),(.13,-.16,.070),.020),('lower-front-after',(-.022,-.01,.032),(-.022,-.2,.032),.019)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6手部精修.blend'));bpy.ops.object.select_all(action='DESELECT')
for a in s.objects:
 if a.type=='MESH':a.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6手部精修.glb'),use_selection=True,export_format='GLB');o.data=full
print('CONNECTED_HAND_FINAL_DONE')
