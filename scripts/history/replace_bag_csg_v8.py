import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v8'
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v7/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
with bpy.data.libraries.load(str(r/'bag-v6/小秦_重建模型.blend'),link=False) as (src,dst):dst.objects=[name for name in src.objects if name.startswith('textured_mesh')]
original=max((o for o in dst.objects if o and o.type=='MESH'),key=lambda o:len(o.data.vertices));body.data=original.data.copy();bpy.data.objects.remove(original,do_unlink=True)
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();v=n.cross(u).normalized();u=v.cross(n).normalized()
parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and ('Bag round' in o.name or 'Bear bag ear' in o.name)]
before=len(body.data.polygons);steps=[]
for part in parts:
 cutter=part.copy();cutter.data=part.data.copy();bpy.context.collection.objects.link(cutter);cutter.name='TEMP old bag removal volume'
 center=c if 'Bag round' in part.name else c+u*((-1 if '-1' in part.name else 1)*.0046)+v*.0049-n*.0008
 for vert in cutter.data.vertices:
  p=cutter.matrix_world@vert.co;q=p-center;d=q.dot(n);radial=q-n*d
  # Cut the full original bag depth, with the front extended beyond its old bulging paint surface.
  if 'Bag round' in part.name:
   newd=d-.0048 if d<-.0017 else d+.002
  else:newd=d-.006 if d<-.0009 else d+.0015
  p=center+radial*1.025+n*newd;vert.co=cutter.matrix_world.inverted()@p
 bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
 mod=body.modifiers.new('Remove old fused bag volume','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);steps.append({'volume':part.name,'faces_after':len(body.data.polygons)});bpy.data.objects.remove(cutter,do_unlink=True)
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));report={'source':'restored uncompressed v6 body + v7 cylinder','method':'exact boolean difference of old body inside main bag and ear volumes','faces_before':before,'faces_after':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'cuts':steps,'new_bag_dimensions_mm':[11.6,3.4],'new_bag_geometry_changed':False,'old_v7_body_compression_removed':True};bm.to_mesh(body.data);bm.free()
(out/'old-bag-removal-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=800;s.render.resolution_y=800;cam=s.camera
for name,loc,target in [('bag-context',Vector((-.014,-.3,.032)),Vector((-.014,0,.032))),('bag-side',c+n*.065+u*.13,c),('bag-edge',c+n*.012+u*.15,c)]:
 cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=1000;s.render.resolution_y=1200
for name,angle in [('front',0),('threequarter',35),('back',180)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;full=body.data.copy();mod=body.modifiers.new('Web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB');body.data=full
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'));print('EXACT_REMOVAL_DONE',json.dumps(report,ensure_ascii=False))
