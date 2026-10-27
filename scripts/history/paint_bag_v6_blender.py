import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v6';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'detail-v5/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
texpath=out/'小熊包_清晰五官图案.png'
texture=bpy.data.images.load(str(texpath));texture.name='Bear bag clean face 1024';texture.pack()
base=body.data.materials[0];material=base.copy();material.name='Bear bag clean face paint';nodes=material.node_tree.nodes;links=material.node_tree.links
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');previous=bs.inputs['Base Color'].links[0].from_socket
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='BearBagFaceUV'
tex=nodes.new('ShaderNodeTexImage');tex.image=texture;tex.extension='CLIP';links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';links.new(previous,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(tex.outputs['Alpha'],mix.inputs[0]);links.new(mix.outputs[0],bs.inputs['Base Color'])
for socket,value in [('Roughness',.9),('Metallic',0),('Coat Weight',0),('Specular IOR Level',.12)]:
 if socket in bs.inputs:
  for link in list(bs.inputs[socket].links):links.remove(link)
  bs.inputs[socket].default_value=value
for link in list(bs.inputs['Normal'].links):links.remove(link)
body.data.materials.append(material);matindex=len(body.data.materials)-1
uv=body.data.uv_layers.new(name='BearBagFaceUV')
co=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)
cx=-.0107;cz=.0368;angle=math.radians(20);c=math.cos(angle);s=math.sin(angle)
dx=co[:,0]-cx;dz=co[:,2]-cz
uu=(dx*c-dz*s)/.009+.5;vv=(dx*s+dz*c)/.0115+.5
loopverts=np.empty(len(body.data.loops),dtype=np.int32);body.data.loops.foreach_get('vertex_index',loopverts)
uvdata=np.column_stack([uu[loopverts],vv[loopverts]]).astype(np.float32);uv.data.foreach_set('uv',uvdata.ravel())
painted=0
for p in body.data.polygons:
 center=p.center;x,y,z=center;dx=x-cx;dz=z-cz;u=(dx*c-dz*s)/.009+.5;v=(dx*s+dz*c)/.0115+.5
 if -.019<y<-.009 and ((u-.5)/.53)**2+((v-.5)/.53)**2<1 and p.normal.y<-.18:
  p.material_index=matindex;painted+=1
# New UV layer must not become the implicit UV for original body texture nodes.
body.data.uv_layers.active_index=0;body.data.uv_layers[0].active_render=True
for n in base.node_tree.nodes:
 if n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:
  uv0=base.node_tree.nodes.new('ShaderNodeUVMap');uv0.uv_map=body.data.uv_layers[0].name;base.node_tree.links.new(uv0.outputs['UV'],n.inputs['Vector'])
for n in nodes:
 if n.type=='TEX_IMAGE' and n!=tex and not n.inputs['Vector'].is_linked:
  uv0=nodes.new('ShaderNodeUVMap');uv0.uv_map=body.data.uv_layers[0].name;links.new(uv0.outputs['UV'],n.inputs['Vector'])
s=bpy.context.scene;s.cycles.samples=24;s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
cam.location=(-.014,-.3,.032);cam.rotation_euler=(Vector((-.014,0,.032))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(out/'bag-after.png');bpy.ops.render.render(write_still=True)
s.render.resolution_x=1000;s.render.resolution_y=1200
for name,angle in [('front',0),('threequarter',35),('back',180)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;full=body.data.copy();mod=body.modifiers.new('Web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB');body.data=full
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'))
(out/'bag-pattern-changes.json').write_text(json.dumps({'reference_crop':'41_小熊包正面.png','resolution':[1024,1024],'painted_polygons':painted,'method':'localized UV-projected alpha-blended clean bear face; underlying original texture retained','geometry_changed':False,'stl_geometry':'unchanged from v5','features':['paired oval eyes with highlights','rounded brown nose','continuous small mouth','warm cream muzzle','original perimeter seam retained']},ensure_ascii=False,indent=2),encoding='utf-8')
print('BAG_PATTERN_DONE',painted)
