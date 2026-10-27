import bpy,bmesh,json,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_手部精修_20261019';D=B/'3D重建_v6基础_自然弧形指缝_20261020';work=D/'_full_boolean_work.blend';shutil.copy2(D/'小秦_v6自然弧形指缝.blend',work);bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6手部精修.blend'));s=bpy.context.scene;o=max((x for x in s.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));name=o.name
with bpy.data.libraries.load(str(work),link=False) as (src,dst):dst.objects=[name]
patch=dst.objects[0];bpy.context.collection.objects.link(patch)
def inside(c):return .0146<c.x<.0232 and -.0135<c.y<-.0052 and .0622<c.z<.0683
ids=set(f.index for f in o.data.polygons if inside(f.center));bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();keys={tuple(round(float(c),8) for c in v.co) for v in bm.verts if any(f.index in ids for f in v.link_faces) and any(f.index not in ids for f in v.link_faces)};bm.free()
for i in range(3):patch.data.materials[i]=o.data.materials[i]
bm=bmesh.new();bm.from_mesh(patch.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if not inside(f.calc_center_median())],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(patch.data);bm.free()
bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in ids],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(o.data);bm.free();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);patch.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.join();bm=bmesh.new();bm.from_mesh(o.data);verts=[v for v in bm.verts if tuple(round(float(c),8) for c in v.co) in keys];bmesh.ops.remove_doubles(bm,verts=verts,dist=.00000005);bad=sum(not e.is_manifold for e in bm.edges);bound=sum(e.is_boundary for e in bm.edges);bm.to_mesh(o.data);bm.free();o.data.update();report={'method':'closed boolean evaluated in temporary mesh, only hand patch transplanted to untouched original','local_hand_box_m':[[.0146,.0232],[-.0135,-.0052],[.0622,.0683]],'replaced_original_faces':len(ids),'nonmanifold_edges':bad,'boundary_edges':bound};(D/'局部回填校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('LOCAL_PATCH_REPORT',json.dumps(report));assert bad==0 and bound==0
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=900;s.render.resolution_y=900;cam=s.camera
for name,target,pos,scale in [('hand-front',(.018,0,.065),(.018,-.20,.065),.020),('hand-oblique',(.018,-.009,.064),(.10,-.16,.070),.020)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'小秦_v6自然弧形指缝.blend'));bpy.ops.object.select_all(action='DESELECT')
for a in s.objects:
 if a.type=='MESH':a.select_set(True)
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6自然弧形指缝.glb'),use_selection=True,export_format='GLB');o.data=full;print('LOCAL_NATURAL_WEBS_DONE')
