# 小秦 · 小熊帽手办资料库

整理日期：2026-10-27。当前收录模型为 **v38：后背粗发束收细（2026-10-26）**。

![外观参考](design/小秦_手办三视外观参考_v1.png)

## 资料导航

| 目录 | 内容 |
| --- | --- |
| `design/` | 建模交接说明、三视外观参考、v1–v5 效果图 |
| `design/details/` | 原始局部细节参考图集 |
| `model/v38/` | 可编辑 Blender 文件、GLB、自动加载预览及对照图、原始校验记录 |
| `scripts/history/` | 历史建模、打包与检查脚本；多数使用原机器绝对路径，运行前需调整 |
| `docs/version-index.json` | 原始各版本目录及顶层模型/校验文件索引 |
| `docs/source-manifest.json` | 收录文件来源、字节数和 SHA-256 |
| `docs/package-verification.json` | 本次整理的完整性与预览数据校验结果 |

## 查看和编辑

克隆或下载整个仓库后，打开 `model/v38/粗发束收细对照.html` 查看前后对照；打开同目录 `小秦_可旋转三维重建.html` 查看可旋转模型。必须保留 `自动加载数据_6b52891b3f9e/` 分块文件夹。预览按原实现自动载入模型；GitHub 文件页只展示源码，不直接运行三维页面。

使用 Blender 打开 `model/v38/小秦_v38后背粗发束收细.blend` 编辑，也可将同名 GLB 导入三维软件。大文件使用普通 Git 保存，初次克隆需要下载完整模型与预览数据。

## 设计与验收状态

目标为含底座约 120 mm 的树脂手办，人物约 114 mm、底座约 6 mm，均为设计目标，需打样确认。具体人物造型、左右方向、斜挎包位置及分件建议见 `design/小秦_手办建模交接说明_v1.md`。该说明保留早期设计阶段措辞，当前已存在三维网格。

v38 基于 v36 对既有后发束做横向收细，替代 v37 的表面刻槽方案。原始校验报告记载：非头发几何、接触修复区域及材质纹理保留，反向三角形诊断为 0；同时继承了 308 条边界边和 308 条非流形边，`inherited_v36_production_acceptance` 为 false。因此当前归档不代表已经通过闭合性、壁厚、拆件装配或实体打印验收。

原始浏览器校验记录报告自动导入成功、无文件选择器、解压模型 SHA 与 GLB 一致，页面与控制台无错误；这是原有记录，本次另行核验文件与分块数据的一致性。

## 版本与归档范围

桌面原 `小秦_最新三维预览.html` 实际仍指向 v33；本仓库直接提供 v38 入口，未使用该旧入口。历史源模型、过程备份、旧自动加载分块保留在原目录，本次以版本索引记录，避免与 v38 混用。v35 从零重建方案与 v34/v35 计划是历史方案，不表示已按方案完成。

未收录相册、宠物动画、Python 运行环境及第三方依赖缓存。原始文件保持不动；归档预览仅补齐了帽子参考图片依赖。本仓库未新增开放源代码或素材授权，第三方资源沿用各自权利归属。

## 三维建模 Skills

