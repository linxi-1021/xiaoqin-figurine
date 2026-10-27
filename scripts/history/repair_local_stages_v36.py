import bpy,numpy as np,json,sys,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_五处局部收口_v36_20261025');step=int(sys.argv[sys.argv.index('--')+1]);names={1:'01裙底',2:'02发底',3:'03发臂让位',4:'04肩腋过渡',5:'05手包轻贴'}
bpy.ops.wm.open_mainfile(filepath=str(D/'过程备份'/(names[step-1]+'.blend')));body=bpy.data.objects['textured_mesh.obj'];m=body.data;co=np.array([v.co[:] for v in m.vertices]);orig=co.copy();norm=np.array([v.normal[:] for v in m.vertices]);a=np.load('models/rebuild/closure_faces.npy');rgb=a[:,7:10];r,g,b=rgb.T;x,y,z=a[:,1:4].T
hair=(r>g*1.42)&(g>b*1.12)&(r>.025)&(g/r.clip(.001)>.12)
cloth=(r>.18)&(g>r*.55)&(b>g*.60)&(r<g*1.55)
def vids(mask):
 ids=set()
 for idx in a[mask,0].astype(int):ids.update(m.polygons[idx].vertices)
 return np.array(sorted(ids),np.int32)
def tree_for(mask):
 faces=[tuple(m.polygons[int(i)].vertices) for i in a[mask,0]]
 return BVHTree.FromPolygons([Vector(v) for v in co],faces)
def smooth_delta(ids,d,rounds=3):
 field=np.zeros_like(co);field[ids]=d;selected=np.zeros(len(co),bool);selected[ids]=True
 edges=np.array([e.vertices[:] for e in m.edges]);e=edges;deg=np.bincount(e.ravel(),minlength=len(co)).clip(1)
 for _ in range(rounds):
  acc=np.zeros_like(field);np.add.at(acc,e[:,0],field[e[:,1]]);np.add.at(acc,e[:,1],field[e[:,0]]);field[ids]=field[ids]*.5+(acc/deg[:,None])[ids]*.5
 return field[ids]
report={'stage':step}
if step==2:
 ids=vids(hair&(z>.0285)&(z<.052)&(y>.003)&(abs(x)<.029));delta=np.zeros((len(ids),3));tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());thin=[]
 for j,i in enumerate(ids):
  n=Vector(norm[i]).normalized();hit=tree.ray_cast(Vector(co[i])-n*.00003,-n,.003)
  if hit[0] is not None:
   thick=hit[3]+.00003
   if thick<.0010:delta[j]=np.array(n)*min(.00045,(.0010-thick)*.65);thin.append(thick)
 delta=smooth_delta(ids,delta,4);co[ids]+=delta
 # Recessed inner tips get only a limited thickening; outer lock directions stay intact.
 report.update({'region_vertices':len(ids),'thin_samples_before':len(thin),'minimum_ray_sample_before_mm':min(thin,default=0)*1000,'maximum_offset_mm':float(np.linalg.norm(delta,axis=1).max()*1000)})
elif step==3:
 sleeve=cloth&(x>.010)&(x<.031)&(z>.046)&(z<.066)&(y<.012)&(y>-.016);tree=tree_for(sleeve)
 ids=vids(hair&(x>.010)&(x<.031)&(z>.047)&(z<.068)&(y>-.004)&(y<.020));delta=np.zeros((len(ids),3));contacts=[]
 for j,i in enumerate(ids):
  h,n,fi,dist=tree.find_nearest(Vector(co[i]),.0018)
  if h is None:continue
  signed=(Vector(co[i])-h).dot(n);change=np.array(n)*(.00010-signed);length=np.linalg.norm(change)
  if length>.0007:change*=.0007/length
  weight=max(0,1-(dist/.0018)**2);delta[j]=change*weight;contacts.append(dist)
 delta=smooth_delta(ids,delta,4);co[ids]+=delta;report.update({'contact_vertices':len(contacts),'maximum_offset_mm':float(np.linalg.norm(delta,axis=1).max()*1000),'target_contact_offset_mm':.10})
elif step==4:
 ids=vids(cloth&(abs(x)>.007)&(abs(x)<.023)&(z>.049)&(z<.068)&(abs(y)<.012));c=co[ids];weight=np.zeros(len(ids))
 for side in [-1,1]:
  d=(c-np.array([side*.0125,.001,.060]))/np.array([.008,.011,.008]);weight=np.maximum(weight,np.clip(1-np.sum(d*d,axis=1),0,1)**2)
 # 0.55 mm controlled transition envelops the existing shoulder-sleeve join.
 delta=norm[ids]*(weight*.00055)[:,None];delta=smooth_delta(ids,delta,5);co[ids]+=delta
 report.update({'region_vertices':len(ids),'nominal_wrap_mm':.55,'maximum_actual_wrap_mm':float(np.linalg.norm(delta,axis=1).max()*1000)})
elif step==5:
 bag=cloth&(r<g*1.4)&(x<-.006)&(x>-.027)&(z>.032)&(z<.048)&(y<-.008);tree=tree_for(bag)
 skin=(r>.35)&(r>g*1.30)&(r<g*2.0)&(g>b*.95)&(g<b*1.7)
 ids=vids(skin&(x<-.013)&(x>-.032)&(z>.033)&(z<.0395)&(y>-.007)&(y<.006));delta=np.zeros((len(ids),3));contacts=[]
 for j,i in enumerate(ids):
  h,n,fi,dist=tree.find_nearest(Vector(co[i]),.0018)
  if h is None:continue
  signed=(Vector(co[i])-h).dot(n);change=np.array(n)*(-.0004-signed);length=np.linalg.norm(change)
  if length>.00045:change*=.00045/length
  weight=max(0,1-(dist/.0018)**4);delta[j]=change*weight;contacts.append(dist)
 delta=smooth_delta(ids,delta,25);co[ids]+=delta
 strap=(r>g*1.25)&(r<g*2.0)&(g>b*1.7)&(r>.15)&(x<-.017)&(x>-.027)&(z>.035)&(z<.042)&(y<.003)&(y>-.007)
 sid=vids(strap);sc=co[sid];w=np.clip(1-((sc[:,2]-.0385)/.0035)**2,0,1);sd=np.zeros((len(sid),3));sd[:,1]=.0004*w
 if len(sid):co[sid]+=smooth_delta(sid,sd,20)
 report.update({'hand_contact_vertices':len(contacts),'hand_max_offset_mm':float(np.linalg.norm(delta,axis=1).max()*1000),'nominal_contact_press_mm':.4,'strap_shift_behind_mm':.45,'strap_vertices':len(sid)})
changed=np.flatnonzero(np.linalg.norm(co-orig,axis=1)>1e-10);m.vertices.foreach_set('co',co.ravel());m.update();bm=bmesh.new();bm.from_mesh(m);report['source_boundary_edges_after']=sum(e.is_boundary for e in bm.edges);report['source_nonmanifold_after']=sum(not e.is_manifold for e in bm.edges);bm.free();report['changed_vertices']=len(changed);report['maximum_change_mm']=float(np.linalg.norm(co-orig,axis=1).max()*1000)
np.savez_compressed(D/'过程备份'/f'stage{step}_displacement.npz',ids=changed,before=orig[changed],after=co[changed]);(D/'过程备份'/f'stage{step}_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'过程备份'/(names[step]+'.blend')))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v36五处局部收口.glb'),use_selection=True,export_format='GLB')
