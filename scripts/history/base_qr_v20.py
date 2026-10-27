import bpy,numpy as np,math,json,bmesh
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底座匹配肤色_v19_20261021';D=B/'3D重建_v6基础_底面刻字二维码_v20_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底座匹配肤色.blend'))
def material(name,srgb,rough=.68):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*[((v+.055)/1.055)**2.4 for v in srgb],1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=0;return m
ivory=material('Underside ivory high contrast substrate',(.94,.91,.85));dark=material('Engraving dark cocoa fill',(.08,.055,.040));base=bpy.data.materials['Pedestal sampled skin peach'];base.name='Pedestal deep cocoa satin';p=base.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*[((v+.055)/1.055)**2.4 for v in [.28,.20,.16]],1);p.inputs['Roughness'].default_value=.64
bottom=-.0008;thickness=.00115;radius=.0247
bpy.ops.mesh.primitive_cylinder_add(vertices=256,radius=radius,depth=thickness,location=(0,0,bottom+thickness/2));plate=bpy.context.object;plate.name='GEO-Ivory underside engraving plate';plate.data.materials.append(ivory)
for f in plate.data.polygons:f.use_smooth=abs(f.normal.z)<.5
matrix=np.load('models/rebuild/qr-matrix.npy')<128;assert matrix.shape==(37,37);pitch=.00065;quiet=4;size=45*pitch;cx=0;cy=-.0032;x0=-size/2;y0=cy-size/2;depth=.00028
bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,cy,bottom+.00030));cut=bpy.context.object;cut.name='TEMP QR cavity';cut.dimensions=(size+.000015,size+.000015,.00110);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=plate.modifiers.new('Recess for true engraved QR insert','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=plate;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
verts=[];faces=[];mis=[];grid={}
def vertex(x,y,z):
 k=(round(x,10),round(y,10),round(z,10))
 if k not in grid:grid[k]=len(verts);verts.append((x,y,z))
 return grid[k]
def face(ids,mi=0):faces.append(tuple(ids));mis.append(mi)
for row in range(45):
 for col in range(45):
  x=x0+col*pitch;y=y0+row*pitch;outer=[vertex(x,y,bottom),vertex(x+pitch,y,bottom),vertex(x+pitch,y+pitch,bottom),vertex(x,y+pitch,bottom)];black=quiet<=row<quiet+37 and quiet<=col<quiet+37 and matrix[row-quiet,col-quiet]
  if not black:face(outer[::-1]);continue
  e=.000010;inner=[vertex(x+e,y+e,bottom+depth),vertex(x+pitch-e,y+e,bottom+depth),vertex(x+pitch-e,y+pitch-e,bottom+depth),vertex(x+e,y+pitch-e,bottom+depth)];face(inner[::-1],1)
  for k in range(4):j=(k+1)%4;face((outer[j],outer[k],inner[k],inner[j]),1)
# Close every outer edge to the backing, keeping QR a single watertight relief solid.
edge=[vertex(x0+i*pitch,y0,bottom) for i in range(46)]+[vertex(x0+size,y0+i*pitch,bottom) for i in range(1,46)]+[vertex(x0+i*pitch,y0+size,bottom) for i in range(44,-1,-1)]+[vertex(x0,y0+i*pitch,bottom) for i in range(44,0,-1)]
backz=bottom+.00089;back=[]
for a in edge:
 x,y,_=verts[a];back.append(vertex(x,y,backz))
for i in range(len(edge)):
 j=(i+1)%len(edge);face((edge[i],edge[j],back[j],back[i]))
face(back)
mesh=bpy.data.meshes.new('Actual recessed QR cells 37x37 with four module quiet zone');mesh.from_pydata(verts,[],faces);mesh.materials.append(ivory);mesh.materials.append(dark);mesh.update();obj=bpy.data.objects.new('GEO-Scannable recessed QR code',mesh);bpy.context.collection.objects.link(obj)
for f,mi in zip(mesh.polygons,mis):f.material_index=mi
bm=bmesh.new();bm.from_mesh(mesh);bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert bad==0
font=bpy.data.fonts.load('C:/Windows/Fonts/simhei.ttf')
def text_object(name,z,extrude):
 cu=bpy.data.curves.new(name,'FONT');cu.body='小秦天天开心';cu.font=font;cu.size=.0032;cu.align_x='CENTER';cu.extrude=extrude;cu.resolution_u=12;o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.location=(0,.0200,z);o.rotation_euler=(math.pi,0,0);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
cut=text_object('TEMP engraved message cutter',bottom+.00034,.00055);mod=plate.modifiers.new('True recessed Chinese birthday message','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=plate;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);text=text_object('GEO-Recessed 小秦天天开心 dark fill',bottom+.00031,.000035);text.data.materials.append(dark)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底面刻字二维码.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底面刻字二维码.glb'),use_selection=True,export_format='GLB');r={'message':'小秦天天开心','qr_payload':'https://happybirthdayxiaoqin.netlify.app/','qr_source':'普通备用二维码.webp','qr_modules':37,'quiet_zone_modules':4,'module_pitch_mm':pitch*1000,'qr_total_width_mm':size*1000,'engraving_depth_mm':depth*1000,'qr_watertight':bad==0,'base_color':'deep cocoa','underside_color':'ivory with dark recessed fill','source_geometry_preserved':True};(D/'刻字二维码参数.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