本项目使用的三维技能包为 [RobLe3/cc-blender-skill](https://github.com/RobLe3/cc-blender-skill)，本机归档版本 **v1.4.0**，源码提交 [`a2634b5`](https://github.com/RobLe3/cc-blender-skill/tree/a2634b588e80265e796aa53f8ab178d75105c2af)，采用 MIT 许可。

核对历史建模聊天的技能读取记录及 [`build_layered_plan.py`](scripts/history/build_layered_plan.py) 后，可确认下表中 **9 项有读取或参考记录**。为完整展示三维技能包能力，同时列出其余 21 项；“技能包提供”表示可用能力，不能据此认定本手办实际调用过。

| Skill（链接至对应说明） | 用途 | 项目记录 |
| --- | --- | --- |
| [`text-to-blender`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/text-to-blender/SKILL.md) | 自然语言任务入口与子技能调度 | 技能包提供，未确认使用 |
| [`blender-skill-harmonizer`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-skill-harmonizer/SKILL.md) | 多技能协调、约束优先级与任务交接 | 技能包提供，未确认使用 |
| [`quality-refinement-autoloop`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/quality-refinement-autoloop/SKILL.md) | 诊断建模质量问题、迭代修正并校验 | 已读取／参考 |
| [`blender-pro-workflow`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-pro-workflow/SKILL.md) | 建模阶段划分、场景装配顺序与评审流程 | 已读取／参考 |
| [`blender-modeling`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-modeling/SKILL.md) | 网格创建、曲线、修改器与局部几何编辑 | 已读取／参考 |
| [`blender-materials`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-materials/SKILL.md) | 角色、服装、帽子和配件的材质设置 | 已读取／参考 |
| [`blender-lighting`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-lighting/SKILL.md) | 灯光、HDRI 与展示照明 | 技能包提供，未确认使用 |
| [`blender-cameras`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-cameras/SKILL.md) | 相机、构图、焦距与观察角度 | 技能包提供，未确认使用 |
| [`blender-rendering`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-rendering/SKILL.md) | 渲染器、采样、降噪与色彩管理 | 技能包提供，未确认使用 |
| [`blender-animation`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-animation/SKILL.md) | 关键帧、曲线、形态键与动作组织 | 技能包提供，未确认使用 |
| [`blender-export`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-export/SKILL.md) | 导出 GLB/glTF、STL 等格式及目标平台检查 | 已读取／参考 |
| [`wireframe-to-3d`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/wireframe-to-3d/SKILL.md) | 正交线框图转曲线、网格与三维模型 | 技能包提供，未确认使用 |
| [`reference-to-3d`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/reference-to-3d/SKILL.md) | 依据参考图锁定比例、外观和重建约束 | 已读取／参考 |
| [`blender-uv-texturing`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/blender-uv-texturing/SKILL.md) | UV、贴图投射、贴花与纹理烘焙 | 已读取／参考 |
| [`reference-analysis-validator`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/reference-analysis-validator/SKILL.md) | 参考素材清单、轮廓分析和叠图一致性检查 | 已读取／参考 |
| [`contour-to-mesh`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/contour-to-mesh/SKILL.md) | 从二维轮廓或遮罩生成网格 | 技能包提供，未确认使用 |
| [`orthographic-registration`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/orthographic-registration/SKILL.md) | 正面、侧面、背面等参考视图配准 | 技能包提供，未确认使用 |
| [`multiview-constraint-solver`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/multiview-constraint-solver/SKILL.md) | 检查多视图约束冲突并确定参考优先级 | 技能包提供，未确认使用 |
| [`atlas-uv-fitting`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/atlas-uv-fitting/SKILL.md) | 图集区域识别及对应部件 UV 拟合 | 技能包提供，未确认使用 |
| [`closed-surface-uv-coverage`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/closed-surface-uv-coverage/SKILL.md) | 检查封闭模型正面、背面和侧壁的贴图覆盖 | 技能包提供，未确认使用 |
| [`mascot-logo-reconstruction`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/mascot-logo-reconstruction/SKILL.md) | 参考约束的吉祥物或标识重建总流程 | 技能包提供，未确认使用 |
| [`multiview-fit-loop`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/multiview-fit-loop/SKILL.md) | 多视图渲染、对照和调整闭环 | 技能包提供，未确认使用 |
| [`fit-repair-optimizer`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/fit-repair-optimizer/SKILL.md) | 依据校验失败项组织修复顺序与依赖 | 技能包提供，未确认使用 |
| [`reference-look-calibration`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/reference-look-calibration/SKILL.md) | 参考图颜色、材质、灯光和渲染外观标定 | 技能包提供，未确认使用 |
| [`source-part-segmentation`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/source-part-segmentation/SKILL.md) | 按结构部件分割参考图、遮罩及遮挡关系 | 已读取／参考 |
| [`texture-driven-mesh-fitting`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/texture-driven-mesh-fitting/SKILL.md) | 让网格边界拟合纹理和参考轮廓 | 技能包提供，未确认使用 |
| [`landmark-fit-repair`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/landmark-fit-repair/SKILL.md) | 五官、尖端、转角等关键点校验与修正 | 技能包提供，未确认使用 |
| [`texture-state-animation`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/texture-state-animation/SKILL.md) | 分层贴图、材质状态动画与导出检查 | 技能包提供，未确认使用 |
| [`orbital-hud-motion`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/orbital-hud-motion/SKILL.md) | 环形、轨道和 HUD 动效 | 技能包提供，未确认使用 |
| [`animation-quality-gate`](https://github.com/RobLe3/cc-blender-skill/blob/a2634b588e80265e796aa53f8ab178d75105c2af/plugin/skills/animation-quality-gate/SKILL.md) | 动画接触表、轮廓稳定性与导出质量检查 | 技能包提供，未确认使用 |

### 建模执行方式

上述 Skills 提供建模与验证流程。历史规划明确记录：当时没有已连接的 Blender MCP；实际模型修改使用本地 **Blender 5.1.1 + 原生 Python / `bpy` 脚本**，预览打包和浏览器检查另有 Python、Node.js 脚本。读取技能不等于执行了其全部步骤，也不代表已通过实体制作验收。

### 建模过程中的辅助 Skills

| Skill | 历史用途 |
| --- | --- |
| `brainstorming` | 梳理参考、分层重建路线和造型修改要求。 |
| `writing-plans` | 编写分阶段建模计划与验收条件。 |
| `subagent-driven-development` | 历史建模任务的子任务组织。 |
| `systematic-debugging` | 定位绒毛越界、底座凸边等几何问题。 |
| `verification-before-completion` | 交付前检查模型、预览与校验结果。 |

### 本次资料整理与上传使用的 Skills

| Skill | 用途 |
| --- | --- |
| `using-superpowers` | 检查适用技能并组织工作流程。 |
| `verification-before-completion` | 核验文件 SHA-256、Git 文件内容、预览链接、模型分块解压结果及远程提交。 |
| `web-access` | 参考联网操作说明；GitHub 上传通过 Git 和 GitHub CLI（`gh`）执行。 |

无需安装这些 Skills 即可查看仓库资料或打开现有模型。上表技能包清单依据本机 manifest；使用状态依据可检索到的历史记录，未将技能包中的全部能力都归为本项目实际使用。
