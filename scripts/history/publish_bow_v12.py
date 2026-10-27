from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_装饰贴帽修正_v12_20261021';p=d/'小秦_可旋转三维重建.html';s=p.read_text(encoding='utf8');s=re.sub(r'<title>.*?</title>','<title>小秦 · 装饰贴帽修正 v12（最新）</title>',s,count=1);s=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 装饰贴帽修正 v12</h1><p>去除支柱，蝴蝶结与垂带沿绒面贴合，吊星贴近帽面。<br>接触处绒毛局部压低，人物保留，自动导入完整模型。</p>',s,count=1,flags=re.S);s=s.replace('setTimeout(()=>earV5.click(),1800)','setTimeout(()=>rearBowV4.click(),1800)');p.write_text(s,encoding='utf8');s=re.sub(r'<base[^>]*>','',s);(b/'小秦_最新三维预览.html').write_text(s.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1),encoding='utf8')
for src,dst in [('bow-v12-back.png','蝴蝶结吊星后视.png'),('bow-v12-oblique.png','蝴蝶结吊星斜后视.png')]:shutil.copy2(Path('models/rebuild')/src,d/dst)
