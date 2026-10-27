import bpy,bmesh,json
from pathlib import Path
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v11/小秦_圆柱小熊斜挎包.blend'));o=bpy.data.objects.get('Original diagonal shoulder strap');bm=bmesh.new();bm.from_mesh(o.data);seen=set();out=[]
for f in bm.faces:
 if f in seen:continue
 st=[f];seen.add(f);co=[]
 while st:
  q=st.pop();co.append(q)
  for e in q.edges:
   for ff in e.link_faces:
    if ff not in seen:seen.add(ff);st.append(ff)
 out.append({'count':len(co),'area_mm2':sum(f.calc_area() for f in co)*1e6,'min_z':min(v.co.z for f in co for v in f.verts)*1000,'max_z':max(v.co.z for f in co for v in f.verts)*1000})
print('STRAP_COMPONENTS',json.dumps(out));bm.free()
