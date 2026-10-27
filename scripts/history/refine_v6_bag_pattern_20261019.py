import bpy,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
BASE=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');SRC=BASE/'3D重建_小熊包图案优化_v6';OUT=BASE/'3D重建_v6基础_小熊包图案细修_20261019'
source_sha=hashlib.sha256((SRC/'小秦_重建模型.blend').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC/'小秦_重建模型.blend'))
def mesh_hashes():
 result={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256()
  for data,prop,dtype,count in [(o.data.vertices,'co',np.float32,3),(o.data.loops,'vertex_index',np.int32,1),(o.data.polygons,'material_index',np.int32,1)]:
   a=np.empty(len(data)*count,dtype=dtype);data.foreach_get(prop,a);h.update(a.tobytes())
  for uv in o.data.uv_layers:
   a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  h.update(np.array(o.matrix_world).tobytes());result[o.name]={'sha256':h.hexdigest(),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}
 return result
before=mesh_hashes();old=bpy.data.images['Bear bag final baked color 1024'];new=bpy.data.images.load(str(OUT/'小熊包_参考细节校正版_2048.png'));new.name='Bear bag reference face 2048';new.colorspace_settings.name='sRGB';new.pack();changed=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image==old:n.image=new;changed.append(m.name)
assert changed and mesh_hashes()==before
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.type=='OPTIX' for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
cam=s.camera
s.render.resolution_x=1000;s.render.resolution_y=1000
cam.location=(-.014,-.3,.032);cam.rotation_euler=(Vector((-.014,0,.032))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(OUT/'bag-after.png');bpy.ops.render.render(write_still=True)
s.render.resolution_x=1000;s.render.resolution_y=1200
for name,angle in [('front',0),('threequarter',35),('back',180)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
assert mesh_hashes()==before
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'小秦_v6包面细修.blend'))
body=max((o for o in s.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));original_mesh=body.data;body.data=original_mesh.copy()
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(OUT/'小秦_v6包面细修.glb'),use_selection=True,export_format='GLB')
body.data=original_mesh
assert mesh_hashes()==before
assert hashlib.sha256((SRC/'小秦_重建模型.blend').read_bytes()).hexdigest()==source_sha
report={'source_version':'v6','source_blend':str(SRC/'小秦_重建模型.blend'),'source_sha256':source_sha,'source_unchanged':True,'geometry_uv_material_assignments_unchanged':True,'mesh_preservation':before,'changed_texture_materials':changed,'texture_resolution':[2048,2048],'reference':'42_小熊包脸与包耳.png + 41_小熊包正面.png','changes':['deeper cocoa oval eyes with tiny upper-left highlights','smaller rounded nose with warm highlight','compact continuous rounded W mouth','remove large contrasting muzzle oval; preserve original bag border and ears'],'method':'Blender UV-texturing skill via explicit native bpy adaptation; reuse v6 bag UV and material slot; swap only active baked bag colour image','glb_optimization':'same 0.3 character mesh ratio as v6; editable blend remains full detail','print_note':'colour-pattern change only; no new embossed geometry or production-print certification'}
(OUT/'包面修改与保留校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('V6_PATTERN_REFINEMENT_DONE',json.dumps(report,ensure_ascii=True))
