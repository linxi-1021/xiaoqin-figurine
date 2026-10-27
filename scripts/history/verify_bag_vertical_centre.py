import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
D=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_包脸上下居中_20261019');bpy.ops.wm.open_mainfile(filepath=str(D/'小秦_v6包脸上下居中.blend'));j=json.loads((D/'表面坐标与投影校验.json').read_text(encoding='utf-8'));C,N,U,V=[Vector(j[x]) for x in ['center_surface_m','normal','right','up']];span=j['uv_span_m'][0];o=max((x for x in bpy.context.scene.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());pts={};records={}
for name,u,v in [('eye_left',.333,1-.444+111/2048),('eye_right',.667,1-.444+111/2048),('nose',.5,1-.548+111/2048),('mouth',.5,1-.610+111/2048)]:
 target=C+U*((u-.5)*span)+V*((v-.5)*span);p,n,idx,dist=tree.ray_cast(target+N*.03,-N);assert p is not None;assert 'Bear bag' in o.data.materials[o.data.polygons[idx].material_index].name;delta=p-C;uv=(delta.dot(U)/span+.5,delta.dot(V)/span+.5);err=max(abs(uv[0]-u),abs(uv[1]-v));assert err<1e-5;pts[name]=p;records[name]={'surface_point_mm':list(p*1000),'uv_error':err,'polygon':idx,'normal':list(n)}
delta=pts['eye_right']-pts['eye_left'];w0=abs(delta.dot(U));w55=abs(delta.dot(U*math.cos(math.radians(55))-N*math.sin(math.radians(55))));j['landmarks_surface_hits']=records;j['eye_width_normal_view_mm']=w0*1000;j['eye_width_oblique55_mm']=w55*1000;j['foreshortening_ratio_55']=w55/w0;assert .3<w55/w0<.85;j['surface_position_check']='PASS';(D/'表面坐标与投影校验.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');print('SURFACE_LANDMARK_CHECK_PASS',w0*1000,w55*1000,w55/w0)

EL,ER=[Vector(x) for x in j['ear_centres_m']];EM=(EL+ER)/2;ear=(ER-EL).normalized();assert abs(ear.dot(U)-1)<1e-6
projected_eye=(pts['eye_right']-pts['eye_left']);eye_vertical_error_mm=abs(projected_eye.dot(V))*1000;nose_midline_error_mm=abs((pts['nose']-EM).dot(U))*1000
assert eye_vertical_error_mm<.001 and nose_midline_error_mm<.001
j['ear_alignment_check']={'status':'PASS','eye_vs_ear_axis_projected_vertical_error_mm':eye_vertical_error_mm,'nose_midline_error_mm':nose_midline_error_mm,'ear_landmark_source':'ear_landmarks.json; visible inner-ear centres, not hidden volumes'}
(D/'表面坐标与投影校验.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');print('EAR_FRAME_CHECK_PASS',eye_vertical_error_mm,nose_midline_error_mm)
