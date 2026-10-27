import sys, json, time
from pathlib import Path

ROOT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
sys.path.insert(0, str(ROOT / 'deps'))
import httpx
from gradio_client import Client, handle_file

V35 = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025')
GEN = V35 / 'generated'
GEN.mkdir(parents=True, exist_ok=True)
LOG = ROOT / 'v35-gen.log'
LOG.write_text('', encoding='utf8')


def log(*a):
    line = f'[{time.strftime("%H:%M:%S")}] ' + ' '.join(str(x) for x in a)
    print(line, flush=True)
    with LOG.open('a', encoding='utf8') as f:
        f.write(line + '\n')


t0 = time.time()
try:
    log('creating client')
    c = Client('https://tencent-hunyuan3d-2-1.hf.space', verbose=False, download_files=str(GEN),
               httpx_kwargs={'timeout': httpx.Timeout(connect=30.0, read=900.0, write=900.0, pool=30.0)})
    log('client ok')
    job = c.submit(
        image=handle_file(str(V35 / 'references' / 'front.png')),
        mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
        steps=30, guidance_scale=5, seed=20261025,
        octree_resolution=384, check_box_rembg=True,
        num_chunks=8000, randomize_seed=False,
        api_name='/generation_all',
    )
    log('submitted')
    last = ''
    while True:
        try:
            if job.done():
                break
        except Exception as e:
            log('POLL_ERR', type(e).__name__, str(e)[:100])
        try:
            s = str(job.status())[:120]
            if s != last:
                log('STATUS', s)
                last = s
        except Exception as e:
            log('STATUS_ERR', type(e).__name__, str(e)[:100])
        if time.time() - t0 > 2700:
            raise TimeoutError('exceeded 45 min')
        time.sleep(20)
    res = job.result()
    log('RESULT', json.dumps(res, ensure_ascii=False, default=str)[:1200])
    (ROOT / 'v35-generation.json').write_text(json.dumps({'ok': True, 'result': res}, ensure_ascii=False, indent=1, default=str), encoding='utf8')
except Exception as e:
    log('GEN_FAILED', f'{type(e).__name__}: {e}')
    (ROOT / 'v35-generation.json').write_text(json.dumps({'ok': False, 'error': f'{type(e).__name__}: {e}'}, ensure_ascii=False, indent=1), encoding='utf8')
