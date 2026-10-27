import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v7';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();v=n.cross(u).normalized();u=v.cross(n).normalized()
R=.0058;T=.0034;B=.00038
# Keep the fused original bag core for attachment, bury only its exposed bag shell under a new cylindrical skin.
# The hand lies outside the negative-u gate; the skirt and sweater lie behind the depth gate.
co=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)
center=np.array(c);axis=np.array(n);uu=np.array(u);vv=np.array(v);q=co-center
a=q@uu;b=q@vv;d=q@axis;rr=np.sqrt(a*a+b*b)
mask=(a>-.0066)&(a<.0073)&(b>-.0073)&(b<.0082)&(d>-.0048)&(d<.004)&(rr<.0084)
# Preserve the upper narrow connector, where the strap enters the bag.
mask&=~((b>.0064)&(abs(a)<.0014))
indices=np.where(mask)[0]
rad=np.minimum(rr[indices],R-.00065);factor=rad/np.maximum(rr[indices],1e-8)
aa=a[indices]*factor;bb=b[indices]*factor;dd=np.clip(d[indices],-T+.0004,-.00045)
co[indices]=center+aa[:,None]*uu+bb[:,None]*vv+dd[:,None]*axis
body.data.vertices.foreach_set('co',co.ravel());body.data.update()
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Specular IOR Level'].default_value=.12;return m
cream=material('Cylindrical bag cream leather',(.76,.59,.42));seam=material('Bag edge warm piping',(.64,.43,.25))
face=material('Cylindrical bag clean bear face',(1,1,1));image=bpy.data.images.load(str(r/'bag-v6/小熊包_清晰五官图案.png'));image.pack();tex=face.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;face.node_tree.links.new(tex.outputs['Color'],face.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
def cyl(name,center,radius,depth,edge,frontmat,side):
 N=128;vs=[];fs=[];mats=[];uvs=[]
 rings=[(-depth,radius-edge),(-depth+edge*.3,radius-edge*.3),(-depth+edge,radius),(-edge,radius),(-edge*.3,radius-edge*.3),(0,radius-edge)]
 for z,rad in rings:
  for i in range(N):
   t=i*math.tau/N;vs.append(tuple(center+u*(rad*math.cos(t))+v*(rad*math.sin(t))+n*z))
 for j in range(len(rings)-1):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i));mats.append(0)
 back=len(vs);vs.append(tuple(center-n*depth));front=len(vs);vs.append(tuple(center))
 for i in range(N):
  fs.append((back,(i+1)%N,i));mats.append(0)
  fs.append((front,(len(rings)-1)*N+i,(len(rings)-1)*N+(i+1)%N));mats.append(1)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(side);mesh.materials.append(frontmat)
 uv=mesh.uv_layers.new(name='Bag face planar UV')
 for p,mi in zip(mesh.polygons,mats):
  p.material_index=mi;p.use_smooth=mi==0
  for li in p.loop_indices:
   q=Vector(vs[mesh.loops[li].vertex_index])-center;uv.data[li].uv=(.5+q.dot(u)/(radius*2),.5+q.dot(v)/(radius*2))
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();return o
bag=cyl('Bag round cylindrical body',c,R,T,B,face,cream)
# Small bear ears retain the reference design while the main body remains a circular cylinder.
for side in [-1,1]:
 earcenter=c+u*(side*.0046)+v*.0049-n*.0008
 cyl('Bear bag ear '+str(side),earcenter,.00145,.0018,.0003,cream,cream)
# Continuous front piping makes the circular silhouette and equal thickness readable.
curve=bpy.data.curves.new('Circular seam','CURVE');curve.dimensions='3D';curve.bevel_depth=.00011;curve.bevel_resolution=3
sp=curve.splines.new('POLY');sp.points.add(127)
for i,p in enumerate(sp.points):
 t=i*math.tau/128;q=c+u*((R-B*.45)*math.cos(t))+v*((R-B*.45)*math.sin(t))-n*.00018;p.co=(*q,1)
sp.use_cyclic_u=True;edge=bpy.data.objects.new('Bag circular edge piping',curve);bpy.context.collection.objects.link(edge);curve.materials.append(seam)
s=bpy.context.scene;s.cycles.samples=24;s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
def camera(loc,target,scale):cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
for name,loc in [('bag-front',c+n*.14),('bag-side',c+n*.065+u*.13),('bag-context',Vector((-.014,-.3,.032)))]:
 camera(loc,c if name!='bag-context' else Vector((-.014,0,.032)),.022 if name!='bag-context' else .024);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=1000;s.render.resolution_y=1200
for name,angle in [('front',0),('threequarter',35),('back',180)]:
 a=math.radians(angle);camera((.27*math.sin(a),-.27*math.cos(a),.105),(0,0,.06),.15);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','CURVE'}:o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.convert(target='MESH')
full=body.data.copy();mod=body.modifiers.new('Web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB');body.data=full
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'))
(out/'bag-shape-report.json').write_text(json.dumps({'main_body':'short circular cylinder','diameter_mm':R*2000,'depth_mm':T*1000,'edge_radius_mm':B*1000,'ear_count':2,'repositioned_old_shell_vertices':len(indices),'retained':'v6 bear face artwork, original strap and pose','note':'Cylinder thickness is measured perpendicular to the circular faces; no perspective flattening used'},ensure_ascii=False,indent=2),encoding='utf-8');print('CYLINDER_BAG_DONE',len(indices))
