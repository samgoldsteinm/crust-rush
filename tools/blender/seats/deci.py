import bpy, bmesh, numpy as np, sys
a=sys.argv[sys.argv.index('--')+1:]; T=np.load(a[0]); out=a[1]; targets=[int(x) for x in a[2:]]
bpy.ops.wm.read_factory_settings(use_empty=True)
res={}
for tg in targets:
    me=bpy.data.meshes.new('s'); bm=bmesh.new(); V=T.reshape(-1,3)
    vs=[bm.verts.new(v) for v in V]
    for i in range(len(T)):
        try: bm.faces.new((vs[3*i],vs[3*i+1],vs[3*i+2]))
        except ValueError: pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.004); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new('s',me); bpy.context.collection.objects.link(o); bpy.context.view_layer.objects.active=o
    m=o.modifiers.new('d','DECIMATE'); m.ratio=min(1,tg/max(1,len(me.polygons))); m.use_collapse_triangulate=True
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg).to_mesh(); e.calc_loop_triangles()
    n=len(e.vertices); P=np.empty(n*3); e.vertices.foreach_get('co',P); P=P.reshape(-1,3)
    F=np.empty(len(e.loop_triangles)*3,np.int32); e.loop_triangles.foreach_get('vertices',F); F=F.reshape(-1,3)
    N=np.empty(n*3); e.vertices.foreach_get('normal',N); N=N.reshape(-1,3)
    res[f'P{tg}']=P; res[f'F{tg}']=F; res[f'N{tg}']=N; print('DECI',tg,len(F))
    bpy.data.objects.remove(o)
np.savez(out,**res)
