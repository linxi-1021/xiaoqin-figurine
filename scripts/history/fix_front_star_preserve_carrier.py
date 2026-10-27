import bpy,numpy as np,math,json,bmesh
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_四指并拢保留长短_20261020';D=B/'3D重建_v6基础_前星星发夹修正_20261020';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6四指并拢.blend'));o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
# Plane follows the oblique right temple: horizontal axis tangent to hair, normal points outwards.
center=Vector((.0191,-.0120,.07945));u=Vector((1,.75,0)).normalized();n=Vector((.75,-1,0)).normalized();v=Vector((0,0,1));R=.0031;inner=R*.49;pts=[]
for i in range(10):
 a=math.pi/2+math.radians(4)+i*math.pi/5;r=R if i%2==0 else inner;pts.append((r*math.cos(a),r*math.sin(a)))
vs=[]
for depth in [-.00055,.00038]:
 for x,z in pts:vs.append(tuple(center+u*x+v*z+n*depth))
fs=[tuple(reversed(range(10))),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
me=bpy.data.meshes.new('Rounded five-point star');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('GEO-Front gold five-point star hair clip',me);bpy.context.collection.objects.link(ob)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
mat=bpy.data.materials.new('Front star warm honey gold');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.83,.43,.075,1);p.inputs['Metallic'].default_value=.48;p.inputs['Roughness'].default_value=.30;me.materials.append(mat)
bev=ob.modifiers.new('Rounded gold edges','BEVEL');bev.width=.00020;bev.segments=5
bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=bev.name)
for f in me.polygons:f.use_smooth=True
norm=ob.modifiers.new('Stable broad star face normals','WEIGHTED_NORMAL');norm.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=norm.name)
bpy.ops.object.select_all(action='DESELECT')
for a in bpy.context.scene.objects:
 if a.type=='MESH':a.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6前星星发夹修正.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6前星星发夹修正.glb'),export_format='GLB',use_selection=True)
