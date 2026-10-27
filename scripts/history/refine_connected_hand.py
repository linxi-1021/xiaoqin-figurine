import bpy,numpy as np,json,hashlib
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包身材质接缝修复_20261019';D=B/'3D重建_v6基础_手部精修_20261019';bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包身材质接缝修复.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));co=np.array([v.co[:] for v in o.data.vertices]);im=o.data.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pix=np.array(im.pixels[:]).reshape(h,w,4);skin=np.zeros(len(co),bool);rows=[]
for f in o.data.polygons:
 x,y,z=f.center
 if not (.0108<x<.0232 and .058<z<.0682 and -.014<y<-.005):continue
 if x<.0145 and z>.0652:continue
 ids=list(f.loop_indices);uv=sum((o.data.uv_layers[0].data[k].uv for k in ids),Vector((0,0)))/len(ids);col=pix[int(uv.y*h)%h,int(uv.x*w)%w,:3]
 if col[0]>.45 and col[1]>.18 and col[2]>.10 and col[1]/max(col[0],.001)>.40:
  skin[list(f.vertices)]=True;rows.append({'co':[list(o.data.vertices[o.data.loops[k].vertex_index].co) for k in ids],'uv':[list(o.data.uv_layers[0].data[k].uv) for k in ids]})
x=co[:,0];z=co[:,2];weight=np.clip((z-.0625)/.0045,0,1)*skin;dz=np.zeros(len(co))
for center,width,depth in [(.01735,.00035,.00145),(.01910,.00035,.00135),(.02075,.00035,.00110)]:dz-=depth*np.exp(-2*((x-center)/width)**2)
dz+=.00050*np.exp(-2*((x-.0182)/.00055)**2);dz*=weight;co[:,2]+=dz;o.data.vertices.foreach_set('co',co.ravel());o.data.update()
# Keep the existing connected hand and wrist: no faces are removed or added.
(D/'hand-texture-faces.json').write_text(json.dumps(rows),encoding='utf8');(D/'手部修改报告.json').write_text(json.dumps({'method':'local deformation of original connected mesh; no replacement palm, no removed faces','moved_vertices':int((abs(dz)>1e-7).sum()),'max_displacement_mm':float(abs(dz).max()*1000),'removed_faces':0,'texture_faces':len(rows)},ensure_ascii=False,indent=2),encoding='utf8')
for node,file in [(o.data.materials[0].node_tree.nodes.get('Image Texture'),'hand-original-color.png'),(o.data.materials[0].node_tree.nodes.get('Image Texture.001'),'hand-original-orm.png')]:node.image.filepath_raw=str(D/file);node.image.file_format='PNG';node.image.save()
group=o.vertex_groups.new(name='Local fingertip and web polish')
for i in np.where(skin)[0]:
 weight=float(np.clip((co[i,2]-.0615)/.0025,0,1))
 if weight>0:group.add([int(i)],weight,'REPLACE')
bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Round repaired fingertip edges','SMOOTH');mod.vertex_group=group.name;mod.factor=.65;mod.iterations=20;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'hand-connected-work.blend'));print('CONNECTED_HAND_SCULPT_DONE')
