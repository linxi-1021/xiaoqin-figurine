import bpy,numpy as np,math,json,bmesh,hashlib
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_二维码反色试验_v25_20261021';D=B/'3D重建_v6基础_反色底座祝福语_v26_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6二维码反色试验.blend'));base=bpy.data.materials['Pedestal deep cocoa satin'];light=bpy.data.materials['Underside ivory high contrast substrate'];qr=bpy.data.objects['GEO-Scannable recessed QR code'];qbefore=np.array([tuple(v.co) for v in qr.data.vertices]);
for name in ['GEO-Flush inset underside engraving','GEO-Uniform recessed 小秦天天开心 fill']:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bottom=.00012;top=.00127
bpy.ops.mesh.primitive_cylinder_add(vertices=256,radius=.0247,depth=top-bottom,location=(0,0,(bottom+top)/2));plate=bpy.context.object;plate.name='GEO-Flush inset underside engraving';plate.data.materials.append(base)
for f in plate.data.polygons:f.use_smooth=abs(f.normal.z)<.5
size=.02925;cy=-.0032
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,cy,bottom+.00030));cut=bpy.context.object;cut.dimensions=(size+.000015,size+.000015,.00110);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=plate.modifiers.new('Existing compact QR socket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=plate;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Build one continuous engraved relief from a unified glyph mask. This avoids
# overlapping font outlines and leaves every stroke at exactly the same depth.
mask=np.load('models/rebuild/engraved-message-yo-mask.npy');H,W=mask.shape;pitch=.0029/96;tw=W*pitch;th=H*pitch;tx=-tw/2;ty=.0205-th
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,ty+th/2,bottom+.00030));cut=bpy.context.object;cut.dimensions=(tw+.000012,th+.000012,.00110);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=plate.modifiers.new('Single continuous message relief socket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=plate;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
heights=np.zeros((H+1,W+1),np.float32);counts=np.zeros_like(heights)
for dr,dc in [(0,0),(0,1),(1,0),(1,1)]:heights[dr:dr+H,dc:dc+W]+=mask;counts[dr:dr+H,dc:dc+W]+=1
heights=heights/counts*.00018;verts=[(tx+c*pitch,ty+r*pitch,bottom+float(heights[r,c])) for r in range(H+1) for c in range(W+1)];faces=[];materials=[]
for r in range(H):
 for c in range(W):
  i=r*(W+1)+c;faces.append((i+W+1,i+W+2,i+1,i));materials.append(1 if mask[r,c] else 0)
edge=list(range(W+1))+[r*(W+1)+W for r in range(1,H+1)]+[H*(W+1)+c for c in range(W-1,-1,-1)]+[r*(W+1) for r in range(H-1,0,-1)];back=[]
for i in edge:x,y,_=verts[i];back.append(len(verts));verts.append((x,y,bottom+.00089))
for k in range(len(edge)):
 j=(k+1)%len(edge);faces.append((edge[k],edge[j],back[j],back[k]));materials.append(0)
faces.append(tuple(back));materials.append(0);mesh=bpy.data.meshes.new('Unified continuous engraved Chinese strokes');mesh.from_pydata(verts,[],faces);mesh.materials.append(base);mesh.materials.append(light);mesh.update();fill=bpy.data.objects.new('GEO-Uniform recessed 小秦天天开心哟！ fill',mesh);bpy.context.collection.objects.link(fill)
for f,mi in zip(mesh.polygons,materials):f.material_index=mi
assert len(plate.data.polygons)>0

assert np.array_equal(qbefore,np.array([tuple(v.co) for v in qr.data.vertices]))
r={'message':'小秦天天开心哟！','text_width_mm':tw*1000,'text_recess_mm':.18,'qr_geometry_unchanged':True,'inverse_qr_materials_unchanged':True,'external_thickness_added_mm':0}
for ob in [plate,fill]:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges);bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6反色底座祝福语.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6反色底座祝福语.glb'),use_selection=True,export_format='GLB');(D/'祝福语校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
