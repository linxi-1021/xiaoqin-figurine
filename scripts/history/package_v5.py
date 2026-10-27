from pathlib import Path
import shutil,json
r=Path(__file__).resolve().parent
src=(r/'package_review.py').read_text(encoding='utf-8')
src=src.replace("o=r/'review'","o=r/'detail-v5'").replace('3D重建_参考图生成版','3D重建_参考细节修正版_v5')
src=src.replace('三维重建检查版','三维参考细节修正版 v5').replace('待修：帽后蝴蝶结、花星发饰缺失；手指和发丝需精修。此版用于外观检查，尚未完成打印结构校验。','按局部参考重建扁平缎带蝴蝶结，调整星夹曲面贴合及花瓣方向，补眼镜内缘浅沟。保留v4手部。尚未完成独立眼镜分件与试打。')
src=src.replace("'back.png','side.png'","'back.png','backthreequarter.png','side.png'")
exec(compile(src,str(r/'package_review.py'),'exec'))
for name in ['bow-detail.png','reference-changes.json','小秦_120mm_打印校验版.stl','geometry-report.json','independent-stl-check.json']:shutil.copy2(r/'detail-v5'/name,target/name)
shutil.copy2(r/'detail-v4/back.png',target/'back-before-v4.png')
(target/'参考图到模型修改对照.md').write_text('''# v5 参考图到模型修改对照

采用65张局部图中的对应部件作为造型参考，没有重新生成角色。

| 参考编号 | 对照部件 | 本轮几何修改 |
|---|---|---|
| 51、52 | 蝴蝶结与中心褶皱 | 替换旧圆管圈；重建两片宽缎带瓣、中心收拢褶皱与圆角包裹结 |
| 53 | 尾带与吊星 | 改为两片封闭扁带并贴合帽面；吊星保留并重新贴合 |
| 55、56 | 后发星夹 | 校正旧版背饰镜像位置，并按每个顶点的实际帽/发曲面调整深度，减少单边埋入与悬浮 |
| 57、58 | 五瓣花 | 校正旧版镜像位置，每片花瓣按花心方向旋转、重新定位到局部发面；保留两朵花 |
| 12—15 | 眼镜与镜桥 | 沿现有内框边缘补浅沟，增强灰模层次；没有改变眼距、脸型，也未独立分件 |
| 26、27 | 手部 | 保留v4的三道指沟和两道掌纹 |

## 检查和限制
BLEND为高精度外观母版；GLB为网页预览；STL为同步更新的融合打印网格，单位毫米。顶点贴合不代表已完成壁厚和强度认证。眼镜仍为一体浮雕结构，未完成真实树脂试打及设备切片。此版为参考细节修正版，不能声称生产定稿。

未在本轮修改的部位：包带与包体、服装褶皱、鞋、主体发束、角色站姿。避免把“对照检查”描述成已经重做。
''',encoding='utf-8')
(target/'说明.txt').write_text('v5：请阅读《参考图到模型修改对照.md》。本轮已按局部图修改蝴蝶结、背饰和眼镜内缘，保留v4手部与原主体。STL单位毫米；尚需薄弱部位复核、切片及试打。',encoding='utf-8')
print('PACKAGED_V5',target)
