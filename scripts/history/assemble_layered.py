import bpy, math, sys, json, os, importlib, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path('D:/Desktop/相册/二维IP制作_20261012/手办设计/全新分层重建_20261019')
sys.path.insert(0,str(ROOT/'tools'))
import body_face
import clothing_bag
import hair_hat
MM=.001
for n in ['milestones','previews','checks','delivery']:(ROOT/n).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS';scene.unit_settings.scale_length=1

def setup_render():
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=900;scene.render.resolution_y=1380;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True
    world=bpy.data.worlds.new('Studio warm neutral');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.78,.73,.65,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='OPTIX';prefs.get_devices()
        if any(d.type=='OPTIX' for d in prefs.devices):
            for d in prefs.devices:d.use=d.type=='OPTIX'
            scene.cycles.device='GPU'
    except Exception as e:print('DEVICE_CPU_FALLBACK',str(e))
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.3
    for name,pos,power,size,color in [('Key',(-.11,-.16,.22),2.2,.12,(1,.89,.76)),('Fill',(.12,-.07,.14),1.3,.13,(.83,.91,1)),('Rim',(.04,.11,.18),2.5,.10,(1,.86,.73))]:
        data=bpy.data.lights.new('LIGHT-'+name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;o=bpy.data.objects.new('LIGHT-'+name,data);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.065))-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('CAM-reference-front');d.type='ORTHO';d.ortho_scale=.140;o=bpy.data.objects.new('CAM-reference-front',d);scene.collection.objects.link(o);scene.camera=o

def camera(angle=0,target=(0,0,.06),scale=.140,elevation=.055):
    c=scene.camera;a=math.radians(angle);t=Vector(target);c.location=t+Vector((.32*math.sin(a),-.32*math.cos(a),elevation));c.rotation_euler=(t-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale

def render(name,angle=0,target=(0,0,.06),scale=.140,samples=20):
    camera(angle,target,scale);scene.cycles.samples=samples;scene.render.filepath=str(ROOT/'previews'/name);bpy.ops.render.render(write_still=True)

def checkpoint(name):
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'milestones'/name))

setup_render()
body_objects=body_face.build_body()
checkpoint('01_body.blend')
render('body_front.png',scale=.126,target=(0,0,.053),samples=12)
render('body_side.png',angle=90,scale=.126,target=(0,0,.053),samples=12)
clothing_bag.build_base();clothing_bag.build_clothes()
checkpoint('02_clothed.blend')
render('clothed_front.png',scale=.126,target=(0,0,.053),samples=12)
body_face.build_face();body_face.build_glasses()
checkpoint('03_face_glasses.blend')
hair_hat.build_hair();hair_hat.build_hat();hair_hat.build_ornaments()
bpy.context.view_layer.update()
# Reference head inclination: transform only head and its attached layers around the neck.
pivot=Vector((0,0,.068));R=Matrix.Rotation(math.radians(8),4,'Y');xf=Matrix.Translation(pivot)@R@Matrix.Translation(-pivot)
headgroup=[o for o in body_objects if o.get('head_component')]
for cname in ['FACE','GLASSES','HAIR','HAT','ORNAMENTS']:
    c=bpy.data.collections.get(cname)
    if c:headgroup.extend(list(c.all_objects))
for o in set(headgroup):o.matrix_world=xf@o.matrix_world
checkpoint('06_hat_hair.blend')
clothing_bag.build_bag()
# Deliberate height normalization is a single uniform scene conversion, never a body deformation.
bpy.context.view_layer.update();points=[]
for o in scene.objects:
    if o.type in {'MESH','CURVE'}:points.extend(o.matrix_world@Vector(v) for v in o.bound_box)
zlo=min(v.z for v in points);zhi=max(v.z for v in points);factor=.120/(zhi-zlo)
adjust=Matrix.Scale(factor,4)@Matrix.Translation((0,0,-zlo))
for o in scene.objects:
    if o.type in {'MESH','CURVE'}:o.matrix_world=adjust@o.matrix_world
camera()
scene['project']='Xiaoqin reference-locked layered reconstruction'
scene['backend']='Blender native Python adaptation; MCP not connected'
scene['source_model_imported']=False
scene['height_uniform_factor']=factor
scene['stages_built_in_order']='BODY,CLOTHES,FACE,GLASSES,HAIR,HAT,ORNAMENTS,BAG'
checkpoint('08_assembled.blend')
for name,ang in [('front_transparent.png',0),('threequarter.png',28),('side.png',90),('back.png',180)]:render(name,angle=ang,samples=24)
render('face_close.png',target=(.002,0,.083),scale=.062,samples=32)
print('LAYERED_ASSEMBLY_DONE',json.dumps({'objects':len(scene.objects),'height_factor':factor,'collections':[c.name for c in bpy.data.collections]},ensure_ascii=False))
