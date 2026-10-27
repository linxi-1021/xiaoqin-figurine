import bpy

BLEND = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend'
OUT = r'D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.glb'

bpy.ops.object.select_all(action='DESELECT')
count = 0
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        o.select_set(True)
        count += 1
bpy.ops.export_scene.gltf(filepath=OUT, use_selection=True, export_format='GLB')
print('EXPORTED', count, 'meshes')
