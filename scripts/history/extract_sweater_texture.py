import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包面匹配原棕色_20261019';D=B/'3D重建_v6基础_毛衣针织包面_20261019';D.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包面匹配原棕色.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));im=o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node.image;im.filepath_raw=str(D/'原模型服装贴图.png');im.file_format='PNG';im.save();print('BOUNDS',[(min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)) for i in range(3)])
# Record torso sample coordinates for identifying a clean original knit region.
tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());rows=[]
for z in [.043,.048,.053,.058,.063]:
 for x in [-.006,0,.006]:
  hit,n,idx,d=tree.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)))
  if hit is None:continue
  f=o.data.polygons[idx];uv=sum((o.data.uv_layers[0].data[i].uv for i in f.loop_indices),Vector((0,0)))/len(f.loop_indices);rows.append({'x':x,'z':z,'hit':list(hit),'uv':list(uv),'material':f.material_index})
(D/'服装采样点.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
