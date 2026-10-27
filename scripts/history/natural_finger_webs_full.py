import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
B=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计');S=B/'3D重建_v6基础_手部精修_20261019';D=B/'3D重建_v6基础_自然弧形指缝_20261020';D.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(S/'小秦_v6手部精修.blend'));s=bpy.context.scene;o=max((x for x in s.objects if x.type=='MESH'),key=lambda x:len(x.data.vertices));labels=np.load(B/'3D重建_v6基础_双手五指重建_20261019/uv-chart-labels.npy');assert len(labels)==len(o.data.polygons)
bm=bmesh.new();bm.from_mesh(o.data);original_bad=sum(not e.is_manifold for e in bm.edges);original_boundary=sum(e.is_boundary for e in bm.edges);bm.free()
ids=set(f.index for f in o.data.polygons if int(labels[f.index]) in [355,133,697,24,32,82] and f.center.z>.0620 and f.center.x>.0145 and f.center.y<-.0055)
assert len(ids)>500
patch=o
inner=bpy.data.materials.new('Finger gap inner skin');inner.use_nodes=True;bs=inner.node_tree.nodes.get('Principled BSDF');rgb=[229/255,162/255,130/255];bs.inputs['Base Color'].default_value=(*[((c+.055)/1.055)**2.4 for c in rgb],1);bs.inputs['Roughness'].default_value=.68;bs.inputs['Specular IOR Level'].default_value=.18;patch.data.materials.append(inner);inneridx=len(patch.data.materials)-1
cuts=[(.01735,.0654,.00019),(.01910,.0653,.00020),(.02075,.0639,.00018)];counts=[]
for n,(x,bottom,width) in enumerate(cuts):
 r=width/2;lean=[-.025,.020,.050][n];zs=np.linspace(bottom+r,[.0678,.0678,.0658][n],28)
 def center(z):return x+lean*(z-bottom-r)+.000035*math.sin(min(1,(z-bottom-r)/.002)*math.pi/2)
 def half(z):
  d=z-bottom-r;return r+.00018*(1-math.exp(-d/.0008))
 left=[(center(z)-half(z)*.92,z) for z in zs[::-1]];right=[(center(z)+half(z)*1.08,z) for z in zs]
 root=[(x+r*math.cos(a),bottom+r+r*math.sin(a)) for a in np.linspace(-math.pi,0,19)]
 outline=left+root[1:-1]+right;N=len(outline);verts=[(xx,y,zz) for y in [-.0130,-.0060] for xx,zz in outline];faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];mesh=bpy.data.meshes.new('Rounded slit tool');mesh.from_pydata(verts,[],faces);mesh.update();tool=bpy.data.objects.new('Slit %d'%(n+1),mesh);bpy.context.collection.objects.link(tool)
 for m in patch.data.materials:tool.data.materials.append(m)
 for f in tool.data.polygons:f.material_index=inneridx
 bm=bmesh.new();bm.from_mesh(tool.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(tool.data);bm.free()
 bpy.ops.object.select_all(action='DESELECT');patch.select_set(True);bpy.context.view_layer.objects.active=patch;mod=patch.modifiers.new('Local narrow finger gap %d'%(n+1),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;before=len(patch.data.polygons);bpy.ops.object.modifier_apply(modifier=mod.name);counts.append([before,len(patch.data.polygons)]);bpy.data.objects.remove(tool,do_unlink=True)
bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bound=sum(e.is_boundary for e in bm.edges);bm.free()
report={'method':'asymmetric curved flared finger webs, round closed roots; original fingertips retained','original_hand_region_faces':len(ids),'boolean_scope':'closed original mesh, cutters bounded to finger-web volume','cut_progress':counts,'original_nonmanifold_edges':original_bad,'after_nonmanifold_edges':bad,'original_boundary_edges':original_boundary,'after_boundary_edges':bound,'gap_widths_mm':[c[2]*1000 for c in cuts],'fingertips_not_remodeled':True};(D/'指缝试修校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('GAP_REPORT',json.dumps(report))
assert bad<=original_bad and bound<=original_boundary,'New open edges: do not deliver this attempt'
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
bpy.context.view_layer.objects.active=o;full=o.data;o.data=full.copy();mod=o.modifiers.new('Same v6 web optimization','DECIMATE');mod.ratio=.3;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.ops.export_scene.gltf(filepath=str(D/'小秦_v6自然弧形指缝.glb'),use_selection=True,export_format='GLB');o.data=full;print('NARROW_GAPS_DONE')


