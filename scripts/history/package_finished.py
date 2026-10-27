from pathlib import Path
import shutil,json
r=Path(__file__).resolve().parent
src=(r/'package_review.py').read_text(encoding='utf-8')
src=src.replace("o=r/'review'","o=r/'finished'").replace('3D重建_参考图生成版','3D重建_结构校验版_v3').replace("script=(o/'viewer.bundle.js')","script=(r/'review'/'viewer.bundle.js')")
src=src.replace('三维重建检查版','三维结构校验版 v3').replace('待修：帽后蝴蝶结、花星发饰缺失；手指和发丝需精修。此版用于外观检查，尚未完成打印结构校验。','已封闭飘带开口、调整装饰贴合并柔化网格。含独立毫米单位 STL 与网格报告。尚需指定工艺后的薄弱部位校验及试打。')
src=src.replace('已知问题：背饰缺失，手指和发丝粗糙，眼镜融合','已处理：背饰、曲面平滑、飘带封口、装饰贴合。待确认：手指和眼镜的造型分离、打印工艺与实际试打').replace("'back.png','side.png'","'back.png','backthreequarter.png','side.png'")
exec(compile(src,str(r/'package_review.py'),'exec'))
for name in ['小秦_120mm_打印校验版.stl','geometry-report.json']:shutil.copy2(r/'finished'/name,target/name)
(target/'说明.txt').write_text('小秦三维结构校验版 v3\nGLB/BLEND：带纹理外观母版，尺寸单位米。\nSTL：独立融合打印网格，数值单位毫米，目标高度约120mm。STL不含颜色，格纹和眼睛为上色参考。\n本轮：飘带封口，装饰下沉贴合，曲面细分，打印体素融合。\n尚未达到生产定稿：手指与眼镜仍需局部造型确认；尚未指定打印材料、完成最薄处验证、支撑切片和实际试打。\n请勿把纹理母版直接当作打印文件。详见geometry-report.json。',encoding='utf-8')
