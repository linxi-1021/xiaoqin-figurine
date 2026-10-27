import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(r/'refined/小秦_重建模型.blend'))
report=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 report.append(dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),boundary_edges=sum(e.is_boundary for e in bm.edges),non_manifold_edges=sum(not e.is_manifold for e in bm.edges)))
 bm.free()
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
bvh=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get()); samples={}
for x,z in [(-.009,.076),(.009,.076),(.022,.069),(.024,.072),(.025,.075),(.026,.078),(0,.0925)]:
 hits=[]
 for direction in [-1,1]:
  p=Vector((x,-direction*.15,z));h=bvh.ray_cast(body.matrix_world.inverted()@p,Vector((0,direction,0)))
  hits.append(list(body.matrix_world@h[0]) if h[0] is not None else None)
 samples[str((x,z))]=hits
(r/'audit-v2.json').write_text(json.dumps(dict(objects=report,surface_samples=samples),indent=2),encoding='utf-8')
print(json.dumps(dict(objects=report,surface_samples=samples)))
