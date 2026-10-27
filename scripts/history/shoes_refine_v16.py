import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_发束细雕_v15_20261021';D=B/'3D重建_v6基础_鞋履细节精修_v16_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6发束细雕.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));m=body.data;nv=len(m.vertices);co=np.empty(nv*3,np.float32);m.vertices.foreach_get('co',co);co=co.reshape(-1,3);before=co.copy();x,y,z=co.T;mask=(z>.0098)&(z<.0162)&(abs(x)<.020)&(y<.012)&(y>-.023);weight=np.clip((z-.0098)/.0010,0,1)*np.clip((.0162-z)/.0013,0,1)*mask;edges=np.empty(len(m.edges)*2,np.int32);m.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2)
for _ in range(3):
 sums=np.zeros_like(co);num=np.zeros(nv);np.add.at(sums,edges[:,0],co[edges[:,1]]);np.add.at(sums,edges[:,1],co[edges[:,0]]);np.add.at(num,edges[:,0],1);np.add.at(num,edges[:,1],1);move=(sums/np.maximum(num[:,None],1)-co)*.24*weight[:,None];length=np.linalg.norm(move,axis=1);move*=np.minimum(1,.000035/np.maximum(length,1e-10))[:,None];co+=move
m.vertices.foreach_set('co',co.ravel());m.update();assert np.array_equal(co[~mask],before[~mask]);shoe=m.materials[0].copy();shoe.name='Cream leather shoes soft satin finish';p=shoe.node_tree.nodes.get('Principled BSDF');
for link in list(p.inputs['Roughness'].links):shoe.node_tree.links.remove(link)
p.inputs['Roughness'].default_value=.62;p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=.06;p.inputs['Coat Roughness'].default_value=.40;m.materials.append(shoe);slot=len(m.materials)-1
for f in m.polygons:
 if .0098<f.center.z<.019 and abs(f.center.x)<.020 and -.023<f.center.y<.012 and f.material_index==0:f.material_index=slot
# Fine continuous sole welt follows the existing shoe surface, rather than floating over it.
trim=bpy.data.materials.new('Soft ivory shoe welt');trim.use_nodes=True;p=trim.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.76,.62,.48,1);p.inputs['Roughness'].default_value=.58;tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());curves=[]
for sign in [-1,1]:
 candidates=co[(co[:,2]>.009)&(co[:,2]<.011)&(co[:,0]*sign>.001)&(abs(co[:,0])<.018)&(co[:,1]<.010)&(co[:,1]>-.020)];cx=float(np.median(candidates[:,0]));cy=float(np.median(candidates[:,1]));points=[]
 for a in np.linspace(0,2*math.pi,120,endpoint=False):
  direction=Vector((math.cos(a),math.sin(a),0));center=Vector((cx,cy,.0102));hit=tree.ray_cast(center+direction*.025,-direction,.027)
  if hit[0] is not None and hit[0].x*sign>.0004 and (hit[0]-center).length<.012:points.append(hit[0]+hit[1]*.00003)
 if True:continue
 cu=bpy.data.curves.new('Shoe sole welt '+str(sign),'CURVE');cu.dimensions='3D';cu.bevel_depth=.000095;cu.bevel_resolution=3;sp=cu.splines.new('NURBS');sp.points.add(len(points)-1)
 for pnt,v in zip(sp.points,points):pnt.co=(*v,1)
 sp.use_cyclic_u=True;sp.order_u=3;sp.use_endpoint_u=False;o=bpy.data.objects.new('GEO-Shoe sole fine welt '+str(sign),cu);bpy.context.collection.objects.link(o);cu.materials.append(trim);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);curves.append(o.name)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6鞋履细节精修.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6鞋履细节精修.glb'),use_selection=True,export_format='GLB');r={'shoe_vertices_refined':int((np.linalg.norm(co-before,axis=1)>1e-9).sum()),'max_displacement_mm':float(np.linalg.norm(co-before,axis=1).max()*1000),'non_shoe_vertices_exactly_preserved':True,'sole_welt_objects':curves,'references':['46_画面左鞋','47_画面右鞋','48_鞋带搭扣','60_后鞋与后跟','65_侧鞋外底']};(D/'鞋履校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
