import bpy,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_二维码紧凑留白_v24_20261021';D=B/'3D重建_v6基础_二维码反色试验_v25_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6二维码紧凑留白.blend'));qr=bpy.data.objects['GEO-Scannable recessed QR code'];base=bpy.data.materials['Pedestal deep cocoa satin'];light=bpy.data.materials['Underside ivory high contrast substrate'];qr.data.materials[0]=base;qr.data.materials[1]=light;qr.data.materials[2]=base
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6二维码反色试验.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6二维码反色试验.glb'),use_selection=True,export_format='GLB');(D/'反色参数.json').write_text(json.dumps({'dark_modules_become_light':True,'light_field_matches_pedestal':True,'geometry_and_payload_unchanged':True},ensure_ascii=False),encoding='utf8')
