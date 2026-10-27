import sys, json, time
from pathlib import Path
from PIL import Image

ROOT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
sys.path.insert(0, str(ROOT / 'deps'))
V35 = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025')
REF = V35 / 'references'
OUT = V35 / 'generated'
REF.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# 主视图：v5 左侧主画面
src = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\小秦_小熊帽手办_斜挎包方向修正_v5.png')
with Image.open(src) as im:
    w, h = im.size
    im.crop((0, 0, round(w * 0.645), h)).save(REF / 'front.png')
# 背面
back = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\建模参考_局部细节图集_v1\00_整体比例\03_背面整体.png')
Image.open(back).convert('RGB').save(REF / 'back.png')

from gradio_client import Client, handle_file

report = {}
try:
    c = Client('https://tencent-hunyuan3d-2-1.hf.space', verbose=False, download_files=str(OUT))
    print('SUBMIT', flush=True)
    job = c.submit(
        image=handle_file(str(REF / 'front.png')),
        mv_image_front=handle_file(str(REF / 'front.png')),
        mv_image_back=handle_file(str(REF / 'back.png')),
        mv_image_left=None,
        mv_image_right=None,
        steps=30, guidance_scale=5, seed=20261025,
        octree_resolution=384, check_box_rembg=True,
        num_chunks=8000, randomize_seed=False,
        api_name='/generation_all',
    )
    last = ''
    t0 = time.time()
    while not job.done():
        msg = str(job.status())
        if msg != last:
            print('STATUS', msg, f'{time.time()-t0:.0f}s', flush=True)
            last = msg
        time.sleep(10)
        if time.time() - t0 > 1800:
            raise TimeoutError('generation exceeded 30 min')
    res = job.result()
    report = {'ok': True, 'result': res}
    print('RESULT', json.dumps(res, ensure_ascii=False, default=str)[:800], flush=True)
except Exception as e:
    report = {'ok': False, 'error': f'{type(e).__name__}: {e}'}
    print('GEN_FAILED', report['error'], flush=True)

(ROOT / 'v35-generation.json').write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding='utf8')
