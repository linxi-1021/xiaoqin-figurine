import bpy,numpy as np,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_四指并拢保留长短_20261020/小秦_v6四指并拢.blend')
o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));im=o.data.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);rows=[]
for f in o.data.polygons:
 x,y,z=f.center
 if x>.012 and .077<z<.094 and y<0:
  uv=np.mean([o.data.uv_layers[0].data[k].uv[:] for k in f.loop_indices],axis=0);c=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3]
  if c[0]>.6 and c[1]>.35 and c[2]<.35 and c[1]/c[0]>.52: rows.append([f.index,x,y,z,*c.tolist()])
np.save('models/rebuild/front_star_faces.npy',np.array(rows));print('GOLD',len(rows),np.min(np.array(rows)[:,1:4],axis=0),np.max(np.array(rows)[:,1:4],axis=0))
