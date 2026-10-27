import bpy,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底座净色_v17_20261021';D=B/'3D重建_v6基础_底座暖灰褐_v18_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底座净色.blend'));m=bpy.data.materials['Pedestal clean warm ivory satin'];m.name='Pedestal deep warm taupe satin';p=m.node_tree.nodes.get('Principled BSDF');c=[.49,.42,.36];p.inputs['Base Color'].default_value=(*[((v+.055)/1.055)**2.4 for v in c],1);p.inputs['Roughness'].default_value=.66
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底座暖灰褐.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底座暖灰褐.glb'),use_selection=True,export_format='GLB');(D/'底座色彩说明.json').write_text(json.dumps({'sRGB':'#7D6B5C','only_pedestal_material_changed':True},ensure_ascii=False),encoding='utf8')
