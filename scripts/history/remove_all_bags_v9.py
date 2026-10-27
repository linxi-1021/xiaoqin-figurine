import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'no-bag-v9';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
# Reconstruct the bag-occluded front skirt with the intact opposite garment panel.
def region(p):return -.019<p.x<-.0025 and .0295<p.z<.044 and p.y<.001
patch=body.copy();patch.data=body.data.copy();patch.name='Reconstructed skirt panel';bpy.context.collection.objects.link(patch)
bm=bmesh.new();bm.from_mesh(patch.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if not region(Vector((-f.calc_center_median().x,f.calc_center_median().y,f.calc_center_median().z)))],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for v in bm.verts:v.co.x=-v.co.x
bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(patch.data);bm.free()
bm=bmesh.new();bm.from_mesh(body.data);deleted=[f for f in bm.faces if region(f.calc_center_median()) and not (f.calc_center_median().x<-.014 and f.calc_center_median().y>-.007)];count=len(deleted);bmesh.ops.delete(bm,geom=deleted,context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(body.data);bm.free()
# Rebuild the sleeve's inner wall exposed by removing the integrated bag.
m=bpy.data.materials.new('Restored ivory knit sleeve');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.8,.72,.60,1);bs.inputs['Roughness'].default_value=.92
tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3200;tex.inputs['Detail'].default_value=2
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.00012;wave=nt.nodes.new('ShaderNodeTexWave');wave.bands_direction='X';wave.inputs['Scale'].default_value=15;wave.inputs['Distortion'].default_value=2;wave.inputs['Detail Scale'].default_value=2;nt.links.new(wave.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=(-.016,-.001,.040));sleeve=bpy.context.object;sleeve.name='Restored inner sleeve wall';sleeve.scale=(.0033,.005,.0062);sleeve.data.materials.append(m)
for f in sleeve.data.polygons:f.use_smooth=True
# Excise the narrow fused leather strap and reconstruct its opening as knit.
import numpy as np
img=next(nd.image for nd in body.data.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image)
pix=np.empty(img.size[0]*img.size[1]*4,dtype=np.float32);img.pixels.foreach_get(pix);pix=pix.reshape(img.size[1],img.size[0],4);uv=body.data.uv_layers[0].data
strap=[]
for f in body.data.polygons:
 p=f.center;line=.009+(p.z-.064)*.65
 if not (.043<p.z<.066 and abs(p.x-line)<.003 and p.y<-.002):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[0]>rgb[2]*1.4 and rgb[1]>rgb[2]*1.1 and rgb[1]<rgb[0]*.90:strap.append(f.index)
body.data.materials.append(m);mi=len(body.data.materials)-1
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table();ids=set(strap)
# Mark adjacent retained faces so the reconstructed opening inherits ivory at its edge.
cut=[bm.faces[j] for j in ids];rim=set()
for f in cut:
 for e in f.edges:
  for q in e.link_faces:
   if q not in cut:rim.add(q)
for q in rim:pass
bmesh.ops.delete(bm,geom=cut,context='FACES');bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bound=[e for e in bm.edges if e.is_boundary and all(v.co.z>.043 for v in e.verts)]
caps=[]
for f in caps:f.material_index=mi;f.smooth=True
if caps:bmesh.ops.triangulate(bm,faces=caps)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
print('REMOVED_STRAP_FACES',len(strap))
# Replace the exposed front knit panel as one continuous surface, avoiding a diagonal repair seam.
uv=body.data.uv_layers[0].data;front_ids=[]
for f in body.data.polygons:
 p=f.center
 if not(-.0125<p.x<.013 and .042<p.z<.065 and p.y<0 and f.normal.y<-.15):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[0]>.48 and rgb[1]>rgb[0]*.80 and rgb[2]>rgb[0]*.59:front_ids.append(f.index)
front_ids=[j for j in front_ids if .043<body.data.polygons[j].center.z<.062 and abs(body.data.polygons[j].center.x)<.009]
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[j] for j in front_ids],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(body.data);bm.free();print('REBUILT_SHIRT_PANEL',len(front_ids))
verts=[];faces=[];N=96
profile=[(.0415,.012,.009),(.043,.0132,.011),(.045,.014,.012),(.049,.014,.012),(.054,.0135,.0115),(.059,.012,.010),(.063,.008,.007),(.065,.005,.004)]
for z,rx,ry in profile:
 for j in range(N):
  t=2*math.pi*j/N;verts.append((rx*math.cos(t),.001+ry*math.sin(t),z))
for k in range(len(profile)-1):
 for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
faces.append(tuple(range(N-1,-1,-1)));faces.append(tuple((len(profile)-1)*N+j for j in range(N)))
me=bpy.data.meshes.new('Restored sweater tailoring');me.from_pydata(verts,[],faces);me.materials.append(m);torso=bpy.data.objects.new('Reconstructed knit beneath removed strap',me);bpy.context.collection.objects.link(torso)
for f in me.polygons:f.use_smooth=True
sub=torso.modifiers.new('Soft knit tailoring','SUBSURF');sub.levels=2
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=800;s.render.resolution_y=960;cam=s.camera
for name,a in [('front',0),('side',65),('threequarter',35)]:
 a=math.radians(-a);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'working.blend'));print('CUT',count)

