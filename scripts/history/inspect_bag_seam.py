import bpy,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_毛衣针织包面_20261019';D=B/'3D重建_v6基础_包身材质接缝修复_20261019';D.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6毛衣针织包面.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));m=o.data.materials[0]
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE':print(n.name,n.image.name,list(n.image.size));n.image.filepath_raw=str(D/(n.image.name+'.png'));n.image.file_format='PNG';n.image.save()
for l in m.node_tree.links:print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
# Serialize only local candidate triangles; other atlas texels remain byte-for-byte unchanged.
rows=[]
for f in o.data.polygons:
 if f.material_index!=0:continue
 c=f.center
 if -.026<c.x<-.003 and -.025<c.y<.001 and .025<c.z<.046:
  ids=list(f.loop_indices)
  rows.append({'co':[list(o.data.vertices[o.data.loops[k].vertex_index].co) for k in ids],'uv':[list(o.data.uv_layers[0].data[k].uv) for k in ids]})
(D/'候选三角面.json').write_text(json.dumps(rows),encoding='utf8');print('CANDIDATES',len(rows))
