from pathlib import Path
import base64,shutil,re
r=Path(__file__).resolve().parent;out=r/'no-bag-v9';target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_去除斜挎包_v9');target.mkdir(exist_ok=True)
s=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_圆柱小熊包_v7/小秦_可旋转三维重建.html').read_text(encoding='utf-8')
s=re.sub(r'<title>.*?</title>','<title>小秦 · 去除斜挎包 v9</title>',s,count=1);s=re.sub(r'<h1>.*?</h1>','<h1>小秦 · 去除斜挎包 v9</h1>',s,count=1);s=re.sub(r'<small>.*?</small>','<small>已移除新旧包体及正面包带，并重建遮挡区域的衣服与裙子。本版为外观预览，尚未重新完成打印网格校验。</small>',s,count=1)
s=s.replace('href="bag-side.png"','href="side.png"').replace('href="bag-front.png"','href="front.png"').replace('包体侧面','人物侧面').replace('包体正面','人物正面')
a=s.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=s.index('";',a);s=s[:a]+base64.b64encode((out/'小秦_去除斜挎包.glb').read_bytes()).decode()+s[b:]
(target/'小秦_可旋转三维重建.html').write_text(s,encoding='utf-8')
for name in ['小秦_去除斜挎包.glb','小秦_去除斜挎包.blend','front.png','side.png','threequarter.png','removal-report.json']:shutil.copy2(out/name,target/name)
(target/'说明.txt').write_text('去除斜挎包 v9\n从v6未压缩人物源网格开始，删除旧包局部面，未导入v7新增圆柱包。删除正面皮革包带面；重建裙子、袖子内侧和胸前毛衣。\nBLEND为可继续编辑的母版，GLB和HTML供旋转预览。衣服修复改变了局部针织细节；本版尚未重新融合、验证打印STL，不沿用旧版打印合格结果。\n',encoding='utf-8')
print(str(target))
