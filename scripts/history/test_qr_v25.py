import cv2,numpy as np,json
from pathlib import Path
r=[]
for name in ['qr-v25-bottom.png','qr-v25-oblique.png']:
 p=Path('models/rebuild')/name
 if not p.exists():continue
 im=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),cv2.IMREAD_COLOR)
 for mode,a in [('original',im),('640px',cv2.resize(im,(753,640))),('blurred',cv2.GaussianBlur(im,(3,3),.6))]:
  direct=cv2.QRCodeDetector().detectAndDecode(a)[0];inverse=cv2.QRCodeDetector().detectAndDecode(255-a)[0];r.append({'image':name,'test':mode,'direct':direct,'auto_inversion':inverse,'direct_pass':direct=='https://happybirthdayxiaoqin.netlify.app/','inverse_pass':inverse=='https://happybirthdayxiaoqin.netlify.app/'})
Path('models/rebuild/qr-v25-inverse-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r))
