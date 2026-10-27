from pathlib import Path
import re,gzip,hashlib,base64,json
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');D=B/'3D重建_v6基础_五处局部收口_v36_20261025';S=B/'3D重建_v6基础_鞋履收敛_v35_20261025'
s=(S/'小秦_可旋转三维重建.html').read_text(encoding='utf8');raw=(D/'小秦_v36五处局部收口.glb').read_bytes();packed=gzip.compress(raw,compresslevel=4);sha=hashlib.sha256(raw).hexdigest();folder=D/('自动加载数据_'+sha[:12]);folder.mkdir(exist_ok=True);size=384*1024;count=(len(packed)+size-1)//size
for i in range(count):(folder/f'{i:04}.js').write_text(f'window.MODEL_PARTS[{i}]=Uint8Array.from(atob("'+base64.b64encode(packed[i*size:(i+1)*size]).decode()+'"),c=>c.charCodeAt(0));',encoding='ascii')
s=re.sub(r'const total=\d+;',f'const total={count};',s,count=1);s=re.sub(r'自动加载数据_[a-f0-9]+',folder.name,s)
s=re.sub(r'<title>.*?</title>','<title>小秦 · 五处局部收口 v36</title>',s,count=1)
(D/'小秦_可旋转三维重建.html').write_text(s,encoding='utf8');print('PACKED',sha,count,hashlib.sha256(gzip.decompress(packed)).hexdigest()==sha)
