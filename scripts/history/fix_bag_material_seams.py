import bpy,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_毛衣针织包面_20261019';D=B/'3D重建_v6基础_包身材质接缝修复_20261019'
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6毛衣针织包面.blend'))
s=bpy.context.scene;o=max((x for x in s.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices))
def signature():
 result={}
 for ob in s.objects:
  if ob.type!='MESH':continue
  h=hashlib.sha256()
  for coll,key,dtype,n in [(ob.data.vertices,'co',np.float32,3),(ob.data.loops,'vertex_index',np.int32,1),(ob.data.polygons,'material_index',np.int32,1)]:
   a=np.empty(len(coll)*n,dtype);coll.foreach_get(key,a);h.update(a.tobytes())
  for uv in ob.data.uv_layers:
   a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  h.update(np.array(ob.matrix_world).tobytes());result[ob.name]=h.hexdigest()
 return result
before=signature()
m=o.data.materials[0]
for node,file,space in [(m.node_tree.nodes.get('Image Texture'),'原UV_包身连续布纹.png','sRGB'),(m.node_tree.nodes.get('Image Texture.001'),'原UV_包身连续粗糙度.png','Non-Color')]:
 im=bpy.data.images.load(str(D/file));im.colorspace_settings.name=space;im.pack();node.image=im
changed=['PBR_Material: locally repainted atlas only; original front shaders preserved']
assert before==signature()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
r=json.loads((D/'表面坐标与投影校验.json').read_text(encoding='utf-8'));W=o.matrix_world;C=W@Vector(r['center_surface_m']);N=(W.to_3x3()@Vector(r['normal'])).normalized();U=(W.to_3x3()@Vector(r['right'])).normalized();V=(W.to_3x3()@Vector(r['up'])).normalized();cam=s.camera;s.render.resolution_x=900;s.render.resolution_y=900
for name,ang in [('bag-oblique-75.png',75)]:
 a=math.radians(ang);back=N*math.cos(a)+U*math.sin(a);cam.location=C+back*.09;right=V.cross(back).normalized();up=back.cross(right).normalized();cam.rotation_euler=Matrix((right,up,back)).transposed().to_euler();cam.data.ortho_scale=.020;s.render.filepath=str(D/name);bpy.ops.render.render(write_still=True)
back=(N-V*.8+U*.3).normalized();cam.location=C+back*.09;right=V.cross(back).normalized();up=back.cross(right).normalized();cam.rotation_euler=Matrix((right,up,back)).transposed().to_euler();s.render.filepath=str(D/'bag-bottom.png');bpy.ops.render.render(write_still=True)
assert before==signature();bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6包身材质接缝修复.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in s.objects:
 if ob.type=='MESH':ob.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6包身材质接缝修复.glb'),use_selection=True,export_format='GLB');o.data=full
(D/'材质修改校验.json').write_text(json.dumps({'geometry_uv_transforms_material_assignments_unchanged':before==signature(),'mesh_count':len(before),'changed_materials':changed,'repair':'original UV0 atlas painted only in bag side and bottom region; same projected cloth coordinates as front; continuous transition to preserved surrounding atlas','face_position_preserved':True},ensure_ascii=False,indent=2),encoding='utf-8');print('UNIFORM_COLOR_DONE')


