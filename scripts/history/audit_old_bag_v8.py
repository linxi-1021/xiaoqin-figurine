import bpy,math,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v8';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v7/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();v=n.cross(u).normalized();u=v.cross(n).normalized()
def selected(p):
 q=p-c;a=q.dot(u);b=q.dot(v);d=q.dot(n)
 return -.0066<a<.0075 and -.0075<b<.0094 and -.0095<d<.0045 and a*a+b*b<.0093**2 and not(b>.0064 and abs(a)<.0016)
red=bpy.data.materials.new('Audit cut region');red.diffuse_color=(.7,.015,.01,1);red.use_nodes=True;red.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.7,.015,.01,1);body.data.materials.append(red);idx=len(body.data.materials)-1
count=0
for f in body.data.polygons:
 if selected(f.center):f.material_index=idx;count+=1
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o!=body:o.hide_render=True
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
for name,loc in [('delete-mask-context',Vector((-.014,-.3,.032))),('delete-mask-side',c+n*.065+u*.13)]:
 target=Vector((-.014,0,.032)) if name.endswith('context') else c
 cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('CUT_CANDIDATE_FACES',count)
