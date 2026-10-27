from pathlib import Path
import base64,shutil,re
r=Path(__file__).resolve().parent;out=r/'no-bag-v10';target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_保留原衣腿去包_v10');target.mkdir(exist_ok=True)
s=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_圆柱小熊包_v7/小秦_可旋转三维重建.html').read_text(encoding='utf-8')
s=re.sub(r'<title>.*?</title>','<title>小秦 · 保留原衣腿去包 v10</title>',s,count=1);s=re.sub(r'<h1>.*?</h1>','<h1>小秦 · 保留原衣腿去包 v10</h1>',s,count=1);s=re.sub(r'<small>.*?</small>','<small>恢复原版衣服、裙子和腿部；去掉包体与正面包带，只局部补回连接处和带下窄条。局部接缝仍需检查，本版为外观预览。</small>',s,count=1)
s=s.replace('href="bag-side.png"','href="side.png"').replace('href="bag-front.png"','href="front.png"').replace('包体侧面','人物侧面').replace('包体正面','人物正面')
a=s.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=s.index('";',a);s=s[:a]+base64.b64encode((out/'小秦_保留原衣腿_去包.glb').read_bytes()).decode()+s[b:]
(target/'小秦_可旋转三维重建.html').write_text(s,encoding='utf-8')
for name in ['小秦_保留原衣腿_去包.glb','小秦_保留原衣腿_去包.blend','front.png','side.png','preservation-report.json','independent-preservation-check.json','Bag attachment local plaid.png','Narrow strap knit repair.png']:shutil.copy2(out/name,target/name)
(target/'说明.txt').write_text('保留原衣腿去包 v10\n基于v6未压缩母版，仅删除包体和皮革包带局部面。没有整体重建毛衣，没有镜像裙子，没有修改腿部。原顶点保持不动。\n仅新建包体连接处的局部补面及约5.3mm宽包带下的窄条；针织及格纹局部采样原贴图。局部接缝仍需外观复核。\n完整精度导出，不做全局减面。独立校验见independent-preservation-check.json。BLEND/GLB是外观版本，尚未重新融合及验证打印STL。',encoding='utf-8')
print(str(target))
