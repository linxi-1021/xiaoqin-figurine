from pathlib import Path
import re,base64
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_包面匹配原棕色_20261019';D=B/'3D重建_v6基础_毛衣针织包面_20261019'
h=(S/'小秦_可旋转三维重建.html').read_text(encoding='utf8');data=base64.b64encode((D/'小秦_v6毛衣针织包面.glb').read_bytes()).decode();h,n=re.subn(r'window.MODEL_DATA\s*=\s*"[^"]*"',lambda m:'window.MODEL_DATA="'+data+'"',h,count=1);assert n==1;h=h.replace('包面匹配原棕色','毛衣针织包面').replace('包面底色匹配原有侧面的暖棕色，保留自然光影。','包面取用原毛衣的米白色与织物纹理，保留小熊五官。');(D/'小秦_可旋转三维重建.html').write_text(h,encoding='utf8');p=Path('models/rebuild/check_bag_brown.cjs').read_text(encoding='utf8').replace('3D重建_v6基础_包面匹配原棕色_20261019','3D重建_v6基础_毛衣针织包面_20261019');Path('models/rebuild/check_bag_sweater.cjs').write_text(p,encoding='utf8')
