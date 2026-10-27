from pathlib import Path
import shutil,base64
r=Path(__file__).resolve().parent;out=r/'bag-v7'
target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_圆柱小熊包_v7');target.mkdir(exist_ok=True)
template=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_小熊包图案优化_v6/小秦_可旋转三维重建.html').read_text(encoding='utf-8')
a=template.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=template.index('";',a);template=template[:a]+base64.b64encode((out/'小秦_重建模型.glb').read_bytes()).decode()+template[b:]
template=template.replace('小熊包图案优化 v6','圆柱小熊包 v7').replace('本轮重绘小熊包面：清晰椭圆眼睛、鼻子和小嘴，保留包边。仅纹理修改，三维几何沿用v5。','包体改为短圆柱：直径11.6mm、厚3.4mm，保留新版熊脸、小熊耳与包带。几何已更新，仍需实际打印验证。').replace('href="bag-before.png"','href="bag-side.png"').replace('包面优化前','包体侧面').replace('href="bag-after.png"','href="bag-front.png"').replace('包面优化后','包体正面')
(target/'小秦_可旋转三维重建.html').write_text(template,encoding='utf-8')
for name in ['小秦_重建模型.glb','小秦_重建模型.blend','bag-front.png','bag-side.png','bag-context.png','bag-shape-report.json','front.png','threequarter.png','back.png','小秦_120mm_打印校验版.stl','geometry-report.json','independent-stl-check.json']:shutil.copy2(out/name,target/name)
(target/'说明.txt').write_text('圆柱小熊包 v7\n包体改为直径11.6mm、厚3.4mm的短圆柱，边缘圆角0.38mm；两个小熊耳，保留v6清晰熊脸贴图。\n修整原融合包壳后增设规整闭合圆柱外壳，原身体、手部及包带保留。\nBLEND为高精度母版；GLB为网页预览；STL为同步更新的融合打印网格（毫米单位）。\n检查：正面bag-front.png，侧面bag-side.png，原相机近景bag-context.png。\n尚需树脂打印材料参数、薄弱部位复核、切片支撑和实际试打，不能仅凭网格闭合认定生产定稿。',encoding='utf-8')
print('PACKAGED_V7',target)
