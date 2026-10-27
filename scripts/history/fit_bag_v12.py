import bpy,bmesh,json,math,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;out=r/'bag-v12';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v11/小秦_圆柱小熊斜挎包.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
def coordinates_hash(o):
 co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co);return hashlib.sha256(co.tobytes()).hexdigest()
# Drop only disconnected scraps in the approved arm/hip gap; never displace the character.
audit=json.loads((out/'contact-audit.json').read_text());remove=set(i for q in audit['local_components'] for i in q['faces']);bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table();before_coords={tuple(v.co) for v in bm.verts};bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');assert all(tuple(v.co) in before_coords for v in bm.verts);bm.to_mesh(body.data);bm.free();body.data.validate(clean_customdata=False)
# The original arm, clothing and legs stay in place. Fit the rigid bag back to the measured cloth plane.
oldc=Vector((-.0107,-.0138,.0368));oldn=Vector((-.3,-.92,.25)).normalized();oldu=Vector((.95,-.31,0)).normalized();oldv=oldn.cross(oldu).normalized();oldu=oldv.cross(oldn).normalized();T=.0034
points=np.array([q['hit'] for q in audit['samples']]);mean=points.mean(axis=0);_,_,vh=np.linalg.svd(points-mean);newn=Vector(vh[-1]);newn.normalize()
if newn.dot(oldn)<0:newn=-newn
qrot=oldn.rotation_difference(newn);newu=qrot@oldu;newv=qrot@oldv;oldback=oldc-oldn*T;mean=Vector(mean);gap=(oldback-mean).dot(newn);newback=oldback-newn*(gap-.00006);newc=newback+newn*T
# Rebuild the garment-only BVH after removing scraps, so contact is measured on actual clothing.
m=body.data;m.calc_loop_triangles();img=m.materials[0].node_tree.nodes.get('Image Texture').image;pix=np.empty(img.size[0]*img.size[1]*4,np.float32);img.pixels.foreach_get(pix);pix=pix.reshape(img.size[1],img.size[0],4);uv=m.uv_layers['UVMap'].data;keep=set()
for f in m.polygons:
 p=f.center
 if not(-.023<p.x<.002 and .029<p.z<.045 and p.y<.008):continue
 if 'plaid' in m.materials[f.material_index].name.lower():keep.add(f.index);continue
 tex=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(tex.y*(img.size[1]-1))%img.size[1],int(tex.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[2]>rgb[0]*.9 and f.normal.y<-.1:keep.add(f.index)
vs=[v.co.copy() for v in m.vertices];ts=[tuple(t.vertices) for t in m.loop_triangles if t.polygon_index in keep];tree=BVHTree.FromPolygons(vs,ts,all_triangles=True)
def contacts(back):
 gaps=[]
 for a in [-.0035,-.00175,0,.00175,.0035]:
  for b in [-.0035,-.00175,0,.00175,.0035]:
   if a*a+b*b>.0045**2:continue
   p=back+newu*a+newv*b;hit,nn,k,d=tree.ray_cast(p+newn*.02,-newn)
   if hit is not None:gaps.append((p-hit).dot(newn))
 return gaps
initial=contacts(newback)
# Permit at most 0.12 mm local compression to obtain a believable soft-cloth contact.
if min(initial)<-.00012:
 correction=-.00012-min(initial);newback+=newn*correction;newc+=newn*correction
final=contacts(newback);xf=Matrix.Translation(newc)@qrot.to_matrix().to_4x4()@Matrix.Translation(-oldc)
parts=[o for o in bpy.context.scene.objects if o.name.startswith(('Bag round cylindrical body','Bear bag ear','Bag circular edge piping'))]
assert len(parts)==4
for o in parts:o.matrix_world=xf@o.matrix_world
# Regenerate the lower strap to the new inner-side anchor; it follows the garment rather than spanning the arm gap.
bridge=bpy.data.objects.get('Bag strap to inner side attachment');mat=bridge.data.materials[0];bpy.data.objects.remove(bridge,do_unlink=True)
start=Vector((-.0034,-.0096,.0449));end=newc+newu*.0049+newv*.0031-newn*.001;mid=(start+end)*.5+Vector((0,-.00015,.00025));verts=[];faces=[];N=32
for i in range(N+1):
 t=i/N;p=(1-t)**2*start+2*t*(1-t)*mid+t*t*end;tangent=(2*(1-t)*(mid-start)+2*t*(end-mid)).normalized();across=newn.cross(tangent).normalized();normal=tangent.cross(across).normalized()
 for w,d in [(-.00072,-.00015),(.00072,-.00015),(.00072,.00015),(-.00072,.00015)]:verts.append(tuple(p+across*w+normal*d))
for i in range(N):
 for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
faces.extend([(3,2,1,0),(N*4,N*4+1,N*4+2,N*4+3)])
me=bpy.data.meshes.new('Shortened fitted lower strap');me.from_pydata(verts,[],faces);me.materials.append(mat);bridge=bpy.data.objects.new('Bag strap to inner side attachment',me);bpy.context.collection.objects.link(bridge)
for f in me.polygons:f.use_smooth=True
bevel=bridge.modifiers.new('Soft leather edges','BEVEL');bevel.width=.00007;bevel.segments=3
report={'base':'v11','bag_style_unchanged':True,'diameter_mm':11.6,'depth_mm':3.4,'bag_center_before':list(oldc),'bag_center_after':list(newc),'translation_mm':list((newc-oldc)*1000),'rotation_degrees':math.degrees(qrot.angle),'old_center_gap_mm':2.6276,'new_contact_gap_mm':{'minimum':min(final)*1000,'maximum':max(final)*1000,'median':float(np.median(final)*1000),'sample_count':len(final)},'removed_isolated_fragments':len(audit['local_components']),'removed_fragment_faces':len(remove),'existing_character_vertices_moved':0,'arm_clothing_gap_filled':False,'bag_body_count':1}
assert float(np.median(final)*1000)<.5,report
(out/'fit-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=800;s.render.resolution_y=960;cam=s.camera
for name,angle in [('front',0),('side',-65),('threequarter',35)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=newc+newn*.015+newu*.13;cam.rotation_euler=(newc-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.026;s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=str(out/'bag-side.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_贴衣圆柱小熊包.blend'));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(out/'小秦_贴衣圆柱小熊包.glb'),use_selection=True,export_format='GLB');print('BAG_FITTED',json.dumps(report,ensure_ascii=False))
