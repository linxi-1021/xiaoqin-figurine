from pathlib import Path
import json,shutil,zipfile
r=Path(__file__).resolve().parent;out=r/'finished';t=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_结构校验版_v3')
check=json.loads((out/'independent-stl-check.json').read_text())
for name in ['independent-stl-check.json','thickness-screening.json','reinforcement.json','print-back.png','hand-detail.png']:shutil.copy2(out/name,t/name)
report=json.loads((out/'geometry-report.json').read_text());report['dimensions_mm']=check['dimensions_mm'];report['volume_mm3']=check['volume_ml']*1000;report['post_reinforcement_independent_check']=check
(t/'geometry-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(t/'树脂手办交接说明.md').write_text(f'''# 小秦 12cm 树脂手办：结构校验交接版

## 文件用途
- 小秦_重建模型.blend / .glb：带纹理外观母版，可继续雕刻。单位为米。
- 小秦_120mm_打印校验版.stl：融合实心网格，数值单位为毫米。高度 {check['dimensions_mm'][2]:.2f} mm。
- HTML：离线旋转查看外观，可切换灰模。该灰模是外观母版，不等同于打印 STL；打印网格另有 print-back.png。

## 已完成
- 补充帽后蝴蝶结、吊星、两颗发星和两朵小花。
- 飘带末端封口，装饰贴合，加密曲面并平滑表面。
- 独立融合打印网格，对蝴蝶结一处薄弱接触区域局部加固。
- 导出后通过独立 trimesh 检查：闭合、法线绕序一致、正体积、单一连通实体、无退化面。
- 实心净体积约 {check['volume_ml']:.1f} mL，不含支撑和打印损耗。

## 未通过的定稿关卡
- 手指间沟槽偏浅，眼镜与脸仍为一体浮雕式结构；尚未完成独立分件雕刻，不能声称造型已全部定稿。
- 厚度射线筛查是抽样检查，不是全表面最小壁厚证明，细小边缘仍需切片及实物验证。
- 未指定具体打印机、树脂型号与曝光配置，未生成设备专用切片和支撑文件。
- 未进行真实试打，尚不能签署生产定稿。

## 制作交接
按约12cm树脂光固化用途准备，保留实心方案。请工作室先导入毫米单位 STL 检查尺寸，决定摆放角度、支撑位置与接触点，按实际设备/树脂参数切片并小批试打。重点检查指尖、帽耳、飘带、发梢和包带。若改为空心，必须另做排液/通气结构并验证，不直接掏空交付。

眼睛、腮红、格纹属于纹理/上色参考，普通树脂打印不会自动产生彩色。此交付包属于结构校验版，不以“生产定稿”命名。
''',encoding='utf-8')
z=t.parent/'小秦_树脂手办_结构校验交付_v3.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as f:
 for p in t.iterdir():
  if p.is_file():f.write(p,p.name)
print('DELIVERED',t)
