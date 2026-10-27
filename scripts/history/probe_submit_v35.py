import sys, time, json
from pathlib import Path

ROOT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
sys.path.insert(0, str(ROOT / 'deps'))
import httpx
from gradio_client import Client, handle_file

t0 = time.time()


def log(*a):
    print(f'[{time.time()-t0:6.1f}s]', *a, flush=True)


log('creating client')
c = Client('https://tencent-hunyuan3d-2-1.hf.space', verbose=False,
           httpx_kwargs={'timeout': httpx.Timeout(connect=30.0, read=900.0, write=900.0, pool=30.0)})
log('client ok')
log('submitting')
job = c.submit(
    image=handle_file(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\手工重建_v35_20261025\references\front.png'),
    mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
    steps=30, guidance_scale=5, seed=20261025,
    octree_resolution=384, check_box_rembg=True,
    num_chunks=8000, randomize_seed=False,
    api_name='/generation_all',
)
log('submitted', str(job.status())[:120])
