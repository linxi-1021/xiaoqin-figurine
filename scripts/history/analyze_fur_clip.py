exec(open('models/rebuild/inspect_fur_clip.py',encoding='utf-8-sig').read().split('for o in bpy.context.scene.objects:')[0])
import numpy as np
ob=bpy.data.objects['GEO-Redesigned hat solid plush tufts'];co=np.array([v.co[:] for v in ob.data.vertices]).reshape(-1,150,3);c=co.mean(1);mi=np.array([ob.data.polygons[i*142].material_index for i in range(len(c))]);q=(c-np.array([.00666,0,.10105]))@np.array([.342,0,.94]);sel=(mi>=5)&(mi<10)&(q<-.014)
print('LOW_CREAM',sel.sum());print(np.round(np.column_stack([np.arange(len(c))[sel],c[sel]*1000,q[sel]*1000]),2).tolist())
np.savez('models/rebuild/fur_clip_components.npz',co=co,mi=mi)
