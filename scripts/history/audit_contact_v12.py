import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent;out=r/'bag-v12';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v11/小秦_圆柱小熊斜挎包.blend'))
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));m=body.data;m.calc_loop_triangles();img=m.materials[0].node_tree.nodes.get('Image Texture').image;pix=np.empty(img.size[0]*img.size[1]*4,np.float32);img.pixels.foreach_get(pix);pix=pix.reshape(img.size[1],img.size[0],4);uv=m.uv_layers['UVMap'].data
keep=set()
for f in m.polygons:
 p=f.center
 if not(-.023<p.x<.002 and .029<p.z<.045 and p.y<.008):continue
 if 'plaid' in m.materials[f.material_index].name.lower():keep.add(f.index);continue
 t=sum((uv[j].uv for j in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rgb=pix[int(t.y*(img.size[1]-1))%img.size[1],int(t.x*(img.size[0]-1))%img.size[0],:3]
 if rgb[2]>rgb[0]*.9 and f.normal.y<-.1:keep.add(f.index)
vs=[v.co.copy() for v in m.vertices];ts=[tuple(t.vertices) for t in m.loop_triangles if t.polygon_index in keep];tree=BVHTree.FromPolygons(vs,ts,all_triangles=True)
c=Vector((-.0107,-.0138,.0368));n=Vector((-.3,-.92,.25)).normalized();u=Vector((.95,-.31,0)).normalized();v=n.cross(u).normalized();u=v.cross(n).normalized();back=c-n*.0034;samples=[]
for a in [-.0035,0,.0035]:
 for b in [-.0035,0,.0035]:
  if a*a+b*b>.0049**2:continue
  p=back+u*a+v*b;hit,norm,k,d=tree.ray_cast(p+n*.025,-n)
  if hit is not None:samples.append({'a':a,'b':b,'gap_mm':(p-hit).dot(n)*1000,'hit':list(hit),'normal':list(norm)})
bm=bmesh.new();bm.from_mesh(m);bm.faces.ensure_lookup_table();seen=set();comps=[]
for f in bm.faces:
 if f in seen:continue
 stack=[f];seen.add(f);comp=[]
 while stack:
  q=stack.pop();comp.append(q)
  for e in q.edges:
   for j in e.link_faces:
    if j not in seen:seen.add(j);stack.append(j)
 if len(comp)>3000:continue
 verts={v for q in comp for v in q.verts};co=np.array([tuple(v.co) for v in verts]);lo=co.min(axis=0);hi=co.max(axis=0)
 if lo[0]>-.024 and hi[0]<.003 and lo[2]>.028 and hi[2]<.048 and hi[1]<.009:comps.append({'faces':[q.index for q in comp],'count':len(comp),'min':lo.tolist(),'max':hi.tolist(),'area_mm2':sum(q.calc_area() for q in comp)*1e6})
bm.free();result={'cloth_triangles':len(ts),'samples':samples,'local_components':comps};(out/'contact-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'samples':samples,'components':[{k:v for k,v in q.items() if k!='faces'} for q in comps]},indent=2))
