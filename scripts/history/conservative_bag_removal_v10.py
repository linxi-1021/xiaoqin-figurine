import bpy,bmesh,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'no-bag-v10';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
source_coords=[tuple(v.co) for v in body.data.vertices]
ids=set(json.loads((r/'bag-v8/old-bag-face-selection.json').read_text())['faces'])
# Restrict every removal to the bag's immediate bounds; leave the shirt/strap/legs intact.
img=next(nd.image for nd in body.data.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image);pix=np.empty(img.size[0]*img.size[1]*4,dtype=np.float32);img.pixels.foreach_get(pix);pix=pix.reshape(img.size[1],img.size[0],4);uv=body.data.uv_layers[0].data
for f in body.data.polygons:
 p=f.center
 if not(-.019<p.x<-.0025 and .030<p.z<.0445 and p.y<.003):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if p.x<-.0145 and p.y>-.007 and p.z>.033:continue
 if p.z>.0415 and p.y>-.010:continue
 if rgb[2]<rgb[0]*.88 and rgb[1]>rgb[0]*.65:ids.add(f.index)
# Keep an immutable source surface and its original UV triangles for local patch sampling.
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import barycentric_transform,closest_point_on_tri
me=body.data;me.calc_loop_triangles();srcverts=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles];triuv=[[Vector((*uv[j].uv,0)) for j in t.loops] for t in me.loop_triangles];tree=BVHTree.FromPolygons(srcverts,tris,all_triangles=True)
white=[]
for f in me.polygons:
 p=f.center
 if not(-.009<p.x<.008 and .043<p.z<.064 and -.012<p.y<0 and f.normal.y<-.55):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[1]>rgb[0]*.84 and rgb[2]>rgb[0]*.64 and rgb[0]>.4:white.append(f.index)
# Preserve original shirt faces outside the narrow leather corridor.
strapids=[]
for f in me.polygons:
 p=f.center;line=.009+(p.z-.064)*.65
 if not(.0435<p.z<.0655 and -.0014<p.x-line<.0031 and p.y<-.002):continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[0]>rgb[2]*1.4 and rgb[1]>rgb[2]*1.1 and rgb[1]<rgb[0]*.90:strapids.append(f.index)
white_tri=[]
white_set=set(white)
for k,t in enumerate(me.loop_triangles):
 if t.polygon_index in white_set:white_tri.append(k)
kd=KDTree(len(white_tri))
for j,k in enumerate(white_tri):kd.insert(sum((srcverts[q] for q in tris[k]),Vector())/3,j)
kd.balance()
def sample_white(p):
 co,j,dist=kd.find(p);k=white_tri[j];a,b,c=[srcverts[q] for q in tris[k]]
 # Use the closest original knit triangle with a small, bounded UV projection.
 normal=(b-a).cross(c-a).normalized();project=closest_point_on_tri(p,a,b,c)
 tex=barycentric_transform(project,a,b,c,*triuv[k]);return co.y,tex.xy
bag_ids=set(ids);ids.update(strapids)
protected=[f.index for f in body.data.polygons if f.center.z<.029 or f.center.z>.045]
assert not(bag_ids&set(protected))
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
# Store original indices for exact preservation verification.
layer=bm.verts.layers.int.new('source_vertex_index')
for v in bm.verts:v[layer]=v.index
bmesh.ops.delete(bm,geom=[bm.faces[j] for j in ids],context='FACES')
bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
assert all(tuple(v.co)==source_coords[v[layer]] for v in bm.verts)
# Close attachment openings without moving any existing vertex.
oldfaces=set(bm.faces);bound=[e for e in bm.edges if e.is_boundary and all(v.co.z<.044 for v in e.verts)];caps=bmesh.ops.holes_fill(bm,edges=bound,sides=0).get('faces',[])
mat=bpy.data.materials.new('Local bag attachment closure');mat.diffuse_color=(.13,.13,.15,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.13,.13,.15,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9;body.data.materials.append(mat)
if caps:bmesh.ops.triangulate(bm,faces=caps)
# Bake the projection into its own continuous texture: source UV islands must never
# be interpolated across the large closure triangles.
def texcolor(tex):
 return pix[min(img.size[1]-1,max(0,int(tex.y*(img.size[1]-1)))),min(img.size[0]-1,max(0,int(tex.x*(img.size[0]-1)))),:3]
def garment_color(x,z):
 if z>.0415:
  y,t=sample_white(Vector((.003,-.008,max(z,.0435))));return texcolor(t)
 x=min(.0105,max(.002,(abs(x)-.002)*.60+.002));z=max(.0318,z)
 for attempt in range(4):
  hit,normal,k,dist=tree.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)))
  if k is not None:
   a,b,c=[srcverts[q] for q in tris[k]];t=barycentric_transform(hit,a,b,c,*triuv[k]);rgb=texcolor(t)
   if hit.y<0 and rgb[2]>rgb[0]*.86:return rgb
  x*=.75
 return np.array((.18,.18,.23))
