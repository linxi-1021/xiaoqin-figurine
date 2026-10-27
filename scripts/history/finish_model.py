import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'finished';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'refined/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
changes=[]
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);boundary=[e for e in bm.edges if e.is_boundary]
 if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0);changes.append({'object':o.name,'closed_boundary_edges':len(boundary)})
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 if o!=body:
  # Sink ornaments into the rear surface rather than leave floating shells.
  if 'star' in o.name.lower():o.location.y-=.0011
  elif 'Daisy' in o.name:o.location.y-=.0010
  elif 'bow' in o.name.lower():o.location.y-=.0010
sub=body.modifiers.new('Surface refinement','SUBSURF');sub.levels=1;sub.render_levels=1
bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=sub.name)
# Keep a textured visual master; a separate fused mesh is used only for printing.
visual=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in visual:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'))
s=bpy.context.scene;s.cycles.samples=40;cam=s.camera
for name,angle in [('front',0),('side',90),('back',180),('threequarter',35),('backthreequarter',145)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.data.ortho_scale=.15;cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
# Duplicate the master so remeshing cannot damage its UVs or textures.
bpy.ops.object.select_all(action='DESELECT')
copies=[]
for o in visual:
 c=o.copy();c.data=o.data.copy();bpy.context.collection.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();p=bpy.context.object;p.name='Print solid 120mm'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
p.data.remesh_voxel_size=.00016;p.data.remesh_voxel_adaptivity=0
bpy.ops.object.voxel_remesh()
bm=bmesh.new();bm.from_mesh(p.data)
# Remove disconnected small islands: decorative features must be attached to the main solid.
unseen=set(bm.verts);groups=[]
while unseen:
 v=unseen.pop();group={v};stack=[v]
 while stack:
  v=stack.pop()
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in unseen:unseen.remove(w);group.add(w);stack.append(w)
 groups.append(group)
groups.sort(key=len,reverse=True)
removed=[len(g) for g in groups[1:]]
if len(groups)>1:bmesh.ops.delete(bm,geom=[v for g in groups[1:] for v in g],context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(p.data)
report={'status':'geometry_checked_pending_physical_print','voxel_size_mm':.16,'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_components_after':1,'removed_island_vertex_counts':removed,'faces':len(bm.faces),'volume_mm3':bm.calc_volume(signed=False)*1e9,'dimensions_mm':[d*1000 for d in p.dimensions],'repairs':changes,'limitations':['No physical resin test print or slicer support validation yet','Thin-feature strength requires material and printer parameters','Textured eyes and plaid are paint references, not raised geometry']};bm.free()
bpy.ops.wm.stl_export(filepath=str(out/'小秦_120mm_打印校验版.stl'),export_selected_objects=True,global_scale=1000)
(out/'geometry-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('PRINT_AUDIT',json.dumps(report,ensure_ascii=False))
