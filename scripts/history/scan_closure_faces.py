import bpy,numpy as np,json
from pathlib import Path
p=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_鞋履收敛_v35_20261025/小秦_v6鞋履收敛.blend');bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['textured_mesh.obj'];m=o.data
im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);rows=[]
for f in m.polygons:
 if not(.028<f.center.z<.072):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);rgb=pix[int(uv[1]*h)%h,int(uv[0]*w)%w,:3];rows.append([f.index,*f.center,*f.normal,*rgb,*uv])
a=np.array(rows);np.save('models/rebuild/closure_faces.npy',a);print('SAVED',a.shape)
for label,sel in [('skirt',(a[:,3]<.05)&(a[:,7]<.32)&(a[:,8]>.065)&(abs(a[:,1])<.019)),('inner',(a[:,3]<.041)&(a[:,6]<-.4)&(abs(a[:,1])<.017)&(abs(a[:,2])<.014))]:
 c=a[sel];print(label,len(c),'bounds mm',np.quantile(c[:,1:4]*1000,[0,.1,.5,.9,1],axis=0).tolist())
