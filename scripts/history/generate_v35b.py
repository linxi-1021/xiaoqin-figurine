import sys, json, time
from pathlib import Path

ROOT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
sys.path.insert(0, str(ROOT / 'deps'))
V35 = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025')
GEN = V35 / 'generated'
GEN.mkdir(parents=True, exist_ok=True)
from gradio_client import Client, handle_file

report = {'attempt': 'single-view, no httpx timeout'}
try:
    c = Client('https://tencent-hunyuan3d-2-1.hf.space', verbose=False,
               download_files=str(GEN), httpx_kwargs={'timeout': None})
    print('SUBMIT', flush=True)
    job = c.submit(
        image=handle_file(str(V35 / 'references' / 'front.png')),
        mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
        steps=30, guidance_scale=5, seed=20261025,
        octree_resolution=384, check_box_rembg=True,
        num_chunks=8000, randomize_seed=False,
        api_name='/generation_all',
    )
    t0 = time.time()
    last = ''
    while True:
        try:
            done = job.done()
        except Exception as e:
            print('POLL_ERR', type(e).__name__, str(e)[:120], flush=True)
            done = False
        if done:
            break
        try:
            msg = str(job.status())[:160]
            if msg != last:
                print('STATUS', msg, f'{time.time()-t0:.0f}s', flush=True)
                last = msg
        except Exception as e:
            print('STATUS_ERR', type(e).__name__, str(e)[:120], flush=True)
        if time.time() - t0 > 2700:
            raise TimeoutError('exceeded 45 min')
        time.sleep(15)
    res = job.result()
    report['ok'] = True
    report['result'] = res
    print('RESULT', json.dumps(res, ensure_ascii=False, default=str)[:1000], flush=True)
except Exception as e:
    report['ok'] = False
    report['error'] = f'{type(e).__name__}: {e}'
    print('GEN_FAILED', report['error'], flush=True)

(ROOT / 'v35-generation.json').write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding='utf8')
