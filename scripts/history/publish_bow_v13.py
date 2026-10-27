from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_柔褶蝴蝶结圆润星_v13_20261021';p=d/'小秦_可旋转三维重建.html';s=p.read_text(encoding='utf8');s=re.sub(r'<title>.*?</title>','<title>小秦 · 柔褶蝴蝶结圆润星 v13（最新）</title>',s,count=1);s=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 柔褶蝴蝶结圆润星 v13</h1><p>蝴蝶结正面柔和收褶，星星圆角鼓面并略带不对称。<br>保留背面贴帽状态及其余模型，自动导入完整模型。</p>',s,count=1,flags=re.S);s=s.replace('setTimeout(()=>earV5.click(),1800)','setTimeout(()=>rearBowV4.click(),1800)');p.write_text(s,encoding='utf8');s=re.sub(r'<base[^>]*>','',s);(b/'小秦_最新三维预览.html').write_text(s.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1),encoding='utf8')
for src,dst in [('bow-v13-back.png','蝴蝶结吊星后视.png'),('bow-v13-oblique.png','蝴蝶结吊星斜后视.png')]:shutil.copy2(Path('models/rebuild')/src,d/dst)
