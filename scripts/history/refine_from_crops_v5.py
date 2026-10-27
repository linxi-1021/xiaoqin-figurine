import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;out=r/'detail-v5';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'detail-v4/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
def surface(x,z):
 h=tree.ray_cast(Vector((x,.15,z)),Vector((0,-1,0)))
 return h[0].y if h[0] is not None else .023
cream=bpy.data.materials.get('Warm cream ribbon');gold=bpy.data.materials.get('Honey gold stars')
cream.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.64,.53,.40,1)
before=bpy.data.collections.new('Archived old bow - hidden');bpy.context.scene.collection.children.link(before)
for o in list(bpy.context.scene.objects):
 if 'bow' in o.name.lower() or (o.type=='MESH' and o.data.materials and o.data.materials[0]==cream):
  bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,vs,fs,material):
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(material)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 for f in data.polygons:f.use_smooth=True
 return o
# Measured from crop 51: broad solid fabric lobes, pinched near the center, no rope holes.
def ribbon(name,side,tail=False):
 nt=28;nu=12;vs=[];fs=[]
 for layer in [0,1]:
  for i in range(nt+1):
   t=i/nt
   for j in range(nu+1):
    u=2*j/nu-1
    if not tail:
     x=side*(.0005+.009*t-.00065*t**8*abs(u)**4);width=.0011+.0020*math.sin(t*math.pi/2)**.6
     z=.0928+.0008*t+width*u
     fold=.00065*math.cos(u*math.pi*2)*math.exp(-3*t)
     thick=.0008+.0018*(1-u*u)*math.sin(math.pi*t/2)+fold
    else:
     x=side*(.0008+.004*t)+u*.0016
     z=.0915-.0085*t+.0005*abs(u)*t**8
     thick=.00085+.00025*(1-u*u)
    y=surface(x,z)-.00025+layer*thick
    vs.append((x,y,z))
 count=(nt+1)*(nu+1)
 def ix(i,j,l):return l*count+i*(nu+1)+j
 for l in [0,1]:
  for i in range(nt):
   for j in range(nu):fs.append((ix(i,j,l),ix(i+1,j,l),ix(i+1,j+1,l),ix(i,j+1,l)))
 boundary=[ix(0,j,0) for j in range(nu+1)]+[ix(i,nu,0) for i in range(1,nt+1)]+[ix(nt,j,0) for j in range(nu-1,-1,-1)]+[ix(i,0,0) for i in range(nt-1,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):fs.append((a,b,b+count,a+count))
 o=mesh(name,vs,fs,cream);bevel=o.modifiers.new('Fabric rounded edges','BEVEL');bevel.width=.00018;bevel.segments=3
 return o
for side in [-1,1]:ribbon('Ribbon lobe '+str(side),side);ribbon('Ribbon tail '+str(side),side,True)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,surface(0,.0928)+.0006,.0928));knot=bpy.context.object;knot.name='Ribbon wrapped center';knot.dimensions=(.0028,.002,.0045);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);knot.data.materials.append(cream);bevel=knot.modifiers.new('Soft knot corners','BEVEL');bevel.width=.00065;bevel.segments=5
for f in knot.data.polygons:f.use_smooth=True
# Back ornaments conform to local hair/cap curvature instead of sinking on one side.
star_names=[];petals=[]
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or o==body:continue
 if 'star' in o.name.lower():
  coords=[o.matrix_world@v.co for v in o.data.vertices];lo=min(p.y for p in coords)
  for v,p in zip(o.data.vertices,coords):
   p.x=-p.x
   p.y=surface(p.x,p.z)-.00025+(p.y-lo);v.co=o.matrix_world.inverted()@p
  star_names.append(o.name)
 if o.data.materials and o.data.materials[0].name.startswith('Daisy ivory'):
  o.location.x=-o.location.x;center=o.location.copy();o.location.y+=surface(center.x,center.z)+.00025-center.y
  # Two measured flower centers, matching the accepted star/flower layout.
  cx,cz=min([(-.016,.065),(.013,.056)],key=lambda c:(c[0]-center.x)**2+(c[1]-center.z)**2)
  a=math.atan2(center.z-cz,center.x-cx);o.rotation_euler.y=math.pi/2-a;petals.append(o.name)
 elif o.data.materials and o.data.materials[0]==gold and 'star' not in o.name.lower():
  o.location.x=-o.location.x;center=o.location.copy();o.location.y+=surface(center.x,center.z)+.0008-center.y
# A shallow inner-frame groove improves relief readability without moving eyes or replacing the face.
co=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)
ids=np.where((abs(co[:,0])<.019)&(co[:,2]>.069)&(co[:,2]<.084))[0];points=co[ids][:,[0,2]]
paths=[[(244,458),(290,422),(370,431),(430,477),(458,538),(435,582),(360,597),(282,570),(240,518),(244,458)],[(609,540),(659,513),(739,528),(794,574),(813,633),(780,673),(702,675),(636,647),(608,596),(609,540)]]
dist=np.full(len(ids),1.)
for path in paths:
 path=[np.array([(x-500)*.046/1000,.079+(500-y)*.046/1000]) for x,y in path]
 for a,b in zip(path,path[1:]):
  v=b-a;t=np.clip(((points-a)*v).sum(1)/(v@v),0,1);dist=np.minimum(dist,np.linalg.norm(points-a-t[:,None]*v,axis=1))
depth=.00016*np.exp(-2*(dist/.00022)**2);changed=0
for j,i in enumerate(ids):
 if depth[j]<.000004:continue
 x,y,z=co[i];h=tree.ray_cast(Vector((float(x),-.15,float(z))),Vector((0,1,0)))
 if h[0] is not None and abs(h[0].y-y)<.00015:co[i,1]+=depth[j];changed+=1
body.data.vertices.foreach_set('co',co.ravel());body.data.update()
changes={'references':[51,52,53,55,56,57,58,12,13,14,15,26,27],'new_bow':'closed broad fabric lobes with center folds; closed flat tails; rounded wrapped knot','conformed_stars':star_names,'radially_oriented_petals':len(petals),'inner_frame_groove_vertices':changed,'max_frame_recess_mm':.16,'unchanged':'v4 hand sculpt, face silhouette, pose, outfit and bag layout','limitations':'eyeglasses remain integral relief; no detached lens reconstruction or physical test print'}
(out/'reference-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.convert(target='MESH')
full=body.data.copy();web=body.modifiers.new('Web optimization','DECIMATE');web.ratio=.3;bpy.ops.object.modifier_apply(modifier=web.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB');body.data=full
s=bpy.context.scene;s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1200;cam=s.camera
def camera(loc,target,scale):cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
for name,angle in [('front',0),('side',90),('back',180),('threequarter',35),('backthreequarter',145)]:
 a=math.radians(angle);camera((.27*math.sin(a),-.27*math.cos(a),.105),(0,0,.06),.15);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.resolution_y=1000;camera((0,.3,.092),(0,0,.092),.035);s.render.filepath=str(out/'bow-detail.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'));print('REFERENCE_REFINEMENT_DONE',json.dumps(changes,ensure_ascii=False))
