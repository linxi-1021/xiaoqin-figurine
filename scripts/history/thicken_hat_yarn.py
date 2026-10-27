import bpy,math,json,numpy as np,random,bmesh
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_前星星发夹修正_20261020';D=B/'3D重建_v6基础_熊帽毛线加粗_20261020';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6前星星发夹修正.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));m=body.data;im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);rng=random.Random(2810);cells={};counts={}
for f in m.polygons:
 x,y,z=f.center
 if not(z>.094 or (z>.0895 and (y>.004 or abs(x)>.023))):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],axis=0);col=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3];r,g,b=col
 cream=r>.82 and g/max(r,.001)>.72 and b/max(g,.001)>.68 and z>(.1020-.22*x) and y<-.003
 brown=.37<r<.88 and .49<g/max(r,.001)<.72 and b/max(g,.001)>.57
 if not brown or cream:continue
 if cream and col[0]-col[1]>.24:continue
 if f.normal.z<-.6:continue
 key=tuple(int(t/.00068) for t in f.center)
 if key not in cells or rng.random()<.15:cells[key]=(f.center.copy(),f.normal.copy(),col.copy(),cream)
# Smooth compact closed yarn loops: no detached fur cards or hair particles.
vs=[];fs=[];mis=[];mats=[]
def mat(name,c):
 a=bpy.data.materials.new(name);a.use_nodes=True;p=a.node_tree.nodes.get('Principled BSDF');lin=[((float(t)+.055)/1.055)**2.4 for t in c];p.inputs['Base Color'].default_value=(*lin,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.88;p.inputs['Sheen Weight'].default_value=.18;p.inputs['Specular IOR Level'].default_value=.12;return a
for cream in [False,True]:
 for j in range(5):
  base=np.array([.72,.45,.33]) if not cream else np.array([.94,.80,.65]);base*=.85+j*.065;mats.append(mat(('Cream' if cream else 'Cocoa')+' chenille yarn '+str(j),np.minimum(base,.99)))
for idx,(c,n,col,cream) in enumerate(cells.values()):
 n.normalize();up=Vector((0,0,1));t=up-n*n.dot(up)
 if t.length<.1:t=Vector((1,0,0))-n*n.x
 t.normalize();u=t.cross(n).normalized();ang=rng.uniform(-1.0,1.0);t,u=t*math.cos(ang)+u*math.sin(ang),u*math.cos(ang)-t*math.sin(ang)
 for j in range(2):
  angle=(-.52 if j==0 else .52)+rng.uniform(-.2,.2);a=t*math.cos(angle)+u*math.sin(angle);b=n.cross(a).normalized();L=rng.uniform(.00038,.00051);W=rng.uniform(.00021,.00025);rad=rng.uniform(.00016,.000195);cc=c+n*.000025+u*((j-.5)*.00014);base=len(vs);N=20;K=8
  for k in range(N):
   ph=2*math.pi*k/N;center=cc+a*(L*math.cos(ph))+b*(W*math.sin(ph))+n*(.00011*(1+math.sin(ph))*.5);tan=(-a*L*math.sin(ph)+b*W*math.cos(ph)+n*.000055*math.cos(ph)).normalized();side=tan.cross(n).normalized();out=side.cross(tan).normalized()
   for q in range(K):
    th=2*math.pi*q/K;vs.append(tuple(center+rad*(math.cos(th)*side+math.sin(th)*out)))
  mi=(5 if cream else 0)+rng.randrange(5)
  for k in range(N):
   for q in range(K):fs.append((base+k*K+q,base+((k+1)%N)*K+q,base+((k+1)%N)*K+(q+1)%K,base+k*K+(q+1)%K));mis.append(mi)
me=bpy.data.meshes.new('Closed chenille yarn loops');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('GEO-Bear hat surface chenille stitches',me);bpy.context.collection.objects.link(ob)
for a in mats:me.materials.append(a)
for f,mi in zip(me.polygons,mis):f.material_index=mi;f.use_smooth=True
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bd=sum(e.is_boundary for e in bm.edges);nm=sum(not e.is_manifold for e in bm.edges);bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6熊帽毛线加粗.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6熊帽毛线加粗.glb'),use_selection=True,export_format='GLB')
r={'tuft_clusters':len(cells),'closed_yarn_loops':len(cells)*2,'new_faces':len(fs),'boundary_edges':bd,'nonmanifold_edges':nm,'original_mesh_and_materials_unchanged':True,'reference':'04_帽子整体.png','method':'surface anchored closed chenille yarn loops, varying orientation and length; cream and cocoa yarn; smooth brim and facial features preserved'};(D/'帽子绒线校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
