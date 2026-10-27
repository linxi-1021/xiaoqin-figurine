import bpy,bmesh,math,json,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v8';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v7/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
# Undo the v7 compression on the original fused mesh, keeping all new cylinder objects intact.
with bpy.data.libraries.load(str(r/'bag-v6/小秦_重建模型.blend'),link=False) as (src,dst):dst.objects=[name for name in src.objects if name.startswith('textured_mesh')]
original=max((o for o in dst.objects if o and o.type=='MESH'),key=lambda o:len(o.data.vertices))
body.data=original.data.copy();bpy.data.objects.remove(original,do_unlink=True)
selection=json.loads((out/'old-bag-face-selection.json').read_text());ids=set(selection['faces'])
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table();before=len(bm.faces)
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in ids],context='FACES')
bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
surviving_original_faces=set(bm.faces)
surviving_original_vertices=set(bm.verts)
boundary=[e for e in bm.edges if e.is_boundary];caps=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[])
for f in caps:f.material_index=0;f.smooth=False
if caps:bmesh.ops.triangulate(bm,faces=caps)
# The old fused bag joins several surfaces, so its cut boundary can contain touching loops.
# Remove overfilled cap triangles, then close each simple boundary cycle independently.
excess=set()
for e in bm.edges:
 if len(e.link_faces)>2:
  ordered=sorted(e.link_faces,key=lambda f:f.calc_area())
  excess.update(ordered[:len(ordered)-2])
if excess:bmesh.ops.delete(bm,geom=list(excess),context='FACES')
bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES')
remaining={e for e in bm.edges if e.is_boundary};cycles=[]
while remaining:
 e=remaining.pop();path=[e.verts[0],e.verts[1]]
 while True:
  current=path[-1]
  candidates=[edge for edge in current.link_edges if edge in remaining]
  if not candidates:break
  edge=candidates[0];remaining.remove(edge);w=edge.other_vert(current)
  if w in path:
   j=path.index(w);cycle=path[j:]
   if len(cycle)>=3:cycles.append(cycle)
   path=path[:j+1]
  else:path.append(w)
for cycle in cycles:
 middle=bm.verts.new(sum((v.co for v in cycle),Vector())/len(cycle))
 for a,b in zip(cycle,cycle[1:]+cycle[:1]):
  f=bm.faces.new((a,b,middle));f.material_index=0
