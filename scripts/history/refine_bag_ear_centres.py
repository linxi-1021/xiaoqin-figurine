import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_包耳基准对齐_20261019';bpy.ops.wm.open_mainfile(filepath=str(B/'3D重建_v6基础_小熊包图案细修_20261019/小秦_v6包面细修.blend'));o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());r=[]
j=json.loads((D/'表面坐标与投影校验.json').read_text(encoding='utf-8'));C,N,U,V=[Vector(j[x]) for x in ['center_surface_m','normal','right','up']]
for name,px,py in [('ear_left',207.2771,184.7733),('ear_right',626.5663,150.0735)]:
 target=C+U*((px-450)*.020/900)+V*((450-py)*.020/900);p,n,idx,dist=tree.ray_cast(target+N*.04,-N);assert p is not None;r.append({'name':name,'refinement_pixel':[px,py],'surface_center':list(p),'normal':list(n),'polygon':idx})
(D/'ear_landmarks_initial.json').write_text((D/'ear_landmarks.json').read_text(encoding='utf-8'),encoding='utf-8');(D/'ear_landmarks.json').write_text(json.dumps({'source':'ear front view, calibrated 900x900 .020m orthographic','method':'visible inner-ear chroma centroids in isolated ROIs, refined from initial front annotation and raycast to unchanged mesh; surface landmarks, not hidden volume centres','ears':r},indent=2),encoding='utf-8');print(json.dumps(r))
