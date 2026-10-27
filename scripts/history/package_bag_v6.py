from pathlib import Path
import shutil,json
r=Path(__file__).resolve().parent;out=r/'bag-v6'
target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_小熊包图案优化_v6');target.mkdir(exist_ok=True)
import base64
model=base64.b64encode((out/'小秦_重建模型.glb').read_bytes()).decode()
template=(Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_参考细节修正版_v5/小秦_可旋转三维重建.html')).read_text(encoding='utf-8')
a=template.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=template.index('";',a)
template=template[:a]+model+template[b:]
template=template.replace('三维参考细节修正版 v5','小熊包图案优化 v6').replace('按局部参考重建扁平缎带蝴蝶结，调整星夹曲面贴合及花瓣方向，补眼镜内缘浅沟。保留v4手部。尚未完成独立眼镜分件与试打。','本轮重绘小熊包面：清晰椭圆眼睛、鼻子和小嘴，保留包边。仅纹理修改，三维几何沿用v5。')
# Add a bag close-up control to the existing bundled viewer script.
template=template.replace('</aside>','<p><a style="color:#eed7b8" href="bag-before.png" target="_blank">包面优化前</a> · <a style="color:#eed7b8" href="bag-after.png" target="_blank">包面优化后</a></p></aside>')
(target/'小秦_可旋转三维重建.html').write_text(template,encoding='utf-8')
for name in ['小秦_重建模型.glb','小秦_重建模型.blend','小熊包_清晰五官图案.png','小熊包_曲面合成贴图.png','bag-before.png','bag-after.png','bag-pattern-changes.json','front.png','threequarter.png','back.png']:shutil.copy2(out/name,target/name)
(target/'说明.txt').write_text('小熊包图案优化v6\n参考41_小熊包正面.png，重绘成对椭圆眼睛、圆润鼻子及连续小嘴。采用1024px局部纹理，带透明渐变边缘贴合原包面，保留包边缝线。\n纹理已打包进BLEND与GLB。比较bag-before.png与bag-after.png。\n本次未改变三维网格几何，STL沿用v5；普通无色树脂打印需后续上色才能呈现该图案。',encoding='utf-8')
print('PACKAGED_BAG_V6',target)
