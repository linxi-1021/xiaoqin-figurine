from pathlib import Path
r=Path(__file__).resolve().parent
src=(r/'package_review.py').read_text(encoding='utf-8')
src=src.replace("o=r/'review'","o=r/'refined'").replace('3D重建_参考图生成版','3D重建_精修版_v2').replace("script=(o/'viewer.bundle.js')","script=(r/'review'/'viewer.bundle.js')")
src=src.replace('三维重建检查版','三维精修版 v2').replace('待修：帽后蝴蝶结、花星发饰缺失；手指和发丝需精修。此版用于外观检查，尚未完成打印结构校验。','已补帽后蝴蝶结、星星吊饰、两颗发星与两朵小花；已清理接缝并柔化表面。手指、眼镜仍需后续结构精修，尚未完成打印校验。')
src=src.replace('已知问题：背饰缺失，手指和发丝粗糙，眼镜融合','精修内容：新增帽后蝴蝶结与星星吊饰、两颗发星及两朵小花；焊接重复顶点并轻度平滑，改善表面反光。；已知问题：手指与眼镜仍有融合').replace("'back.png','side.png'","'back.png','backthreequarter.png','side.png'")
exec(compile(src,str(r/'package_review.py'),'exec'))

