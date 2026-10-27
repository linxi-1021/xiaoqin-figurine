import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parent;out=r/'bag-v6';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'detail-v5/小秦_重建模型.blend'))
s=bpy.context.scene;s.cycles.samples=20;s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
cam.location=(-.014,-.3,.032);cam.rotation_euler=(Vector((-.014,0,.032))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.024
s.render.filepath=str(out/'bag-before.png');bpy.ops.render.render(write_still=True)
