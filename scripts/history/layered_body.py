"""New source-built inner mannequin and face. All public coordinates are mm."""
import bpy, bmesh, math, numpy as np
from mathutils import Vector
MM=.001

def collection(name):
    c=bpy.data.collections.get(name)
    if not c:c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
    return c

def move(o,c):
    for cc in list(o.users_collection):cc.objects.unlink(o)
    collection(c).objects.link(o)
    return o

def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.get('MAT-'+name)
    if m:return m
    m=bpy.data.materials.new('MAT-'+name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    if 'skin' in name:bs.inputs['Subsurface Weight'].default_value=.06
    return m

def mesh(name,vs,fs,mat,c):
    me=bpy.data.meshes.new('MESH-'+name);me.from_pydata([tuple(Vector(p)*MM) for p in vs],[],fs);me.update()
    o=bpy.data.objects.new('GEO-'+name,me);collection(c).objects.link(o)
    if mat:me.materials.append(mat)
    for f in me.polygons:f.use_smooth=True
    return o

def sphere(name,center,radii,mat,c,segments=48,rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=Vector(center)*MM)
    o=bpy.context.object;o.name='GEO-'+name;o.scale=Vector(radii)*MM
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    move(o,c);o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return o

def smooth_path(points,n=8):
    p=[Vector(v) for v in points];out=[]
    for i in range(len(p)-1):
        a=p[max(0,i-1)];b=p[i];c=p[i+1];d=p[min(len(p)-1,i+2)]
        for j in range(n):
            t=j/n;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    out.append(p[-1]);return out

def tube(name,points,radii,mat,c,sides=16,samples=8,depth=1):
    ps=smooth_path(points,samples);vs=[];fs=[]
    for i,p in enumerate(ps):
        t=i/(len(ps)-1);f=t*(len(radii)-1);j=min(int(f),len(radii)-2);rr=(1-(f-j))*radii[j]+(f-j)*radii[j+1]
        tangent=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized()
        ref=Vector((0,1,0))
        if abs(ref.dot(tangent))>.92:ref=Vector((1,0,0))
        u=tangent.cross(ref).normalized();v=tangent.cross(u).normalized()
        for k in range(sides):
            a=k*math.tau/sides;vs.append(p+rr*(math.cos(a)*u+math.sin(a)*v*depth))
    for i in range(len(ps)-1):
        for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    fs.append(tuple(range(sides-1,-1,-1)));fs.append(tuple((len(ps)-1)*sides+j for j in range(sides)))
    return mesh(name,vs,fs,mat,c)

def head_profile(z):
    zs=np.array([65.7,66.5,68,71,76,83,90,96,99,100.1])
    xs=np.array([0,6,12.5,17.3,20.1,21,20.2,16.8,9,0])
    ys=np.array([0,5,8.5,11.2,13,13.35,12.7,10.8,6,0])
    return float(np.interp(z,zs,xs)),float(np.interp(z,zs,ys))

def face_y(x,z):
    rx,ry=head_profile(z)
    return -ry*max(.01,1-(x/max(rx,.01))**2)**.36

def build_body(api=None):
    skin=material('peach skin',(.82,.49,.34),.52);parts=[]
    # Closed inner volumes: complete even under all clothing and accessories.
    for nm,ctr,rad in [('Torso',(0,0,55),(9.4,5.7,11)),('Pelvis',(0,0,44.5),(9,5.8,6.8)),('Neck',(0,0,65.5),(3.3,3.4,4.5))]:
        parts.append(sphere('Body-'+nm,ctr,rad,skin,'BODY'))
    arms=[('R',[(-9.5,0,61),(-13.5,-.4,57),(-16.5,-1,52),(-20,-3,43)],[3.3,3.2,2.8,2.1]),('L',[(9.5,0,61),(13,-.7,58),(16,-2,56),(19,-8,65)],[3.4,3.1,2.9,2.2])]
    for label,path,rad in arms:parts.append(tube('Body-'+label+'-Arm',path,rad,skin,'BODY',samples=14,sides=24))
    for sign in [-1,1]:parts.append(sphere('Body-Shoulder-'+str(sign),(sign*8.8,0,61),(3.8,3.3,3.8),skin,'BODY'))
    for label,path in [('R',[(-5.2,0,44),(-6.3,-.7,35),(-7.5,-1.6,28),(-8,-1,18),(-7.5,-1,10)]),('L',[(5.2,0,44),(6,-.3,35),(6.2,-.7,27),(6.5,-.3,18),(6.5,-1,10)])]:
        parts.append(tube('Body-'+label+'-Leg',path,[4,3.8,3.1,2.7,2.2],skin,'BODY',samples=12,sides=28,depth=.98))
        x=-7.5 if label=='R' else 6.5;parts.append(sphere('Body-'+label+'-Foot',(x,-2.8,10),(3.6,5.3,2.8),skin,'BODY'))
    parts.append(sphere('Body-L-Palm',(23,-10.4,70),(3.5,1.55,3.65),skin,'BODY'))
    parts.append(tube('Body-L-Wrist',[(19,-8,64),(20.8,-9.2,67),(22.3,-10.1,69)],[2.15,2.05,1.8],skin,'BODY',sides=24))
    fingers=[('Thumb',[(20.5,-10.6,69.5),(19.6,-11.3,71.3),(19.5,-11.4,73.5)],[1.15,1,.78]),('Index',[(21.8,-10.4,71.7),(21.7,-10.7,74.4),(22.1,-10.8,77)],[1.05,.88,.72]),('Middle',[(23.5,-10.2,72),(24.5,-10.5,74.3),(26,-10.7,76.5)],[1.0,.88,.72]),('Ring',[(25,-10.3,71),(27.1,-10.6,72.6),(29,-10.7,74.3)],[.94,.8,.65]),('Pinky',[(25.8,-10.6,69.5),(28,-10.9,70.5),(30,-11,72.1)],[.85,.73,.6])]
    for nm,path,rad in fingers:
        parts.append(tube('Body-L-'+nm,path,rad,skin,'BODY',samples=10,sides=16));parts.append(sphere('Body-L-'+nm+'-Tip',path[-1],(rad[-1],rad[-1],rad[-1]),skin,'BODY',segments=20,rings=12))
    parts.append(sphere('Body-R-Palm',(-20.5,-4.9,40.3),(2.8,1.65,2.6),skin,'BODY'))
    parts.append(tube('Body-R-Wrist',[(-19.5,-2.7,44),(-20,-4,42),(-20.5,-4.5,41)],[2.15,2.1,2.0],skin,'BODY',sides=20))
    for i,(x,z) in enumerate([(-22.5,37.8),(-21.3,37.2),(-20.1,37.5),(-18.9,38.2)]):
        ps=[(x+.35,-5.0,40.1),(x,-5.4,38.9),(x,-5.8,z)];parts.append(tube('Body-R-Finger%d'%i,ps,[.82,.75,.65],skin,'BODY',sides=14));parts.append(sphere('Body-R-Finger%d-Tip'%i,ps[-1],(.65,.65,.65),skin,'BODY',segments=16,rings=10))
    parts.append(tube('Body-R-Thumb',[(-18.7,-5.5,41),(-17.8,-6.2,40.2),(-17.6,-6.5,39.3)],[.95,.85,.65],skin,'BODY'))
    # Voxel union affects only the newly constructed inner body; no outside layer exists yet.
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='GEO-Body-CompleteInner';body.data.remesh_voxel_size=.00016;bpy.ops.object.voxel_remesh()
    mod=body.modifiers.new('Soft continuous skin','SMOOTH');mod.factor=.30;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    for f in body.data.polygons:f.use_smooth=True
    # The head is an independently closed, contour-profiled form, never a face photograph.
    vs=[];fs=[];N=128;NZ=100
    for iz in range(1,NZ):
        z=65.7+(100.1-65.7)*iz/NZ;rx,ry=head_profile(z)
        for i in range(N):
            a=math.tau*i/N;x=rx*math.cos(a);y=ry*math.sin(a)
            if y<0:y=-ry*max(0,1-(x/rx)**2)**.36
            vs.append((x,y,z))
    for iz in range(NZ-2):
        for i in range(N):fs.append((iz*N+i,iz*N+(i+1)%N,(iz+1)*N+(i+1)%N,(iz+1)*N+i))
    bot=len(vs);vs.append((0,0,65.7));top=len(vs);vs.append((0,0,100.1))
    for i in range(N):fs.append((bot,(i+1)%N,i));fs.append((top,(NZ-2)*N+i,(NZ-2)*N+(i+1)%N))
    head=mesh('Body-Head',vs,fs,skin,'BODY');head['head_component']=True
    return [body,head]

def build_face(api=None):
    skin=material('peach skin',(.82,.49,.34),.52);white=material('eye porcelain white',(.91,.88,.78),.28);brown=material('warm brown iris',(.095,.035,.012),.28);dark=material('deep brown pupil',(.023,.009,.004),.24);shine=material('eye soft white catchlight',(.99,.99,.99),.13);lash=material('soft brown lashes',(.065,.023,.012),.56);lip=material('warm smile',(.37,.105,.055),.6);out=[]
    for sign in [-1,1]:
        x=sign*8.8
        out.append(sphere('Face-EyeWhite-'+str(sign),(x,-10.85,81.1),(5.45,3.0,5.8),white,'FACE',segments=64,rings=40))
        out.append(sphere('Face-Iris-'+str(sign),(x+.25,-13.55,81.2),(3.8,.46,4.65),brown,'FACE',segments=64,rings=40))
        out.append(sphere('Face-Pupil-'+str(sign),(x+.25,-13.94,81.6),(2.0,.18,3.55),dark,'FACE'))
        out.append(sphere('Face-Catchlight-'+str(sign),(x-.8,-14.14,83.9),(.9,.10,1.05),shine,'FACE',segments=24,rings=16))
        out.append(sphere('Face-SecondaryHighlight-'+str(sign),(x+1.35,-14.02,79),(.32,.09,.36),shine,'FACE',segments=20,rings=12))
        brow=[(x-4.2,-11.85,88.6),(x-2.2,-12.6,89.5),(x+.5,-12.9,89.6),(x+3.5,-12,88.8)]
        out.append(tube('Face-Eyebrow-'+str(sign),brow,[.28,.43,.40,.18],lash,'FACE',samples=10,sides=12))
        upper=[(x-4.9,-12.0,83.0),(x-3,-13.4,85.7),(x,-13.8,86.5),(x+3.5,-12.8,85.5),(x+5,-11.5,83.4)]
        out.append(tube('Face-UpperLid-'+str(sign),upper,[.18,.25,.27,.24,.12],lash,'FACE',samples=10,sides=12))
        for k in range(2):
            sx=x+sign*(3.3+k*.7);z=85.4-k*.65
            out.append(tube('Face-Eyelash-%s-%s'%(sign,k),[(sx,-13,z),(sx+sign*.6,-13.3,z+.6),(sx+sign*.9,-13.2,z+1.1)],[.22,.18,.04],lash,'FACE',samples=5,sides=8))
        ear=sphere('Face-Ear-'+str(sign),(sign*20.1,0,78.3),(2.3,2,4),skin,'FACE');out.append(ear)
        inner=material('inner ear rose',(.66,.30,.23),.63);out.append(sphere('Face-EarInner-'+str(sign),(sign*21.45,-1.05,78.5),(.6,.35,2.2),inner,'FACE'))
    out.append(sphere('Face-TinyNose',(0,-13.35,76.7),(.7,.7,.65),skin,'FACE'))
    mouth=[(-1.9,face_y(-1.9,73.4)-.09,73.4),(-1.2,face_y(-1.2,72.8)-.09,72.8),(0,face_y(0,72.5)-.09,72.5),(1.2,face_y(1.2,72.8)-.09,72.8),(1.9,face_y(1.9,73.3)-.09,73.3)]
    out.append(tube('Face-GentleSmile',mouth,[.11,.15,.15,.13,.08],lip,'FACE',samples=8,sides=10))
    # Soft blush is a translucent decal, not a protruding pink lump.
    W=128;yy,xx=np.mgrid[0:W,0:W];d=((xx-(W-1)/2)/(W/2))**2+((yy-(W-1)/2)/(W/2))**2;rgba=np.zeros((W,W,4),np.float32);rgba[:,:,:3]=(.97,.30,.32);rgba[:,:,3]=np.clip(1-d,0,1)**1.5*.38
    im=bpy.data.images.new('Soft cheek tint',width=W,height=W,alpha=True);im.pixels.foreach_set(rgba.ravel());im.pack()
    m=material('soft translucent cheek',(1,.3,.3),.9);bs=m.node_tree.nodes.get('Principled BSDF');tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);m.surface_render_method='DITHERED'
    for sign in [-1,1]:
        vs=[];fs=[];NX=20;NZ=12
        for iz in range(NZ+1):
            z=74.6+(iz/NZ-.5)*4.2
            for ix in range(NX+1):
                x=sign*13.5+(ix/NX-.5)*6.4;vs.append((x,face_y(x,z)-.035,z))
        for iz in range(NZ):
            for ix in range(NX):a=iz*(NX+1)+ix;fs.append((a,a+1,a+NX+2,a+NX+1))
        o=mesh('Face-Blush-'+str(sign),vs,fs,m,'FACE');uv=o.data.uv_layers.new(name='UVMap')
        for f in o.data.polygons:
            for li in f.loop_indices:
                vi=o.data.loops[li].vertex_index;uv.data[li].uv=((vi%(NX+1))/NX,(vi//(NX+1))/NZ)
        o['visual_decal']=True;out.append(o)
    return out

def build_glasses(api=None):
    frame=material('dark chocolate glasses',(.075,.025,.012),.28);clear=material('clear lenses',(.91,.96,1),.13);bs=clear.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.035;clear.surface_render_method='DITHERED';out=[]
    # Each frame and temple is its own editable closed structure.
    for sign in [-1,1]:
        cx=sign*8.8;ps=[];N=100
        for i in range(N+1):
            a=math.tau*i/N;x=cx+8.1*math.copysign(abs(math.cos(a))**.88,math.cos(a));z=81.6+6.6*math.copysign(abs(math.sin(a))**.9,math.sin(a));y=-16.1+.0028*x*x;ps.append((x,y,z))
        o=tube('Glasses-Frame-'+str(sign),ps,[.57,.57],frame,'GLASSES',sides=12,samples=1)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES_ONLY');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000005);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();out.append(o)
        out.append(tube('Glasses-Temple-'+str(sign),[(sign*16.7,-15.3,82.7),(sign*20.5,-9,82.1),(sign*21.8,-1,81.2),(sign*21.3,2,78.3)],[.5,.45,.4,.4],frame,'GLASSES',sides=12,samples=12))
        lens=sphere('Glasses-Lens-'+str(sign),(cx,-15.75,81.6),(7.6,.12,6.05),clear,'GLASSES',segments=64,rings=40);lens['visual_transparent_lens']=True;out.append(lens)
    out.append(tube('Glasses-NoseBridge',[(-.8,-16.05,82.0),(-.35,-16.3,82.6),(.35,-16.3,82.6),(.8,-16.05,82.0)],[.37,.4,.4,.37],frame,'GLASSES',sides=12,samples=7))
    return out
