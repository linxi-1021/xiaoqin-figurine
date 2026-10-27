import bpy,numpy as np,json
from pathlib import Path
p=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_前星星发夹修正_20261020/小秦_v6前星星发夹修正.blend');bpy.ops.wm.open_mainfile(filepath=str(p));o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));m=o.data;im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);rows=[]
for f in m.polygons:
 if f.center.z<.088:continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);c=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3];rows.append([f.index,*f.center,*f.normal,*c])
a=np.array(rows);np.save('models/rebuild/hat-surface-samples.npy',a)
for label,sign in [('left',-1),('right',1)]:
 b=a[(a[:,1]*sign>0)&(a[:,2]<0)&(a[:,9]>a[:,7]*1.2)&(a[:,9]>.15)&(a[:,7]<.5)];print(label,'BLUE',len(b),np.quantile(b[:,1:4],[0,.5,1],axis=0).tolist())
