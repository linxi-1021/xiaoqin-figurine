import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_双手五指重建_20261019';D.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co);vi=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',vi);uv=np.empty(len(o.data.loops)*2,np.float32);o.data.uv_layers[0].data.foreach_get('uv',uv);fc=np.array([f.center[:] for f in o.data.polygons]);np.savez(D/'original-uv-mesh.npz',co=co.reshape(-1,3),vi=vi.reshape(-1,3),uv=uv.reshape(-1,3,2),centers=fc)
t=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());seeds={}
for name,x,z in [('palm',.017,.062),('thumb',.0125,.064),('fingers',.018,.066),('wrist',.0165,.0588),('fist',-.0195,.034),('fist-front',-.022,.034),('cuff',.016,.056),('hair',.014,.070)]:
 hit,n,idx,d=t.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)));seeds[name]={'face':idx,'hit':list(hit) if hit else None}
(D/'chart-seeds.json').write_text(json.dumps(seeds),encoding='utf8');print(seeds)
