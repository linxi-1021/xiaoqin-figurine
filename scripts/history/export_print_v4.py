from pathlib import Path
import bpy,bmesh,json
r=Path(__file__).resolve().parent;out=r/'detail-v4'
bpy.ops.wm.open_mainfile(filepath=str(out/'小秦_重建模型.blend'))
changes=[{'feature':'hand creases','source':'sculpt-changes.json'}]
visual=[o for o in bpy.context.scene.objects if o.type=='MESH']
src=(r/'finish_model.py').read_text(encoding='utf-8').split('# Duplicate the master so remeshing cannot damage its UVs or textures.')[1]
src=src.replace("p.data.remesh_voxel_size=.00016", "bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.0008,location=(.008502,.025084,.090275))\nbpy.context.object.select_set(True);p.select_set(True);bpy.context.view_layer.objects.active=p;bpy.ops.object.join()\np.data.remesh_voxel_size=.00016")
exec(compile(src,str(r/'finish_model.py'),'exec'))
