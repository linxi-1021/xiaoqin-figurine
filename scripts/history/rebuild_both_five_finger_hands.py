import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_双手五指重建_20261019';bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));s=bpy.context.scene;o=max((x for x in s.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));labels=np.load(D/'uv-chart-labels.npy');im=o.data.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);remove=[];raised=[];lower=[];raised_charts=set(json.loads((D/'additional-raised-skin-charts.json').read_text()))
for f in o.data.polygons:
 lab=int(labels[f.index]);x,y,z=f.center
 # Semantic hand UV charts take priority over accidental old bag material assignments.
 kill=False
 if lab in raised_charts:kill=True
 if lab==355 and .0581<z<.0684:
  uv=sum((o.data.uv_layers[0].data[k].uv for k in f.loop_indices),Vector((0,0)))/len(f.loop_indices);c=pix[int(uv.y*h)%h,int(uv.x*w)%w,:3]
  if x>.0147 or (c[0]>.5 and c[1]>.25 and c[2]>.12):kill=True
 if kill:raised.append(f.index)
 if lab in [557,393,702,755,793,252,180,568,320,306] or (lab==336 and x<-.0158 and .0303<z<.0344):kill=True;lower.append(f.index)
 if kill:remove.append(f.index)
bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(o.data);bm.free()
mat=bpy.data.materials.new('Rebuilt hands warm skin');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');rgb=[234/255,164/255,130/255];lin=[((c+.055)/1.055)**2.4 for c in rgb];bs.inputs['Base Color'].default_value=(*lin,1);bs.inputs['Roughness'].default_value=.62;bs.inputs['Specular IOR Level'].default_value=.18
parts=[]
def ell(name,loc,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);a=bpy.context.object;a.name=name;a.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(a);return a
def capsule(name,a,b,r):
 a=Vector(a);b=Vector(b);v=b-a;bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=r,radius2=r*.96,depth=v.length,location=(a+b)*.5);ob=bpy.context.object;ob.name=name;ob.rotation_euler=v.to_track_quat('Z','Y').to_euler();parts.append(ob);ell(name+' root',a,(r,r,r));ell(name+' tip',b,(r*.96,r*.96,r*.96))
def union(name,digits,voxel=.000065):
 bpy.ops.object.select_all(action='DESELECT')
 for a in parts:a.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hand=bpy.context.object;hand.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);m=hand.modifiers.new('Closed organic finger union','REMESH');m.mode='VOXEL';m.voxel_size=voxel;m.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=m.name);m=hand.modifiers.new('Round finger webs','SMOOTH');m.factor=.42;m.iterations=4;bpy.ops.object.modifier_apply(modifier=m.name);hand.data.materials.append(mat)
 for f in hand.data.polygons:f.use_smooth=True
 hand['digit_count']=5;hand['digits']=digits;parts.clear();return hand
# Open hand: four distinct rounded fingertips plus one opposable thumb.
ell('Open palm',(.0182,-.0112,.0618),(.00345,.0015,.0031));ell('Open wrist',(.0164,-.0103,.0588),(.0026,.00155,.0022))
open_digits=[('thumb',(.0144,-.0106,.0614),(.0122,-.0108,.0641),.00088),('index',(.0154,-.0105,.0635),(.0157,-.0105,.0666),.00074),('middle',(.0171,-.0104,.0638),(.0180,-.0104,.0676),.00078),('ring',(.0187,-.0104,.0635),(.0204,-.0103,.0666),.00072),('little',(.0200,-.0103,.0629),(.0222,-.0102,.0648),.00065)]
open_digits=[(n,(a[0]+.0012,a[1]-.0008,a[2]),(b[0]+.0012,b[1]-.0008,b[2]),r) for n,a,b,r in open_digits]
for name,a,b,r in open_digits:capsule(name,a,b,r)
opened=union('Open hand - five fingers','thumb,index,middle,ring,little')
# Close the source hair end exposed behind the thumb, using its own brown material.
hm=bpy.data.materials.new('Closed source hair tip');hm.use_nodes=True;hb=hm.node_tree.nodes.get('Principled BSDF');hb.inputs['Base Color'].default_value=(.075,.022,.008,1);hb.inputs['Roughness'].default_value=.65
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(.01225,-.0114,.0647));cap=bpy.context.object;cap.name='Closed hair tip behind thumb';cap.scale=(.00110,.00055,.00065);cap.data.materials.append(hm)
for f in cap.data.polygons:f.use_smooth=True

# Curled hand: four fingers bend down and return to the palm; thumb crosses outside.
ell('Fist palm',(-.0205,-.0026,.0349),(.00205,.00145,.0018));ell('Fist wrist',(-.0200,-.0013,.0369),(.0017,.00155,.0021))
fist_digits=[]
for i,(x,r,z) in enumerate([(-.0221,.00046,.0343),(-.0211,.00052,.0345),(-.0200,.00054,.0346),(-.0189,.00052,.0346)]):
 path=[(x,-.0025,z+.0010),(x,-.0046,z+.0001),(x,-.0049,z-.0009),(x,-.0038,z-.0013)];fist_digits.append({'finger':i+1,'path':path})
 for j,(a,b) in enumerate(zip(path,path[1:])):capsule('Curled finger %d segment %d'%(i+1,j),a,b,r)
thumb=[(-.0187,-.0018,.0357),(-.0183,-.0044,.0352),(-.0200,-.0055,.0349)]
for i,(a,b) in enumerate(zip(thumb,thumb[1:])):capsule('Fist external thumb %d'%i,a,b,.00061)
for a in parts:a.location.y-=.0028
fist_digits=[{'finger':d['finger'],'path':[(p[0],p[1]-.0028,p[2]) for p in d['path']]} for d in fist_digits]
thumb=[(p[0],p[1]-.0028,p[2]) for p in thumb]
closed=union('Curled hand - four fingers and thumb','little,ring,middle,index,thumb',.000045)
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
views=[('open-front',(.0175,-.0104,.0636),(.0175,-.20,.0636),.020),('open-oblique',(.0175,-.0104,.0636),(.13,-.16,.075),.021),('fist-front',(-.0205,-.0035,.0350),(-.0205,-.2,.0350),.012),('fist-side',(-.0205,-.0035,.0350),(-.13,-.07,.041),.012)]
for name,target,pos,scale in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6双手五指重建.blend'));bpy.ops.object.select_all(action='DESELECT')
for a in s.objects:
 if a.type=='MESH':a.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();m=o.modifiers.new('Same v6 web optimization','DECIMATE');m.ratio=.3;bpy.ops.object.modifier_apply(modifier=m.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6双手五指重建.glb'),use_selection=True,export_format='GLB');o.data=full
(D/'双手结构记录.json').write_text(json.dumps({'source':'v6 bag seam repair','old_hand_faces_removed':len(remove),'raised_removed':len(raised),'lower_removed':len(lower),'removed_original_polygon_indices':remove,'protected_uv_charts':[357,366,465,298,318],'open_hand_digits':[{'name':n,'root':a,'tip':b,'radius':r} for n,a,b,r in open_digits],'curled_fingers':fist_digits,'external_thumb':thumb},ensure_ascii=False,indent=2),encoding='utf8');print('BOTH_FIVE_FINGER_HANDS_DONE')
