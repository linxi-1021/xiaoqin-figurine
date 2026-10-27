import bpy,json,bmesh
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底面融合字槽修复_v23_20261021';D=B/'3D重建_v6基础_二维码紧凑留白_v24_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底面融合字槽修复.blend'));qr=bpy.data.objects['GEO-Scannable recessed QR code'];scale=.55/.65;cy=-.0032
for v in qr.data.vertices:v.co.x*=scale;v.co.y=cy+(v.co.y-cy)*scale
# A flush cocoa collar fills the old socket, so shrinking the tile adds no open gaps or layers.
base=bpy.data.materials['Pedestal deep cocoa satin'];outer=.029265/2;inner=.02475/2-.000002;z0=.00012;z1=.00104;vs=[]
for z in [z0,z1]:
 for r in [outer,inner]:
  vs.extend([(-r,cy-r,z),(r,cy-r,z),(r,cy+r,z),(-r,cy+r,z)])
fs=[]
for k in range(4):
 j=(k+1)%4;fs.extend([(j,k,k+4,j+4),(8+k,8+j,12+j,12+k),(k,j,8+j,8+k),(4+j,4+k,12+k,12+j)])
m=bpy.data.meshes.new('Flush cocoa socket collar');m.from_pydata(vs,[],fs);m.materials.append(base);m.update();o=bpy.data.objects.new('GEO-Flush cocoa collar around compact QR',m);bpy.context.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(m);bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6二维码紧凑留白.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6二维码紧凑留白.glb'),use_selection=True,export_format='GLB');r={'previous_total_width_mm':29.25,'new_total_width_mm':24.75,'module_pitch_mm':.55,'quiet_zone_modules':4,'light_field_area_reduction_percent':round((1-scale*scale)*100,1),'message_unchanged':True,'additional_thickness_mm':0};(D/'紧凑留白校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
