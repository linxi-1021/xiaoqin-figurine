from pathlib import Path
import re,base64
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_包身材质接缝修复_20261019');p=D/'小秦_可旋转三维重建.html';h=p.read_text(encoding='utf8');data=base64.b64encode((D/'小秦_v6包身材质接缝修复.glb').read_bytes()).decode();h,n=re.subn(r'window.MODEL_DATA\s*=\s*"[^"]*"',lambda m:'window.MODEL_DATA="'+data+'"',h,count=1);assert n==1;p.write_text(h,encoding='utf8')
