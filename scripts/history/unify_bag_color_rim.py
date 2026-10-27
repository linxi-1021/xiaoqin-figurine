import bpy,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包脸上下居中_20261019';D=B/'3D重建_v6基础_小熊包统一底色_20261019'
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包脸上下居中.blend'))
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
before=signature();cream=[242/255,211/255,177/255];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in cream]
img=bpy.data.images.load(str(D/'小熊包_统一奶油底色.png'));img.colorspace_settings.name='sRGB';img.pack()
changed=[]
for m in o.data.materials:
 if not ('Legacy wrong-side' in m.name or 'Bear bag physical surface' in m.name):continue
 m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();p=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial');l.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*linear,1);p.inputs['Roughness'].default_value=.82;p.inputs['Specular IOR Level'].default_value=.16
 if 'physical surface' in m.name:
  t=n.new('ShaderNodeTexImage');t.image=img;t.extension='EXTEND';uv=n.new('ShaderNodeUVMap');uv.uv_map='BearBagSurfaceUV';l.new(uv.outputs['UV'],t.inputs['Vector']);l.new(t.outputs['Color'],p.inputs['Base Color'])
 changed.append(m.name)
assert len(changed)==2;assert before==signature()
r=json.loads((D/'表面坐标与投影校验.json').read_text(encoding='utf-8'));cc=Vector(r['center_surface_m']);nn=Vector(r['normal']);uu=Vector(r['right']);vv=Vector(r['up']);extra=0
for f in o.data.polygons:
 q=f.center-cc; a=q.dot(uu); b=q.dot(vv); depth=q.dot(nn)
 if f.material_index==0 and (a/.00635)**2+(b/.0068)**2<1 and -.0038<depth<.0018 and f.normal.dot(nn)>0:
  f.material_index=2;extra+=1
print('Additional bag rim faces',extra)
after_assignment=signature()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
r=json.loads((D/'表面坐标与投影校验.json').read_text(encoding='utf-8'));W=o.matrix_world;C=W@Vector(r['center_surface_m']);N=(W.to_3x3()@Vector(r['normal'])).normalized();U=(W.to_3x3()@Vector(r['right'])).normalized();V=(W.to_3x3()@Vector(r['up'])).normalized();cam=s.camera;s.render.resolution_x=900;s.render.resolution_y=900
for name,ang in [('bag-face-normal.png',0),('bag-oblique-55.png',55)]:
 a=math.radians(ang);back=N*math.cos(a)+U*math.sin(a);cam.location=C+back*.09;right=V.cross(back).normalized();up=back.cross(right).normalized();cam.rotation_euler=Matrix((right,up,back)).transposed().to_euler();cam.data.ortho_scale=.020;s.render.filepath=str(D/name);bpy.ops.render.render(write_still=True)
assert after_assignment==signature();bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6小熊包统一底色.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in s.objects:
 if ob.type=='MESH':ob.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6小熊包统一底色.glb'),use_selection=True,export_format='GLB');o.data=full
(D/'材质修改校验.json').write_text(json.dumps({'geometry_and_uv_unchanged':True,'bag_rim_material_faces':extra,'material_assignments_stable_after_local_rim_fix':after_assignment==signature(),'mesh_count':len(before),'changed_materials':changed,'uniform_base_srgb':[242,211,177],'face_position_preserved':True},ensure_ascii=False,indent=2),encoding='utf-8');print('UNIFORM_COLOR_DONE')
