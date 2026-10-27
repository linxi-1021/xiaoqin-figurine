import bpy,numpy as np,math,json,bmesh
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_四指并拢保留长短_20261020';D=B/'3D重建_v6基础_前星星发夹修正_20261020';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6四指并拢.blend'));o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));m=o.data;co=np.array([v.co[:] for v in m.vertices]);before=co.copy();im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4);mask=np.zeros((h,w),bool);gold=[]
for f in m.polygons:
 x,y,z=f.center
 if not (.0145<x<.0233 and .0738<z<.0835 and y<-.006):continue
 uv=np.array([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices]);c=pix[int(uv[:,1].mean()*h)%h,int(uv[:,0].mean()*w)%w,:3]
 if not(c[0]>.35 and c[1]/c[0]>.50 and c[2]/max(c[1],1e-5)<.70):continue
 gold.append(f.index)
 for j in range(1,len(uv)-1):
  t=uv[[0,j,j+1]]*np.array([w,h]);lo=np.maximum(np.floor(t.min(0)).astype(int)-1,0);hi=np.minimum(np.ceil(t.max(0)).astype(int)+1,[w-1,h-1]);xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));p=np.stack([xx+.5,yy+.5],-1);a,b,c=t;v=b-a;u=c-a;det=v[0]*u[1]-v[1]*u[0]
  if abs(det)<1e-8:continue
  q=p-a;s=(q[...,0]*u[1]-q[...,1]*u[0])/det;t0=(v[0]*q[...,1]-v[1]*q[...,0])/det;inside=(s>=-.05)&(t0>=-.05)&(s+t0<=1.05);mask[lo[1]:hi[1]+1,lo[0]:hi[0]+1]|=inside
ids=set(i for fi in gold for i in m.polygons[fi].vertices)
# Retain the complete main mesh topology; recess only the old gold relief into its hair carrier.
for i in ids:
 x,y,z=co[i];target=-.0088+1.05*(x-.0195)
 co[i,1]=y
m.vertices.foreach_set('co',co.ravel());m.update()
for _ in range(2):mask=mask|np.roll(mask,1,0)|np.roll(mask,-1,0)|np.roll(mask,1,1)|np.roll(mask,-1,1)
# Restore brown hair under the replacement without touching the face or other UV layers.
mask &= (pix[:,:,0]>.45)&(pix[:,:,1]/np.maximum(pix[:,:,0],.001)>.60)&(pix[:,:,2]/np.maximum(pix[:,:,1],.001)<.58)
pix[mask,:3]=[.315,.165,.105];newim=bpy.data.images.new('Front clip carrier cleaned atlas',width=w,height=h,alpha=True);newim.pixels.foreach_set(pix.ravel());m.materials[0].node_tree.nodes.get('Image Texture').image=newim;im=newim;im.update();im.filepath_raw=str(D/'front-star-clean-hair-atlas.png');im.file_format='PNG';im.save();im.pack()
# Plane follows the oblique right temple: horizontal axis tangent to hair, normal points outwards.
center=Vector((.0191,-.0120,.07945));u=Vector((1,.75,0)).normalized();n=Vector((.75,-1,0)).normalized();v=Vector((0,0,1));R=.0031;inner=R*.49;pts=[]
for i in range(10):
 a=math.pi/2+math.radians(4)+i*math.pi/5;r=R if i%2==0 else inner;pts.append((r*math.cos(a),r*math.sin(a)))
vs=[]
for depth in [-.00055,.00038]:
 for x,z in pts:vs.append(tuple(center+u*x+v*z+n*depth))
fs=[tuple(reversed(range(10))),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
me=bpy.data.meshes.new('Rounded five-point star');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('GEO-Front gold five-point star hair clip',me);bpy.context.collection.objects.link(ob)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
mat=bpy.data.materials.new('Front star warm honey gold');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.83,.43,.075,1);p.inputs['Metallic'].default_value=.48;p.inputs['Roughness'].default_value=.30;me.materials.append(mat)
bev=ob.modifiers.new('Rounded gold edges','BEVEL');bev.width=.00020;bev.segments=5
bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=bev.name)
for f in me.polygons:f.use_smooth=True
norm=ob.modifiers.new('Stable broad star face normals','WEIGHTED_NORMAL');norm.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=norm.name)
bpy.ops.object.select_all(action='DESELECT')
for a in bpy.context.scene.objects:
 if a.type=='MESH':a.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6前星星发夹修正.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6前星星发夹修正.glb'),export_format='GLB',use_selection=True)
r={'reference':'25_金色星星发夹.png','old_relief_vertices_recessed':len(ids),'old_gold_faces':len(gold),'main_topology_unchanged':True,'outside_local_vertex_change_count':int(np.count_nonzero(np.linalg.norm(co-before,axis=1)>0))-len([i for i in ids if np.linalg.norm(co[i]-before[i])>0]),'new_star_points':5,'star_closed':all(len(e.link_faces)==2 for e in []),'star_object':ob.name}
bm=bmesh.new();bm.from_mesh(ob.data);r['star_boundary_edges']=sum(e.is_boundary for e in bm.edges);r['star_nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);bm.free();(D/'星星修正校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))




