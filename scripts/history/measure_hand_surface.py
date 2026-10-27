import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_手部精修_20261019';S=B/'3D重建_v6基础_包身材质接缝修复_20261019';bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));m=o.data.materials[0];im=m.node_tree.nodes.get('Image Texture').image;w,h=im.size;p=np.array(im.pixels[:]).reshape(h,w,4);rows=[]
for f in o.data.polygons:
 x,y,z=f.center
 if .010<x<.026 and .058<z<.070 and y<-.004:
  uv=sum((o.data.uv_layers[0].data[k].uv for k in f.loop_indices),Vector((0,0)))/len(f.loop_indices);col=p[int(uv.y*h)%h,int(uv.x*w)%w,:3]
  if col[0]>.55 and col[1]>.3 and col[2]>.25:rows.append([*f.center,*col])
a=np.array(rows);print('HAND bounds percentiles',np.percentile(a[:,:3],[0,10,50,90,100],axis=0));(D/'hand-surface-points.json').write_text(json.dumps(rows),encoding='utf8')