def texture_material(name,pixels):
 h,w,_=pixels.shape;im=bpy.data.images.new(name,width=w,height=h,alpha=True);im.colorspace_settings.name='sRGB';im.pixels.foreach_set(pixels.ravel());im.filepath_raw=str(out/(name+'.png'));im.file_format='PNG';im.save();im.pack()
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;uvn=m.node_tree.nodes.new('ShaderNodeUVMap');uvn.uv_map='LocalRepairUV';m.node_tree.links.new(uvn.outputs['UV'],n.inputs['Vector']);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.88;m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color']);return m
W=256;H=256;bitmap=np.ones((H,W,4),np.float32)
for iy in range(H):
 z=.029+.016*iy/(H-1)
 for ix in range(W):bitmap[iy,ix,:3]=garment_color(-.021+.019*ix/(W-1),z)
capmat=texture_material('Bag attachment local plaid',bitmap);body.data.materials.append(capmat);capidx=len(body.data.materials)-1;repairuv=bm.loops.layers.uv.new('LocalRepairUV')
for f in bm.faces:
 if f in oldfaces:continue
 f.material_index=capidx;f.smooth=True
 for loop in f.loops:
  p=loop.vert.co;loop[repairuv].uv=((p.x+.021)/.019,(p.z-.029)/.016)
bm.to_mesh(body.data);bm.free()
# Knit ribbon follows the adjacent source shirt; no outside garment vertex is moved.
verts=[];faces=[];texcoords=[];NZ=64;NX=12
for iz in range(NZ+1):
 z=.0435+(.0655-.0435)*iz/NZ;cx=.009+(z-.064)*.65
 for ix in range(NX+1):
  x=cx-.0018+.0053*ix/NX
  # Sample untouched knit just beside the removed leather.
  y,tex=sample_white(Vector((min(x+.002,.007),-.007,z)))
  verts.append((x,y-.00012,z));texcoords.append(tex)
grid=np.array(verts,dtype=float).reshape(NZ+1,NX+1,3)
for iteration in range(12):
 yy=grid[:,:,1].copy();grid[1:-1,1:-1,1]=.5*yy[1:-1,1:-1]+.125*(yy[:-2,1:-1]+yy[2:,1:-1]+yy[1:-1,:-2]+yy[1:-1,2:])
verts=[tuple(q) for q in grid.reshape(-1,3)]
for iz in range(NZ):
 for ix in range(NX):
  a=iz*(NX+1)+ix;faces.append((a,a+1,a+NX+2,a+NX+1))
patchme=bpy.data.meshes.new('Narrow knit restoration');patchme.from_pydata(verts,[],faces);patchuv=patchme.uv_layers.new(name='LocalRepairUV')
for f in patchme.polygons:
 f.use_smooth=True
 for j in f.loop_indices:patchuv.data[j].uv=((patchme.loops[j].vertex_index%(NX+1))/NX,(patchme.loops[j].vertex_index//(NX+1))/NZ)
stripmap=np.ones((512,64,4),np.float32)
for iz in range(512):
 z=.0435+.022*iz/511;cx=.009+(z-.064)*.65
 for ix in range(64):
  x=cx-.0018+.0053*ix/63;y,t=sample_white(Vector((x+.0035,-.008,z)));stripmap[iz,ix,:3]=texcolor(t)
patchme.materials.append(texture_material('Narrow strap knit repair',stripmap))
patch=bpy.data.objects.new('Local knit under removed strap',patchme);bpy.context.collection.objects.link(patch)
report={'base':'v6 original body','deleted_bag_faces':len(ids),'protected_faces':len(protected),'moved_original_vertices':0,'shirt_rebuilt':False,'skirt_mirrored':False,'leg_geometry_modified':False,'strap_removed':True,'removed_strap_faces':len(strapids),'knit_patch_width_mm':5.3,'local_caps':len(caps),'web_decimation':False}
(out/'preservation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=800;s.render.resolution_y=960;cam=s.camera
for name,angle in [('front',0),('side',-65)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'working.blend'));print(json.dumps(report))
