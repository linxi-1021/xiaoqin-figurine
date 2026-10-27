from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,html,shutil,zipfile,math

base=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计')
out=base/'建模参考_局部细节图集_v1';out.mkdir(exist_ok=True)
sources={'主参考v5':base/'小秦_小熊帽手办_斜挎包方向修正_v5.png','三视补充':base/'小秦_手办三视外观参考_v1.png'}
images={k:Image.open(p).convert('RGB') for k,p in sources.items()}
# Coordinates are measured in original source pixels. No upscaling or generative editing.
rows=[]
def add(group,name,source,box,note):rows.append((group,name,source,box,note))
def main(group,name,box,note):add(group,name,'主参考v5',box,note)
def secondary(group,name,box,note):add(group,name,'三视补充',box,note)
main('00_整体比例','正面主姿势',(0,0,715,1385),'主参考；锁定帽子、脸、身体、底座的整体比例。')
main('00_整体比例','正侧整体',(727,0,1118,711),'主参考的侧前视角；核对包带走向与包的位置。')
main('00_整体比例','背面整体',(728,724,1118,1380),'主参考；锁定帽后蝴蝶结、四个发饰和包的背面。')
main('01_熊帽','帽子整体',(110,15,715,480),'帽冠与帽檐分层；耳朵不要与帽冠融成平面。')
main('01_熊帽','画面左侧熊耳',(153,25,376,252),'观察耳根、内耳凹陷与毛绒轮廓。画面方位不等于角色解剖左右。')
main('01_熊帽','画面右侧熊耳',(542,124,715,354),'观察外耳厚度与内耳凹槽。')
main('01_熊帽','帽面熊脸',(293,153,591,358),'熊眼、浅色眼周、鼻子为分层元素，避免单靠颜色表达形体。')
main('01_熊帽','帽面蓝眼与睫毛',(339,196,426,278),'原图局部很小；用于轮廓与配色参考，不代表毫米级尺寸。')
main('01_熊帽','帽面鼻子',(427,241,505,298),'圆润椭球鼻，注意贴合帽面。')
main('01_熊帽','帽檐弧线与厚度',(163,271,667,471),'帽檐为连续薄壳弧面，保留前缘圆角。')
main('01_熊帽','毛绒纹理样本',(189,205,304,295),'只确定毛绒方向与密度；12cm模型不宜逐根照搬纤维。')
main('02_五官眼镜','脸部与眼镜整体',(178,417,603,658),'保留眼距、镜片形状与微笑；眼镜边界需在灰模中可读。')
main('02_五官眼镜','画面左镜框',(214,427,407,574),'观察框体圆角、内框边界与镜框厚度。')
main('02_五官眼镜','画面右镜框',(398,474,591,623),'避免镜框下缘完全融进脸颊；镜片是透明外观参考。')
main('02_五官眼镜','鼻梁镜桥',(367,470,464,533),'桥接两片镜框，圆角连续，避免悬空细桥。')
main('02_五官眼镜','镜腿铆点',(541,497,601,557),'小白点为装饰/高光，不能全部误判成凸起。')
main('02_五官眼镜','画面左眼',(253,462,367,553),'瞳孔、睫毛与眼白用于上色参考；是否浮雕另行决定。')
main('02_五官眼镜','画面右眼',(438,510,550,596),'两眼需保持一致的表情，不按透视图机械做成同尺寸平面。')
main('02_五官眼镜','鼻口与腮红',(253,538,540,646),'鼻口浅浮雕；腮红主要为颜色，不是凸起。')
main('02_五官眼镜','耳朵与镜腿衔接',(543,537,599,614),'保留耳部与发丝、镜腿的遮挡层次。')
main('03_头发与前发饰','刘海分束',(132,324,563,478),'按大束分层，先体积后发丝沟槽，避免密集刻线。')
main('03_头发与前发饰','画面左前发束',(15,423,247,901),'S形主发束；观察转折与发梢回卷。')
main('03_头发与前发饰','画面右前发束',(553,487,711,981),'发束需要侧向厚度，不能只有正面起伏。')
main('03_头发与前发饰','胸前卷发',(225,593,420,838),'发束覆盖毛衣和包带，注意层叠关系。')
main('03_头发与前发饰','金色星星发夹',(561,438,633,513),'前发夹位于角色解剖左侧，即正面画面右侧。')
main('04_手部','挥手手掌与五指',(510,608,646,732),'造型主要依据；区分拇指与四指，保留指根连接强度。')
main('04_手部','挥手指尖',(529,612,641,692),'观察指尖圆角与指间凹口；不可把高光当沟槽。')
main('04_手部','挥手手腕与袖口',(485,686,617,799),'袖口包住手腕，保持袖口厚度及褶皱。')
main('04_手部','下垂手与袖口',(138,859,256,983),'核对手掌与包的遮挡关系，避免手部粘到包面。')
main('05_服装','毛衣整体',(143,644,618,940),'先做宽松衣服体积，再补主要编织与褶皱。')
main('05_服装','领口罗纹',(296,645,429,717),'领口厚度与纵向罗纹；避免脖子周围出现深裂缝。')
main('05_服装','麻花编织',(410,750,531,867),'编织为浅起伏，原图光影并不等于精确截面。')
main('05_服装','挥手袖部褶皱',(483,709,623,867),'袖口紧、上臂宽松，形成集中褶皱。')
main('05_服装','百褶裙整体',(276,844,583,1016),'格纹主要为上色；褶皱需有真实前后深度。')
main('05_服装','裙腰与褶根',(321,839,530,937),'裙腰进入毛衣下摆，褶根从腰部向下展开。')
main('05_服装','裙摆边缘',(285,953,581,1018),'裙摆边缘厚度适配打印，不按贴图锯齿建模。')
main('06_斜挎包','包带完整走向',(268,654,486,908),'从角色解剖左肩到右髋；正面画面从右上到左下。')
main('06_斜挎包','肩部包带',(413,654,482,748),'包带贴着毛衣曲面；不悬浮、不穿入前发束。')
main('06_斜挎包','包带中段与压线',(333,741,425,860),'包带厚度、边缘倒角及双边压线。')
main('06_斜挎包','金属扣与连接环',(280,835,368,904),'扣环与包耳连接；12cm打印时需适度加粗。')
main('06_斜挎包','小熊包正面',(204,858,354,999),'包在角色解剖右髋，熊脸向前外侧，保留厚度。')
main('06_斜挎包','小熊包脸与包耳',(216,860,344,962),'包耳与包体相连；五官可以采用浅浮雕配合上色。')
main('06_斜挎包','包边缝线',(276,898,352,992),'沿包体边缘环绕，缝线不要做成悬浮细丝。')
main('07_腿鞋底座','双腿姿态',(281,989,500,1147),'核对膝盖、脚踝与重心；不改变已确认站姿。')
main('07_腿鞋底座','袜口罗纹',(257,1081,507,1161),'袜口与腿、鞋口要分层，避免整体糊成一块。')
main('07_腿鞋底座','画面左鞋',(235,1114,389,1242),'观察鞋头、搭扣、鞋帮与鞋底圆角。')
main('07_腿鞋底座','画面右鞋',(386,1126,514,1244),'核对两鞋体积及前后位置，不强行完全对称。')
main('07_腿鞋底座','鞋带搭扣',(245,1124,503,1190),'鞋带为宽扁条，贴合鞋面，细缝不宜掏空。')
main('07_腿鞋底座','底座与双脚接地',(91,1184,665,1347),'底座上下面平整，脚底与底座有稳定连接。')
secondary('08_背面细节','背帽与蝴蝶结',(1060,39,1463,355),'背饰形状补充；位置服从主参考v5，蝴蝶结位于帽上。')
secondary('08_背面细节','蝴蝶结整体',(1181,181,1387,341),'应为扁平缎带，两个环、中心结、两条短尾。')
secondary('08_背面细节','蝴蝶结中心与褶皱',(1213,207,1320,291),'中心结包裹两侧缎带，褶皱由中心放射。')
secondary('08_背面细节','蝴蝶结尾带与吊星',(1244,254,1383,347),'星星连接在尾带附近；打印时不要独立悬空。')
secondary('08_背面细节','后发整体分束',(1039,324,1514,672),'大束从帽下连续向发梢展开，避免后脑勺平板化。')
secondary('08_背面细节','后发上方星夹',(1144,367,1207,428),'两颗后发星夹之一；数量与位置对照主参考。')
secondary('08_背面细节','后发下方星夹',(1341,499,1405,556),'两颗后发星夹之二，贴合发束表面。')
secondary('08_背面细节','后发上方小花',(1312,399,1383,466),'五片圆润花瓣与花心；花瓣避免分离成碎件。')
secondary('08_背面细节','后发下方小花',(1156,495,1220,559),'第二朵小花；尺寸与第一朵保持统一的Q版语言。')
secondary('08_背面细节','包背与后肩带',(1264,509,1468,707),'从背面应见包的素面背板，不能再画一张熊脸。')
secondary('08_背面细节','后鞋与后跟',(1173,782,1401,905),'观察鞋后帮、鞋底厚度与袜口层次。')
secondary('09_侧面补充','侧面整体',(544,37,1005,977),'只补充厚度和发束轮廓；此视图手势/左右关系有冲突，不用来决定姿势。')
secondary('09_侧面补充','侧面帽檐厚度',(550,199,959,356),'观察帽檐外伸及帽冠到帽檐的过渡。')
secondary('09_侧面补充','镜框侧面厚度',(610,315,720,413),'仅观察镜框贴脸距离和镜腿层次；不作为角色左右依据。')
secondary('09_侧面补充','侧发厚度与发梢',(770,343,997,696),'观察脑后体积、发束分层和末端内卷。')
secondary('09_侧面补充','侧鞋外底',(644,805,827,907),'观察鞋底厚度与鞋头上翘，左右方向不作为约束。')

