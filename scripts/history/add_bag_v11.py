import bpy,bmesh,json,math,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v11';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'no-bag-v10/小秦_保留原衣腿_去包.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
def geometry_hash(o):
 co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co);loops=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',loops);uv=np.empty(len(o.data.loops)*2,np.float32);o.data.uv_layers['UVMap'].data.foreach_get('uv',uv);return hashlib.sha256(co.tobytes()+loops.tobytes()+uv.tobytes()).hexdigest()
before=geometry_hash(body)
patch=bpy.data.objects.get('Local knit under removed strap')
if patch:bpy.data.objects.remove(patch,do_unlink=True)
# Restore exactly the leather faces removed in v10, rather than remodel the sweater.
with bpy.data.libraries.load(str(r/'bag-v6/小秦_重建模型.blend'),link=False) as (src,dst):dst.objects=[name for name in src.objects if name.startswith('textured_mesh')]
strap=max((o for o in dst.objects if o and o.type=='MESH'),key=lambda o:len(o.data.vertices));strap.name='Original diagonal shoulder strap';bpy.context.collection.objects.link(strap)
img=strap.data.materials[0].node_tree.nodes.get('Image Texture').image;pix=np.empty(img.size[0]*img.size[1]*4,np.float32);img.pixels.foreach_get(pix);pix=pix.reshape(img.size[1],img.size[0],4);uv=strap.data.uv_layers['UVMap'].data;ids=set()
for f in strap.data.polygons:
 p=f.center;line=.009+(p.z-.064)*.65
 if not(.0435<p.z<.0655 and -.0014<p.x-line<.0031 and p.y<-.002):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[0]>rgb[2]*1.4 and rgb[1]>rgb[2]*1.1 and rgb[1]<rgb[0]*.90:ids.add(f.index)
bm=bmesh.new();bm.from_mesh(strap.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in ids],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(strap.data);bm.free();strap.data.validate(clean_customdata=False)
# Append only the approved, clean cylindrical bag components. Never append v7's body.
with bpy.data.libraries.load(str(r/'bag-v7/小秦_重建模型.blend'),link=False) as (src,dst):
 names=[n for n in src.objects if n.startswith(('Bag round cylindrical body','Bear bag ear','Bag circular edge piping'))];dst.objects=names
parts=[o for o in dst.objects if o]
for o in parts:bpy.context.collection.objects.link(o)
assert len(parts)==4,[o.name for o in parts]
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();v=n.cross(u).normalized();u=v.cross(n).normalized()
leather=bpy.data.materials.new('Strap lower leather bridge');leather.use_nodes=True;bs=leather.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.50,.27,.12,1);bs.inputs['Roughness'].default_value=.85
# Short, flat connector to the inner upper side of the bag, with real width and thickness.
start=Vector((-.0034,-.0096,.0449));end=c+u*.0049+v*.0031-n*.001;mid=(start+end)/2+Vector((0,-.0005,.0004));vs=[];fs=[];N=24
for i in range(N+1):
 t=i/N;p=(1-t)**2*start+2*t*(1-t)*mid+t*t*end;tangent=(2*(1-t)*(mid-start)+2*t*(end-mid)).normalized();across=n.cross(tangent).normalized();normal=tangent.cross(across).normalized()
 for w,d in [(-.00072,-.00015),(.00072,-.00015),(.00072,.00015),(-.00072,.00015)]:vs.append(tuple(p+across*w+normal*d))
for i in range(N):
 for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
fs.extend([(3,2,1,0),(N*4,N*4+1,N*4+2,N*4+3)])
me=bpy.data.meshes.new('Flat bag strap connector');me.from_pydata(vs,[],fs);me.materials.append(leather);bridge=bpy.data.objects.new('Bag strap to inner side attachment',me);bpy.context.collection.objects.link(bridge)
for f in me.polygons:f.use_smooth=True
bevel=bridge.modifiers.new('Soft leather edges','BEVEL');bevel.width=.00007;bevel.segments=3
assert before==geometry_hash(body)
report={'base':'v10 preserved garment and legs','body_geometry_uv_unchanged':True,'body_sha256':before,'removed_v10_knit_patch':True,'restored_original_strap_faces':len(ids),'bag_body_count':1,'bear_ears':2,'bag_style':'approved v7 short circular cylinder','diameter_mm':11.6,'depth_mm':3.4,'bag_parts':[o.name for o in parts],'global_decimation':False}
(out/'addition-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=800;s.render.resolution_y=960;cam=s.camera
for name,angle in [('front',0),('side',-65),('threequarter',35)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=c+n*.035+u*.11;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.026;s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=str(out/'bag-side.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_圆柱小熊斜挎包.blend'));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(out/'小秦_圆柱小熊斜挎包.glb'),use_selection=True,export_format='GLB');print('ADDED_APPROVED_BAG',json.dumps(report,ensure_ascii=False))
