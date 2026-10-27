from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent/'bag-v8/garment-repair.png'
y,x=np.mgrid[0:512,0:512];wx=(x/511-.5)*.05;wz=.055-y/511*.03
checker=((np.floor(wx/.0045)+np.floor(wz/.0045))%2)[...,None]
rgb=np.where(checker,np.array([85,88,105]),np.array([65,69,86])).astype(float)
line=((np.mod(wx+.00025,.0045)<.0005)|(np.mod(wz+.00025,.0045)<.0005))[...,None]
rgb=np.where(line,rgb*.45+np.array([167,169,177])*.55,rgb)
knit=np.array([239,222,195])[None,None,:]+(np.sin(wx*6000)*2)[...,None]
rgb=np.where((wz>.0405)[...,None],knit,rgb)
Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(p)
