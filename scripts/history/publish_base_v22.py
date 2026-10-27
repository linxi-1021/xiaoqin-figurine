from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_底面留白收敛_v22_20261021';p=d/'小秦_可旋转三维重建.html';s=p.read_text(encoding='utf8');s=re.sub(r'<title>.*?</title>','<title>小秦 · 底面配色统一 v22（最新）</title>',s,count=1);s=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 底面配色统一 v22</h1><p>空余底面匹配深可可底座，刻字用米白填色。<br>二维码保留四格浅色留白，6项渲染识别测试通过。</p>',s,count=1,flags=re.S);p.write_text(s,encoding='utf8');s=re.sub(r'<base[^>]*>','',s);(b/'小秦_最新三维预览.html').write_text(s.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1),encoding='utf8')
for src,dst in [('qr-v22-bottom.png','底面配色正视.png'),('qr-v22-oblique.png','底面配色斜视.png'),('qr-v22-scan-check.json','二维码识别验证.json')]:shutil.copy2(Path('models/rebuild')/src,d/dst)
