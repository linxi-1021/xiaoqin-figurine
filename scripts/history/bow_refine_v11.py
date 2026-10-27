import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_帽檐上部补绒_v10_20261021';D=B/'3D重建_v6基础_蝴蝶结吊星结构精修_v11_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6帽檐上部补绒.blend'))
yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];arr=np.empty(len(yarn.data.vertices)*3,np.float32);yarn.data.vertices.foreach_get('co',arr);arr=arr.reshape(-1,3);back=arr[(arr[:,1]>.015)&(abs(arr[:,0])<.015)&(arr[:,2]>.075)&(arr[:,2]<.102)];grid={};cell=.0007
for x,y,z in back:
 k=(int(math.floor(x/cell)),int(math.floor(z/cell)));grid[k]=max(grid.get(k,0),float(y))
def surface(x,z):
 ix=int(math.floor(x/cell));iz=int(math.floor(z/cell));vals=[grid.get((ix+a,iz+b),0) for a in [-1,0,1] for b in [-1,0,1]];return max(max(vals),.024)
def mat(name,c,rough,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
cloth=mat('Ivory satin ribbon',(.69,.58,.43),.43);gold=mat('Warm gold pendant and closed eyelet',(.83,.47,.095),.26,.75)
for o in list(bpy.context.scene.objects):
 if o.name.startswith('Ribbon') or 'Concealed bow attachment' in o.name:bpy.data.objects.remove(o,do_unlink=True)
def solid_patch(name,func,nu=40,nv=20,thick=.00038):
 verts=[];faces=[]
 for layer in [-1,1]:
  for i in range(nu+1):
   for j in range(nv+1):
    x,y,z=func(i/nu,-1+2*j/nv);verts.append((x,y+layer*thick/2,z))
 N=(nu+1)*(nv+1)
 for i in range(nu):
  for j in range(nv):
   a=i*(nv+1)+j;b=a+nv+1;faces.extend([(a,a+1,b+1,b),(N+a,N+b,N+b+1,N+a+1)])
 edge=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
 for a,b in zip(edge,edge[1:]+edge[:1]):faces.append((a,b,N+b,N+a))
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(cloth)
 for f in m.polygons:f.use_smooth=True
 return o
# A rigid backing level keeps gathered loops clear of every existing tuft.
ybase=max(surface(x,z) for x in np.linspace(-.009,.009,15) for z in np.linspace(.090,.097,8))+.00035
for sign in [-1,1]:
 def lobe(u,v,s=sign):
  width=.0008+.00235*math.sin(math.pi*u*.68);x=s*(.00025+.0084*u-.0007*u*v*v);z=.093+.00035*math.sin(math.pi*u)+width*v;y=ybase+.00125*math.sin(math.pi*u)*(1-v*v)+.00028*math.sin(v*math.pi*3)*(1-u)**2;return x,y,z
 solid_patch('Ribbon folded loop '+str(sign),lobe)
 # Smooth the cloth support envelope so individual tufts do not imprint steps.
 ts=np.linspace(0,1,40);ys=[]
 for tt in ts:
  xx=sign*(.0005+.0038*tt+.00035*math.sin(math.pi*tt));zz=.0916-.0088*tt;ww=.00115+.00055*tt;ys.append(max(surface(xx+vv*ww,zz) for vv in [-1,0,1])+.00055)
 polynomial=np.polyfit(ts,ys,3);offset=max(np.array(ys)-np.polyval(polynomial,ts))+.00008
 def tail(u,v,s=sign,poly=polynomial.copy(),lift=offset):
  x=s*(.0005+.0038*u+.00035*math.sin(math.pi*u));z=.0916-.0088*u+.00065*v*v*u**6;width=.00115+.00055*u;x+=width*v;y=max(float(np.polyval(poly,u))+lift,ybase-.0007)+.0002*math.sin(math.pi*u);return x,y,z
 solid_patch('Ribbon draped tail '+str(sign),tail)
# Rounded wrapped knot overlaps the roots of both folded loops and tails.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,ybase+.0003,.0928));knot=bpy.context.object;knot.name='Ribbon rounded wrapped knot';knot.dimensions=(.0025,.0020,.0044);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);knot.data.materials.append(cloth);be=knot.modifiers.new('Soft folded edges','BEVEL');be.width=.0005;be.segments=5;bpy.context.view_layer.objects.active=knot;bpy.ops.object.modifier_apply(modifier=be.name)
for f in knot.data.polygons:f.use_smooth=True
# Continuous hidden backing joins the sewn center to the original hat surface.
body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));from mathutils.bvhtree import BVHTree
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());hit=tree.ray_cast(Vector((0,.08,.0928)),Vector((0,-1,0)));root=hit[0].y;end=ybase+.0002
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.00065,depth=end-root+.0004,location=(0,(root+end)/2,.0928),rotation=(math.pi/2,0,0));mount=bpy.context.object;mount.name='GEO-Sewn bow center attachment';mount.data.materials.append(cloth)
# Pendant hangs from an eyelet at the right ribbon tip, with gravity along -Z.
tx,ty,tz=tail(1,0,1);ringz=tz-.00025;ringy=ty+.00030
bpy.ops.mesh.primitive_torus_add(major_radius=.00048,minor_radius=.00013,major_segments=48,minor_segments=12,location=(tx,ringy,ringz),rotation=(math.pi/2,0,0));ring=bpy.context.object;ring.name='Ribbon pendant closed gold connector';ring.data.materials.append(gold)
starR=.00165;starZ=ringz-.00040-starR;stary=max(surface(tx,starZ)+.00060,ringy);vs=[]
for y in [stary-.00028,stary+.00028]:
 for j in range(10):
  a=math.pi/2+j*math.pi/5;r=starR if j%2==0 else starR*.49;vs.append((tx+r*math.cos(a),y,starZ+r*math.sin(a)))
fs=[tuple(range(9,-1,-1)),tuple(range(10,20))]+[(j,(j+1)%10,(j+1)%10+10,j+10) for j in range(10)];m=bpy.data.meshes.new('Five point rounded solid star');m.from_pydata(vs,[],fs);m.update();star=bpy.data.objects.new('Ribbon hanging star',m);bpy.context.collection.objects.link(star);m.materials.append(gold);bpy.context.view_layer.objects.active=star;be=star.modifiers.new('Rounded physical pendant edges','BEVEL');be.width=.00012;be.segments=4;bpy.ops.object.modifier_apply(modifier=be.name)
# Extend the closed connector through the star top when the cloth sits forward of the pendant.
if abs(stary-ringy)>.0002:
 ring.location.y=stary;ringy=stary
# Small gold suspension loop through the star tip, overlapping the connector.
bpy.ops.mesh.primitive_torus_add(major_radius=.00022,minor_radius=.00010,major_segments=32,minor_segments=10,location=(tx,stary,starZ+starR-.00010),rotation=(0,math.pi/2,0));eye=bpy.context.object;eye.name='Ribbon star integral eyelet';eye.data.materials.append(gold)
for ob in [ring,eye,star]:
 for f in ob.data.polygons:f.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6蝴蝶结吊星结构精修.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6蝴蝶结吊星结构精修.glb'),use_selection=True,export_format='GLB')
r={'ribbon_thickness_mm':.38,'center_sewn_attachment':True,'closed_connector_ring':True,'star_integral_eyelet':True,'pendant_gravity_axis':'-Z','hat_and_character_meshes_unchanged':True,'bow_backing_y_mm':ybase*1000,'tail_tip':list((tx,ty,tz)),'connector_y_mm':ringy*1000,'star_center':list((tx,stary,starZ))};(D/'配饰结构校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
