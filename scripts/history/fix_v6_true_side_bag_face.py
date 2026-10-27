import bpy,bmesh,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');SRC=B/'3D重建_v6基础_小熊包图案细修_20261019';OUT=B/'3D重建_v6基础_按人物侧面校正包脸_20261019'
bpy.ops.wm.open_mainfile(filepath=str(SRC/'小秦_v6包面细修.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 if any(d.type=='OPTIX' for d in p.devices):s.cycles.device='GPU'
except Exception:pass
v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);v=v.reshape(-1,3);geom_before=hashlib.sha256(v.tobytes()).hexdigest()
uv0=np.empty(len(o.data.uv_layers[0].data)*2,np.float32);o.data.uv_layers[0].data.foreach_get('uv',uv0);uv0_hash=hashlib.sha256(uv0.tobytes()).hexdigest()
mi=next(i for i,m in enumerate(o.data.materials) if 'Bear bag' in m.name);faces=[f.index for f in o.data.polygons if f.material_index==mi]
tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());C=tree.ray_cast(Vector((-.05,-.0095,.0358)),Vector((1,0,0)))[0]
normals=[]
for dx in np.linspace(-.0008,.0008,5):
 for dz in np.linspace(-.0008,.0008,5):
  hit,n,idx,dist=tree.ray_cast(Vector((-.05,C.y+dx,C.z+dz)),Vector((1,0,0)))
  if hit is not None:normals.append(n)
N=sum(normals,Vector()).normalized();V=Vector((0,0,1));V=(V-N*V.dot(N)).normalized();U=V.cross(N).normalized();V=N.cross(U).normalized();span=.0120
W=o.matrix_world;cw=W@C;nw=(W.to_3x3()@N).normalized();uw=(W.to_3x3()@U).normalized();vw=(W.to_3x3()@V).normalized()
cam=s.camera;s.render.resolution_x=900;s.render.resolution_y=900

def local_view(name,ang=0):
 a=math.radians(ang);direction=(nw*math.cos(a)+uw*math.sin(a));cam.location=cw+direction*.09;back=direction.normalized();right=vw.cross(back).normalized();up=back.cross(right).normalized();cam.rotation_euler=Matrix((right,up,back)).transposed().to_euler();cam.data.ortho_scale=.020;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
local_view('projection-before.png')
legacy=o.data.materials[mi].copy();legacy.name='Legacy wrong-side bag face erased';nn=legacy.node_tree.nodes;ll=legacy.node_tree.links;bb=nn.get('Principled BSDF');ci=bpy.data.images.load(str(OUT/'小熊包_原包面无五官底色.png'));ci.pack();cn=nn.new('ShaderNodeTexImage');cn.image=ci;cu=nn.new('ShaderNodeUVMap');cu.uv_map='BearBagFaceUV';ll.new(cu.outputs['UV'],cn.inputs['Vector']);ll.new(cn.outputs['Color'],bb.inputs['Base Color']);o.data.materials[mi]=legacy
old_mi=mi;mi=len(o.data.materials)
faces=[]
for f in o.data.polygons:
 q=f.center-C;xx=q.dot(U);zz=q.dot(V);dd=q.dot(N)
 if (xx/.0056)**2+(zz/.0062)**2<1 and -.0035<dd<.0015 and f.normal.dot(N)>.25 and -.0175<f.center.x<-.0105 and -.016<f.center.y<-.0045 and .029<f.center.z<.043:faces.append(f.index)
assert len(faces)>300, len(faces)
mask_attr=o.data.color_attributes.new(name='TEMP_BagOriginalMask',type='BYTE_COLOR',domain='CORNER')
for fi in faces:
 if o.data.polygons[fi].material_index==old_mi:
  for li in o.data.polygons[fi].loop_indices:mask_attr.data[li].color=(1,1,1,1)

# Tangent-frame UV uses all three spatial coordinates, equal physical scales.
uv=o.data.uv_layers.new(name='BearBagSurfaceUV');loops=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',loops);q=v-np.array(C);coords=np.column_stack((q@np.array(U)/span+.5,q@np.array(V)/span+.5)).astype(np.float32);uv.data.foreach_set('uv',coords[loops].ravel())
base=o.data.materials[0];m=base.copy();m.name='Bear bag physical surface projection';bs=m.node_tree.nodes.get('Principled BSDF');links=m.node_tree.links;nodes=m.node_tree.nodes;old_color=bs.inputs['Base Color'].links[0].from_socket
clean=bpy.data.images.load(str(OUT/'小熊包_原包面无五官底色.png'));clean.pack();ct=nodes.new('ShaderNodeTexImage');ct.image=clean;cu=nodes.new('ShaderNodeUVMap');cu.uv_map='BearBagFaceUV';links.new(cu.outputs['UV'],ct.inputs['Vector']);at=nodes.new('ShaderNodeVertexColor');at.layer_name='TEMP_BagOriginalMask';under=nodes.new('ShaderNodeMixRGB');links.new(at.outputs['Color'],under.inputs[0]);links.new(old_color,under.inputs[1]);links.new(ct.outputs['Color'],under.inputs[2]);old_color=under.outputs[0]
for node in list(nodes):
 if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
  a=nodes.new('ShaderNodeUVMap');a.uv_map=o.data.uv_layers[0].name;links.new(a.outputs['UV'],node.inputs['Vector'])
