from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_底面融合字槽修复_v23_20261021';p=d/'小秦_可旋转三维重建.html';s=p.read_text(encoding='utf8');s=re.sub(r'<title>.*?</title>','<title>小秦 · 底面融合与字槽修复 v23（最新）</title>',s,count=1);s=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 底面融合 v23</h1><p>完整统一凹刻“小秦天天开心”。<br>香槟米色与可可色二维码，6项渲染识别测试通过。保持嵌入，不增厚。</p>',s,count=1,flags=re.S);p.write_text(s,encoding='utf8');s=re.sub(r'<base[^>]*>','',s);(b/'小秦_最新三维预览.html').write_text(s.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1),encoding='utf8')
for src,dst in [('qr-v23-bottom.png','融合底面正视.png'),('qr-v23-oblique.png','融合底面斜视.png'),('qr-v23-scan-check.json','最终二维码识别验证.json')]:shutil.copy2(Path('models/rebuild')/src,d/dst)
(d/'制作说明.md').write_text('修复文字：移除旧字体布尔结果，重建统一深度0.18毫米的连续字槽面，浅香槟色填字，六字完整一致。\n二维码采用底座同色可可码点与浅香槟底色，四周各4模块留白，远端角部收圆；尺寸、内容和0.28毫米码槽深度不变。\n原底座内部镶嵌结构保留，无外加厚度。\n六项渲染识别测试全部通过，底面三个网格均无开放边和非流形边。\n实体打印后按两色填槽、采用哑光，并手机复扫确认。\n',encoding='utf8')
