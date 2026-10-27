from pathlib import Path
import base64,shutil,json
r=Path(__file__).resolve().parent;o=r/'review'
target=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_参考图生成版');target.mkdir(exist_ok=True)
model=base64.b64encode((o/'小秦_重建模型.glb').read_bytes()).decode()
script=(o/'viewer.bundle.js').read_text(encoding='utf-8')
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>小秦 · 三维重建检查版</title><style>body{margin:0;color:#eee;font:15px system-ui}aside{position:fixed;top:20px;left:20px;max-width:360px;padding:20px;background:#18191ddd;border-radius:16px}h1{font-size:22px;margin:0 0 10px}p{line-height:1.7;color:#c1c4ce}button{padding:9px 14px;margin:5px 4px 0 0;border:0;border-radius:8px;cursor:pointer}small{display:block;margin-top:12px;color:#c1c4ce}</style><aside><h1>小秦 · 三维重建检查版</h1><p id="status">正在加载真实网格…</p><button id="gray">纹理 / 灰模</button><button id="rotate">自动旋转</button><button id="reset">重置视角</button><small>待修：帽后蝴蝶结、花星发饰缺失；手指和发丝需精修。此版用于外观检查，尚未完成打印结构校验。</small></aside><script>window.MODEL_DATA="'''+model+'";</script><script>'+script+'</script></html>'
(target/'小秦_可旋转三维重建.html').write_text(html,encoding='utf-8')
for name in ['小秦_重建模型.glb','小秦_重建模型.blend','front.png','back.png','side.png','threequarter.png']:shutil.copy2(o/name,target/name)
(target/'说明.txt').write_text('参考图重建检查版\n生成：腾讯官方 Hunyuan3D-2.1；检查与源文件：Blender 5.1.1。\n模型高约120mm。HTML可直接双击离线旋转，切换灰模查看几何。\n已知问题：背饰缺失，手指和发丝粗糙，眼镜融合，尚未通过打印闭合性、壁厚、分件结构校验。\n旧灰模及旧交付包已移入回收站，保留已确认设计图。',encoding='utf-8')
print(target)
