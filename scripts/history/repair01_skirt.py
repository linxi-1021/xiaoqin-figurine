import bpy,math,json,numpy as np,bmesh
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_鞋履收敛_v35_20261025';D=B/'3D重建_v6基础_五处局部收口_v36_20261025'
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6鞋履收敛.blend'))
body=bpy.data.objects['textured_mesh.obj'];m=body.data
# The dark inner hem uses the existing garment texture material, without changing its image.
a=np.load('models/rebuild/closure_faces.npy');c=a[(a[:,3]>.032)&(a[:,3]<.038)&(a[:,7]<.15)&(a[:,9]>a[:,7]*.8)&(a[:,2]<-.006)&(abs(a[:,1])<.014)]
uv=tuple(c[len(c)//2,10:12]);print('UV',uv)
inner_mat=bpy.data.materials.new('Repair inner cloth sampled from original atlas');inner_mat.use_nodes=True
nt=inner_mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.7
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=m.materials[0].node_tree.nodes.get('Image Texture').image;nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])

def tex_object(o,name,uv):
 o.name=name;o.data.materials.append(inner_mat);layer=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for k in layer.data:k.uv=uv
 for f in o.data.polygons:f.use_smooth=True
 return o
# Closed inner saddle fills the cavity under the original skirt and overlaps the thigh roots internally.
bpy.ops.mesh.primitive_uv_sphere_add(segments=128,ring_count=48,location=(0,-.0008,.0331));o=bpy.context.object;o.scale=(.0135,.0100,.0022);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);tex_object(o,'REPAIR-01 Solid skirt inner saddle',uv)
# Closed rounded inner hem with a 1.2 mm circular section, inset within the source edge.
vs=[];fs=[];N=192;K=16
for i in range(N):
 t=2*math.pi*i/N;ct=Vector((.0132*math.cos(t),-.0008+.0097*math.sin(t),.0333+.00045*math.cos(t)));radial=Vector((math.cos(t),math.sin(t),0))
 for j in range(K):vs.append(ct+.00060*(radial*math.cos(j*2*math.pi/K)+Vector((0,0,math.sin(j*2*math.pi/K)))))
for i in range(N):
 for j in range(K):fs.append((i*K+j,((i+1)%N)*K+j,((i+1)%N)*K+(j+1)%K,i*K+(j+1)%K))
me=bpy.data.meshes.new('Closed rounded inner hem');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('REPAIR-01 Rolled inner hem 1.2mm',me);bpy.context.collection.objects.link(ob);tex_object(ob,ob.name,uv)
# Correct closed shell orientation.
for ob in bpy.context.scene.objects:
 if ob.name.startswith('REPAIR-01'):
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(ob.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(D/'过程备份'/'01裙底.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v36五处局部收口.glb'),use_selection=True,export_format='GLB')
