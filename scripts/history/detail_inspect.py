import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'detail-v4';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'finished/小秦_重建模型.blend'))
s=bpy.context.scene;s.cycles.samples=24;s.render.resolution_x=1000;s.render.resolution_y=1000
m=bpy.data.materials.new('Inspect');m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.18,.21,.25,1);n.inputs['Roughness'].default_value=.8;s.view_layers[0].material_override=m
cam=s.camera;cam.location=(.018,-.3,.07);cam.rotation_euler=(Vector((.018,0,.07))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.025
s.render.filepath=str(out/'hand-before.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-.3,.079);cam.rotation_euler=(Vector((0,0,.079))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.046;s.render.filepath=str(out/'face-before.png');bpy.ops.render.render(write_still=True)
