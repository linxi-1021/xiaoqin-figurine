from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_前后帽统一粗绒_v8_20261021';p=d/'小秦_可旋转三维重建.html';s=p.read_text(encoding='utf8');s=re.sub(r'<title>.*?</title>','<title>小秦 · 前后统一粗绒 v8（最新）</title>',s,count=1);s=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 前后统一粗绒 v8</h1><p>前帽以实际后帽线股尺寸加厚，五官周围渐变留出间距。<br>保留熊耳分色、后帽与蝴蝶结。自动导入。</p>',s,count=1,flags=re.S);p.write_text(s,encoding='utf8');s=re.sub(r'<base[^>]*>','',s);(b/'小秦_最新三维预览.html').write_text(s.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1),encoding='utf8');shutil.copy2('models/rebuild/hat-front-v8-front.png',d/'前后统一粗绒正面.png')
