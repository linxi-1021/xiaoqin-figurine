from pathlib import Path
import numpy as np,json
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_双手五指重建_20261019');a=np.load(D/'original-uv-mesh.npz');uv=a['uv'].reshape(-1,4,2);vi=a['vi'].reshape(-1,4);points,inv=np.unique(np.round(uv.reshape(-1,2),7),axis=0,return_inverse=True);ids=inv.reshape(-1,4);edges=np.concatenate([ids[:,[0,1]],ids[:,[1,2]],ids[:,[2,3]],ids[:,[3,0]]]);graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(points),len(points)));n,labels=connected_components(graph,directed=False);fl=labels[ids[:,0]];seeds=json.loads((D/'chart-seeds.json').read_text());out={}
for k,v in seeds.items():
 lab=int(fl[v['face']]);sel=fl==lab;c=a['co'][vi[sel]].reshape(-1,3);out[k]={'chart':lab,'faces':int(sel.sum()),'min':c.min(0).tolist(),'max':c.max(0).tolist()}
print(json.dumps(out,indent=2));np.save(D/'uv-chart-labels.npy',fl);(D/'uv-chart-summary.json').write_text(json.dumps(out,indent=2))
