import bpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import barycentric_transform
from mathutils.bvhtree import BVHTree
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_毛衣针织包面_20261019');S=D.parent/'3D重建_v6基础_包面匹配原棕色_20261019';bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6包面匹配原棕色.blend'));o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));im=o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node.image;w,h=im.size;src=np.array(im.pixels[:]).reshape(h,w,4);tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());size=256;out=np.ones((size,size,4),np.float32);cache={}
for iy in range(size):
 z=.0475+iy/(size-1)*.006
 for ix in range(size):
  x=.0035+ix/(size-1)*.004
  hit,n,fi,dist=tree.ray_cast(Vector((x,-.1,z)),Vector((0,1,0)))
  if fi not in cache:
   f=o.data.polygons[fi];ids=list(f.loop_indices)[:3];cache[fi]=([o.data.vertices[o.data.loops[k].vertex_index].co.copy() for k in ids],[Vector((*o.data.uv_layers[0].data[k].uv,0)) for k in ids])
  a,b=cache[fi];uv=barycentric_transform(hit,*a,*b);fx=uv.x*w;fy=uv.y*h;x0=int(fx)%w;y0=int(fy)%h;tx=fx-int(fx);ty=fy-int(fy);out[iy,ix]=src[y0,x0]*(1-tx)*(1-ty)+src[y0,(x0+1)%w]*tx*(1-ty)+src[(y0+1)%h,x0]*(1-tx)*ty+src[(y0+1)%h,(x0+1)%w]*tx*ty
img=bpy.data.images.new('Sweater physically sampled patch',width=size,height=size,alpha=True);img.pixels.foreach_set(out.ravel());img.filepath_raw=str(D/'毛衣原表面采样.png');img.file_format='PNG';img.save();print('SWEATER_SAMPLE_DONE')
