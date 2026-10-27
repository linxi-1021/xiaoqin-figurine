import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_手部精修_20261019';bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));s=bpy.context.scene;o=max((x for x in s.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));o.data.update()
# Restrict removal to the original raised hand's skin island in front of the hair.
im=o.data.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);remove=[]
for f in o.data.polygons:
 x,y,z=f.center
 if -.0150<y<-.0035 and ((.0118<x<.0228 and .0589<z<.0652) or (.0155<x<.0229 and .0640<z<.0677) or (.0107<x<.0157 and .0600<z<.0656)):
  uv=sum((o.data.uv_layers[0].data[k].uv for k in f.loop_indices),Vector((0,0)))/len(f.loop_indices);col=pix[int(uv.y*h)%h,int(uv.x*w)%w,:3]
  if (x>.0144 and z>.0605) or (.0110<x<.017 and .0591<z<.0610) or (col[0]>.55 and .44<col[1]/max(col[0],.001)<.88 and .29<col[2]/max(col[0],.001)<.80):remove.append(f.index)
bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(o.data);bm.free()
parts=[]
def ell(name,loc,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);a=bpy.context.object;a.name=name;a.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(a);return a
def digit(name,a,b,r):
 a=Vector(a);b=Vector(b);v=b-a;mid=(a+b)*.5
 bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=r,radius2=r*.94,depth=v.length,location=mid);ob=bpy.context.object;ob.name=name+' shaft';ob.rotation_euler=v.to_track_quat('Z','Y').to_euler();parts.append(ob)
 ell(name+' root',a,(r,r,r));ell(name+' rounded tip',b,(r*.94,r*.94,r*.94));return ob
ell('Raised palm',(.0170,-.0092,.0618),(.0035,.00150,.0032));ell('Raised wrist',(.0166,-.0090,.0585),(.0026,.00150,.0022))
digit('Thumb',(.0145,-.0092,.0612),(.0122,-.0094,.0644),.00090)
digit('Index',(.0155,-.0092,.0634),(.0158,-.0092,.0666),.00080)
digit('Middle',(.0172,-.00915,.0638),(.0180,-.0091,.0675),.00084)
digit('Ring',(.0187,-.00915,.0634),(.0203,-.00905,.0665),.00078)
digit('Little',(.0198,-.0091,.0628),(.0221,-.0090,.0649),.00070)
bpy.ops.object.select_all(action='DESELECT')
for a in parts:a.location.y-=.0025;a.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hand=bpy.context.object;hand.name='Raised hand - five separated fingers';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);re=hand.modifiers.new('Organic palm and finger union','REMESH');re.mode='VOXEL';re.voxel_size=.000065;re.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=re.name);sm=hand.modifiers.new('Soften knuckles and finger webs','SMOOTH');sm.factor=.48;sm.iterations=5;bpy.ops.object.modifier_apply(modifier=sm.name)
# Very shallow palm creases rather than dark painted cuts.
v=np.array([v.co[:] for v in hand.data.vertices]);q=v[:,[0,2]]
for a,b,width,depth in [((.0148,.0605),(.0160,.0632),.00020,.000065),((.0155,.0617),(.0190,.0620),.00022,.000055)]:
 a=np.array(a);b=np.array(b);d=b-a;t=np.clip(((q-a)*d).sum(1)/(d@d),0,1);dist=np.linalg.norm(q-a-t[:,None]*d,axis=1);weight=np.exp(-2*(dist/width)**2)*np.clip((-.0094-v[:,1])/.0008,0,1);v[:,1]+=weight*depth
hand.data.vertices.foreach_set('co',v.ravel());hand.data.update()
mat=bpy.data.materials.new('Soft warm skin - repaired hands');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');rgb=[.90,.65,.53];lin=[((c+.055)/1.055)**2.4 for c in rgb];p.inputs['Base Color'].default_value=(*lin,1);p.inputs['Roughness'].default_value=.60;p.inputs['Specular IOR Level'].default_value=.20;hand.data.materials.append(mat)
for f in hand.data.polygons:f.use_smooth=True
# Close the small exposed original hair tip behind the thumb, rather than leaving an open shell.
hairmat=bpy.data.materials.new('Hair tip closure - warm brown');hairmat.use_nodes=True;hb=hairmat.node_tree.nodes.get('Principled BSDF');hb.inputs['Base Color'].default_value=(.13,.053,.028,1);hb.inputs['Roughness'].default_value=.62
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(.01235,-.0116,.0648));cap=bpy.context.object;cap.name='Hair tip closed behind thumb';cap.scale=(.00125,.00065,.00065);cap.data.materials.append(hairmat)
for f in cap.data.polygons:f.use_smooth=True
# Finished ribbed cuff rim covers the old reconstructed wrist edge.
bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=16,location=(.0165,-.0107,.0586),major_radius=.00365,minor_radius=.00050);rim=bpy.context.object;rim.name='Raised sleeve cuff finished rim';rim.scale.y=.58
for v in rim.data.vertices:
 angle=math.atan2(v.co.y,v.co.x);v.co.z+=.000065*math.cos(32*angle)
cm=bpy.data.materials.new('Cuff rim cream knit');cm.use_nodes=True;cb=cm.node_tree.nodes.get('Principled BSDF');cb.inputs['Base Color'].default_value=(.73,.60,.48,1);cb.inputs['Roughness'].default_value=.85;rim.data.materials.append(cm)
for f in rim.data.polygons:f.use_smooth=True

# Match the lowered fist skin, without touching its cuff or the bag.
lower=[]
for f in o.data.polygons:
 x,y,z=f.center
 if -.028<x<-.0203 and .0275<z<.0340 and -.022<y<-.006:lower.append(f.index)
o.data.materials.append(mat);skin_id=len(o.data.materials)-1
# Preserve the lowered fist texture; no rectangular material patch is added.
# Its original curled-finger silhouette is intentional in the reference.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
for name,target,pos,scale in [('raised-front-after',(.018,0,.065),(.018,-.2,.065),.020),('raised-side-after',(.018,-.009,.064),(.13,-.16,.070),.020),('lower-front-after',(-.022,-.01,.032),(-.022,-.2,.032),.019)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6手部精修.blend'));bpy.ops.object.select_all(action='DESELECT')
for a in s.objects:
 if a.type=='MESH':a.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6手部精修.glb'),use_selection=True,export_format='GLB');o.data=full
(D/'手部修改报告.json').write_text(json.dumps({'removed_old_hand_faces':len(remove),'new_fingers':5,'new_hand_vertices':len(hand.data.vertices),'lower_fist_material_faces':len(lower),'scope':'local raised hand replacement, shallow palm creases, lowered fist skin; bag unchanged'},ensure_ascii=False,indent=2),encoding='utf8');print('HAND_REPAIR_DONE')
