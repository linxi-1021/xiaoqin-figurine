import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;out=r/'refined';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'review/小秦_重建模型.blend'))
body=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM');bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=body.modifiers.new('Weld duplicated UV boundary vertices','WELD');mod.merge_threshold=.0000001
bpy.ops.object.modifier_apply(modifier=mod.name)
for p in body.data.polygons:p.use_smooth=True
mod=body.modifiers.new('Gentle surface cleanup','SMOOTH');mod.factor=.18;mod.iterations=2
bpy.ops.object.modifier_apply(modifier=mod.name)
for m in body.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':n.inputs['Roughness'].default_value=.72;n.inputs['Metallic'].default_value=0
bvh=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
def surface(x,z):
 origin=Vector((x,.15,z));hit=bvh.ray_cast(body.matrix_world.inverted()@origin,Vector((0,-1,0)))
 return (body.matrix_world@hit[0]).y if hit[0] is not None else .02
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.65;return m
cream=mat('Warm cream ribbon',(.91,.81,.64));gold=mat('Honey gold stars',(.89,.56,.15));white=mat('Daisy ivory petals',(.96,.9,.78))
def tube(name,points,radius,material,cyclic=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=4;c.resolution_u=16
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for b,p in zip(s.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def bead(name,x,y,z,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=(x,y,z));o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def star(name,x,z,size):
 y=surface(x,z)+.0007;vs=[]
 for depth in [0,.001]:
  for i in range(10):
   a=math.pi/2+i*math.pi/5;rr=size*(1 if i%2==0 else .46);vs.append((x+rr*math.cos(a),y+depth,z+rr*math.sin(a)))
 faces=[tuple(reversed(range(10))),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(gold);mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=.00025;mod.segments=3
 return o
# Bow sits on the rear hat, above the hairline. Curves follow the measured cap surface.
cx=0;cz=.0925;cy=surface(cx,cz)+.0012
for side in [-1,1]:
 tube('Hat bow loop '+str(side),[(0,cy,cz),(side*.005,cy+.0015,cz+.003),(side*.009,cy,cz+.0015),(side*.006,cy+.001,cz-.0025),(0,cy,cz)],.00125,cream,True)
 tube('Hat bow tail '+str(side),[(side*.001,cy,cz-.001),(side*.003,surface(side*.003,cz-.005)+.0018,cz-.005),(side*.004,surface(side*.004,cz-.009)+.0016,cz-.009)],.001,cream)
bead('Bow central knot',0,cy+.0006,cz,(.002,.0017,.002),cream)
star('Ribbon hanging star',.004,cz-.010,.0017)
for i,(x,z) in enumerate([(-.012,.070),(.012,.060)]):star('Hair star '+str(i+1),x,z,.002)
for i,(x,z) in enumerate([(.016,.065),(-.013,.056)]):
 y=surface(x,z)+.001
 for j in range(5):
  a=j*math.tau/5;bead('Daisy %d petal %d'%(i+1,j+1),x+.0015*math.cos(a),y,z+.0015*math.sin(a),(.001,.00065,.0013),white)
 bead('Daisy %d center'%(i+1),x,y+.0006,z,(.0009,.0007,.0009),gold)
# Export body and embellishments only; keep lights and camera out of geometry exports.
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.context.scene.objects):
 if o.type in {'MESH','CURVE'}:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB')
s=bpy.context.scene;s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1200
cam=s.camera
for name,angle in [('front',0),('side',90),('back',180),('threequarter',35),('backthreequarter',145)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'))
print('REFINED_COMPLETE')
