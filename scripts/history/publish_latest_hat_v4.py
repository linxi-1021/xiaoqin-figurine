from pathlib import Path
from urllib.parse import quote
import re,shutil
b=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');d=b/'3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020';p=d/'小秦_可旋转三维重建.html';h=p.read_text(encoding='utf8');h=re.sub(r'<title>.*?</title>','<title>小秦 · 后帽粗绒 v4（最新）</title>',h,count=1);h=re.sub(r'<h1>.*?</h1><p>.*?</p>','<h1>小秦 · 后帽粗绒 v4（最新）</h1><p>后部绒簇减少、加粗，蝴蝶结露在绒面上方。<br>前部保持原样，打开后自动导入。</p>',h,count=1,flags=re.S);h=h.replace('查看帽檐底面（本次修改）','查看帽檐底面')
if 'rear-bow-v4-check' not in h:
 h+='<script>const rearBowV4=document.createElement("button");rearBowV4.id="rear-bow-v4-check";rearBowV4.textContent="查看后帽与蝴蝶结（本次修改）";rearBowV4.style.background="#e7bd80";rearBowV4.onclick=()=>{if(!window.modelCamera)return;modelControls.autoRotate=false;modelControls.target.set(0,.090,-.023);modelCamera.position.set(0,.095,-.105);modelControls.update()};document.querySelector("#status").after(rearBowV4);const focusRearV4=setInterval(()=>{if(window.pet&&window.modelCamera){clearInterval(focusRearV4);setTimeout(()=>rearBowV4.click(),1500)}},300)</script>'
p.write_text(h,encoding='utf8');h=re.sub(r'<base[^>]*>','',h);stable=h.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="'+quote(d.name)+'/">',1);(b/'小秦_最新三维预览.html').write_text(stable,encoding='utf8')
for src,dst in [('hat-rear-v4-back.png','帽后粗绒与蝴蝶结.png'),('hat-rear-v4-oblique.png','蝴蝶结上浮斜后视.png')]:shutil.copy2(Path('models/rebuild')/src,d/dst)
(d/'本版说明.md').write_text('后部减少绒线数量，增大线股和隆起；前部绒线坐标逐点保留。\n蝴蝶结、尾带、吊星作为整组向外移动，保持各自形状和相对位置；下方补铺连续绒面。\n中心结有隐藏固定点，使外移后的蝴蝶结仍与帽子相连。\n自动导入最新完整模型，默认展示后部。\n',encoding='utf8')