# Close the removed bag's attachment at the garment surface, not as a second bag-shaped slab.
# New faces have no original UV islands; give the small garment closures their own plain materials.
def closure_mat(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.9;body.data.materials.append(m);return len(body.data.materials)-1
coat_mat=closure_mat('Coat attachment closure',(.65,.53,.42));skirt_mat=closure_mat('Skirt attachment closure',(.095,.105,.14))
new_caps=[f for f in bm.faces if f not in surviving_original_faces]
closure_vertices={v for f in new_caps for v in f.verts}
for vert in closure_vertices:
 if vert in surviving_original_vertices:continue
 x,z=vert.co.x,vert.co.z
 t=max(0,min(1,(z-.0395)/.002));t=t*t*(3-2*t);radius=.0185-.004*t
 vert.co.y=.003-.0115*math.sqrt(max(.02,1-(x/radius)**2))
for f in new_caps:f.material_index=coat_mat if f.calc_center_median().z>.0405 else skirt_mat;f.smooth=True
# The replacement bag closes the attachment in the fused print mesh. Do not keep
# spanning filler faces in the visual assembly: they would recreate a visible slab.
bmesh.ops.delete(bm,geom=new_caps,context='FACES')
bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
report={'source':'v6 original mesh restored before cutting; v7 new cylinder retained','old_bag_faces_deleted':len(ids),'faces_before':before,'faces_after':len(bm.faces),'closure_boundary_edges_before':len(boundary),'boundary_edges_after':sum(e.is_boundary for e in bm.edges),'non_manifold_edges_after':sum(not e.is_manifold for e in bm.edges),'new_cylinder_objects':[o.name for o in bpy.context.scene.objects if o.type=='MESH' and ('Bag round' in o.name or 'Bear bag ear' in o.name)],'method':'delete semantically connected old-bag faces and close attachment openings; no hiding, shrinking or covering of old bag'}
report['method']='physically delete old bag faces; restore original garment and hand coordinates; remove spanning filler faces'
report['visual_assembly_attachment']='open assembly attachment; fused STL checked separately'
bm.to_mesh(body.data);bm.free();body.data.update()
(out/'old-bag-removal-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized()
v=n.cross(u).normalized()
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('Bag round' in o.name or 'Bear bag ear' in o.name or 'Bag circular' in o.name or o.name=='Circular seam'):
  o.location-=n*.0048
leather=bpy.data.materials.new('Clean bag connector leather');leather.use_nodes=True;leather.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.24,.10,1)
connector=bpy.data.curves.new('Clean lower strap connector','CURVE');connector.dimensions='3D';connector.bevel_depth=.0005;connector.bevel_resolution=4;connector.use_fill_caps=True
sp=connector.splines.new('BEZIER');sp.bezier_points.add(2)
for pt,co in zip(sp.bezier_points,[Vector((-.0098,-.003,.0465)),Vector((-.0096,-.006,.0435)),c+v*.0057-n*.0048]):pt.co=co;pt.handle_left_type='AUTO';pt.handle_right_type='AUTO'
obj=bpy.data.objects.new('Clean lower strap connector',connector);bpy.context.collection.objects.link(obj);connector.materials.append(leather)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
# Reconstruct the covered garment from the intact opposite side, keeping real knit/plaid UVs.
image=next(nd.image for nd in body.data.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image)
pixels=np.empty(image.size[0]*image.size[1]*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(image.size[1],image.size[0],4);uv0=body.data.uv_layers[0].data
keep=set()
for f in body.data.polygons:
 p=f.center
 if not(0<=p.x<.020 and .0305<p.z<.049 and p.y<.004 and f.normal.y<-.2):continue
 t=sum((uv0[i].uv for i in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pixels[int(t.y*(image.size[1]-1))%image.size[1],int(t.x*(image.size[0]-1))%image.size[0],:3]
 if (rgb[2]>=rgb[0]*.9 and max(rgb)>.04) or (rgb[1]>.4 and rgb[0]-rgb[1]<.25):keep.add(f.index)
patch=body.copy();patch.data=body.data.copy();patch.name='Garment repair from intact opposite side';bpy.context.collection.objects.link(patch)
bm2=bmesh.new();bm2.from_mesh(patch.data);bm2.faces.ensure_lookup_table();bmesh.ops.delete(bm2,geom=[f for f in bm2.faces if f.index not in keep],context='FACES');bmesh.ops.delete(bm2,geom=[v for v in bm2.verts if not v.link_faces],context='VERTS')
for vert in bm2.verts:vert.co.x=-vert.co.x;vert.co.y+=.00015
bmesh.ops.reverse_faces(bm2,faces=list(bm2.faces));bm2.to_mesh(patch.data);bm2.free()
s=bpy.context.scene;s.cycles.samples=20;s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
preview='--preview' in sys.argv
if preview:s.cycles.samples=8;s.render.resolution_x=600;s.render.resolution_y=600
for name,loc,target in [('bag-context',Vector((-.014,-.3,.032)),Vector((-.014,0,.032))),('bag-side',c+n*.065+u*.13,c),('bag-edge',c+n*.012+u*.15,c)]:
 if preview and name not in {'bag-edge','bag-context'}:continue
 cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=1000;s.render.resolution_y=1200
for name,angle in [('front',0),('threequarter',35),('back',180)]:
 if preview:continue
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;full=body.data.copy();mod=body.modifiers.new('Web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB');body.data=full
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'));print('OLD_BAG_DELETED',json.dumps(report,ensure_ascii=False))
