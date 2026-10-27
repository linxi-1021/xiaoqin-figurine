import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v8'
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();v=n.cross(u).normalized();u=v.cross(n).normalized()
image=next(nd.image for nd in body.data.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image and 'base' in nd.image.name.lower()) if any(nd.type=='TEX_IMAGE' and nd.image and 'base' in nd.image.name.lower() for nd in body.data.materials[0].node_tree.nodes) else next(nd.image for nd in body.data.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image)
pixels=np.empty(image.size[0]*image.size[1]*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(image.size[1],image.size[0],4);uv=body.data.uv_layers[0].data
def color(f):
 t=sum((uv[i].uv for i in f.loop_indices),Vector((0,0)))/len(f.loop_indices);return pixels[int(t.y*(image.size[1]-1))%image.size[1],int(t.x*(image.size[0]-1))%image.size[0],:3]
def selected(f):
 p=f.center;q=p-c;a=q.dot(u);b=q.dot(v);d=q.dot(n)
 if p.z<.0305:return False
 if f.material_index!=1 and p.x<-.0145:return False
 if f.material_index!=1 and (p.z>.0405 or (a<-.0038 and d>-.0015)):return False
 lower=-.0095 if d<-.0035 and p.x>-.0175 else -.0066
 if not(lower<a<.0075 and -.0075<b<.0094 and -.0095<d<.0045 and a*a+b*b<.0093**2):return False
 if b>.0085 and abs(a)<.0032:return False
 rgb=color(f)
 return f.material_index==1 or rgb[0]>rgb[2]*1.03
red=bpy.data.materials.new('Audit isolated old bag');red.use_nodes=True;red.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.7,.015,.01,1);body.data.materials.append(red);idx=len(body.data.materials)-1
allowed={f.index for f in body.data.polygons if selected(f)}
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
selectedids={i for i in allowed if body.data.polygons[i].material_index==1};stack=list(selectedids)
while stack:
 i=stack.pop()
 for e in bm.faces[i].edges:
  for neighbor in e.link_faces:
   j=neighbor.index
   if j in allowed and j not in selectedids:selectedids.add(j);stack.append(j)
bm.free();selectedids=sorted(selectedids)
for i in selectedids:body.data.polygons[i].material_index=idx
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o!=body:o.hide_render=True
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=800;s.render.resolution_y=800;cam=s.camera
cam.location=c+n*.065+u*.13;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024;s.render.filepath=str(out/'source-cut-mask.png');bpy.ops.render.render(write_still=True)
(out/'old-bag-face-selection.json').write_text(json.dumps({'source':'v6 before v7 shell compression','texture':image.name,'faces':selectedids,'count':len(selectedids)}));print('SOURCE_FACE_SELECTION',len(selectedids),image.name)
