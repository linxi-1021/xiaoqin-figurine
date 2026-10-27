from pathlib import Path
import cv2,numpy as np,re,base64,json
b=Path('D:/Desktop/相册/qr/融合艺术版_v2');r=[]
for name in ['普通备用二维码.webp','小米巧克力奶酪二维码.svg']:
 data=(b/name).read_bytes()
 if name.endswith('.svg'):data=base64.b64decode(re.search(rb'base64,([^"\s]+)',data)[1])
 im=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR);value,points,straight=cv2.QRCodeDetector().detectAndDecode(im);r.append({'file':name,'decoded':value,'shape':im.shape,'matrix_size':None if straight is None else list(straight.shape)})
 if straight is not None:np.save('models/rebuild/qr-matrix.npy',straight)
Path('models/rebuild/qr-source-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=False))
