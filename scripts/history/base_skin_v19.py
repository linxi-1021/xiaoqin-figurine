import bpy,numpy as np,json
from pathlib import Path
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_底座暖灰褐_v18_20261021';D=B/'3D重建_v6基础_底座匹配肤色_v19_20261021';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6底座暖灰褐.blend'));body=max((o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('GEO-Redesigned')),key=lambda o:len(o.data.vertices));m=body.data;im=m.materials[0].node_tree.nodes.get('Image Texture').image;w,h=im.size;pixels=np.array(im.pixels[:]).reshape(h,w,4);samples=[]
# Sample exposed lower legs, excluding socks, highlights and shaded contours.
for f in m.polygons:
 x,y,z=f.center
 if not(.025<z<.037 and abs(x)<.016 and y<-.002):continue
 uv=np.mean([m.uv_layers[0].data[k].uv[:] for k in f.loop_indices],0);r,g,b=pixels[int(uv[1]*h)%h,int(uv[0]*w)%w,:3]
 if .5<r<.98 and .40<g/r<.83 and .42<b/max(g,.001)<.88:samples.append((r,g,b))
assert len(samples)>20;srgb=np.median(np.array(samples),axis=0);base=bpy.data.materials['Pedestal deep warm taupe satin'];base.name='Pedestal sampled skin peach';p=base.node_tree.nodes.get('Principled BSDF');linear=[((float(v)+.055)/1.055)**2.4 for v in srgb];p.inputs['Base Color'].default_value=(*linear,1);p.inputs['Roughness'].default_value=.66
r={'skin_sample_faces':len(samples),'sample_source':'exposed legs texture median','sRGB':srgb.tolist(),'hex':'#'+''.join(f'{round(float(v)*255):02X}' for v in srgb),'only_pedestal_material_changed':True};(D/'肤色取样校验.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6底座匹配肤色.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6底座匹配肤色.glb'),use_selection=True,export_format='GLB')
