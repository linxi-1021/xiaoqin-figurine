import bpy,numpy as np,json,time
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底面刻字二维码_v20_20261021';D=B/'3D重建_v6基础_底面齐平镶嵌_v21_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底面刻字二维码.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));coords=np.array([tuple(v.co) for v in body.data.vertices]);original_min=float(coords[:,2].min());protected=coords[coords[:,2]>.002].copy();plate=bpy.data.objects['GEO-Ivory underside engraving plate'];qr=bpy.data.objects['GEO-Scannable recessed QR code'];text=bpy.data.objects['GEO-Recessed 小秦天天开心 dark fill'];bottom=.00012;shift=bottom-(-.0008)
for o in [plate,qr,text]:o.location.z+=shift
plate.name='GEO-Flush inset underside engraving';radius=.024705;ceiling=.00110;low=-.0020
# Isolate only the pedestal before the boolean: the reconstructed character has
# pre-existing open regions, so a full-character boolean would damage distant detail.
import bmesh
base_slots={i for i,m in enumerate(body.data.materials) if m and m.name=='Pedestal deep cocoa satin'}
assert base_slots
basebody=body.copy();basebody.data=body.data.copy();basebody.name='GEO-Original pedestal with inset socket';bpy.context.collection.objects.link(basebody)
bm=bmesh.new();bm.from_mesh(basebody.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in base_slots],context='FACES');boundary=[e for e in bm.edges if e.is_boundary]
if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(basebody.data);bm.free();basebody.data.update()
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index in base_slots],context='FACES');bm.to_mesh(body.data);bm.free();body.data.update()
bpy.ops.mesh.primitive_cylinder_add(vertices=256,radius=radius,depth=ceiling-low,location=(0,0,(low+ceiling)/2));cut=bpy.context.object;cut.name='TEMP Original pedestal inset socket';mod=basebody.modifiers.new('Inset pocket inside original pedestal','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=basebody;print('Applying original-base pocket',flush=True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
after=np.array([tuple(v.co) for ob in [body,basebody] for v in ob.data.vertices]);newmin=float(min(after[:,2].min(),bottom));r={'original_bottom_z_mm':original_min*1000,'new_assembly_bottom_z_mm':newmin*1000,'inset_face_z_mm':bottom*1000,'inward_setback_mm':(bottom-original_min)*1000,'added_external_thickness_mm':max(0,(original_min-newmin)*1000),'socket_radius_mm':radius*1000,'socket_depth_ceiling_mm':ceiling*1000,'engraving_depth_mm':.28,'qr_matrix_unchanged':True,'message':'小秦天天开心'}
# Exact coordinate set audit verifies the character above the pocket is untouched.
from mathutils.kdtree import KDTree
from mathutils import Vector
points=after[after[:,2]>.002];kd=KDTree(len(points))
for i,pnt in enumerate(points):kd.insert(Vector(pnt),i)
kd.balance();distances=np.array([kd.find(Vector(pnt))[2] for pnt in protected]);r['max_protected_surface_change_mm']=float(distances.max()*1000);r['protected_vertices_over_0_1_micron']=int((distances>1e-7).sum());print(json.dumps(r),flush=True);assert distances.max()<1e-7;assert r['added_external_thickness_mm']==0
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底面齐平镶嵌.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底面齐平镶嵌.glb'),use_selection=True,export_format='GLB');(D/'齐平镶嵌校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
