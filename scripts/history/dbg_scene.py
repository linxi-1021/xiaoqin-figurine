import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"D:\Desktop\相册\二维IP制作_20261012\手办设计\3D重建_v6基础_鞋履收敛_v35_20261025\小秦_v6鞋履收敛.blend")
print("OBJECTS", len(bpy.context.scene.objects))
for o in bpy.context.scene.objects:
    if o.type == "MESH":
        print("MESH", o.name, [round(v,4) for v in o.dimensions])
print("CAMERAS", [o.name for o in bpy.data.objects if o.type=="CAMERA"])
