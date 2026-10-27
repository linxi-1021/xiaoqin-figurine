from pathlib import Path
import shutil,json
r=Path(__file__).resolve().parent
src=(r/'package_review.py').read_text(encoding='utf-8')
src=src.replace("o=r/'review'","o=r/'detail-v4'").replace('3D重建_参考图生成版','3D重建_局部雕刻版_v4')
src=src.replace('三维重建检查版','三维局部雕刻版 v4').replace('待修：帽后蝴蝶结、花星发饰缺失；手指和发丝需精修。此版用于外观检查，尚未完成打印结构校验。','新增三道指部沟槽和两道掌纹，保持手指根部连接。点击下方按钮检查局部。眼镜仍是一体浮雕结构，尚未完成试打定稿。')
src=src.replace("'back.png','side.png'","'back.png','backthreequarter.png','side.png'")
exec(compile(src,str(r/'package_review.py'),'exec'))
for name in ['hand-before.png','hand-after.png','face-before.png','sculpt-changes.json','小秦_120mm_打印校验版.stl','geometry-report.json','independent-stl-check.json']:shutil.copy2(r/'detail-v4'/name,target/name)
(target/'说明.txt').write_text('v4 局部雕刻版\n本轮重点：依据正交放大图刻出三道指部沟槽和两道掌纹，柔化沟槽边缘。手指根部保留连接；不是独立分指模型。\nBLEND为高精度母版；GLB为精简后的网页预览。STL同步更新手部造型并进行体素融合，单位毫米。\n本轮未对眼镜作独立分件重建，它仍是贴脸浮雕结构。仍需局部造型确认、薄弱部位和切片支撑检查及实际试打，不能视为生产定稿。\n对比图hand-before.png和hand-after.png为相同相机、灯光和灰色材质，可直接比较几何变化。',encoding='utf-8')
print('PACKAGED_V4',target)
