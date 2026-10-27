import sys, json, time
from pathlib import Path

ROOT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
sys.path.insert(0, str(ROOT / 'deps'))
import httpx
from gradio_client import Client, handle_file

V35 = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025')
GEN = V35 / 'generated'
GEN.mkdir(parents=True, exist_ok=True)

report = {'attempt': 'single view, explicit httpx timeouts'}
t0 = time.time()
try:
    c = Client('https://tencent-hunyuan3d-2-1.hf.space', verbose=False, download_files=str(GEN),
               httpx_kwargs={'timeout': httpx.Timeout(connect=30.0, read=900.0, write=900.0, pool=30.0)})
    print('CLIENT_OK', f'{time.time()-t0:.0f}s', flush=True)
    job = c.submit(
        image=handle_file(str(V35 / 'references' / 'front.png')),
        mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
        steps=30, guidance_scale=5, seed=20261025,
        octree_resolution=384, check_box_rembg=True,
        num_chunks=8000, randomize_seed=False,
        api_name='/generation_all',
    )
    print('SUBMITTED', flush=True)
    last = ''
    while True:
        try:
            done = job.done()
        except Exception as e:
            print('POLL_ERR', type(e).__name__, str(e)[:100], flush=True)
            done = False
        if done:
            break
        try:
            s = str(job.status())[:140]
            if s != last:
                print('STATUS', s, f'{time.time()-t0:.0f}s', flush=True)
                last = s
        except Exception as e:
            print('STATUS_ERR', type(e).__name__, str(e)[:100], flush=True)
        if time.time() - t0 > 2700:
            raise TimeoutError('exceeded 45 min')
        time.sleep(20)
    res = job.result()
    report.update(ok=True, result=res)
    print('RESULT', json.dumps(res, ensure_ascii=False, default=str)[:1200], flush=True)
except Exception as e:
    report.update(ok=False, error=f'{type(e).__name__}: {e}')
    print('GEN_FAILED', report['error'], flush=True)

(ROOT / 'v35-generation.json').write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding='utf8')
