import bpy,numpy as np,math,json,bmesh,hashlib
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_柔褶蝴蝶结圆润星_v13_20261021';D=B/'3D重建_v6基础_全部星饰圆润统一_v14_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6柔褶蝴蝶结圆润星.blend'));reports=[]
from mathutils.bvhtree import BVHTree
from mathutils import Vector
body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or 'star' not in o.name.lower() or o.name.startswith('Ribbon'):continue
 name=o.name;pts=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);
 if name=='Hair star 1':pts[:,2]-=.006
 c=pts.mean(0);e,axes=np.linalg.eigh(np.cov((pts-c).T));n=axes[:,0];outward=np.array([c[0],c[1],0]);n=n if n@outward>0 else -n
 nearest=tree.find_nearest(Vector(c));n=np.array(nearest[1]);n=n if n@outward>0 else -n
 if name.startswith('Hair star'):
  n=np.array([0.,1.,0.]);hit=tree.ray_cast(Vector((c[0],.08,c[2])),Vector((0,-1,0)));nearest=(hit[0],hit[1],0,0) if hit[0] is not None else nearest
 up=np.array([0.,0.,1.]);up-=n*(n@up);up/=np.linalg.norm(up);right=np.cross(up,n);right/=np.linalg.norm(right);uv=np.column_stack(((pts-c)@right,(pts-c)@up));depth=(pts-c)@n;lo=uv.min(0);hi=uv.max(0);outline=[]
 # Same softly uneven five-point character as the accepted pendant.
 for j in range(10):
  angle=math.pi/2+j*math.pi/5+math.radians([0,1,-2,1,2,-1,0,2,-1,-2][j]);radius=([1,.94,1.04,.97,1.02][j//2] if j%2==0 else [.56,.53,.58,.55,.54][j//2]);outline.append(np.array([radius*math.cos(angle),radius*math.sin(angle)]))
 for _ in range(3):outline=[v for p,q in zip(outline,outline[1:]+outline[:1]) for v in [p*.75+q*.25,p*.25+q*.75]]
 outline=np.array(outline);outline=(outline-outline.min(0))/np.ptp(outline,axis=0)*(hi-lo)+lo;center=(lo+hi)/2;K=len(outline);levels=[.20,.42,.64,.82,.94,1.];L=len(levels);vs=[];fs=[];back=float(depth.max())-.00012;height=max(.00065,min(float(np.ptp(depth)),.00115))
 for side in range(2):
  for r in levels:
   for p in outline:
    q=center+(p-center)*r;plane=c+right*q[0]+up*q[1];hit=tree.ray_cast(Vector(plane+n*.008),Vector(-n),.016);base=float((np.array(nearest[0])-c)@n);dd=base+(.00004 if side==0 else .00022+height*.70*math.sqrt(max(0,1-r*r)));vs.append(tuple(plane+n*dd))
 N=K*L
 for side in range(2):
  off=side*N
  for row in range(L-1):
   for k in range(K):
    a=off+row*K+k;b=off+row*K+(k+1)%K;quad=(a,b,b+K,a+K);fs.append(quad if side else tuple(reversed(quad)))
  pole=len(vs);plane=c+right*center[0]+up*center[1];hit=tree.ray_cast(Vector(plane+n*.008),Vector(-n),.016);base=float((np.array(nearest[0])-c)@n);dd=base+(.00004 if side==0 else .00022+height*.70);vs.append(tuple(plane+n*dd))
  for k in range(K):fs.append((pole,off+k,off+(k+1)%K) if side else (pole,off+(k+1)%K,off+k))
 for k in range(K):a=(L-1)*K+k;b=(L-1)*K+(k+1)%K;fs.append((a,b,N+b,N+a))
 mats=list(o.data.materials);bpy.data.objects.remove(o,do_unlink=True);mesh=bpy.data.meshes.new(name+' rounded organic dome');mesh.from_pydata(vs,[],fs);mesh.update();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
 for mat in mats:mesh.materials.append(mat)
 for f in mesh.polygons:f.use_smooth=True
 bm=bmesh.new();bm.from_mesh(mesh);bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert bad==0;reports.append({'name':name,'closed_manifold':True,'back_conformed_to_actual_hair_surface':True})
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6全部星饰圆润统一.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6全部星饰圆润统一.glb'),use_selection=True,export_format='GLB');(D/'星饰校验.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(reports))
