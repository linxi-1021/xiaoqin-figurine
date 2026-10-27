import bpy, json, math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent
result=json.loads((r/'generation-result.json').read_text(encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=result[1]['value'])
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3))); hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
root=bpy.data.objects.new('Character_120mm',None); bpy.context.collection.objects.link(root)
for o in list(bpy.context.scene.objects):
 if o!=root and o.parent is None:o.parent=root
scale=.12/(hi.z-lo.z);root.scale=(scale,)*3; root.location=(-(lo.x+hi.x)*scale/2,-(lo.y+hi.y)*scale/2,-lo.z*scale)
bpy.context.view_layer.update()
out=r/'review';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'小秦_重建模型.glb'),use_selection=True,export_format='GLB')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24
s.render.resolution_x=900;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.world.color=(.25,.25,.25)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((.15,-.2,.25),10,.18),((-.15,-.05,.15),6,.15),((0,.2,.22),12,.15)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,.06))
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.15;cam.data.clip_start=.001
s.view_settings.view_transform='AgX'
for name,angle in [('front',0),('side',90),('back',180),('threequarter',35)]:
 a=math.radians(angle);cam.location=(.27*math.sin(a),-.27*math.cos(a),.105);aim(cam,(0,0,.06));s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'小秦_重建模型.blend'))
print('RENDER_COMPLETE',out)
