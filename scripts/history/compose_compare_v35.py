from pathlib import Path
from PIL import Image, ImageDraw

REF = Path(r'D:\Desktop\相册\二维IP制作_20261012\手办设计\建模参考_局部细节图集_v1\00_整体比例\01_正面主姿势.png')
BO = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35\hair2-front.png')
OUT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35\compare-front-hair2.png')

H = 1100
ref = Image.open(REF).convert('RGB')
bo = Image.open(BO).convert('RGB')
ref = ref.resize((int(ref.width * H / ref.height), H), Image.LANCZOS)
bo = bo.resize((int(bo.width * H / bo.height), H), Image.LANCZOS)
pad = 30
canvas = Image.new('RGB', (ref.width + bo.width + pad * 3, H + 80), (32, 32, 34))
canvas.paste(ref, (pad, 60))
canvas.paste(bo, (ref.width + pad * 2, 60))
d = ImageDraw.Draw(canvas)
d.text((pad + 6, 18), 'REFERENCE (v5)', fill=(255, 220, 160))
d.text((ref.width + pad * 2 + 6, 18), 'HAIR v2', fill=(160, 220, 255))
for i in range(0, 101, 10):
    y = 60 + int(H * i / 100)
    d.line([(pad, y), (canvas.width - pad, y)], fill=(0, 120, 180), width=1)
    d.text((2, y - 5), str(i), fill=(150, 190, 210))
canvas.save(OUT)
print('saved', OUT, canvas.size)
