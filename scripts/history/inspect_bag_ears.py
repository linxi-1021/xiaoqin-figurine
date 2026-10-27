import bpy,bmesh
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_包耳基准对齐_20261019';D.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(B/'3D重建_v6基础_按人物侧面校正包脸_20261019/小秦_v6侧面包脸校正.blend'));o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));dup=o.copy();dup.data=o.data.copy();bpy.context.collection.objects.link(dup)
bm=bmesh.new();bm.from_mesh(dup.data);bad=[]
for f in bm.faces:
 p=f.calc_center_median()
 if not(-.0175<p.x<-.005 and -.017<p.y<-.0035 and .029<p.z<.045):bad.append(f)
bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(dup.data);bm.free();
for x in bpy.context.scene.objects:
 if x.type=='MESH' and x!=dup:x.hide_render=True
m=bpy.data.materials.new('Diagnostic neutral');m.diffuse_color=(.5,.5,.5,1);dup.data.materials.clear();dup.data.materials.append(m)
for f in dup.data.polygons:f.material_index=0
s=bpy.context.scene;s.render.resolution_x=900;s.render.resolution_y=900;s.cycles.samples=12;s.render.engine='CYCLES';cam=s.camera
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except:pass
C=Vector((-.011,-.0095,.036));cam.data.ortho_scale=.020
for name,n in [('ear-side',(-1,0,0)),('ear-front',(0,-1,0))]:
 cam.location=C+Vector(n)*.09;cam.rotation_euler=(C-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
