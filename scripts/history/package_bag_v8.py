from pathlib import Path
import shutil,base64
r=Path(__file__).resolve().parent;out=r/'bag-v8'
target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_清除旧包体_v8');target.mkdir(exist_ok=True)
template=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_圆柱小熊包_v7/小秦_可旋转三维重建.html').read_text(encoding='utf-8')
a=template.index('window.MODEL_DATA="')+len('window.MODEL_DATA="');b=template.index('";',a);template=template[:a]+base64.b64encode((out/'小秦_重建模型.glb').read_bytes()).decode()+template[b:]
template=template.replace('圆柱小熊包 v7','清除旧包体 v8').replace('包体改为短圆柱：直径11.6mm、厚3.4mm，保留新版熊脸、小熊耳与包带。几何已更新，仍需实际打印验证。','恢复主体未挤压的形状，并用精确布尔切除旧包重叠网格。新圆柱包、熊脸与尺寸保留。可打开侧面图片核对。').replace('href="bag-front.png"','href="bag-edge.png"').replace('包体正面','正侧面检查')
(target/'小秦_可旋转三维重建.html').write_text(template,encoding='utf-8')
for name in ['小秦_重建模型.glb','小秦_重建模型.blend','bag-side.png','bag-edge.png','bag-context.png','old-bag-removal-report.json','front.png','threequarter.png','back.png','小秦_120mm_打印校验版.stl','geometry-report.json','independent-stl-check.json']:shutil.copy2(out/name,target/name)
(target/'说明.txt').write_text('清除旧包体 v8\n恢复v7之前未挤压的主体，用新包范围做精确布尔差集，切除旧包重叠网格。新圆柱包、熊耳、图案和尺寸保留。\nBLEND/GLB为外观母版；STL为重新融合后的打印校验网格（毫米）。检查结果以各自报告为准，尚未完成实际试打。\n正侧面bag-edge.png、斜侧面bag-side.png用于检查旧包重叠。详见删除报告和独立STL检查。',encoding='utf-8')
print('PACKAGED_V8',target)
