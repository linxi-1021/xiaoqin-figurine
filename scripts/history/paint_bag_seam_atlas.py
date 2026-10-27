from pathlib import Path
from PIL import Image
import numpy as np,json,shutil,cv2
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_毛衣针织包面_20261019';D=B/'3D重建_v6基础_包身材质接缝修复_20261019';r=json.loads((S/'表面坐标与投影校验.json').read_text(encoding='utf8'));C=np.array(r['center_surface_m']);U=np.array(r['right']);V=np.array(r['up']);N=np.array(r['normal']);original=np.array(Image.open(D/'Image_0.png').convert('RGB'));orm=np.array(Image.open(D/'Image_1.png').convert('RGB'));cloth=np.array(Image.open(S/'毛衣原色针织底纹.png').convert('RGB'));H,W=original.shape[:2];mask=np.zeros((H,W),np.float32);target=np.zeros_like(original);rows=json.loads((D/'候选三角面.json').read_text())
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
for f in rows:
 uv=np.array(f['uv'])*[W,-H]+[0,H];co=np.array(f['co'])
 for i in range(1,len(uv)-1):
  ids=[0,i,i+1];p=uv[ids];c=co[ids];lo=np.maximum(np.floor(p.min(0)).astype(int)-1,0);hi=np.minimum(np.ceil(p.max(0)).astype(int)+1,[W-1,H-1])
  if np.any(hi<lo):continue
  yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];pts=np.stack([xx+.5,yy+.5],-1);A=np.array([p[0]-p[2],p[1]-p[2]]).T
  if abs(np.linalg.det(A))<1e-9:continue
  ab=(pts-p[2])@np.linalg.inv(A).T;bc=np.concatenate([ab,(1-ab.sum(-1))[...,None]],-1);inside=np.min(bc,axis=-1)>=-.02;world=bc@c;q=world-C;u=q@U;v=q@V;d=q@N
  rad=np.sqrt((u/.0072)**2+(v/.0073)**2);a=smooth((1.18-rad)/.18)*smooth((d+.0062)/.0014)*smooth((.003-d)/.0008)*smooth((world[:,:,0]+.0215)/.002)*smooth((world[:,:,2]-.0275)/.0015);a=np.maximum(a,smooth(bc@np.array(f['seam_weight'])[ids]));a*=inside
  cu=np.clip(u/.012+.5,0,1);cv=np.clip(v/.012+.5,0,1);px=np.minimum((cu*2047).astype(int),2047);py=np.minimum(((1-cv)*2047).astype(int),2047);cl=cloth[py,px];sl=np.s_[lo[1]:hi[1]+1,lo[0]:hi[0]+1];old=mask[sl];take=a>old;target[sl][take]=cl[take];old[take]=a[take]
# Extend a few atlas texels into gutters to prevent bilinear filtering seams.
for _ in range(3):
 grow=cv2.dilate(mask,np.ones((3,3),np.uint8));new=(mask<.01)&(grow>.01)
 for ch in range(3):
  filled=cv2.dilate(np.where(mask>.01,target[:,:,ch],0).astype('uint8'),np.ones((3,3),np.uint8));target[:,:,ch][new]=filled[new]
 mask[new]=grow[new]
a=mask[:,:,None];out=np.rint(original*(1-a)+target*a).astype('uint8');Image.fromarray(out).save(D/'原UV_包身连续布纹.png');neworm=orm.astype(float);neworm[:,:,1]=orm[:,:,1]*(1-mask)+.82*255*mask;neworm[:,:,2]=orm[:,:,2]*(1-mask);Image.fromarray(np.rint(neworm).astype('uint8')).save(D/'原UV_包身连续粗糙度.png');Image.fromarray((mask*255).astype('uint8')).save(D/'局部修改范围.png');shutil.copy2(S/'表面坐标与投影校验.json',D/'表面坐标与投影校验.json');print('Modified texels',int((mask>0).sum()))
