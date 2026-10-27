import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_蝴蝶结吊星结构精修_v11_20261021';D=B/'3D重建_v6基础_装饰贴帽修正_v12_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6蝴蝶结吊星结构精修.blend'));yarn=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];tree=BVHTree.FromObject(yarn,bpy.context.evaluated_depsgraph_get())
# Fit a continuous support surface to the actual plush crown under the decoration.
def features(x,z):
 x=x/.01;z=(z-.09)/.01;return np.array([1,x,z,x*x,x*z,z*z,x**3,x*x*z,x*z*z,z**3])
rows=[];ys=[]
for x in np.linspace(-.010,.010,27):
 for z in np.linspace(.077,.098,28):
  hit=tree.ray_cast(Vector((x,.07,z)),Vector((0,-1,0)))
  if hit[0] is not None:rows.append(features(x,z));ys.append(hit[0].y)
coef=np.linalg.lstsq(np.array(rows),np.array(ys),rcond=None)[0]
def support(x,z):return float(features(x,z)@coef)
# Remove the long center pedestal entirely.
for o in list(bpy.context.scene.objects):
 if 'attachment' in o.name:bpy.data.objects.remove(o,do_unlink=True)
cloths=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('Ribbon folded') or o.name.startswith('Ribbon draped'))]
contact_points=[]
for o in cloths:
 coords=[o.matrix_world@v.co for v in o.data.vertices];N=len(coords)//2
 assert N*2==len(coords)
 # Both skins share x,z, so move each pair together and retain real cloth thickness.
 inv=o.matrix_world.inverted()
 for j in range(N):
  a=coords[j];b=coords[j+N];base=support(a.x,a.z)-.00024;thick=abs(b.y-a.y);a.y=base;b.y=base+thick
  o.data.vertices[j].co=inv@a;o.data.vertices[j+N].co=inv@b;contact_points.append((a.x,a.z,base))
# Knot back embeds slightly into the compressed plush, without any supporting column.
knot=bpy.data.objects['Ribbon rounded wrapped knot'];coords=[knot.matrix_world@v.co for v in knot.data.vertices];lo=min(v.y for v in coords);hi=max(v.y for v in coords);inv=knot.matrix_world.inverted()
for vert,p in zip(knot.data.vertices,coords):
 p.y=support(p.x,p.z)-.00030+(p.y-lo)*.72;vert.co=inv@p
# Keep the pendant connected to the same tail; lower its entire connected group onto the curved hat.
pendants=[bpy.data.objects[n] for n in ['Ribbon pendant closed gold connector','Ribbon hanging star','Ribbon star integral eyelet']];star=pendants[1];pts=[star.matrix_world@v.co for v in star.data.vertices];cx=sum(p.x for p in pts)/len(pts);cz=sum(p.z for p in pts)/len(pts);low=min(p.y for p in pts);delta=support(cx,cz)-.00010-low
for o in pendants:o.location.y+=delta
# Connector must touch the ribbon end after conforming, instead of bridging a depth gap.
ring=pendants[0];rp=ring.matrix_world.translation;end_y=support(rp.x,.0828)+.00014;ring.location.y=end_y+.00012
# Local tuft compression models the ribbon pressing into soft fleece and prevents protrusion through cloth.
from mathutils.kdtree import KDTree
kd=KDTree(len(contact_points))
for i,(x,z,y) in enumerate(contact_points):kd.insert(Vector((x,0,z)),i)
kd.balance();compressed=0
for v in yarn.data.vertices:
 p=v.co
 if p.y<.018 or not(-.011<p.x<.011 and .081<p.z<.099):continue
 _,i,dist=kd.find(Vector((p.x,0,p.z)))
 if dist<.0010:
  limit=support(p.x,p.z)-.00022
  t=float(np.clip((.0010-dist)/.00055,0,1));t=t*t*(3-2*t)
  if p.y>limit:p.y=p.y+(limit-p.y)*t;compressed+=1
# Retain the soft gathered shape in the knot; the cloth backing is fully seated on the fur.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6装饰贴帽修正.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6装饰贴帽修正.glb'),use_selection=True,export_format='GLB')
r={'pedestal_removed':True,'cloth_surface_conformed':True,'cloth_back_embed_mm':.24,'local_compressed_fur_vertices':compressed,'star_group_depth_shift_mm':delta*1000,'cloth_objects':[o.name for o in cloths]};(D/'贴帽校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
