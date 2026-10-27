from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
r=Path(__file__).resolve().parent;out=r/'bag-v6';out.mkdir(exist_ok=True)
src=(r/'paint_bag_v6.py').read_text(encoding='utf-8')
a=src.index('# A procedural');b=src.index('texture=bpy.data.images.load')
exec(src[a:b])
src=src.replace('from PIL import Image,ImageDraw,ImageFilter\n','').replace(src[a:b],"texpath=out/'小熊包_清晰五官图案.png'\n")
(r/'paint_bag_v6_blender.py').write_text(src,encoding='utf-8')
print('TEXTURE_READY',texpath)
