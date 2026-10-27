import json
from pathlib import Path
import numpy as np
from PIL import Image

BASE = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计')
REF = BASE / '建模参考_局部细节图集_v1'
OUT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\ref-measure.json')

files = {
    'front': REF / '00_整体比例' / '01_正面主姿势.png',
    'side': REF / '00_整体比例' / '02_正侧整体.png',
    'back': REF / '00_整体比例' / '03_背面整体.png',
    'three': BASE / '小秦_手办三视外观参考_v1.png',
}

result = {}
for key, path in files.items():
    img = Image.open(path).convert('RGB')
    a = np.asarray(img).astype(np.int16)
    h, w, _ = a.shape
    # 背景取四角中位色
    corners = np.concatenate([a[0:8, 0:8].reshape(-1, 3), a[0:8, -8:].reshape(-1, 3),
                              a[-8:, 0:8].reshape(-1, 3), a[-8:, -8:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    diff = np.abs(a - bg).sum(axis=2)
    mask = diff > 26
    # 去掉边缘零星像素
    ys, xs = np.where(mask)
    if len(ys) == 0:
        continue
    top, bottom = ys.min(), ys.max()
    left, right = xs.min(), xs.max()
    H = bottom - top + 1
    W = right - left + 1
    rows = []
    for frac in np.arange(0, 1.0001, 0.02):
        y = int(round(top + frac * (H - 1)))
        row = np.where(mask[y])[0]
        if len(row) == 0:
            rows.append((round(float(frac), 3), 0, 0.0, 0.0))
            continue
        rows.append((round(float(frac), 3), int(len(row)),
                     round(float((row.min() - left) / W), 3),
                     round(float((row.max() - left) / W), 3)))
    result[key] = {
        'file': str(path), 'size': [w, h], 'bbox': [int(left), int(top), int(right), int(bottom)],
        'figure_w': int(W), 'figure_h': int(H), 'aspect': round(W / H, 4),
        'bg': [int(v) for v in bg],
        'rows': rows,
    }

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf8')
for k, v in result.items():
    print(k, 'size', v['size'], 'bbox', v['bbox'], 'w/h', v['figure_w'], v['figure_h'], 'aspect', v['aspect'])
