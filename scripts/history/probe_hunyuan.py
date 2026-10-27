import sys, json, time
from pathlib import Path

ROOT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
sys.path.insert(0, str(ROOT / 'deps'))

report = {'step': 'probe'}
try:
    from gradio_client import Client
    c = Client('https://tencent-hunyuan3d-2-1.hf.space', verbose=False)
    report['connected'] = True
    info = c.view_api(return_format='dict', print_info=False)
    named = info.get('named_endpoints', {}) if isinstance(info, dict) else {}
    report['named_endpoints'] = sorted(named.keys())
    gen = named.get('/generation_all', {})
    params = [p.get('parameter_name') for p in gen.get('parameters', [])]
    report['generation_all_params'] = params
except Exception as e:
    report['connected'] = False
    report['error'] = f'{type(e).__name__}: {e}'

print(json.dumps(report, ensure_ascii=False, indent=1))
