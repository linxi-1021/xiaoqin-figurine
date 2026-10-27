import bpy
from pathlib import Path
r=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(r/'bag-v6/小秦_重建模型.blend'));b=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));print('UV',[(v.name,v.active_render) for v in b.data.uv_layers])
for m in b.data.materials:
 print('MAT',m.name)
 for n in m.node_tree.nodes:
  if n.type in ['TEX_IMAGE','UVMAP']:print('NODE',n.name,n.type,n.image.name if n.type=='TEX_IMAGE' and n.image else '',n.uv_map if n.type=='UVMAP' else '')
 for l in m.node_tree.links:print('LINK',l.from_node.name,l.from_socket.name,'>',l.to_node.name,l.to_socket.name)
