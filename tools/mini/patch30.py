"""Patch 30 (web v195): real trees on every track that has trees.
The owner, 2026-11-14: "update all the maps with the new trees we made a while ago im noticing some of the older maps still have the old
blocky trees and shrubs".
Every tree outside the house went through forest() as one of five low-polygon models (tree_round1/2, tree_shrub, tree_pine1/2). Now
forest() stands each one up as crossed cards carrying a picture of a real, photo-scanned tree (Poly Haven, CC0; the pictures are made by
tools/blender/treepics.py and stored with put_tex.py as tex_tree_<name>): three cards for a tree near the track, two further out.
  tree_round1 -> the gnarled island tree or the jacaranda      tree_round2 -> the slim tree or the tall island tree
  tree_pine1 and tree_pine2 -> the fir (the scanned pine was too large for this PC to render: 5 GB)
  tree_shrub  -> a bush: the crown of the gnarled tree, set on the ground
The freezer tracks' 1800 little green cones become small firs. The old models stay in the build as the fallback for a picture that has
not arrived. Looks only: nothing here moves a kart (trees were never solid in a race). The PC gets them with the next track export.
Run once: py.cmd tools/mini/patch30.py   (after the pictures are in the texture store)"""
import numpy as np
from PIL import Image
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function treeCards' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    if s.count(a) == 0 and '\n' in a: a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


def hf(name):
    """how much of the picture's height the tree fills (both halves agree to a hair)"""
    im = np.asarray(Image.open(f'D:/crust-rush/blender/treepics/{name}.png').convert('RGBA')); a = im[..., 3] > 128
    return round(1 - np.where(a.any(1))[0].min() / im.shape[0], 3)


# name: [how much of the card's height the tree fills, the tree's height in the game at scale 1]
PICS = {'jac': 18.0, 'small': 20.0, 'isl1': 17.5, 'isl2': 16.0, 'fir': 24.0}
tab = ','.join(f"{k}:[{hf(k)},{v}]" for k, v in PICS.items())
CODE = ("/* ---- real trees (web v195, tools/mini/patch30.py): a tree is crossed cards with a picture of a photo-scanned tree; three cards near the track, two far off.\n"
        "   TREE_PIC: the picture's name -> [how much of the card's height the tree fills, its height in the game at scale 1]; TREE_AS: which pictures stand in for\n"
        "   each of the old models (a bush is the crown of a tree: [picture, from, to] up the card). The cards' normals point straight up, so a tree is lit evenly\n"
        "   from every side, as a mass of leaves is. */\n"
        "const TREE_PIC={" + tab + "},TREE_AS={tree_round1:['isl2','jac'],tree_round2:['small','isl1'],tree_pine1:['fir'],tree_pine2:['fir'],tree_shrub:[['isl2',.2,.58]]};\n"
        "function treeCardGeo(S,n,v0,v1){const P=[],U=[],Nn=[],I=[],h=S*(v1-v0);for(let i=0;i<n;i++){const a=i*Math.PI/n+.4,c=Math.cos(a),sn=Math.sin(a),u0=(i%2)*.5,fl=i===2,b=P.length/3;\n"
        "    for(const [lx,ly,uu,vv] of [[-S/2,0,0,v0],[S/2,0,1,v0],[S/2,h,1,v1],[-S/2,h,0,v1]]){P.push(lx*c,ly,lx*sn);U.push(u0+(fl?1-uu:uu)*.5,vv);Nn.push(0,1,0);}I.push(b,b+1,b+2,b,b+2,b+3);}\n"
        "  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(U,2));g.setAttribute('normal',new THREE.Float32BufferAttribute(Nn,3));g.setIndex(I);return g;}\n"
        "function treeCards(as,L,y,snow,rr,hq,tint){/* one instanced mesh for each picture in `as`; the trees of the list take the pictures in turn */\n"
        "  const m4=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),v=new THREE.Vector3(),sc=new THREE.Vector3(),U=QUAL[qKey].hqAll&&!QUAL[qKey].mob;\n"
        "  as.forEach((pc,pi)=>{const id=Array.isArray(pc)?pc[0]:pc,v0=Array.isArray(pc)?pc[1]:0,v1=Array.isArray(pc)?pc[2]:1,T=TREE_PIC[id],mine=L.filter((t,i)=>i%as.length===pi);if(!mine.length)return;\n"
        "    const tex=propTex('tex_tree_'+id);tex.userData.alpha=true;const bush=Array.isArray(pc),S=bush?13:T[1]/T[0],k=tint?(tint[0]+tint[1]+tint[2])/3:1;\n"
        "    const col=new THREE.Color(1,1,1);if(tint)col.setRGB(tint[0]*1.5,tint[1]*1.5,tint[2]*1.5);if(snow)col.lerp(new THREE.Color('#dfeaf6'),.45);\n"
        "    const mat=new THREE.MeshStandardMaterial({name:'treecard_'+id,map:tex,alphaTest:.4,side:THREE.DoubleSide,roughness:.95,color:col,emissive:col,emissiveMap:tex,emissiveIntensity:.16*k});\n"
        "    const im=new THREE.InstancedMesh(treeCardGeo(S,hq?3:2,v0,v1),mat,mine.length);\n"
        "    mine.forEach((t,i)=>{q.setFromEuler(e.set(0,t[4]??rr()*6.28,0));const s0=t[3]*(bush?.8:1);m4.compose(v.set(t[1],(t[5]??(typeof y==='function'?y(t[1],t[2]):y))-.4,t[2]),q,sc.set(s0,s0*(.9+rr()*.25),s0));im.setMatrixAt(i,m4);});\n"
        "    im.castShadow=!!U;if(U)im.customDepthMaterial=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,map:tex,alphaTest:.4});im.receiveShadow=false;im.userData.noLift=true;world.add(im);});}\n")
rep("function forest(list,y,snow,rng,hq,tint){/* list: [name,x,z,scale,rot] */const rr=rng||rnd;const by={};for(const t of list)(by[t[0]]=by[t[0]]||[]).push(t);",
    CODE + "function forest(list,y,snow,rng,hq,tint){/* list: [name,x,z,scale,rot] */const rr=rng||rnd;const by={};for(const t of list)(by[t[0]]=by[t[0]]||[]).push(t);\n"
    "  /* real trees where their pictures are in (web v195); the old models below are what is left for one that is not */if(typeof PROP_TEX!=='undefined')for(const name in by){const as=TREE_AS[name];if(as&&as.every(pc=>PROP_TEX['tex_tree_'+(Array.isArray(pc)?pc[0]:pc)])){treeCards(as,by[name],y,snow,rr,hq??(QUAL[qKey].hqAll&&!QUAL[qKey].mob),tint);delete by[name];}}")
# the freezer tracks' little green cones: small firs and pines
rep("    place(new THREE.ConeGeometry(1,3,7).translate(0,1.5,0),lit('#ffffff',{roughness:.9}),spots(1800,10,460,10),[2,4.5],{cols:['#2f5d46','#3b6e52','#294f3c']});",
    "    if(typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_tree_fir){/* (web v195: these were 1800 green cones) */const sm=[];for(const [x,z] of spots(1800,10,460,10))sm.push([R()<.6?'tree_pine1':'tree_pine2',x,z,.3+R()*.42]);forest(sm,(x,z)=>groundAt(x,z),.75,R,false,null);}\n"
    "    else place(new THREE.ConeGeometry(1,3,7).translate(0,1.5,0),lit('#ffffff',{roughness:.9}),spots(1800,10,460,10),[2,4.5],{cols:['#2f5d46','#3b6e52','#294f3c']});")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched', tab)
