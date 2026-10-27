import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'detail-v5'
bpy.ops.wm.open_mainfile(filepath=str(out/'小秦_重建模型.blend'))
m=bpy.data.materials.new('Neutral diagnostic');m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.18,.21,.25,1);n.inputs['Roughness'].default_value=.8
s=bpy.context.scene;s.view_layers[0].material_override=m;s.render.resolution_x=800;s.render.resolution_y=800;s.cycles.samples=16;cam=s.camera
for name,loc,target,scale in [('face-gray',(0,-.3,.079),(0,0,.079),.046),('bow-gray',(0,.3,.092),(0,0,.092),.035)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
