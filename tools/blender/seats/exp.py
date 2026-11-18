# blender --background --python exp.py -- <model> <out.npz>
import bpy, sys, numpy as np, bmesh
a=sys.argv[sys.argv.index('--')+1:]; src,out=a
bpy.ops.wm.read_factory_settings(use_empty=True)
e=src.lower()
if e.endswith('.fbx'): bpy.ops.import_scene.fbx(filepath=src)
elif e.endswith('.obj'): bpy.ops.wm.obj_import(filepath=src)
else: bpy.ops.import_scene.gltf(filepath=src)
dg=bpy.context.evaluated_depsgraph_get(); T=[]; L=[]; names=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    me=o.evaluated_get(dg).to_mesh(); me.calc_loop_triangles(); M=np.array(o.matrix_world)
    n=len(me.vertices); V=np.empty(n*3,np.float32); me.vertices.foreach_get('co',V); V=V.reshape(-1,3); V=V@M[:3,:3].T+M[:3,3]
    nt=len(me.loop_triangles); 
    if not nt: continue
    tv=np.empty(nt*3,np.int32); me.loop_triangles.foreach_get('vertices',tv); mi=np.empty(nt,np.int32); me.loop_triangles.foreach_get('material_index',mi)
    mats=[(s.material.name if s.material else 'none') for s in o.material_slots] or ['none']
    for j,mn in enumerate(mats):
        lab=f'{mn}@{o.name}'
        if lab not in names: names.append(lab)
    lab_idx=np.array([names.index(f'{mats[min(m,len(mats)-1)]}@{o.name}') for m in range(len(mats))])
    T.append(V[tv.reshape(-1,3)]); L.append(lab_idx[np.minimum(mi,len(mats)-1)])
np.savez_compressed(out,T=np.concatenate(T).astype(np.float32),L=np.concatenate(L),names=np.array(names))
print('EXPORTED',sum(len(t) for t in T),'tris',len(names),'labels')
