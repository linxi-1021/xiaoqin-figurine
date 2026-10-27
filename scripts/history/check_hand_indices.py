import bpy
from pathlib import Path
from collections import Counter
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');bpy.ops.wm.open_mainfile(filepath=str(B/'3D重建_v6基础_包身材质接缝修复_20261019/小秦_v6包身材质接缝修复.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));print('POLYS',len(o.data.polygons),len(o.data.loops),Counter(len(f.vertices) for f in o.data.polygons));print('MODS',[(m.name,m.type) for m in o.modifiers]);print('MATRIX',o.matrix_world);print('SEEDPALM',o.data.polygons[389645].center[:]);print('FIRSTCO',o.data.vertices[o.data.polygons[389645].vertices[0]].co[:])
