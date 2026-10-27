from pathlib import Path
import sys,json,time,shutil,traceback
sys.path.insert(0,str(Path(__file__).parent/'deps'))
from gradio_client import Client,handle_file
from PIL import Image

root=Path(__file__).resolve().parent
refs=root/'references';refs.mkdir(exist_ok=True)
approved=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/小秦_小熊帽手办_斜挎包方向修正_v5.png')
with Image.open(approved) as im:
    # Extract the existing approved hero panel; no invented geometry or image edits.
    im.crop((0,0,round(im.width*.645),im.height)).save(refs/'approved-single-view.png')
manifest={'source_files':[str(approved)],'primary_view':'front-three-quarter','pipeline':'Official Tencent Hunyuan3D-2.1 image-to-3D, followed by Blender inspection','accepted_design':'Bear hat, glasses, long brown wavy hair, cream sweater, plaid skirt, waving anatomical left hand, bear bag at anatomical right hip, rear hat bow, two hair stars and two daisies','expected_primary_parts':{'count':1,'labels':['one complete figurine on its circular base']},'validation_thresholds':{'front_mask_iou_min':.90,'bbox_center_tolerance_px':12},'notes':['Hero panel is the visual source of truth. Generated side view previously had handedness inconsistency and is not a geometric constraint.','A generated mesh is a candidate until front/back render and silhouette inspection pass.']}
(root/'reference_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
try:
    c=Client('https://tencent-hunyuan3d-2-1.hf.space',verbose=False,download_files=str(root/'generated'))
    print('Submitting official Hunyuan3D-2.1 image-to-3D job',flush=True)
    job=c.submit(image=handle_file(str(refs/'approved-single-view.png')),mv_image_front=None,mv_image_back=None,mv_image_left=None,mv_image_right=None,steps=30,guidance_scale=5,seed=261018,octree_resolution=384,check_box_rembg=True,num_chunks=8000,randomize_seed=False,api_name='/generation_all')
    last=''
    while not job.done():
        status=job.status();msg=str(status)
        if msg!=last:print(msg,flush=True);last=msg
        time.sleep(8)
    result=job.result()
    (root/'generation-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print('Generation result:',json.dumps(result,ensure_ascii=False,default=str),flush=True)
except Exception as e:
    error={'type':type(e).__name__,'message':str(e)}
    (root/'generation-error.json').write_text(json.dumps(error,ensure_ascii=False,indent=2),encoding='utf-8')
    print('GENERATION_FAILED',json.dumps(error,ensure_ascii=False),flush=True)
    raise
