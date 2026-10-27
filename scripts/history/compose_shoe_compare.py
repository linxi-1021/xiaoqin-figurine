from pathlib import Path
from PIL import Image, ImageDraw

A = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v34-shoe-34.png')
B = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35-shoe-shoe-34.png')
OUT = Path(r'C:\Users\ASUS\Documents\ChatGPT\birth-album-maker\models\rebuild\v35\shoe-compare.png')
OUT.parent.mkdir(parents=True, exist_ok=True)

a = Image.open(A).convert('RGB')
b = Image.open(B).convert('RGB')
H = 700
a = a.resize((int(a.width * H / a.height), H), Image.LANCZOS)
b = b.resize((int(b.width * H / b.height), H), Image.LANCZOS)
pad = 20
c = Image.new('RGB', (a.width + b.width + pad * 3, H + 60), (30, 30, 32))
c.paste(a, (pad, 50))
c.paste(b, (a.width + pad * 2, 50))
d = ImageDraw.Draw(c)
d.text((pad + 4, 16), 'v34  (thick platform sole)', fill=(255, 190, 120))
d.text((a.width + pad * 2 + 4, 16), 'v35  (original shoe + subtle straps)', fill=(150, 220, 255))
c.save(OUT)
print('saved', OUT)