manifest=[]
for idx,(group,name,source,box,note) in enumerate(rows,1):
 im=images[source];x0,y0,x1,y1=box
 assert 0<=x0<x1<=im.width and 0<=y0<y1<=im.height,(name,box)
 folder=out/group;folder.mkdir(exist_ok=True)
 file=folder/f'{idx:02d}_{name}.png';crop=im.crop(box);crop.save(file)
 # Verify actual pixel identity to the corresponding original region.
 assert Image.open(file).tobytes()==crop.tobytes()
 manifest.append(dict(id=idx,group=group,name=name,source=source,source_file=str(sources[source]),source_size=list(im.size),crop_box=list(box),size=list(crop.size),file=file.relative_to(out).as_posix(),note=note,scale='原始像素；未放大；未AI补画'))
(out/'裁切坐标与建模说明.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
srcdir=out/'原始参考图';srcdir.mkdir(exist_ok=True)
for p in sources.values():shutil.copy2(p,srcdir/p.name)

font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',13)
cols=5;cw=260;ch=240
sheet=Image.new('RGB',(cols*cw,65+math.ceil(len(manifest)/cols)*ch),'#f5f1eb');d=ImageDraw.Draw(sheet)
d.text((20,15),f'小秦建模局部参考 · {len(manifest)} 张原像素裁切',font=font,fill='#372b25')
for i,item in enumerate(manifest):
 x=(i%cols)*cw;y=65+(i//cols)*ch
 thumb=ImageOps.contain(Image.open(out/item['file']),(cw-22,ch-62))
 sheet.paste(thumb,(x+(cw-thumb.width)//2,y+5+(ch-62-thumb.height)//2))
 d.text((x+10,y+ch-52),f"{item['id']:02d} {item['name']}",font=font,fill='#372b25')
 d.text((x+10,y+ch-26),f"{item['size'][0]}×{item['size'][1]} · {item['source']}",font=small,fill='#71645c')
sheet.save(out/'00_局部参考总览.jpg',quality=94)

cards=''.join(f'''<button class="card" data-index="{i}" data-group="{html.escape(a['group'])}" data-search="{html.escape(a['group']+a['name']+a['note'])}"><img loading="lazy" src="{html.escape(a['file'])}"><b>{a['id']:02d} {html.escape(a['name'])}</b><span>{a['size'][0]} × {a['size'][1]} · {a['source']}</span></button>''' for i,a in enumerate(manifest))
groups=''.join(f'<option value="{g}">{g}</option>' for g in dict.fromkeys(a['group'] for a in manifest))
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>小秦 · 建模局部参考</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f1eb;color:#382e28;font:15px system-ui}header{padding:36px max(24px,5vw) 20px;background:#e8ddd0}h1{margin:0;font-size:30px}p{line-height:1.8;max-width:920px}nav{display:flex;gap:12px;flex-wrap:wrap}input,select,button{font:inherit}input,select{padding:12px;border:1px solid #cbbbae;border-radius:10px;background:#fffaf3}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:18px;padding:28px 5vw}.card{text-align:left;padding:10px;border:1px solid #e0d5ca;border-radius:14px;background:#fffaf5;cursor:pointer;color:inherit}.card:hover{border-color:#aa7958}.card img{width:100%;height:220px;object-fit:contain;background:#eee6dc;border-radius:8px}.card b{display:block;margin:12px 0 6px}.card span{font-size:13px;color:#887465}dialog{border:0;border-radius:18px;width:min(1100px,95vw);max-height:94vh;background:#fffaf5;padding:24px}dialog::backdrop{background:#17120fe0}.detail{display:grid;grid-template-columns:1fr 300px;gap:24px}.detail img{width:100%;max-height:68vh;object-fit:contain;background:#e9e0d6}.tools{display:flex;gap:10px;margin-bottom:16px}.tools button{padding:9px 15px;background:#eee2d5;border:0;border-radius:8px;cursor:pointer}a{color:#86502f}small{line-height:1.8;display:block;color:#7d6d61}#native{max-width:100%;display:inline-block;margin-top:16px} @media(max-width:760px){.detail{grid-template-columns:1fr}.card img{height:180px}header{padding:24px}.detail img{max-height:48vh}}</style><header><h1>小秦 · 建模局部参考</h1><p>按部位拆出的 <strong>COUNT</strong> 张小图。点击查看原像素、裁切位置与建模要点。主参考为已确认的 v5；三视图补充背面和厚度。<b>侧面手势方向存在冲突，不作为姿态依据。</b> 小图不增加原图中不存在的细节。</p><nav><input id="search" placeholder="搜索：眼镜 / 指尖 / 包带…"><select id="group"><option value="">全部部位</option>GROUPS</select><span id="count"></span></nav></header><main>CARDS</main><dialog><div class="tools"><button id="prev">← 上一张</button><button id="next">下一张 →</button><button id="close">关闭 ×</button></div><div class="detail"><img id="preview"><article><h2 id="name"></h2><p id="note"></p><small id="meta"></small><a id="native" target="_blank">打开原始裁切 PNG</a></article></div></dialog><script>const items=DATA;let index=0;const dialog=document.querySelector('dialog');function show(i){index=(i+items.length)%items.length;const a=items[index];document.querySelector('#preview').src=a.file;document.querySelector('#name').textContent=String(a.id).padStart(2,'0')+' '+a.name;document.querySelector('#note').textContent=a.note;document.querySelector('#meta').textContent=a.source+' | '+a.size.join('×')+' px | 裁切框 '+a.crop_box.join(', ')+' | '+a.scale;document.querySelector('#native').href=a.file;if(!dialog.open)dialog.showModal()}document.querySelectorAll('.card').forEach(b=>b.onclick=()=>show(Number(b.dataset.index)));document.querySelector('#prev').onclick=()=>show(index-1);document.querySelector('#next').onclick=()=>show(index+1);document.querySelector('#close').onclick=()=>dialog.close();document.addEventListener('keydown',e=>{if(dialog.open&&e.key==='ArrowRight')show(index+1);if(dialog.open&&e.key==='ArrowLeft')show(index-1)});function filter(){const q=document.querySelector('#search').value.trim();const g=document.querySelector('#group').value;let count=0;document.querySelectorAll('.card').forEach(b=>{b.hidden=!!((q&&!b.dataset.search.includes(q))||(g&&b.dataset.group!==g));if(!b.hidden)count++});document.querySelector('#count').textContent=count+' 张'}document.querySelector('#search').oninput=filter;document.querySelector('#group').onchange=filter;filter();</script></html>'''
page=page.replace('COUNT',str(len(manifest))).replace('GROUPS',groups).replace('CARDS',cards).replace('DATA',json.dumps(manifest,ensure_ascii=False))
(out/'小秦_建模局部参考索引.html').write_text(page,encoding='utf-8')
readme='''# 小秦建模局部参考图集

从已确认的 v5 效果图和三视补充图中按部位裁切。每张 PNG 均为原像素，无插值放大或 AI 补画。

## 使用顺序
1. 先用整体图锁定比例、站姿和包带方向，再打开局部图完善部件。
2. 手指与眼镜优先：按手指凹口和镜框厚度雕刻，不能仅依赖彩色贴图。
3. 熊帽与头发：先分大体块，再处理主要毛绒起伏和发束沟槽。
4. 背面：帽后蝴蝶结及吊星，头发两颗星星和两朵小花；装饰贴合载体。
5. 服装、斜挎包、鞋：补编织、压线、扣环、褶皱、鞋底层次；细节尺寸要适配约12cm树脂光固化。

## 参考优先级与冲突
主参考v5决定人物姿势与左右关系：角色解剖左手挥手；包带从左肩到右髋；小熊包熊脸朝前外侧，背面是素面。蝴蝶结在后帽上，不在头发上。
三视补充图仅用于外形与细节补充，侧面手势和方向存在不一致，不可直接当作严格正交蓝图。原图为渲染效果参考，不提供真实毫米尺寸或未显示区域的截面。透明镜片、高光、腮红和格纹不能全部转换为凸起几何。

## 文件
- HTML 索引：按部位筛选、搜索、点击查看和键盘前后翻图。
- PNG 小图：保留裁切区域原始像素，文件名含全局编号与部件名。
- JSON：每张图的原图路径、源图尺寸、裁切坐标、原生分辨率和建模要点。
- JPG 总览：缩略图目录，查找用；精修请打开对应PNG。
- 原始参考图：两张完整源图副本。

本次交付为建模参考资料整理，没有修改当前 v4 三维网格。
'''
(out/'建模使用说明.md').write_text(readme,encoding='utf-8')
z=base/'小秦_建模局部参考图集_v1.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as f:
 for p in out.rglob('*'):
  if p.is_file():f.write(p,p.relative_to(out))
print(json.dumps({'count':len(manifest),'groups':len(set(a['group'] for a in manifest)),'pixel_identity_verified':True,'folder':str(out),'zip':str(z)},ensure_ascii=False))
