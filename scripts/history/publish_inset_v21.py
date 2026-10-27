from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_底面齐平镶嵌_v21_20261021';p=d/'小秦_可旋转三维重建.html';s=p.read_text(encoding='utf8');s=re.sub(r'<title>.*?</title>','<title>小秦 · 底面齐平镶嵌 v21（最新）</title>',s,count=1);s=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 底面齐平镶嵌 v21</h1><p>刻字与二维码嵌入原底座，不增加底座厚度。<br>底面微内收0.11毫米，二维码6项渲染识别测试通过。</p>',s,count=1,flags=re.S);s=s.replace('modelControls.target.set(0,-.0008,0)','modelControls.target.set(0,.00012,0)');p.write_text(s,encoding='utf8');s=re.sub(r'<base[^>]*>','',s);(b/'小秦_最新三维预览.html').write_text(s.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1),encoding='utf8')
for src,dst in [('qr-v21-bottom.png','嵌入底面正视.png'),('qr-v21-oblique.png','嵌入底面斜视.png'),('qr-v21-scan-check.json','嵌入后二维码识别验证.json')]:shutil.copy2(Path('models/rebuild')/src,d/dst)
(d/'制作说明.md').write_text('由v20改为原底座内部嵌槽，刻字、二维码整体收入槽内；底面相对原最低点内收约0.11毫米，未向外增加厚度。\n原字符与37×37二维码矩阵、0.65毫米格距、四格留白、0.28毫米凹刻保持。\n嵌入后六项渲染解码测试全部通过。打印仍需按浅色底、深色凹槽填色并复扫。\n',encoding='utf8')
