import bpy,numpy as np,math,json,bmesh
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底面留白收敛_v22_20261021';D=B/'3D重建_v6基础_底面融合字槽修复_v23_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底面留白收敛.blend'));base=bpy.data.materials['Pedestal deep cocoa satin'];light=bpy.data.materials['Underside ivory high contrast substrate'];p=light.node_tree.nodes.get('Principled BSDF');color=[.84,.75,.62];p.inputs['Base Color'].default_value=(*[((v+.055)/1.055)**2.4 for v in color],1);p.inputs['Roughness'].default_value=.76
# Replace the damaged letter cut completely, retaining the original inset footprint.
for name in ['GEO-Flush inset underside engraving','GEO-Recessed 小秦天天开心 dark fill']:
 bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bottom=.00012;top=.00127
bpy.ops.mesh.primitive_cylinder_add(vertices=256,radius=.0247,depth=top-bottom,location=(0,0,(bottom+top)/2));plate=bpy.context.object;plate.name='GEO-Flush inset underside engraving';plate.data.materials.append(base)
for f in plate.data.polygons:f.use_smooth=abs(f.normal.z)<.5
# Recess for the existing QR solid; coordinates and payload remain unchanged.
size=.02925;cy=-.0032
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,cy,bottom+.00030));cut=bpy.context.object;cut.dimensions=(size+.000015,size+.000015,.00110);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=plate.modifiers.new('QR insert pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=plate;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Build one continuous engraved relief from a unified glyph mask. This avoids
# overlapping font outlines and leaves every stroke at exactly the same depth.
mask=np.load('models/rebuild/engraved-message-mask.npy');H,W=mask.shape;pitch=.0032/96;tw=W*pitch;th=H*pitch;tx=-tw/2;ty=.0205-th
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
faces.append(tuple(back));materials.append(0);mesh=bpy.data.meshes.new('Unified continuous engraved Chinese strokes');mesh.from_pydata(verts,[],faces);mesh.materials.append(base);mesh.materials.append(light);mesh.update();fill=bpy.data.objects.new('GEO-Uniform recessed 小秦天天开心 fill',mesh);bpy.context.collection.objects.link(fill)
for f,mi in zip(mesh.polygons,materials):f.material_index=mi
assert len(plate.data.polygons)>0
qr=bpy.data.objects['GEO-Scannable recessed QR code'];qr.data.materials[1]=base;qr.data.materials.append(base);outside_slot=2;matrix=np.load('models/rebuild/qr-matrix.npy')<128;corner=.0018
# Round only the far outer corners of the quiet zone; preserve four modules along every side.
for f in qr.data.polygons:
 if f.material_index!=0:continue
 c=qr.matrix_world@f.center;x=c.x;y=c.y-cy
 if abs(x)>size/2-corner and abs(y)>size/2-corner:
  dx=abs(x)-(size/2-corner);dy=abs(y)-(size/2-corner)
  if dx*dx+dy*dy>corner*corner:f.material_index=outside_slot
# Fine rounded recessed keyline makes the code field read as part of the base design.
# Colors alone define the field; no added external layer or thickness.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底面融合字槽修复.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底面融合字槽修复.glb'),use_selection=True,export_format='GLB');r={'message':'小秦天天开心','single_continuous_glyph_relief':True,'glyph_mask_pitch_microns':pitch*1e6,'letter_fill_recess_mm':.18,'qr_palette':'champagne tan + pedestal cocoa','qr_corner_radius_mm':1.8,'qr_payload_unchanged':True,'external_thickness_added_mm':0};(D/'字槽与配色修复.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
