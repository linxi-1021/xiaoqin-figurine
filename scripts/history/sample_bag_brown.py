import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包脸上下居中_20261019';bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包脸上下居中.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));r=json.loads((S/'表面坐标与投影校验.json').read_text(encoding='utf8'));C=Vector(r['center_surface_m']);N=Vector(r['normal']);U=Vector(r['right']);V=Vector(r['up']);m=o.data.materials[0];im=m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node.image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);colors=[]
for f in o.data.polygons:
 q=f.center-C
 if f.material_index==0 and (q.dot(U)/.0065)**2+(q.dot(V)/.0065)**2<1 and -.005<q.dot(N)<-.001:
  uv=sum((o.data.uv_layers[0].data[i].uv for i in f.loop_indices),Vector((0,0)))/len(f.loop_indices);colors.append(pix[int(uv.y*h)%h,int(uv.x*w)%w,:3])
a=np.array(colors);print('BAG_SIDE_SRGB',len(a),np.percentile(a,[25,50,75],axis=0)*255)
