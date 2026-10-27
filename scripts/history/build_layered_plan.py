from pathlib import Path
import json, shutil

r = Path(__file__).resolve().parent
ctx = json.loads((r/'layered-planning-context.json').read_text(encoding='utf-8'))
root = Path(ctx['planning_folder'])
content = Path(ctx['session_dir'])/'content'
rows = ctx['refs']
stages = [
 {'id':0,'name':'参考与比例锁定','part':'参考相机、坐标、部件清单','refs':[1,2,3,61], 'work':'主参考 v5 决定正面比例、姿势与左右；补充图只补深度。记录视图矛盾，先标注不确定处。','gate':'有正面/侧面/背面基准、65 张细节追踪表，明确哪些尺寸是推定值。'},
 {'id':1,'name':'完整身体与姿势','part':'头部基础、躯干、骨盆、双臂、双手、双腿、脚','refs':[1,2,19,20,26,27,29,44,49,60,61], 'work':'先做完整 Q 版身体，左手挥手、右手自然下垂。隐藏衣帽与包时，身体仍完整；不需要制作器官或无关解剖细节。被衣物遮挡的体积是依据姿势推定的结构。','gate':'正侧背与低角度均成立；手指数量正确；腿和手没有缺面、薄片或断裂。身体阶段不通过就不加外层。'},
 {'id':2,'name':'衣服、袜子与鞋','part':'毛衣、袖子、裙子、袜子、鞋与底座','refs':[28,29,30,31,32,33,34,35,36,44,45,46,47,48,49,60,65], 'work':'围绕身体制作独立衣壳。毛衣在包带下、头发下也连续存在；裙子完整环绕，褶皱不因包遮挡而中断。先轮廓、袖口、腰线，再做编织与鞋底层次。','gate':'隐藏衣服看见完整身体；隐藏包仍有完整衣服。手臂与躯干间允许空隙，不用跨接薄片填满。'},
 {'id':3,'name':'五官与独立眼镜','part':'眼球/眼睑、眉、鼻嘴、镜框、镜腿与镜片','refs':[12,13,14,15,16,17,18,19,20,63], 'work':'按局部图定位眼睛、微笑和腮红。眼镜具有真实侧面厚度，镜腿接至耳侧。颜色与几何分开：高光、腮红不全部做成凸块。','gate':'正面叠图核对五官位置；侧面检查镜腿、眼睑和脸颊；不能用一张脸部图片冒充立体结构。'},
 {'id':4,'name':'头发主体与发束','part':'发根内层、刘海、左右前发、背部主发束','refs':[21,22,23,24,25,54,64], 'work':'从发根体积到大束波浪，再补沟槽。发束是有截面和收尖的面体，不用等粗圆管堆成头发。先确认遮挡衣服的关系，再处理帽下接缝。','gate':'正侧背轮廓分别对照；后脑不空、头发不穿过肩膀和帽檐；主要发束能独立编辑。'},
 {'id':5,'name':'熊帽与毛绒层次','part':'帽体、帽檐、双耳、帽面五官、毛绒起伏','refs':[4,5,6,7,8,9,10,11,50,62], 'work':'先帽体壳与帽檐，再耳朵和熊脸。以主毛绒起伏形成体积；微细绒感区分渲染材质与打印可保留的几何，不把图片噪点全变成疙瘩。','gate':'帽体贴合头发而不互穿；帽檐厚度与侧面相符；熊耳数量与位置正确。'},
 {'id':6,'name':'后帽蝴蝶结与发饰','part':'帽后蝴蝶结、短尾带、吊星、发上两星两花、前星夹','refs':[25,50,51,52,53,54,55,56,57,58], 'work':'蝴蝶结放在后帽，使用宽扁且有厚度的带面。两颗星和两朵花分别贴合后发束；前星夹按主参考定位。装饰与载体分别命名。','gate':'逐件计数并核对背图；无悬浮、穿插或把蝴蝶结放到头发上的错误。'},
 {'id':7,'name':'最后装配斜挎包','part':'短圆柱包、双耳、熊脸、包边、扣环、肩带','refs':[37,38,39,40,41,42,43,59], 'work':'包体与肩带独立。沿用已确认短圆柱熊包样式，左肩至右胯，熊脸朝前外侧，背面素面。先依衣服表面确定包背接触面，再布置扣环及带路，不移动衣服去迎合包。','gate':'只有一个包体；隐藏包和带后衣服依旧完整。侧面无明显悬空；记录接触间隙、穿插与带的连接点。'},
 {'id':8,'name':'外观验收与打印副本','part':'可编辑母版、预览模型、独立打印副本','refs':[1,3,49,60,65], 'work':'母版保留各层和修改器；预览从副本导出。约 120mm 树脂手办的分件、壁厚、细杆、支撑与排液在打印副本处理，不破坏外观母版。','gate':'完成六面/低角度/局部对照、对象计数、法线和连通性检查；切片与实际试打后才能称生产定稿。'}
]
coverage = sorted({x for s in stages for x in s['refs']})
assert coverage == list(range(1,66)), coverage
data = {'status':'brainstorming_draft_awaiting_review','mesh_started':False,'source_of_truth':'主参考 v5 + 65 张原像素局部图 + 用户已确认修改','print_target':'约120mm，树脂光固化；工程参数待切片与试打确认','tools':{'skills':['reference-to-3d','blender-modeling','source-part-segmentation','blender-export'],'blender':'已存在 Blender 5.1.1 本地运行时','mcp':'当前没有已连接工具；实施前必须明确执行后端，不能假称接入成功'},'archive':ctx['archive'],'stages':stages,'reference_coverage':coverage,'refs':rows}
(root/'分层重建规划.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
parts = '\n'.join(f"### {s['id']:02d} {s['name']}\n\n- 部件：{s['part']}\n- 参考图编号：{', '.join('%02d'%n for n in s['refs'])}\n- 做法：{s['work']}\n- 验收：{s['gate']}\n" for s in stages)
trace = '\n'.join(f"| {q['id']:02d} | {q['name']} | {', '.join(str(s['id']) for s in stages if q['id'] in s['refs'])} | {q['note']} |" for q in rows)
doc = f'''# 小秦全新分层重建：brainstorming 规划草案

日期：2026-10-19。状态：待用户评审；尚未创建新网格。

## 已保存的当前版本

v12 原文件未覆盖。已单独复制到 `{ctx['archive']}`，11 个原文件逐一 SHA-256 校验一致，清单为保存校验.json。
新项目位于 `{root}`，与原 v12 及其存档分开；当前只有规划与参考素材。

## 目标与边界

重新建立一套可以逐层隐藏、单独修改的模型，按身体 → 衣服/鞋 → 五官眼镜 → 头发 → 帽子 → 装饰 → 包与带的依赖顺序完成。衣服完整存在于头发、包和带之下，身体完整存在于衣服之下。
主体造型沿用已确认的小秦：大眼镜、棕色长卷发、熊帽、米白毛衣、灰蓝格裙、左手挥手、右手下垂、米白鞋袜与圆底座。角色左侧为正面画面的右侧；斜挎带从角色左肩到右胯。
目标仍为约 12cm 树脂光固化手办。隐藏身体部分只需合理结构，不制作无关内部器官。现有参考无法证明被遮挡部分的精确形状，必须在清单标记为推定。

## 两种路线与推荐

| 路线 | 做法 | 优点 | 代价/局限 |
|---|---|---|---|
| A：参考约束的 Blender 分层重建（推荐） | 每个结构部件从参考轮廓、深度和部件关系建网格，细分曲面/曲线辅助，逐阶段校验 | 身体、衣物、头发、包完全可分；能消除上一套融合网格的根本问题 | 有机造型较慢；脚本或技能本身不能保证专业雕刻质量，必须依据渲染对照逐项过关 |
| B：各部件图生3D后再整理 | 分别生成内身体、衣服、头发和配饰，再拓扑和装配 | 可较快得到有机体积候选 | 被遮挡部分、部件比例和接口易不一致；重拓扑工作量与结果不确定 |

推荐 A。旧模型只作效果对照，不能作为新身体/衣物的融合母体。不要重复整个人一次图生3D后再切包的流程。

## 3D 技能与工具的真实状态

本地已核对 cc-blender-skill 的 reference-to-3d、blender-modeling、source-part-segmentation 指南；可用于参考清单、分件、网格操作和验证流程设计。它们的标准建模流程要求 Blender MCP。目前没有已连接的 Blender MCP 工具，插件目录本次搜索也没有返回直接可用的 Blender 插件；不能宣称已经接入。
本机存在已使用过的 Blender 5.1.1 原生 Python 执行环境。正式开建前先确定后端：按技能原版连接 MCP 并执行只读场景查询；若采用原生 Python，则应作为明确的后端适配说明，而不是假称 MCP 已执行。连接或后端选择未验证前不开始新模型。
技能中有机角色部分只覆盖基础体块和一般网格流程，精细脸型、卷发和手指仍需要逐步造型与视觉验收；不能因为用了 skill 就承诺自动达到手工雕刻水平。

## 参考优先级

1. 已确认主参考 v5：正面比例、姿势、左右、包带方向。
2. 65 张局部图：逐件查看原像素图，不用总览缩略图做细节测量。
3. 补充三视：只补深度与背面。它不是严格正交工程蓝图，手势等冲突必须记入冲突清单。
4. 用户后续明确修改：后帽蝴蝶结、发上两星两花、短圆柱熊包、贴衣、手臂与衣物间可镂空。

尺寸先标为设计初值，再经比例叠图与实物需求修正。包的 11.6mm 直径、3.4mm 厚度仅是已认可版本的起点，不冒充参考图提供的实测尺寸。

## 由里向外的阶段与验收

{parts}

## 工程组织与不可破坏约束

- 使用语义对象和独立集合：BODY、CLOTHES、FACE、GLASSES、HAIR、HAT、ORNAMENTS、BAG、PRINT_COPY。包体必须恰好一个；后发装饰为两星两花。
- 建立毫米尺度、统一坐标、固定参考相机。参考图片对象单独放 REF 集合且不导出。
- 每个阶段保留独立 .blend 里程碑、正侧背和局部图、验证 JSON。未验收前不覆盖已通过阶段。
- 外层只能通过独立对象和约束装配。修改包时禁止重新切割毛衣、移动腿或全局压缩人物网格。
- 用遮挡测试代替表面看起来没问题：关闭包、关闭头发、关闭衣物，各内层必须完整。检查剖面和背面，不能用深色背景掩盖破面。
- 颜色、材质、贴图与几何分开建。格纹、腮红和高光不全部转成浮雕；镜框、指缝、主要编织/毛绒体积有真实结构。
- 参考相似度、网格健康和实际打印是三种不同验收。闭合不等于相似，渲染好看不等于可打印，未试打不称生产定稿。

## 首个实施里程碑

先完成后端只读查询、参考测量与身体基础，不同时开做帽子、衣服和包。交付完整身体的正面/侧面/背面与手腿特写，再决定是否进入衣物阶段。其目的在于尽早暴露比例和姿势问题。

## 逐图追踪（65/65 覆盖）

| 图号 | 图名 | 阶段 | 建模要点 |
|---|---|---|---|
{trace}

## 本轮未执行

没有开始新身体网格，没有重新生成整人，没有修改或覆盖 v12，也没有安装/声称接通 MCP。此文档是可评审草案，不是已完成模型的验收报告。
'''
(root/'分层重建规划_草案.md').write_text(doc,encoding='utf-8')

html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>小秦 · 由里向外重建规划</title>
<style>:root{--paper:#f5f0e8;--ink:#302c28;--muted:#79716a;--accent:#8c553f;--line:#ddd2c5}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}header{background:#302c28;color:#f8f2e8;padding:38px max(5vw,22px)}header small{letter-spacing:.18em;color:#cfbda7}h1{font-size:clamp(28px,4vw,46px);font-weight:620;margin:8px 0}h2{font-size:24px;margin:0 0 12px}h3{font-size:18px;margin:0 0 8px}p{margin:8px 0}main{max-width:1240px;margin:auto;padding:30px 24px 60px}.notice,.panel{background:#fffcf7;border:1px solid var(--line);border-radius:18px;padding:24px;margin:20px 0}.notice{border-left:5px solid #6b8b72}.badge{display:inline-block;border:1px solid currentColor;border-radius:99px;padding:3px 12px;font-size:12px;margin:3px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.hero{display:grid;grid-template-columns:1.2fr 1fr;gap:24px;align-items:center}.hero img{width:100%;max-height:600px;object-fit:contain;background:#ebe0d1;border-radius:14px}.muted{color:var(--muted)}button{font:inherit;border:1px solid var(--line);background:#fffaf3;border-radius:9px;padding:8px 13px;cursor:pointer}button:hover,button.active{background:var(--accent);color:white;border-color:var(--accent)}.stages{display:flex;flex-wrap:wrap;gap:8px}.stage{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:18px}.label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}.gate{background:#e9efe7;padding:12px 16px;border-radius:10px;margin-top:14px}.options{display:grid;grid-template-columns:1fr 1fr;gap:18px}.option{border:1px solid var(--line);border-radius:14px;padding:20px;cursor:pointer;background:white}.option.selected{outline:3px solid var(--accent)}.option strong{font-size:19px}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line)}.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:12px;margin-top:18px}.ref{background:white;border:1px solid var(--line);border-radius:12px;padding:10px;cursor:pointer}.ref img{width:100%;height:130px;object-fit:contain}.ref span{display:block;font-size:13px}.ref em{font-size:11px;color:var(--muted);font-style:normal}dialog{border:0;border-radius:16px;max-width:min(95vw,1000px);max-height:94vh;padding:24px;background:#fffaf3}dialog::backdrop{background:#241e1ad9}dialog img{display:block;max-width:100%;max-height:67vh;object-fit:contain;margin:auto}.close{float:right}.refs-small{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.refs-small button{font-size:12px}.node{padding:13px;border-left:3px solid var(--accent);margin:8px 0;background:#f2e8dc}.checks li{margin:9px 0}.skill{font-family:ui-monospace,monospace}.foot{font-size:13px;color:var(--muted);margin-top:30px}.path{word-break:break-all;font-size:12px}.diagram{width:100%;max-height:420px}.archive{display:flex;gap:14px;align-items:center}.archive img{width:95px;height:130px;object-fit:contain;border-radius:9px}#diagram-bag{transition:transform .35s}a{color:var(--accent)}@media(max-width:760px){.grid,.hero,.stage,.options{grid-template-columns:1fr}main{padding:18px}header{padding:25px}.panel{padding:18px}}
</style><header><small>PLANNING / 2026.10.19</small><h1>先有完整的身体，再逐层穿戴。</h1><p>小秦 · 全新分层重建规划　<span class="badge">规划草案</span><span class="badge">尚未开始新网格</span></p></header><main>
<section class="notice"><div class="archive"><img data-asset="saved-v12.png" alt="已保存 v12 预览"><div><h3>当前 v12 已独立保存</h3><p>11 个文件逐一 SHA-256 校验一致；原文件保持原位。新项目另建目录。</p><div id="archive" class="path"></div></div></div></section>
<section class="hero"><img data-asset="hero.png" alt="已确认 v5 外观主参考"><div><div class="label">Source of truth</div><h2>保持已确认造型，重建内部结构。</h2><p>米白毛衣、灰蓝格裙、棕色长卷发与熊帽；角色左手挥手，包从左肩斜跨到右胯。蝴蝶结在后帽，两星两花在后发束。</p><p>主参考锁比例与左右，65 张局部图逐项核对。补充侧背图不当作严格工程蓝图。</p><div class="node">从身体开始，新衣服必须在包带和头发下也完整存在。隐藏包，衣服不会破；隐藏衣服，身体不会缺。</div><p class="muted">约 120mm 树脂手办目标。被遮挡部分是结构推定，不假称参考图提供了真实截面。</p></div></section>
<section class="panel"><div class="grid"><div><h2>可拆分层次，而不是一次融合。</h2><p class="muted">这是局部剖面示意，不是新模型效果图。</p><svg class="diagram" viewBox="0 0 570 400" role="img" aria-label="身体、衣服与斜挎包的独立关系"><ellipse cx="215" cy="200" rx="100" ry="140" fill="#e6d9be" stroke="#bca98a" stroke-width="3"/><ellipse cx="215" cy="200" rx="76" ry="112" fill="#eabda5" stroke="#c48f75" stroke-width="2"/><text x="215" y="194" text-anchor="middle" fill="#55392f" font-size="23">完整身体</text><text x="215" y="225" text-anchor="middle" fill="#71594e" font-size="15">一直保留在衣服里面</text><path d="M120 95L60 55" stroke="#a99576" stroke-width="2"/><text x="15" y="43" fill="#5b5043" font-size="17">独立衣壳</text><g id="diagram-bag"><path d="M270 85L330 225" stroke="#ac794d" stroke-width="13" fill="none"/><circle cx="337" cy="270" r="48" fill="#fff6df" stroke="#ac794d" stroke-width="4"/><circle cx="308" cy="231" r="13" fill="#fff6df" stroke="#ac794d" stroke-width="3"/><circle cx="368" cy="231" r="13" fill="#fff6df" stroke="#ac794d" stroke-width="3"/><circle cx="324" cy="267" r="3.5" fill="#80543c"/><circle cx="351" cy="267" r="3.5" fill="#80543c"/><path d="M330 280Q337 290 344 280" fill="none" stroke="#80543c" stroke-width="3"/><text x="415" y="270" fill="#5b5043" font-size="17">独立包与肩带</text></g></svg><button id="hide-bag">演示：隐藏包</button><button id="separate-bag">演示：移开包</button></div><div><div class="label">Editable layers</div><div class="node">内层 · 完整头部、躯干、双臂、手、双腿</div><div class="node">衣着 · 毛衣、裙子、袜子、鞋</div><div class="node">脸部 · 五官 → 镜框与镜腿</div><div class="node">头部外层 · 发根 → 发束 → 帽体 → 毛绒</div><div class="node">末层 · 蝴蝶结与发饰 → 包体、扣环、肩带</div><p>手臂与衣服之间允许自然镂空。各部件有各自边界和厚度，不用跨接薄片填空隙。</p></div></div></section>
<section class="panel"><h2>实施路线先选清楚</h2><div class="options"><div class="option" data-choice="route-a" onclick="pickRoute(this)"><strong>A · 参考约束的 Blender 分层重建</strong><span class="badge">推荐</span><p>轮廓、姿态、部件关系先锁定，再做细分网格和局部细节。每一层独立检查。</p><p class="muted">优点：部件可控，隐藏和修改不破坏内层。代价：有机造型需要较慢的迭代，skill 不能自动代替专业雕刻。</p></div><div class="option" data-choice="route-b" onclick="pickRoute(this)"><strong>B · 各部件分别图生3D后整理</strong><p>单独生成部件候选，再重拓扑与装配。</p><p class="muted">优点：较快得到有机体积。代价：被遮挡形状、比例和接口不稳定，仍需大量整理。</p></div></div><p id="choice-status" class="muted">点击只记录路线偏好，不会自动开始建模。请在聊天里确认规划。</p></section>
<section class="panel"><h2>由里向外，逐阶段过关</h2><div id="stages" class="stages"></div><div class="stage"><div><div id="stage-label" class="label"></div><h3 id="stage-name"></h3><p id="stage-parts"></p><p id="stage-work"></p><div id="stage-gate" class="gate"></div><div id="stage-refs" class="refs-small"></div></div><div><h3>首个里程碑只做身体</h3><p>后端连通、参考测量完成后，先交付身体正/侧/背与手腿特写。身体比例和姿势没过关，不同时堆上衣服、帽子和包。</p><p class="muted">每一阶段保留独立 .blend、对照渲染和验证记录。修改外层不得回写破坏内层。</p></div></div></section>
<section class="panel"><h2>65 张细节图，逐件追踪</h2><p>点击查看原像素图片与建模要点。阶段筛选可检查每项结构依据，不用缩略总览代替细节图。</p><div id="filters" class="stages"></div><p id="ref-count" class="muted"></p><div id="gallery" class="gallery"></div></section>
<section class="panel"><h2>技能与工具：已发现不等于已连接</h2><table><tr><th>环节</th><th>计划与当前状态</th></tr><tr><td>参考与分件</td><td><span class="skill">reference-to-3d / source-part-segmentation</span>：本地指南已核对；先建立参考清单、部件数量与冲突记录。</td></tr><tr><td>网格与材料</td><td><span class="skill">blender-modeling</span> 等技能：作为流程依据；有机角色精修不能仅靠基础图元和自动脚本保证质量。</td></tr><tr><td>执行后端</td><td>已有 Blender 5.1.1 原生运行时。技能标准流程要求 MCP，当前未连接；实施前先验证 MCP，或明确采用原生 Python 的适配方案，不假称已接入。</td></tr><tr><td>质量门槛</td><td>正面叠图、侧背与低角度；逐层隐藏检查；对象计数、法线、碎片、接触、贴图分别验证。打印副本单独分件或融合。</td></tr></table></section>
<section class="panel"><h2>要避免重演的问题</h2><ul class="checks"><li>包下方必须是完整衣服，禁止从整人融合网格里切包后再大面积补衣服。</li><li>衣服下方必须有身体，腿不能依赖裙子补面才显得完整。</li><li>头发、帽子、眼镜、包和装饰独立命名，数量与摆放逐项对照参考。</li><li>预览优化仅在副本做；不对已验收母版全局减面或压缩。</li><li>闭合、外观相似和可打印分别验收；实际试打之前不称生产定稿。</li></ul><p><strong>当前停在规划评审。</strong>没有创建新网格，尚未安装或接通 MCP；当前 v12 已保存。</p></section>
<p class="foot">本页为 brainstorming 规划草案。推荐路线 A；请在聊天中说明确认或修改意见。详细文档与逐图追踪表位于同目录「分层重建规划_草案.md」。</p></main>
<dialog id="modal"><button class="close" onclick="document.getElementById('modal').close()">关闭</button><h3 id="modal-title"></h3><img id="modal-img" alt="细节图"><p id="modal-note"></p><p id="modal-size" class="muted"></p></dialog>
<script>const DATA=__DATA__;const asset=n=>(location.protocol==='file:'?'assets/':'/files/')+n;document.querySelectorAll('[data-asset]').forEach(x=>x.src=asset(x.dataset.asset));document.getElementById('archive').textContent=DATA.archive;
let stageIndex=0,bagHidden=false,bagMoved=false;const $=id=>document.getElementById(id);$('hide-bag').onclick=()=>{bagHidden=!bagHidden;$('diagram-bag').style.opacity=bagHidden?0:1;$('hide-bag').textContent=bagHidden?'恢复包（身体/衣服始终完整）':'演示：隐藏包'};$('separate-bag').onclick=()=>{bagMoved=!bagMoved;$('diagram-bag').style.transform=bagMoved?'translateX(70px)':'none'};
function pickRoute(el){document.querySelectorAll('.option').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');localStorage.setItem('xiaoqin-layered-route',el.dataset.choice);if(typeof window.toggleSelect==='function')window.toggleSelect(el);$('choice-status').textContent='已记录 '+el.dataset.choice+' 偏好；仍需在聊天中确认规划。'}
function openRef(id){const q=DATA.refs.find(x=>x.id===id);$('modal-title').textContent=String(q.id).padStart(2,'0')+' · '+q.name;$('modal-img').src=asset('ref-'+String(id).padStart(2,'0')+'.png');$('modal-note').textContent=q.note;$('modal-size').textContent=q.size.join(' × ')+' 原像素 · '+q.source+' · 对应阶段 '+DATA.stages.filter(s=>s.refs.includes(id)).map(s=>s.id).join('、');$('modal').showModal()}
function gallery(ids=null){const refs=ids?DATA.refs.filter(q=>ids.includes(q.id)):DATA.refs;$('ref-count').textContent='当前 '+refs.length+' 张 / 全部 65 张（规划追踪覆盖 65/65）';$('gallery').innerHTML='';for(const q of refs){const b=document.createElement('button');b.className='ref';b.innerHTML='<img loading="lazy" src="'+asset('ref-'+String(q.id).padStart(2,'0')+'.png')+'" alt="'+q.name+'"><span>'+String(q.id).padStart(2,'0')+' '+q.name+'</span><em>'+q.size.join('×')+' · '+q.source+'</em>';b.onclick=()=>openRef(q.id);$('gallery').appendChild(b)}}
function stage(i){stageIndex=i;const s=DATA.stages[i];$('stage-label').textContent='STAGE '+String(i).padStart(2,'0');$('stage-name').textContent=s.name;$('stage-parts').textContent=s.part;$('stage-work').textContent=s.work;$('stage-gate').textContent='过关条件：'+s.gate;$('stage-refs').innerHTML='';for(const id of s.refs){const b=document.createElement('button');b.textContent='细节 '+String(id).padStart(2,'0');b.onclick=()=>openRef(id);$('stage-refs').appendChild(b)}document.querySelectorAll('#stages button').forEach((b,k)=>b.classList.toggle('active',k===i))}
DATA.stages.forEach((s,i)=>{const b=document.createElement('button');b.textContent=String(i).padStart(2,'0')+' '+s.name;b.onclick=()=>stage(i);$('stages').appendChild(b)});const all=document.createElement('button');all.textContent='全部 65 张';all.onclick=()=>gallery();$('filters').appendChild(all);DATA.stages.forEach(s=>{const b=document.createElement('button');b.textContent=s.name;b.onclick=()=>gallery(s.refs);$('filters').appendChild(b)});stage(0);gallery();
</script></html>'''
html = html.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
(root/'小秦_分层重建规划.html').write_text(html,encoding='utf-8')
assert (Path(ctx['session_dir'])/'state').is_dir()
(content/'layered-design-01.html').write_text(html,encoding='utf-8')
print(json.dumps({'root':str(root),'draft':str(root/'分层重建规划_草案.md'),'coverage':len(coverage),'html':str(root/'小秦_分层重建规划.html')},ensure_ascii=False))
