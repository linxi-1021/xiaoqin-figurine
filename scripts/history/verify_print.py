from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'tooling'))
import trimesh,numpy as np
p=r/'finished/小秦_120mm_打印校验版.stl'
m=trimesh.load_mesh(p,process=True)
report={'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'dimensions_mm':m.extents.tolist(),'volume_ml':float(m.volume/1000),'connected_components':len(trimesh.graph.connected_components(m.face_adjacency,nodes=np.arange(len(m.faces)))),'center_of_mass_mm':m.center_mass.tolist(),'degenerate_faces':int(np.sum(m.area_faces<1e-10))}
assert report['watertight'] and report['winding_consistent'] and report['positive_volume'] and report['connected_components']==1,report
(r/'finished/independent-stl-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))

