import bpy
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'no-bag-v9/working.blend'));s=bpy.context.scene;cam=s.camera;cam.location=(0,-.27,.105);cam.rotation_euler=(Vector((0,0,.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.15;bpy.context.view_layer.update()
for x,y in [(412,529),(382,581),(421,519)]:
 loc=cam.matrix_world@Vector(((x/800-.5)*.125,(.5-y/960)*.15,0));d=cam.matrix_world.to_quaternion()@Vector((0,0,-1));hit,p,n,f,o,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),loc,d);print(x,y,hit,list(p),o.name if o else '')
