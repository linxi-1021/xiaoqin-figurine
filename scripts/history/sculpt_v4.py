import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;out=r/'detail-v4';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'finished/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
sub=body.modifiers.new('Local sculpt sampling resolution','SUBSURF');sub.levels=1;bpy.ops.object.modifier_apply(modifier=sub.name)
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
co=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)
def world(pixel):return np.array([.018+(pixel[0]-500)*.025/1000,.07+(500-pixel[1])*.025/1000])
# Positions measured in the orthographic hand diagnostic, not guessed from the hero view.
paths=[([(463,615),(450,671),(432,720)],.00022,.00032), ([(530,638),(515,702),(490,761)],.00024,.0004), ([(615,721),(581,764),(554,801)],.00023,.00036), ([(345,802),(405,827),(457,826)],.00015,.00016), ([(425,854),(458,880),(469,911)],.00014,.00012)]
ids=np.where((co[:,0]>.011)&(co[:,0]<.024)&(co[:,2]>.058)&(co[:,2]<.069))[0]
front=np.zeros(len(ids),dtype=bool)
for j,i in enumerate(ids):
 x,y,z=co[i];hit=tree.ray_cast(Vector((float(x),-.1,float(z))),Vector((0,1,0)))
 front[j]=hit[0] is not None and abs(hit[0].y-y)<.00022
points=co[ids][:,[0,2]];disp=np.zeros(len(ids))
for pixels,width,depth in paths:
 path=[world(p) for p in pixels];dist=np.full(len(ids),1.)
 for a,b in zip(path,path[1:]):
  v=b-a;t=np.clip(((points-a)*v).sum(1)/(v@v),0,1);d=np.linalg.norm(points-a-t[:,None]*v,axis=1);dist=np.minimum(dist,d)
 disp=np.maximum(disp,depth*np.exp(-2*(dist/width)**2))
disp*=front
co[ids,1]+=disp
body.data.vertices.foreach_set('co',co.ravel());body.data.update()
group=body.vertex_groups.new(name='Hand crease finishing')
for i,d in zip(ids,disp):
 if d>.000002:group.add([int(i)],min(1,float(d/.00008)),'REPLACE')
smooth=body.modifiers.new('Polish carved finger grooves','SMOOTH');smooth.vertex_group=group.name;smooth.factor=.35;smooth.iterations=3
bpy.ops.object.modifier_apply(modifier=smooth.name)
(out/'sculpt-changes.json').write_text(json.dumps({'source':'v3 textured master','orthographic_hand_center_m':[.018,0,.07],'hand_ortho_scale_m':.025,'sculpted_vertices':int(np.sum(disp>.00001)),'max_depth_mm':float(disp.max()*1000),'features':['three shallow finger separation grooves','two palm creases'],'note':'Root connections preserved; no replacement primitive hand'},indent=2))
# Recess bow center into cap slightly and keep the existing accepted silhouette.
for o in bpy.context.scene.objects:
 if o.name=='Bow central knot':o.scale.y*=.85
s=bpy.context.scene;s.cycles.samples=40;s.cycles.use_denoising=True
cam=s.camera
def camera(location,target,scale):
 cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
m=bpy.data.materials.new('Diagnostic matte gray');m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.18,.21,.25,1);n.inputs['Roughness'].default_value=.8
s.render.resolution_x=1000;s.render.resolution_y=1000;s.view_layers[0].material_override=m
camera((.018,-.3,.07),(.018,0,.07),.025);s.render.filepath=str(out/'hand-after.png');bpy.ops.render.render(write_still=True)
s.view_layers[0].material_override=None;s.render.resolution_y=1200
for name,angle in [('front',0),('side',90),('back',180),('threequarter',35),('backthreequarter',145)]:
 a=math.radians(angle);camera((.27*math.sin(a),-.27*math.cos(a),.105),(0,0,.06),.15);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
fullmesh=body.data.copy()
web=body.modifiers.new('Web preview optimization','DECIMATE');web.ratio=.3;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=web.name)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB')
body.data=fullmesh
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'))
print('SCULPT_DONE')
