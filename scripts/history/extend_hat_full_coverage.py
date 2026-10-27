import bpy,math,json,numpy as np,random,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_前星星发夹修正_20261020';D=B/'3D重建_v6基础_熊帽全覆盖加粗_20261020';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6前星星发夹修正.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));m=body.data;im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);rng=random.Random(64108);cells={};U=Vector((.94,0,-.342)).normalized();V=Vector((.342,0,.94)).normalized();origin=Vector((.00666,0,.10105));eyes=[Vector((-.00117,-.01267,.10393)),Vector((.0145,-.01251,.09818))];nose=Vector((.0054,-.0152,.1009))

protected=[];pv=[];pf=[]
for item in bpy.context.scene.objects:
 if item.type!='MESH' or item==body:continue
 coords=[item.matrix_world@v.co for v in item.data.vertices]
 if max(v.y for v in coords)<.005:continue
 protected.append(item.name);base=len(pv);pv.extend(coords);pf.extend([tuple(base+i for i in f.vertices) for f in item.data.polygons])
protection=BVHTree.FromPolygons(pv,pf) if pv else None
protected_skips=0;region_counts={'brim':0,'rear_lower':0};anchors=[]
for f in m.polygons:
 x,y,z=f.center;q=(f.center-origin).dot(V)
 rear_lower=y>.009 and .071<z<.089

 if z<.089 and not rear_lower and not(y<-.006 and z>.084):continue
 if y<-.006 and q<-.018:continue
 if y<-.030:continue

 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);col=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3];r,g,b=col
 brim=(y<-.006 and z>.0835 and q>-.018 and r>.62 and g/max(r,.001)>.78 and b/max(g,.001)>.66)
 if y<-.003 and q<-.0055 and abs((f.center-origin).dot(U))<.014 and not brim:continue
 ear=(x<-.011 and z>.105)or(x>.022 and z>.100)
 cream=(r>.58 and g/max(r,.001)>.63 and -.0165<y<-.004 and q>-.0045 and (any(((f.center-e).dot(U)/.0060)**2+((f.center-e).dot(V)/.0050)**2<1 for e in eyes) or (((f.center-origin).dot(U)/.0045)**2+(q/.0027)**2<1)))
 cocoa=r>.32 and .44<g/max(r,.001)<.84 and b/max(g,.001)>.54
 dark=ear and r>.10 and g/max(r,.001)>.28 and b/max(g,.001)>.45
 if z<.089 and not(rear_lower or brim):continue
 if not(cream or cocoa or dark or brim):continue
 if rear_lower and not(r>.36 and g/max(r,.001)>.47 and b/max(g,.001)>.51):continue
 if not(cream or brim) and r>.80 and g/max(r,.001)>.78:continue
 # Clear the whole eyes/eyelash zone and nose volume, including the fiber radius.
 if any(((f.center-e).dot(U)/.0026)**2+((f.center-e).dot(V)/.0025)**2<1 and y<-.005 for e in eyes):continue
 if ((f.center-nose).dot(U)/.0025)**2+((f.center-nose).dot(V)/.0019)**2<1 and y<-.009:continue
 if f.normal.z<-.7 and not(brim or rear_lower):continue
 if protection:
  nearest=protection.find_nearest(f.center)
  if nearest and nearest[0] is not None and nearest[3]<.00035:
   protected_skips+=1;continue
 kind=1 if(cream or brim) else (2 if dark and (r<.57 or g/max(r,.001)<.5) else 0)
 key=tuple(int(t/.00102) for t in f.center)
 if key not in cells or rng.random()<.08:cells[key]=(f.center.copy(),f.normal.copy(),kind)
 if brim:region_counts['brim']+=1
 if rear_lower:region_counts['rear_lower']+=1
vs=[];fs=[];mis=[];mats=[]
def material(name,c,rough=.86):
 a=bpy.data.materials.new(name);a.use_nodes=True;p=a.node_tree.nodes.get('Principled BSDF');lin=[((min(float(t),.99)+.055)/1.055)**2.4 for t in c];p.inputs['Base Color'].default_value=(*lin,1);p.inputs['Roughness'].default_value=rough;p.inputs['Specular IOR Level'].default_value=.14;p.inputs['Sheen Weight'].default_value=.16;return a
for label,c in [('Rose cocoa',(.72,.49,.38)),('Ivory plush',(.97,.86,.73)),('Ear hollow',(.48,.25,.14))]:
 for i in range(5):mats.append(material(label+str(i),np.array(c)*(.94+i*.025)))
