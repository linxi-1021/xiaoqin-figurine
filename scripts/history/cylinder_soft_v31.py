import bpy,numpy as np,bmesh,math,json,hashlib
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_祝福语微右移_v29_20261021';D=B/'3D重建_v6基础_柔和圆角底座_v31_20261022';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6祝福语微右移.blend'));base=bpy.data.materials['Pedestal deep cocoa satin'];top=.0089;bottom=.00012;radius=.0264
removed=['GEO-Original pedestal with inset socket','GEO-Flush cocoa collar around compact QR','GEO-Flush inset underside engraving']
for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));before=np.array([tuple(v.co) for v in body.data.vertices]);protected=before[before[:,2]>.0092];bm=bmesh.new();bm.from_mesh(body.data);faces=[f for f in bm.faces if all(v.co.z<top for v in f.verts)];bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(body.data);bm.free();body.data.update();afterset=set(tuple(v.co) for v in body.data.vertices);assert all(tuple(p) in afterset for p in protected)
bpy.ops.mesh.primitive_cylinder_add(vertices=384,radius=radius,depth=top-bottom,location=(0,0,(bottom+top)/2));cyl=bpy.context.object;cyl.name='GEO-Regular cylindrical pedestal';cyl.data.materials.append(base);be=cyl.modifiers.new('Soft manufactured rim','BEVEL');be.width=.00120;be.segments=12;be.limit_method='ANGLE';be.angle_limit=.5;bpy.ops.object.modifier_apply(modifier=be.name)
for f in cyl.data.polygons:f.use_smooth=abs(f.normal.z)<.999
# Only rectangular sockets are cut into the clean cylinder; their inserts stay inside its envelope.
records=[]
for name in ['GEO-Scannable recessed QR code','GEO-Uniform recessed 小秦天天开心哟！ fill']:
 o=bpy.data.objects[name];points=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);lo=points.min(0);hi=points.max(0);ceiling=float(hi[2]-.000035);low=bottom-.001;center=((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(low+ceiling)/2);bpy.ops.mesh.primitive_cube_add(size=1,location=center);cut=bpy.context.object;cut.dimensions=(float(hi[0]-lo[0]+.000012),float(hi[1]-lo[1]+.000012),ceiling-low);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=cyl.modifiers.new('Internal flush socket '+name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=cyl;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);records.append({'insert':name,'minimum_z_mm':float(lo[2]*1000),'maximum_radius_mm':float(np.linalg.norm(points[:,:2],axis=1).max()*1000)})
# Flat n-gon caps, smooth manufactured bevels, continuous circular wall.
for f in cyl.data.polygons:f.use_smooth=abs(f.normal.z)<.999
bm=bmesh.new();bm.from_mesh(cyl.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(cyl.data);bm.free();assert bad==0
world=np.array([tuple(cyl.matrix_world@v.co) for v in cyl.data.vertices]);assert world[:,2].min()>=bottom-1e-8 and world[:,2].max()<=top+1e-8;assert all(r['minimum_z_mm']>=bottom*1000-1e-6 and r['maximum_radius_mm']<radius*1000 for r in records)
# At every sidewall sample, the outer surface is a circle of the prescribed radius.
from mathutils import Vector
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([Vector(v) for v in world],[tuple(f.vertices) for f in cyl.data.polygons]);radii=[]
for angle in np.linspace(0,2*math.pi,48,endpoint=False):
 direction=Vector((math.cos(angle),math.sin(angle),0));hit=tree.ray_cast(Vector((0,0,(top+bottom)/2))+direction*.06,-direction);assert hit[0] is not None;radii.append(math.hypot(hit[0].x,hit[0].y))
radii=np.array(radii);assert abs(radii-radius).max()<.000002
r={'diameter_mm':radius*2000,'height_mm':(top-bottom)*1000,'flat_top_z_mm':top*1000,'flat_bottom_z_mm':bottom*1000,'rim_round_mm':1.20,'sidewall_radial_error_mm':float(abs(radii-radius).max()*1000),'nonmanifold_edges':bad,'old_parts_removed':removed,'character_above_9_2mm_preserved_exactly':True,'qr_and_message_unchanged':True,'inserts':records};(D/'圆柱与嵌件校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6柔和圆角底座.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6柔和圆角底座.glb'),use_selection=True,export_format='GLB')
