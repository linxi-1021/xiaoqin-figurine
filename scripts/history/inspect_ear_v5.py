import bpy,numpy as np
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020/小秦_v6后帽粗绒浮贴蝴蝶结_v4.blend')
m=bpy.data.objects['GEO-Redesigned hat solid plush tufts'].data
c=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',c);c=c.reshape(-1,150,3).mean(1);mi=np.array([m.polygons[i*142].material_index for i in range(len(c))]);np.savez('models/rebuild/ear-inspect.npz',c=c,mi=mi)
