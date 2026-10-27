import bpy,bmesh,numpy as np,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_熊帽檐下包绒_v3_20261020';D=B/'3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6熊帽檐下包绒_v3.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];old=yarn.data;body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and o!=yarn),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,150,3);ns=len(co);assert len(old.polygons)==ns*142
centers=co.mean(1);keep=np.ones(ns,bool);rear=centers[:,1]>.003;deep=centers[:,1]>.006;normals=np.zeros((ns,3),np.float32);anchors=np.zeros((ns,3),np.float32);cells={};removed=0
for i in np.flatnonzero(rear):
 hit=tree.find_nearest(Vector(centers[i]));anchors[i]=hit[0];normals[i]=hit[1];key=tuple(np.floor(anchors[i]/.00145).astype(int))
 if deep[i]:
  count=cells.get(key,0)
  if count>=3:keep[i]=False;removed+=1
  else:cells[key]=count+1
ids=np.flatnonzero(keep);out=co[ids].copy();selected_rear=np.flatnonzero(rear[ids]);a=np.clip((centers[ids[selected_rear],1]-.003)/.004,0,1);a=a*a*(3-2*a)
for jj,alpha in zip(selected_rear,a):
 i=ids[jj];v=co[i].astype(np.float64).reshape(15,10,3);line=v.mean(1);n=normals[i].astype(float);anchor=anchors[i].astype(float);vec=line-anchor;vertical=(vec@n)[:,None]*n;tangent=vec-vertical;new_line=anchor+tangent*(1+.18*alpha)+vertical*(1+.65*alpha)+n*.00010*alpha;out[jj]=(new_line[:,None,:]+(v-line[:,None,:])*(1+.55*alpha)).reshape(150,3)
front_before=co[ids[~rear[ids]]];front_after=out[~rear[ids]];front_equal=np.array_equal(front_before,front_after)
# Fill the old recessed bow footprint before positioning the bow on the new plush.
coverage={};cg=.00050
for pp in out[rear[ids]].reshape(-1,3):
 kk=(int(math.floor(pp[0]/cg)),int(math.floor(pp[2]/cg)));coverage[kk]=max(coverage.get(kk,-1),float(pp[1]))
def covered_height(x,z):
 ix=int(math.floor(x/cg));iz=int(math.floor(z/cg));return max([coverage.get((ix+dx,iz+dz),-1) for dx in [-1,0,1] for dz in [-1,0,1]])
fill=[];fillm=[];frng=random.Random(7314);fanchor=0
for row,z in enumerate(np.arange(.079,.099,.00125)):
 for x in np.arange(-.0105,.0106,.00125):
  x=float(x+(.000625 if row%2 else 0));hit=tree.ray_cast(Vector((x,.08,float(z))),Vector((0,-1,0)))
  if hit[0] is None or hit[0].y<.018 or hit[1].y<.25:continue
  c=hit[0];n=hit[1].normalized()
  if covered_height(c.x,c.z)>c.y+.00065:continue
  fanchor+=1;t=Vector((.342,0,.94));t=(t-n*n.dot(t)).normalized();u=t.cross(n).normalized()
  for j in range(3):
   aa=(j-1)*.55+frng.uniform(-.18,.18);a=t*math.cos(aa)+u*math.sin(aa);b=n.cross(a).normalized();length=frng.uniform(.0013,.0017);radius=frng.uniform(.00065,.00080);height=frng.uniform(.00095,.00125);cc=c+u*(j-1)*.00020-n*.00018;verts=[];phase=frng.random()*6.28
   for ii in range(15):
    tt=ii/14;center=cc+a*length*(tt-.45)+b*.00011*math.sin(math.pi*tt*1.5+phase)+n*height*math.sin(math.pi*tt);tangent=(a*length+b*.000165*math.pi*math.cos(math.pi*tt*1.5+phase)+n*height*math.pi*math.cos(math.pi*tt)).normalized();side=tangent.cross(n).normalized();up=side.cross(tangent).normalized();rr=radius*(.38+.62*math.sin(math.pi*tt)**.5)
    for k in range(10):
     ph=2*math.pi*k/10;tw=.94+.06*math.cos(2*ph+tt*math.pi*3);verts.append(tuple(center+rr*tw*(side*math.cos(ph)+up*math.sin(ph))))
   fill.append(verts);fillm.append(frng.randrange(5))
if fill:out=np.concatenate([out,np.array(fill,dtype=np.float32)],axis=0)

