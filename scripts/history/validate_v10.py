import bpy
from pathlib import Path
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'no-bag-v10/小秦_保留原衣腿_去包.blend'));b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));print('VALIDATE_CHANGED',b.data.validate(verbose=True,clean_customdata=False));b.data.update(calc_edges=True);print('SECOND_VALIDATE',b.data.validate(verbose=True,clean_customdata=False))
