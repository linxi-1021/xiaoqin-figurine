import bpy,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底面齐平镶嵌_v21_20261021';D=B/'3D重建_v6基础_底面留白收敛_v22_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底面齐平镶嵌.blend'));base=bpy.data.materials['Pedestal deep cocoa satin'];plate=bpy.data.objects['GEO-Flush inset underside engraving'];plate.data.materials[0]=base
# QR tile retains its four-module light quiet zone; all other backing matches the pedestal.
text=bpy.data.objects['GEO-Recessed 小秦天天开心 dark fill'];ivory=bpy.data.materials['Underside ivory high contrast substrate'];text.data.materials.clear();text.data.materials.append(ivory)
for f in text.data.polygons:f.material_index=0
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底面留白收敛.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底面留白收敛.glb'),use_selection=True,export_format='GLB');(D/'底面配色说明.json').write_text(json.dumps({'backing_matches_original_pedestal':True,'qr_quiet_zone_modules':4,'qr_geometry_unchanged':True,'message_fill':'ivory for contrast on cocoa'},ensure_ascii=False,indent=2),encoding='utf8')