# Rebuild closed strand topology while retaining every front vertex exactly.
tot=np.array([old.polygons[i].loop_total for i in range(142)],np.int32);starts=np.array([old.polygons[i].loop_start for i in range(142)],np.int32);nv=old.polygons[141].loop_start+old.polygons[141].loop_total;template=np.array([old.loops[i].vertex_index for i in range(nv)],np.int32);assert nv==580
mi=np.array([old.polygons[int(i)*142].material_index for i in ids]+fillm,np.int32);new=bpy.data.meshes.new('Coarse rear plush - front preserved');new.vertices.add(len(out)*150);new.vertices.foreach_set('co',out.reshape(-1));new.loops.add(len(out)*580);new.loops.foreach_set('vertex_index',(np.arange(len(out),dtype=np.int32)[:,None]*150+template).ravel());new.polygons.add(len(out)*142);new.polygons.foreach_set('loop_start',(np.arange(len(out),dtype=np.int32)[:,None]*580+starts).ravel());new.polygons.foreach_set('loop_total',np.tile(tot,len(out)));new.polygons.foreach_set('material_index',np.repeat(mi,142));new.polygons.foreach_set('use_smooth',np.ones(len(out)*142,bool))
for mat in old.materials:new.materials.append(mat)
new.update(calc_edges=True);yarn.data=new
# Quantized rear surface envelope provides the true plush height under the bow.
rearverts=out[out.mean(1)[:,1]>.003].reshape(-1,3);surface={};grid=.00050
for p in rearverts:
 k=(int(math.floor(p[0]/grid)),int(math.floor(p[2]/grid)));surface[k]=max(surface.get(k,-1),float(p[1]))
def furheight(x,z):
 ix=int(math.floor(x/grid));iz=int(math.floor(z/grid));a=[surface[(ix+dx,iz+dz)] for dx in [-1,0,1] for dz in [-1,0,1] if (ix+dx,iz+dz) in surface];return max(a) if a else None
bows=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Ribbon')];delta=0.;used=0
for o in bows:
 for v in o.data.vertices:
  p=o.matrix_world@v.co;n=o.matrix_world.to_3x3()@v.normal
  if n.y<.20:continue
  h=furheight(p.x,p.z)
  if h is not None:delta=max(delta,h+.00065-p.y);used+=1
delta=max(delta,.0010)
for o in bows:o.location.y+=delta
# Small concealed attachment keeps the knot physically joined to the hat.
knot=bpy.data.objects.get('Ribbon wrapped center');kp=sum((knot.matrix_world@v.co for v in knot.data.vertices),Vector())/len(knot.data.vertices);hit=tree.ray_cast(Vector((kp.x,.10,kp.z)),Vector((0,-1,0)));root=hit[0].y if hit[0] else kp.y-delta;end=min((knot.matrix_world@v.co).y for v in knot.data.vertices)+.00035;depth=end-root+.0004
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.00075,depth=depth,location=(kp.x,(root+end)*.5,kp.z),rotation=(math.pi/2,0,0));mount=bpy.context.object;mount.name='GEO-Concealed bow attachment';mount.data.materials.append(knot.data.materials[0])
for f in mount.data.polygons:f.use_smooth=True
# Visibility clearance after moving the complete bow, tails and star together.
clear=[]
for o in bows:
 for v in o.data.vertices:
  p=o.matrix_world@v.co;n=o.matrix_world.to_3x3()@v.normal
  if n.y<.20:continue
  h=furheight(p.x,p.z)
  if h is not None:clear.append(p.y-h)
bm=bmesh.new();bm.from_mesh(new);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6后帽粗绒浮贴蝴蝶结_v4.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6后帽粗绒浮贴蝴蝶结_v4.glb'),use_selection=True,export_format='GLB')
r={'front_vertex_values_preserved_exactly':bool(front_equal),'original_front_strands':int((~rear).sum()),'rear_strands_before':int(rear.sum()),'rear_strands_after':int((rear&keep).sum())+len(fill),'bow_underlay_new_strands':len(fill),'bow_underlay_tufts':fanchor,'rear_density_reduction_percent':round(100*(removed-len(fill))/max(1,int(rear.sum())),1),'rear_cross_section_scale':1.55,'rear_rise_scale':1.65,'bow_group_translation_y_mm':delta*1000,'bow_group': [o.name for o in bows],'minimum_bow_front_clearance_mm':min(clear)*1000 if clear else None,'concealed_attachment':mount.name,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold};(D/'后帽与蝴蝶结校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
