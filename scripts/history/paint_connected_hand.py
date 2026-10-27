from pathlib import Path
from PIL import Image
import json,numpy as np,cv2
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_手部精修_20261019');a=np.array(Image.open(D/'hand-original-color.png').convert('RGB'));orm=np.array(Image.open(D/'hand-original-orm.png').convert('RGB'));H,W=a.shape[:2];mask=np.zeros((H,W),np.float32)
for f in json.loads((D/'hand-texture-faces.json').read_text()):
 uv=np.array(f['uv'])*[W,-H]+[0,H];co=np.array(f['co'])
 for j in range(1,len(uv)-1):
  ids=[0,j,j+1];p=uv[ids];c=co[ids];lo=np.maximum(np.floor(p.min(0)).astype(int)-1,0);hi=np.minimum(np.ceil(p.max(0)).astype(int)+1,[W-1,H-1]);yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];pts=np.stack([xx+.5,yy+.5],-1);A=np.array([p[0]-p[2],p[1]-p[2]]).T
  if abs(np.linalg.det(A))<1e-9:continue
  ab=(pts-p[2])@np.linalg.inv(A).T;bc=np.concatenate([ab,(1-ab.sum(-1))[...,None]],-1);q=bc@c;wt=np.clip((q[:,:,2]-.0588)/.0014,0,1);wt=wt*wt*(3-2*wt);wt*=np.min(bc,axis=-1)>=-.03;sl=np.s_[lo[1]:hi[1]+1,lo[0]:hi[0]+1];mask[sl]=np.maximum(mask[sl],wt)
mask=cv2.dilate(mask,np.ones((3,3),np.uint8));alpha=mask[:,:,None];target=np.array([229,162,130]);out=np.rint(a*(1-alpha)+target*alpha).astype('uint8');Image.fromarray(out).save(D/'hand-clean-skin-atlas.png');o=orm.astype(float);o[:,:,1]=o[:,:,1]*(1-mask)+.68*255*mask;o[:,:,2]*=(1-mask);Image.fromarray(np.rint(o).astype('uint8')).save(D/'hand-matte-orm-atlas.png');print('HAND_TEXTURE_PAINTED',int((mask>0).sum()))