art=bpy.data.images.load(str(OUT/'小熊包_局部表面图案.png'));art.colorspace_settings.name='sRGB';art.pack();t=nodes.new('ShaderNodeTexImage');t.image=art;t.extension='CLIP';u=nodes.new('ShaderNodeUVMap');u.uv_map=uv.name;links.new(u.outputs['UV'],t.inputs['Vector']);mix=nodes.new('ShaderNodeMixRGB');links.new(t.outputs['Alpha'],mix.inputs[0]);links.new(old_color,mix.inputs[1]);links.new(t.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
for nm,value in [('Roughness',.9),('Metallic',0),('Specular IOR Level',.12),('Coat Weight',0)]:
 if nm in bs.inputs:
  for link in list(bs.inputs[nm].links):links.remove(link)
  bs.inputs[nm].default_value=value
o.data.materials.append(m)
for fi in faces:o.data.polygons[fi].material_index=mi
# Checker is on the actual 3D face; no overlay plane is created.
size=512;yy,xx=np.mgrid[:size,:size];checker=np.ones((size,size,4),np.float32);checker[:,:,:3]=np.where(((xx//32+yy//32)%2)[:,:,None],np.array([.13,.36,.8]),np.array([.95,.95,.95]));ci=bpy.data.images.new('Bag surface checker',width=size,height=size,alpha=True);ci.pixels.foreach_set(checker.ravel());t.image=ci;local_view('surface-checker.png');t.image=art
# Bake only the existing bag-face polygons; original UV0 textures stay intact.
tmp=o.copy();tmp.data=o.data.copy();bpy.context.collection.objects.link(tmp);bm=bmesh.new();bm.from_mesh(tmp.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=mi],context='FACES');bmesh.ops.delete(bm,geom=[x for x in bm.verts if not x.link_faces],context='VERTS');bm.to_mesh(tmp.data);bm.free();tmp.data.materials.clear();tmp.data.materials.append(m.copy())
for f in tmp.data.polygons:f.material_index=0
tmp.data.uv_layers.active=tmp.data.uv_layers.get(uv.name);tmp.data.uv_layers.active.active_render=True;bake=bpy.data.images.new('Bag surface final 2048',width=2048,height=2048,alpha=False);bake.generated_color=(.85,.70,.55,1);bm=tmp.data.materials[0];target=bm.node_tree.nodes.new('ShaderNodeTexImage');target.image=bake;bm.node_tree.nodes.active=target
bpy.ops.object.select_all(action='DESELECT');tmp.select_set(True);bpy.context.view_layer.objects.active=tmp;s.cycles.samples=1;bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=16,use_clear=False);bake.filepath_raw=str(OUT/'小熊包_物理表面烘焙.png');bake.file_format='PNG';bake.save();bake.pack();bpy.data.objects.remove(tmp,do_unlink=True)
tt=nodes.new('ShaderNodeTexImage');tt.image=bake;tt.extension='EXTEND';links.new(u.outputs['UV'],tt.inputs['Vector']);links.new(tt.outputs['Color'],bs.inputs['Base Color']);o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True;o.data.color_attributes.remove(mask_attr);s.cycles.samples=24
local_view('bag-face-normal.png');local_view('bag-oblique-55.png',55);local_view('bag-oblique-minus-45.png',-45)
cam.location=(-.014,-.3,.032);cam.rotation_euler=(Vector((-.014,0,.032))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(OUT/'bag-after.png');bpy.ops.render.render(write_still=True)
s.render.resolution_y=1200;cam.location=(0,-.27,.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(OUT/'front.png');bpy.ops.render.render(write_still=True)
vv=np.empty(v.size,np.float32);o.data.vertices.foreach_get('co',vv);assert hashlib.sha256(vv.tobytes()).hexdigest()==geom_before
uv_after=np.empty(uv0.size,np.float32);o.data.uv_layers[0].data.foreach_get('uv',uv_after);assert hashlib.sha256(uv_after.tobytes()).hexdigest()==uv0_hash
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'小秦_v6侧面包脸校正.blend'))
bpy.ops.object.select_all(action='DESELECT')
for x in s.objects:
 if x.type=='MESH':x.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(OUT/'小秦_v6侧面包脸校正.glb'),use_selection=True,export_format='GLB');o.data=full
report={'base':'v6 geometry; corrected face is on character lateral side (-X)','geometry_unchanged':True,'original_uv0_unchanged':True,'wrong_side_pattern_erased':True,'true_face':'anatomical right bag face viewed from character side; -X outward','patch_faces':len(faces),'center_surface_m':list(C),'normal':list(N),'right':list(U),'up':list(V),'uv_span_m':[span,span],'orthogonality_error':max(abs(U.dot(V)),abs(U.dot(N)),abs(V.dot(N))),'method':'surface-measured tangent frame using XYZ; same physical U/V scale; artwork baked onto existing bag faces; no floating plane','validation_views':['surface-checker.png','bag-face-normal.png','bag-oblique-55.png','bag-oblique-minus-45.png'],'limits':'Tangent projection on the existing organic bag surface; no bag geometry redesign; no claim of zero-distortion global geodesic UV'}
(OUT/'表面坐标与投影校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('SURFACE_PROJECTION_DONE',json.dumps(report))
