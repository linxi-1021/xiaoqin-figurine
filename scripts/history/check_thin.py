import bpy,json,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(r/'finished/小秦_重建模型.blend'))
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.stl_import(filepath=str(r/'finished/小秦_120mm_打印校验版.stl'))
p=bpy.context.object
bpy.context.view_layer.objects.active=p;p.scale=(.001,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
tree=BVHTree.FromObject(p,bpy.context.evaluated_depsgraph_get())
random.seed(261018);samples=random.sample(list(p.data.polygons),min(8000,len(p.data.polygons)))
thin=[];hits=[];rejected_grazing=0
for f in samples:
 n=f.normal.normalized();start=f.center-n*.00001;hit=tree.ray_cast(start,-n,.05)
 if hit[0] is not None and hit[1].dot(n)<-.3:
  thick=(hit[0]-f.center).length*1000;hits.append(thick)
  if thick<.8:thin.append({'point_mm':[v*1000 for v in f.center],'sampled_thickness_mm':thick})
 elif hit[0] is not None:rejected_grazing+=1
report={'method':'8000 deterministic random face samples; inward normal ray, opposing hit normals dot < -0.3. Screening only, not certified minimum wall thickness','sample_count':len(samples),'valid_hits':len(hits),'rejected_grazing_hits':rejected_grazing,'under_0_8mm_sample_count':len(thin),'smallest_samples':sorted(thin,key=lambda a:a['sampled_thickness_mm'])[:80]}
(r/'finished/thickness-screening.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('THICKNESS',len(thin),len(hits))
# Render imported STL alone, so floating or lost decoration is visible.
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o!=p:o.hide_render=True
mat=bpy.data.materials.new('Print gray');mat.diffuse_color=(.25,.28,.33,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.25,.28,.33,1);bs.inputs['Roughness'].default_value=.85;p.data.materials.clear();p.data.materials.append(mat)
for f in p.data.polygons:f.use_smooth=True
s=bpy.context.scene;s.cycles.samples=24;cam=s.camera
for name,location,target,scale in [('print-back',(0,.27,.105),(0,0,.06),.15),('hand-detail',(0,-.27,.085),(.019,0,.069),.035)]:
 cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(r/'finished'/(name+'.png'));bpy.ops.render.render(write_still=True)
