from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\建模参考_局部细节图集_v1\00_整体比例')
OUT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild')
for name in ('01_正面主姿势', '02_正侧整体', '03_背面整体'):
    img = Image.open(BASE / f'{name}.png').convert('RGB')
    w, h = img.size
    d = ImageDraw.Draw(img)
    for i in range(0, 101, 5):
        y = int(h * i / 100)
        d.line([(0, y), (w, y)], fill=(0, 150, 255), width=1)
        d.text((4, min(y + 1, h - 12)), f'{i}', fill=(0, 90, 200))
    for j in range(0, 101, 10):
        x = int(w * j / 100)
        d.line([(x, 0), (x, h)], fill=(255, 90, 0), width=1)
    img.save(OUT / f'grid-{name}.png')
    print('saved', name, w, h)
