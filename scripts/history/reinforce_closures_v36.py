import bpy,numpy as np,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_五处局部收口_v36_20261025');part=int(sys.argv[sys.argv.index('--')+1]);source={2:'05手包轻贴',3:'06发底实体补强',4:'07发臂实体补强'};dest={2:'06发底实体补强',3:'07发臂实体补强',4:'08肩腋实体补强'}
bpy.ops.wm.open_mainfile(filepath=str(D/'过程备份'/(source[part]+'.blend')));o=bpy.data.objects['textured_mesh.obj'];m=o.data;tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pixels=np.array(im.pixels[:]).reshape(h,w,4);points=[];palette=[]
for f in m.polygons:
 x,y,z=f.center
 if part==2 and not(.0285<z<.052 and y>.003 and abs(x)<.029):continue
 if part==3 and not(.010<x<.031 and .047<z<.068 and -.004<y<.020):continue
 if part==4 and not(.007<abs(x)<.023 and .049<z<.068 and abs(y)<.012):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);r,g,b=pixels[int(uv[1]*h)%h,int(uv[0]*w)%w,:3]
 if part in [2,3] and not(r>g*1.42 and g>b*1.12 and r>.025 and g/max(r,.001)>.12):continue
 if part==4 and not(r>.18 and g>r*.55 and r<g*1.55):continue
 hit=tree.ray_cast(f.center-f.normal*.00003,-f.normal,.0010)
 if hit[0] is None or hit[3]>.00077 or hit[3]<.00002:continue
 c=(f.center+hit[0])*.5
 if any((c-cc).length<.00055 for cc in points):continue
 points.append(c);palette.append(uv)
print('CANDIDATE_CAPS',part,len(points),flush=True)
if len(points)>180:raise RuntimeError('Too many repair candidates; refused broad repair')
mat=bpy.data.materials.new('Local reinforcement original atlas');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.7;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
vs=[];fs=[];uvs=[]
for c,uv in zip(points,palette):
 base=len(vs);N=24;K=12
 vs.append(c+Vector((0,0,.00065)));uvs.append(uv)
 for j in range(1,K):
  ph=math.pi*j/K
  for i in range(N):
   t=2*math.pi*i/N;vs.append(c+Vector((math.sin(ph)*math.cos(t),math.sin(ph)*math.sin(t),math.cos(ph)))*.00065);uvs.append(uv)
 bottom=len(vs);vs.append(c-Vector((0,0,.00065)));uvs.append(uv)
 for i in range(N):fs.append((base,base+1+i,base+1+(i+1)%N))
 for j in range(K-2):
  for i in range(N):fs.append((base+1+j*N+i,base+1+(j+1)*N+i,base+1+(j+1)*N+(i+1)%N,base+1+j*N+(i+1)%N))
 for i in range(N):fs.append((bottom,base+1+(K-2)*N+(i+1)%N,base+1+(K-2)*N+i))
me=bpy.data.meshes.new('Local closed reinforcement caps');me.from_pydata(vs,[],fs);me.update();caps=bpy.data.objects.new('Temporary local reinforcement',me);bpy.context.collection.objects.link(caps);me.materials.append(mat);layer=me.uv_layers.new(name='UVMap')
for f in me.polygons:
 f.use_smooth=True
 for li in f.loop_indices:layer.data[li].uv=uvs[me.loops[li].vertex_index]
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
if points:
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Local repair union '+str(part),'BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.use_self=True;mod.object=caps;print('UNION_START',flush=True);bpy.ops.object.modifier_apply(modifier=mod.name);print('UNION_DONE',flush=True)
bpy.data.objects.remove(caps,do_unlink=True);bm=bmesh.new();bm.from_mesh(o.data);boundary=sum(e.is_boundary for e in bm.edges);bad=sum(not e.is_manifold for e in bm.edges);bm.free();print('UNION_TOPOLOGY',boundary,bad,flush=True)
if bad>308:raise RuntimeError('Union introduced non-manifold edges; refusing save')
bpy.ops.wm.save_as_mainfile(filepath=str(D/'过程备份'/(dest[part]+'.blend')));bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v36五处局部收口.glb'),use_selection=True,export_format='GLB')
