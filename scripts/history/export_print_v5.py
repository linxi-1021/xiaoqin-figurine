from pathlib import Path
import bpy,bmesh,json
r=Path(__file__).resolve().parent;out=r/'detail-v5'
bpy.ops.wm.open_mainfile(filepath=str(out/'小秦_重建模型.blend'))
changes=json.loads((out/'reference-changes.json').read_text(encoding='utf-8'))
visual=[o for o in bpy.context.scene.objects if o.type=='MESH']
src=(r/'finish_model.py').read_text(encoding='utf-8').split('# Duplicate the master so remeshing cannot damage its UVs or textures.')[1]
exec(compile(src,str(r/'finish_model.py'),'exec'))
