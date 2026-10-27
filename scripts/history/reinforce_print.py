import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'finished'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(out/'小秦_120mm_打印校验版.stl'));p=bpy.context.object
report=json.loads((out/'thickness-screening.json').read_text())
for item in report['smallest_samples']:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.8,location=item['point_mm']);o=bpy.context.object;o.name='Localized hidden ribbon reinforcement'
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=p;bpy.ops.object.join()
p.data.remesh_voxel_size=.16;p.data.remesh_voxel_adaptivity=0;bpy.ops.object.voxel_remesh()
bpy.ops.wm.stl_export(filepath=str(out/'小秦_120mm_打印校验版.stl'),export_selected_objects=True)
(out/'reinforcement.json').write_text(json.dumps({'method':'0.8mm radius local reinforcement at screened weak ribbon contact','reinforced_points':report['smallest_samples']},indent=2))
