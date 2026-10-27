import cv2,numpy as np,json
from pathlib import Path
rows=[]
for name in ['qr-v21-bottom.png','qr-v21-oblique.png']:
 im=cv2.imdecode(np.frombuffer((Path('models/rebuild')/name).read_bytes(),np.uint8),cv2.IMREAD_COLOR)
 for mode,a in [('original',im),('640px',cv2.resize(im,(753,640))),('blurred',cv2.GaussianBlur(im,(3,3),.6))]:
  value,points,_=cv2.QRCodeDetector().detectAndDecode(a);rows.append({'image':name,'test':mode,'decoded':value,'pass':value=='https://happybirthdayxiaoqin.netlify.app/'})
Path('models/rebuild/qr-v21-scan-check.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows));
