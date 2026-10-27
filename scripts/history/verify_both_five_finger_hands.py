import bpy,bmesh,numpy as np,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_双手五指重建_20261019'
def bodyrows(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co);vi=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',vi);cols=[co.reshape(-1,3)[vi].reshape(-1,12)]
 for uv in o.data.uv_layers:
  a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);cols.append(a.reshape(-1,8))
 a=np.empty(len(o.data.polygons),np.int32);o.data.polygons.foreach_get('material_index',a);cols.append(a[:,None].astype(np.float32));return np.ascontiguousarray(np.concatenate(cols,axis=1))
r=json.loads((D/'双手结构记录.json').read_text(encoding='utf8'));old=bodyrows(S/'小秦_v6包身材质接缝修复.blend');new=bodyrows(D/'小秦_v6双手五指重建.blend');keep=np.ones(len(old),bool);keep[r['removed_original_polygon_indices']]=False
assert old[keep].shape==new.shape
same=np.array_equal(old[keep],new)
if not same:
 a=old[keep].copy().view(np.dtype((np.void,old.dtype.itemsize*old.shape[1]))).ravel();b=new.copy().view(np.dtype((np.void,new.dtype.itemsize*new.shape[1]))).ravel();same=np.array_equal(np.sort(a),np.sort(b))
assert same
result={'passed':True,'all_surviving_original_faces_coordinates_uvs_materials_unchanged':True,'surviving_original_faces':int(keep.sum()),'removed_old_hand_faces':int((~keep).sum()),'new_hands':{}}
for name in ['Open hand - five fingers','Curled hand - four fingers and thumb']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);left=set(bm.verts);components=0
 while left:
  components+=1;stack=[left.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in left:left.remove(n);stack.append(n)
 bm.free();assert bad==0 and components==1;result['new_hands'][name]={'digit_count':o['digit_count'],'closed_manifold':True,'connected_components':components,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}
(D/'双手独立结构校验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result))
s=bpy.context.scene;s.cycles.samples=16;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera;points={}
mat=bpy.data.materials.new('Five finger structural gray');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.21,.24,1);bs.inputs['Roughness'].default_value=.85;s.view_layers[0].material_override=mat
for name,target,pos,scale in [('open-front',(.0175,-.0104,.0636),(.0175,-.20,.0636),.020),('fist-front',(-.0205,-.0035,.0350),(-.0205,-.2,.0350),.012)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.view_layer.update();pnts=[]
 if name=='open-front':items=[(d['name'],d['tip']) for d in r['open_hand_digits']]
 else:items=[('thumb',r['external_thumb'][-1])]+[(n,d['path'][2]) for n,d in zip(['little','ring','middle','index'],r['curled_fingers'])]
 for n,p in items:
  q=world_to_camera_view(s,cam,Vector(p));pnts.append({'name':n,'pixel':[q.x*900,(1-q.y)*900]})
 points[name]=pnts;s.render.filepath=str(D/(name+'-gray.png'));bpy.ops.render.render(write_still=True)
(D/'五指投影检查点.json').write_text(json.dumps(points,ensure_ascii=False,indent=2),encoding='utf8');print('FIVE_FINGER_CHECK_DONE')
