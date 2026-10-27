import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_装饰贴帽修正_v12_20261021';D=B/'3D重建_v6基础_柔褶蝴蝶结圆润星_v13_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6装饰贴帽修正.blend'));changed=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name.startswith('Ribbon folded') or o.name.startswith('Ribbon draped')):continue
 N=len(o.data.vertices)//2;nu=40;nv=20;assert N==(nu+1)*(nv+1);inv=o.matrix_world.inverted()
 for i in range(nu+1):
  u=i/nu
  for j in range(nv+1):
   v=-1+2*j/nv;idx=N+i*(nv+1)+j;p=o.matrix_world@o.data.vertices[idx].co
   if 'folded' in o.name:
    # Rounded gathering ridges run from the central knot out into the wing.
    rise=(.00030+.00045*math.exp(-((u-.24)/.30)**2))*(1-v*v)*(.50+.50*math.cos(2.7*math.pi*v+u*.9))
    rise+=.00030*math.sin(math.pi*u)**.8*(1-v*v)
   else:
    rise=.00042*(1-u)**1.3*(1-v*v)*(.55+.45*math.cos(2*math.pi*v+.6*u))+.00010*math.sin(math.pi*u)*(1-v*v)
   p.y+=rise;o.data.vertices[idx].co=inv@p
 changed.append(o.name)
# Preserve the suspension eyelet and replace only the pendant body with a soft organic gold star.
o=bpy.data.objects['Ribbon hanging star'];pts=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);center=pts.mean(0);xmin,ymin,zmin=pts.min(0);xmax,ymax,zmax=pts.max(0);gold=o.data.materials[0];bpy.data.objects.remove(o,do_unlink=True)
R=.00165;outline=[]
outer=[1.00,.94,1.04,.97,1.02];inner=[.56,.53,.58,.55,.54]
for j in range(10):
 a=math.pi/2+j*math.pi/5+math.radians([0,1,-2,1,2,-1,0,2,-1,-2][j]);r=R*(outer[j//2] if j%2==0 else inner[j//2]);outline.append(np.array([r*math.cos(a),r*math.sin(a)]))
for _ in range(3):
 outline=[p*.75+q*.25 for p,q in zip(outline,outline[1:]+outline[:1]) for p in [p]] if False else [v for p,q in zip(outline,outline[1:]+outline[:1]) for v in [p*.75+q*.25,p*.25+q*.75]]
outline=np.array(outline);outline[:,0]*=(xmax-xmin)/(outline[:,0].max()-outline[:,0].min());outline[:,1]*=(zmax-zmin)/(outline[:,1].max()-outline[:,1].min());outline[:,0]+=((xmin+xmax)/2)-(outline[:,0].max()+outline[:,0].min())/2;outline[:,1]+=zmax-outline[:,1].max();cx=(xmin+xmax)/2;cz=(zmin+zmax)/2;cy=(ymin+ymax)/2;K=len(outline);levels=[.20,.42,.64,.82,.94,1.0];vs=[];fs=[]
for sign in [-1,1]:
 for r in levels:
  for x,z in outline:
   vs.append((cx+(x-cx)*r,cy+sign*(.00012+.00028*math.sqrt(max(0,1-r*r))),cz+(z-cz)*r))
L=len(levels);N=K*L
for side in range(2):
 off=side*N
 for row in range(L-1):
  for k in range(K):
   a=off+row*K+k;b=off+row*K+(k+1)%K;c=b+K;d=a+K;fs.append((a,b,c,d) if side else (d,c,b,a))
 pole=len(vs);vs.append((cx,cy+(-1 if side==0 else 1)*.00040,cz))
 for k in range(K):fs.append((pole,off+k,off+(k+1)%K) if side else (pole,off+(k+1)%K,off+k))
for k in range(K):
 a=(L-1)*K+k;b=(L-1)*K+(k+1)%K;fs.append((a,b,N+b,N+a))
m=bpy.data.meshes.new('Soft asymmetric rounded gold star');m.from_pydata(vs,[],fs);m.update();star=bpy.data.objects.new('Ribbon hanging star',m);bpy.context.collection.objects.link(star);m.materials.append(gold)
for f in m.polygons:f.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6柔褶蝴蝶结圆润星.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6柔褶蝴蝶结圆润星.glb'),use_selection=True,export_format='GLB')
(D/'本版说明.json').write_text(json.dumps({'folded_cloth_front_only':changed,'cloth_back_contact_preserved':True,'star_rounded_outline_iterations':3,'star_slight_asymmetry':True,'star_eyelet_position_preserved':True},ensure_ascii=False,indent=2),encoding='utf8')
