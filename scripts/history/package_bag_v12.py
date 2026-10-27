from pathlib import Path
import base64,re,shutil
r=Path(__file__).resolve().parent;out=r/'bag-v12';target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_小熊包贴衣调整_v12');target.mkdir(exist_ok=True)
s=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_保留原衣腿去包_v10/小秦_可旋转三维重建.html').read_text(encoding='utf-8')
s=re.sub(r'<title>.*?</title>','<title>小秦 · 小熊包贴衣调整 v12</title>',s,count=1);s=re.sub(r'<h1>.*?</h1>','<h1>小秦 · 小熊包贴衣调整 v12</h1>',s,count=1);s=re.sub(r'<small>.*?</small>','<small>包体位置与倾角贴合衣物，连接带同步收短。保留短圆柱小熊包样式，手臂与衣服之间保留空隙，清理局部孤立碎片。人物原顶点没有移动。</small>',s,count=1)
s=s.replace('href="side.png"','href="bag-side.png"').replace('人物侧面','包体侧面')
a=s.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=s.index('";',a);s=s[:a]+base64.b64encode((out/'小秦_贴衣圆柱小熊包.glb').read_bytes()).decode()+s[b:]
(target/'小秦_可旋转三维重建.html').write_text(s,encoding='utf-8')
for name in ['小秦_贴衣圆柱小熊包.glb','小秦_贴衣圆柱小熊包.blend','front.png','side.png','threequarter.png','bag-side.png','fit-report.json','character-preservation-check.json']:shutil.copy2(out/name,target/name)
shutil.copy2(r/'no-bag-v10/independent-preservation-check.json',target/'原衣腿保留校验.json')
(target/'说明.txt').write_text('小熊包贴衣调整 v12\n依据衣服表面拟合包背朝向，包体平移并转动，保持直径11.6mm、厚3.4mm及熊脸双耳设计不变。同步重做较短的下连接带。\n包背21个采样点间隙中位数约0.104mm，局部最大约0.266mm；允许约0.12mm局部压入，以模拟衣料接触。\n清理手臂/胯侧20处孤立碎片，共388个面，不填满手臂与衣服之间的空隙。人物原顶点没有移动，腿部及上身保留校验见character-preservation-check.json。\nBLEND为可编辑母版；GLB/HTML供外观预览，本次未制作融合打印STL。',encoding='utf-8')
print('PACKAGED',str(target))
