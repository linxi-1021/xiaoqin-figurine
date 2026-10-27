from pathlib import Path
import re,base64
p=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_熊帽绒线细化_20261020');h=p/'小秦_可旋转三维重建.html';s=h.read_text(encoding='utf8');s=re.sub(r'window.MODEL_DATA="[^"]*"','window.MODEL_DATA="'+base64.b64encode((p/'小秦_v6熊帽绒线细化.glb').read_bytes()).decode()+'"',s,count=1);h.write_text(s,encoding='utf8')