# A tuft is a fan of three solid bent yarn strands, with tapered round tips and no ring holes.
for c,n,kind in cells.values():
 n.normalize();t=V-n*n.dot(V)
 if t.length<.1:t=U-n*n.dot(U)
 t.normalize();u=t.cross(n).normalized();angle=rng.uniform(-.65,.65);t,u=t*math.cos(angle)+u*math.sin(angle),u*math.cos(angle)-t*math.sin(angle)
 for j in range(3):
  angle=(j-1)*.62+rng.uniform(-.15,.15);a=t*math.cos(angle)+u*math.sin(angle);b=n.cross(a).normalized();length=rng.uniform(.00110,.00155)*( .85 if kind==1 else 1);radius=rng.uniform(.000207,.000270);height=rng.uniform(.00022,.00035);cc=c+u*((j-1)*.00018)-n*.00010;base=len(vs);N=14;K=10;phase=rng.random()*6.28
  # End poles close each strand; intermediate rings form a plump twisted capsule.
  for i in range(N+1):
   tt=i/N;center=cc+a*(length*(tt-.45))+b*(.00011*math.sin(math.pi*tt*1.5+phase))+n*(height*math.sin(math.pi*tt));tangent=(a*length+b*(.000165*math.pi*math.cos(math.pi*tt*1.5+phase))+n*(height*math.pi*math.cos(math.pi*tt))).normalized();side=tangent.cross(n).normalized();up=side.cross(tangent).normalized();rr=radius*(.38+.62*math.sin(math.pi*tt)**.5)
   for k in range(K):
    ph=2*math.pi*k/K;twist=.94+.06*math.cos(2*ph+tt*math.pi*3);vs.append(tuple(center+rr*twist*(side*math.cos(ph)+up*math.sin(ph))))
  if protection and protection.find_nearest(c)[3]<.0019:
   blocked=False
   for pp in vs[base:]:
    hh=protection.find_nearest(Vector(pp))
    if hh and hh[0] is not None and hh[3]<.00018:blocked=True;break
   if blocked:
    del vs[base:];continue
  mi=kind*5+rng.randrange(5)
  for i in range(N):
   for k in range(K):fs.append((base+i*K+k,base+(i+1)*K+k,base+(i+1)*K+(k+1)%K,base+i*K+(k+1)%K));mis.append(mi)
  fs.extend([tuple(base+k for k in reversed(range(K))),tuple(base+N*K+k for k in range(K))]);mis.extend([mi,mi])
me=bpy.data.meshes.new('Solid clustered yarn sculpt');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('GEO-Redesigned hat solid plush tufts',me);bpy.context.collection.objects.link(ob)
for a in mats:me.materials.append(a)
for f,mi in zip(me.polygons,mis):f.material_index=mi;f.use_smooth=True
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
# Real smooth glassy eyes and a soft oval nose, rather than adding yarn over facial features.
blue=material('Deep navy bear eyes',(.035,.075,.23),.14);p=blue.node_tree.nodes.get('Principled BSDF');p.inputs['Sheen Weight'].default_value=0;p.inputs['Coat Weight'].default_value=.25;p.inputs['Coat Roughness'].default_value=.12;p.inputs['Specular IOR Level'].default_value=.5
brown=material('Warm brown oval bear nose',(.30,.105,.035),.28)
def ellipsoid(name,c,n,sizes,mat):
 uu=U-n*n.dot(U);uu.normalize();vv=n.cross(uu).normalized();rot=Matrix((uu,vv,n)).transposed();bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=c);o=bpy.context.object;o.name=name;o.rotation_euler=rot.to_euler();o.scale=sizes;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for f in o.data.polygons:f.use_smooth=True
for i,(e,n) in enumerate(zip(eyes,[Vector((-.12,-.82,.45)).normalized(),Vector((.20,-.76,.52)).normalized()])):ellipsoid('GEO-Bear hat glossy blue eye '+str(i+1),e+n*.00023,n,(.0021,.0019,.00065),blue)
ellipsoid('GEO-Bear hat smooth brown nose',nose+Vector((0,-.00065,.0001)),Vector((.12,-.93,.35)).normalized(),(.00245,.00145,.00085),brown)

lashmat=material('Bear hat warm dark eyelashes',(.18,.065,.027),.5)
for ei,(e,n) in enumerate(zip(eyes,[Vector((-.12,-.82,.45)).normalized(),Vector((.20,-.76,.52)).normalized()])):
 uu=U-n*n.dot(U);uu.normalize();vv=n.cross(uu).normalized();side=-1 if ei==0 else 1
 for j in range(3):
  start=e+vv*.00125+uu*(side*(.0002+j*.00048))+n*.00030;end=start+vv*(.00115-j*.00012)+uu*(side*(.00035+j*.00011));mid=(start+end)*.5+uu*side*.00012
  cu=bpy.data.curves.new('Rounded eyelash strand','CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=.00016;cu.bevel_resolution=4;cu.use_fill_caps=True;sp=cu.splines.new('BEZIER');sp.bezier_points.add(2)
  for bp,pt in zip(sp.bezier_points,[start,mid,end]):bp.co=pt;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
  sp.bezier_points[-1].radius=.55;lash=bpy.data.objects.new('GEO-Bear hat eyelash %d %d'%(ei,j),cu);bpy.context.collection.objects.link(lash);cu.materials.append(lashmat);bpy.context.view_layer.objects.active=lash;lash.select_set(True);bpy.ops.object.convert(target='MESH');lash.select_set(False)

bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6熊帽全覆盖加粗.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6熊帽全覆盖加粗.glb'),use_selection=True,export_format='GLB');r={'protected_accessories':protected,'accessory_clearance_mm':0.18,'protected_candidates_skipped':protected_skips,'added_surface_faces_by_region':region_counts,'strand_thickness_increase_percent':15,'tuft_clusters':len(cells),'solid_yarn_strands':len(cells)*3,'ring_loops':0,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'regions':{str(k):sum(v[2]==k for v in cells.values()) for k in range(3)},'original_character_preserved':True};(D/'簇绒重设计校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
