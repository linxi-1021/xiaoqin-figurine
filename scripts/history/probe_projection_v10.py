import bpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'));b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));print('MATX',b.matrix_world)
m=b.data;m.calc_loop_triangles();vs=[v.co.copy() for v in m.vertices];ts=[tuple(t.vertices) for t in m.loop_triangles];us=[[Vector((*m.uv_layers[0].data[j].uv,0)) for j in t.loops] for t in m.loop_triangles];tree=BVHTree.FromPolygons(vs,ts,all_triangles=True);img=b.data.materials[0].node_tree.nodes.get('Image Texture').image;pix=np.array(img.pixels[:]).reshape(img.size[1],img.size[0],4)
for x,z in [(.01,.035),(.014,.038),(.006,.04),(.004,.055)]:
 hit,n,k,d=tree.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)));a,bb,c=[vs[i] for i in ts[k]];uv=barycentric_transform(hit,a,bb,c,*us[k]);print(x,z,'HIT',list(hit),'UV',list(uv),'RGB',pix[int(uv.y*(img.size[1]-1)),int(uv.x*(img.size[0]-1)),:3])
