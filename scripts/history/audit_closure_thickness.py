import bpy,numpy as np,json,hashlib,bmesh
from pathlib import Path
from mathutils.bvhtree import BVHTree
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_五处局部收口_v36_20261025');bpy.ops.wm.open_mainfile(filepath=str(D/'过程备份'/'05手包轻贴.blend'));body=bpy.data.objects['textured_mesh.obj'];m=body.data;co=np.array([v.co[:] for v in m.vertices]);a=np.load('models/rebuild/closure_faces.npy');r,g,b=a[:,7:10].T;x,y,z=a[:,1:4].T;tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());regions={'hair':(r>g*1.42)&(g>b*1.12)&(z>.0285)&(z<.052)&(y>.003),'hair_arm':(r>g*1.42)&(x>.01)&(z>.047)&(z<.068)&(y>-.004)&(y<.02),'shoulder':(r>.18)&(g>r*.55)&(r<g*1.55)&(abs(x)>.007)&(abs(x)<.023)&(z>.049)&(z<.068)&(abs(y)<.012),'hand':(r>.35)&(r>g*1.3)&(r<g*2)&(x<-.013)&(x>-.032)&(z>.033)&(z<.0395)&(y>-.007)&(y<.006)};samples={}
for name,mask in regions.items():
 ids=a[mask,0].astype(int);ids=ids[::max(1,len(ids)//2500)];ts=[]
 for idx in ids:
  f=m.polygons[idx];n=f.normal;hit=tree.ray_cast(f.center-n*.00003,-n,.02)
  if hit[0] is not None and hit[3]>.00002:ts.append((hit[3]+.00003)*1000)
 samples[name]={'samples':len(ts),'min_mm':min(ts,default=0),'p05_mm':float(np.quantile(ts,.05)) if ts else 0,'below_0_8mm':sum(t<.8 for t in ts),'method':'inward normal ray; diagnostic samples, not a global minimum-thickness certificate'}
print(json.dumps(samples))
(D/'过程备份'/'thickness_diagnostic.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2),encoding='utf8')
