from pathlib import Path
import base64,re,shutil
r=Path(__file__).resolve().parent;out=r/'bag-v11';target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_圆柱小熊包重新装配_v11');target.mkdir(exist_ok=True)
s=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_保留原衣腿去包_v10/小秦_可旋转三维重建.html').read_text(encoding='utf-8')
s=re.sub(r'<title>.*?</title>','<title>小秦 · 圆柱小熊斜挎包 v11</title>',s,count=1);s=re.sub(r'<h1>.*?</h1>','<h1>小秦 · 圆柱小熊斜挎包 v11</h1>',s,count=1);s=re.sub(r'<small>.*?</small>','<small>短圆柱小熊包：直径11.6mm、厚3.4mm，双熊耳与清晰熊脸。保留人物衣裙、腿部网格，恢复原斜挎带，单独装配一个包体。本版供外观预览。</small>',s,count=1)
s=s.replace('href="side.png"','href="bag-side.png"').replace('人物侧面','包体侧面')
a=s.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=s.index('";',a);s=s[:a]+base64.b64encode((out/'小秦_圆柱小熊斜挎包.glb').read_bytes()).decode()+s[b:]
(target/'小秦_可旋转三维重建.html').write_text(s,encoding='utf-8')
for name in ['小秦_圆柱小熊斜挎包.glb','小秦_圆柱小熊斜挎包.blend','front.png','side.png','threequarter.png','bag-side.png','addition-report.json']:shutil.copy2(out/name,target/name)
shutil.copy2(r/'no-bag-v10/independent-preservation-check.json',target/'原衣腿保留校验.json')
(target/'说明.txt').write_text('圆柱小熊斜挎包 v11\n沿用v7认可的干净短圆柱小熊包组件：11.6mm直径、3.4mm厚度、两个小熊耳、熊脸与包边。仅导入这四个独立部件，未导入v7粗糙人物包壳。\n以v10人物为底稿，其人物主体的坐标、面拓扑与UV哈希不变。移除v10带下窄条补面，恢复从v6提取的原斜挎带，再用短皮带连接右胯包体内上侧。\nBLEND为完整精度可编辑母版，GLB和HTML用于外观预览。尚未融合并复核打印网格。',encoding='utf-8')
print('PACKAGED',str(target))
