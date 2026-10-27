import bpy,json,struct,hashlib,collections,numpy as np
from mathutils import Vector
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'no-bag-v10'
def fingerprint(body,kind):
 uv=body.data.uv_layers['UVMap'].data;counts=collections.Counter()
 for f in body.data.polygons:
  p=f.center
  if kind=='legs':keep=p.z<.029
  else:
   line=.009+(p.z-.064)*.65;keep=p.z>.045 and not(.0435<p.z<.0655 and -.0014<p.x-line<.0031 and p.y<-.002)
  if not keep:continue
  corners=[]
  for j in f.loop_indices:
   co=body.data.vertices[body.data.loops[j].vertex_index].co;t=uv[j].uv;corners.append(struct.pack('5f',*co,*t))
  counts[hashlib.blake2b(b''.join(sorted(corners)),digest_size=16).digest()]+=1
 return counts
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'));b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));before={k:fingerprint(b,k) for k in ['legs','outside_strap']}
# Fit only the original intact front knit to reconstruct the leather-covered depth.
im=b.data.materials[0].node_tree.nodes.get('Image Texture').image;pix=np.empty(im.size[0]*im.size[1]*4,np.float32);im.pixels.foreach_get(pix);pix=pix.reshape(im.size[1],im.size[0],4);uv=b.data.uv_layers['UVMap'].data;fit=[]
for f in b.data.polygons:
 p=f.center
 if not(-.009<p.x<.008 and .043<p.z<.064 and -.012<p.y<0 and f.normal.y<-.55):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(im.size[1]-1))%im.size[1],int(t.x*(im.size[0]-1))%im.size[0],:3]
 if rgb[1]>rgb[0]*.84 and rgb[2]>rgb[0]*.64 and rgb[0]>.4:fit.append(tuple(p*1000))
fit=np.array(fit);x=fit[:,0];z=fit[:,2]-54;A=np.column_stack([np.ones(len(x)),x,z,x*x,x*z,z*z]);coeff=np.linalg.lstsq(A,fit[:,1],rcond=None)[0]

bpy.ops.wm.open_mainfile(filepath=str(out/'working.blend'));b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));b.data.validate(verbose=True,clean_customdata=False);b.data.update(calc_edges=True);assert not b.data.validate(clean_customdata=False);after={k:fingerprint(b,k) for k in before};checks={k:{'unchanged':before[k]==after[k],'source_faces':sum(before[k].values()),'result_faces':sum(after[k].values())} for k in before};assert all(v['unchanged'] for v in checks.values()),checks
(out/'independent-preservation-check.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
# Smooth only the new local patch, never the source garment.
import numpy as np
patch=bpy.data.objects.get('Local knit under removed strap')
if patch:
 # Rebuild only the authorized narrow strip with knit-scale relief, avoiding a flat ribbon.
 material=patch.data.materials[0];vv=[];ff=[];NX=53;NZ=220
 for iz in range(NZ+1):
  zz=.0435+.022*iz/NZ;cx=.009+(zz-.064)*.65
  for ix in range(NX+1):
   xx=cx-.0018+.0053*ix/NX;x=xx*1000;z=zz*1000-54
   yy=float(np.dot(coeff,[1,x,z,x*x,x*z,z*z]))*.001+.00007
   wave=2*np.pi*xx/.0015+1.05*np.sin(2*np.pi*zz/.0032)
   edge=np.sin(np.pi*ix/NX)**.7
   yy-=edge*.0003*(.5+.5*np.cos(wave))**2
   vv.append((xx,yy,zz))
 for iz in range(NZ):
  for ix in range(NX):
   j=iz*(NX+1)+ix;ff.append((j,j+1,j+NX+2,j+NX+1))
 me=bpy.data.meshes.new('Local reconstructed knit relief');me.from_pydata(vv,[],ff);me.materials.append(material);uv=me.uv_layers.new(name='LocalRepairUV')
 for f in me.polygons:
  f.use_smooth=True
  for j in f.loop_indices:
   vi=me.loops[j].vertex_index;uv.data[j].uv=((vi%(NX+1))/NX,(vi//(NX+1))/NZ)
 patch.data=me
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=800;s.render.resolution_y=960;cam=s.camera
for name,angle in [('front',0),('side',-65)]:
 import math
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_保留原衣腿_去包.blend'));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=b;bpy.ops.export_scene.gltf(filepath=str(out/'小秦_保留原衣腿_去包.glb'),use_selection=True,export_format='GLB');print('PRESERVED',json.dumps(checks))
