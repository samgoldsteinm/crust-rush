/* Crust Rush → glTF exporter (runs inside the game page; classic script, shares the game's globals).
   Bakes visible world geometry into world space, groups it by material and by spatial cell, and writes .glb.
   Textures: flipY images are written flipped (UVs kept), the map's uvTransform is baked into the UVs,
   non-sRGB colour textures are re-encoded so a glTF (sRGB) decode gives back the values three.js used. */
(function(){
const SRGB=3001;
/* ---- props the PC build draws itself: trees, palms, bushes and rocks. They're recorded where the game places them
   (without changing what it builds or the seeded stream it draws from) and left out of the baked track; the PC draws
   finished models in their place, or these same shapes from the copies kept here. ---- */
const HDK=new Set(['palm','treeA','treeB','shrub','pineA','pineB','pine','bush','rock']);
const PROPS={kinds:{},items:{}};let hdN=0,fcall=0;
const q3=a=>Array.from(a||[],v=>Math.round(v*1000)/1000);
try{const _dl=detailLibQ;detailLibQ=function(th){const L=_dl(th);for(const k in L){const t=L[k];if(HDK.has(k)&&t&&t.P&&!t.__hd){t.__hd=k+'#'+(++hdN);PROPS.kinds[t.__hd]={base:k,theme:th,P:q3(t.P),N:q3(t.N),C:q3(t.C),GP:q3(t.GP),GC:q3(t.GC),rad:t.rad||0,h:t.h||0};PROPS.items[t.__hd]=[];}}return L;};}catch(e){console.warn('hd detailLibQ',e);}
try{const _da=dbAdd;dbAdd=function(t,x,z,ry,s,tint,yOff,blob){if(t&&t.__hd){if(DB_THIN){const kp=dbKeep();if(kp<1&&dbHash(x,z)>kp)return;}
    const tn=tint==null?null:(tint.isColor?'#'+tint.getHexString():(typeof tint==='number'?'#'+tint.toString(16).padStart(6,'0'):String(tint)));
    PROPS.items[t.__hd].push([+x.toFixed(2),+(groundAt(x,z)+(yOff||0)).toFixed(2),+z.toFixed(2),+(ry||0).toFixed(4),+(s||1).toFixed(4),tn]);return;}
  return _da(t,x,z,ry,s,tint,yOff,blob);};}catch(e){console.warn('hd dbAdd',e);}
try{const _fo=forest;forest=function(list,y,snow,rng,hq,tint){const before=world.children.length;const r=_fo(list,y,snow,rng,hq,tint);const call=++fcall;
    const names=[];const seen=new Set();for(const t of list)if(!seen.has(t[0])){seen.add(t[0]);names.push(t[0]);}
    const added=world.children.slice(before).filter(o=>o.isInstancedMesh);
    added.forEach((im,i)=>{const base=names[i];if(!base)return;const key='f'+call+'_'+base;im.userData.hdProp=key;const g=im.geometry;
      const P=q3(g.attributes.position.array),N=q3(g.attributes.normal?g.attributes.normal.array:[]),C=q3(g.attributes.color?g.attributes.color.array:[]),I=g.index?Array.from(g.index.array):null;
      PROPS.kinds[key]={base,forest:1,snow:snow||0,hq:hq===false?0:1,P,N,C,I,GP:[],GC:[],shadow:im.castShadow?1:0};
      const m=new THREE.Matrix4(),pv=new THREE.Vector3(),qv=new THREE.Quaternion(),sv=new THREE.Vector3(),ev=new THREE.Euler();const it=[];
      for(let k=0;k<im.count;k++){im.getMatrixAt(k,m);m.decompose(pv,qv,sv);ev.setFromQuaternion(qv,'YXZ');it.push([+pv.x.toFixed(2),+pv.y.toFixed(2),+pv.z.toFixed(2),+ev.y.toFixed(4),+sv.x.toFixed(4),+sv.y.toFixed(4),+sv.z.toFixed(4)]);}
      PROPS.items[key]=it;});
    return r;};}catch(e){console.warn('hd forest',e);}
window.__exportProps=function(){const out={kinds:{},items:{}};for(const k in PROPS.kinds){if(PROPS.items[k]&&PROPS.items[k].length){out.kinds[k]=PROPS.kinds[k];out.items[k]=PROPS.items[k];}}return out;};
const l2s=c=>c<=0.0031308?c*12.92:1.055*Math.pow(c,1/2.4)-0.055;
function b64ToU8(d){const s=atob(d.slice(d.indexOf(',')+1)),u=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u[i]=s.charCodeAt(i);return u;}
function u8ToB64(u){let s='';const C=0x8000;for(let i=0;i<u.length;i+=C)s+=String.fromCharCode.apply(null,u.subarray(i,i+C));return btoa(s);}

class GLB{
  constructor(){this.j={asset:{version:'2.0',generator:'Crust Rush exporter'},scene:0,scenes:[{nodes:[]}],nodes:[],meshes:[],materials:[],accessors:[],bufferViews:[],buffers:[],images:[],textures:[],samplers:[]};
    this.chunks=[];this.len=0;this.mats=new Map();this.texs=new Map();this.samps=new Map();this.ext=new Set();this.stats={tris:0,verts:0,texBytes:0,skipped:{}};}
  view(arr,target){const pad=(4-this.len%4)%4;if(pad){this.chunks.push(new Uint8Array(pad));this.len+=pad;}
    const u=arr instanceof Uint8Array?arr:new Uint8Array(arr.buffer,arr.byteOffset,arr.byteLength);this.chunks.push(u.slice());
    const v={buffer:0,byteOffset:this.len,byteLength:u.byteLength};if(target)v.target=target;this.len+=u.byteLength;this.j.bufferViews.push(v);return this.j.bufferViews.length-1;}
  acc(arr,type,ct,count,target,mm){const a={bufferView:this.view(arr,target),componentType:ct,count,type};if(mm){a.min=mm[0];a.max=mm[1];}this.j.accessors.push(a);return this.j.accessors.length-1;}
  sampler(t){const w=x=>x===1000?10497:x===1002?33648:33071,k=w(t.wrapS)+'|'+w(t.wrapT);if(!this.samps.has(k)){this.j.samplers.push({magFilter:9729,minFilter:9987,wrapS:w(t.wrapS),wrapT:w(t.wrapT)});this.samps.set(k,this.j.samplers.length-1);}return this.samps.get(k);}
  texture(t,role){const key=t.uuid+'|'+role;if(this.texs.has(key))return this.texs.get(key);const im=t.image;let w=im&&(im.width||im.videoWidth),h=im&&(im.height||im.videoHeight);
    if(!w||!h||w<2||h<2){this.texs.set(key,null);return null;}
    const sc=Math.min(1,2048/Math.max(w,h)),W=Math.max(1,Math.round(w*sc)),H=Math.max(1,Math.round(h*sc));const c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');
    if(t.flipY){g.translate(0,H);g.scale(1,-1);}
    try{if(im.data&&!(im instanceof HTMLCanvasElement)){const tmp=document.createElement('canvas');tmp.width=w;tmp.height=h;const id=tmp.getContext('2d').createImageData(w,h);const d=im.data;
        if(d.length===w*h*4){for(let i=0;i<d.length;i++)id.data[i]=d[i]>1?d[i]:Math.round(d[i]*255);}else{this.texs.set(key,null);return null;}tmp.getContext('2d').putImageData(id,0,0);g.drawImage(tmp,0,0,W,H);}
      else g.drawImage(im,0,0,W,H);}catch(e){this.texs.set(key,null);return null;}
    const alpha=role==='color'&&t.userData&&t.userData.alpha;let hasA=false;
    if(role==='color'&&t.encoding!==SRGB){const id=g.getImageData(0,0,W,H),d=id.data;for(let i=0;i<d.length;i+=4){d[i]=Math.round(l2s(d[i]/255)*255);d[i+1]=Math.round(l2s(d[i+1]/255)*255);d[i+2]=Math.round(l2s(d[i+2]/255)*255);if(d[i+3]<250)hasA=true;}g.putImageData(id,0,0);}
    else if(role==='color'){const d=g.getImageData(0,0,W,H).data;for(let i=3;i<d.length;i+=16)if(d[i]<250){hasA=true;break;}}
    const png=hasA||alpha||role==='normal'||role==='rough',url=c.toDataURL(png?'image/png':'image/jpeg',.9),bytes=b64ToU8(url);this.stats.texBytes+=bytes.length;
    if(this.extDir){const fn='t'+this.j.images.length+(png?'.png':'.jpg');(this.files=this.files||[]).push({name:fn,b64:url.slice(url.indexOf(',')+1)});this.j.images.push({uri:this.extDir+'/'+fn,mimeType:png?'image/png':'image/jpeg',name:(t.name||'tex')+'_'+role});}
    else this.j.images.push({bufferView:this.view(bytes),mimeType:png?'image/png':'image/jpeg',name:(t.name||'tex')+'_'+role});
    this.j.textures.push({source:this.j.images.length-1,sampler:this.sampler(t)});const ti=this.j.textures.length-1;this.texs.set(key,ti);return ti;}
  material(m,vc){const key=m.uuid+(vc?'|vc':'');if(this.mats.has(key))return this.mats.get(key);
    const M={name:(m.name||m.type)+'_'+this.j.materials.length,pbrMetallicRoughness:{}};const P=M.pbrMetallicRoughness,col=m.color||new THREE.Color(1,1,1);
    P.baseColorFactor=[col.r,col.g,col.b,m.transparent?(m.opacity==null?1:m.opacity):1];
    const basic=m.isMeshBasicMaterial,std=m.isMeshStandardMaterial;
    P.roughnessFactor=std?m.roughness:(m.isMeshPhongMaterial?.45:.85);P.metallicFactor=std?m.metalness:0;
    if(m.map){const ti=this.texture(m.map,'color');if(ti!=null)P.baseColorTexture={index:ti};}
    /* three reads roughness from the map's green channel, as glTF does; metalness (blue) only matters when metalness>0 */
    if(m.roughnessMap&&std&&!m.metalnessMap&&!(m.metalness>0)){const ti=this.texture(m.roughnessMap,'rough');if(ti!=null)P.metallicRoughnessTexture={index:ti};}
    if(m.normalMap&&!basic){const ti=this.texture(m.normalMap,'normal');if(ti!=null)M.normalTexture={index:ti,scale:m.normalScale?m.normalScale.x:1};}
    /* the glow's own picture (lit windows, signs, neon seams): without it the whole surface glows evenly. Tracks only (window.CR_GLB_EMISSIVE) */
    if(window.CR_GLB_EMISSIVE&&m.emissiveMap&&!basic&&m.emissive&&(m.emissive.r+m.emissive.g+m.emissive.b)>0){const ti=this.texture(m.emissiveMap,'color');if(ti!=null)M.emissiveTexture={index:ti};}
    if(m.emissive&&(m.emissive.r+m.emissive.g+m.emissive.b)>0){const s=m.emissiveIntensity==null?1:m.emissiveIntensity,mx=Math.max(m.emissive.r,m.emissive.g,m.emissive.b)*s;
      if(mx>1){M.emissiveFactor=[m.emissive.r*s/mx,m.emissive.g*s/mx,m.emissive.b*s/mx];M.extensions=Object.assign(M.extensions||{},{KHR_materials_emissive_strength:{emissiveStrength:mx}});this.ext.add('KHR_materials_emissive_strength');}
      else M.emissiveFactor=[m.emissive.r*s,m.emissive.g*s,m.emissive.b*s];}
    if(basic){M.extensions=Object.assign(M.extensions||{},{KHR_materials_unlit:{}});this.ext.add('KHR_materials_unlit');}
    if(m.transparent&&(m.opacity<.999||m.map))M.alphaMode='BLEND';else if(m.alphaTest>0){M.alphaMode='MASK';M.alphaCutoff=m.alphaTest;}
    if(m.side===THREE.DoubleSide)M.doubleSided=true;
    this.j.materials.push(M);const mi=this.j.materials.length-1;this.mats.set(key,mi);return mi;}
  /* parts: [{P:Float32Array,N:Float32Array,UV:Float32Array|null,C:Float32Array|null(rgb),I:Uint32Array}] sharing one material */
  primitive(parts,mi,useUV,useC){let nv=0,ni=0;for(const q of parts){nv+=q.P.length/3;ni+=q.I.length;}if(!nv||!ni)return null;
    const P=new Float32Array(nv*3),N=new Float32Array(nv*3),UV=useUV?new Float32Array(nv*2):null,C=useC?new Float32Array(nv*3):null,I=nv>65535?new Uint32Array(ni):new Uint16Array(ni);let vo=0,io=0;
    const mn=[1e30,1e30,1e30],mx=[-1e30,-1e30,-1e30];
    for(const q of parts){const n=q.P.length/3;P.set(q.P,vo*3);N.set(q.N,vo*3);if(UV){if(q.UV)UV.set(q.UV,vo*2);}if(C){if(q.C)C.set(q.C,vo*3);else C.fill(1,vo*3,(vo+n)*3);}
      for(let i=0;i<q.I.length;i++)I[io+i]=q.I[i]+vo;for(let i=0;i<n;i++)for(let a=0;a<3;a++){const v=q.P[i*3+a];if(v<mn[a])mn[a]=v;if(v>mx[a])mx[a]=v;}vo+=n;io+=q.I.length;}
    /* weld identical vertices (same position, normal, colour, uv): merged batches arrive unshared */
    const key=new Map(),rm=new Int32Array(nv);let w=0;const wP=[],wN=[],wU=[],wC=[];
    for(let i=0;i<nv;i++){const k=Math.round(P[i*3]*64)+','+Math.round(P[i*3+1]*64)+','+Math.round(P[i*3+2]*64)+'|'+Math.round(N[i*3]*127)+','+Math.round(N[i*3+1]*127)+','+Math.round(N[i*3+2]*127)+(C?'|'+Math.round(C[i*3]*255)+','+Math.round(C[i*3+1]*255)+','+Math.round(C[i*3+2]*255):'')+(UV?'|'+Math.round(UV[i*2]*4096)+','+Math.round(UV[i*2+1]*4096):'');
      let r=key.get(k);if(r===undefined){r=w++;key.set(k,r);wP.push(P[i*3],P[i*3+1],P[i*3+2]);wN.push(N[i*3],N[i*3+1],N[i*3+2]);if(UV)wU.push(UV[i*2],UV[i*2+1]);if(C)wC.push(C[i*3],C[i*3+1],C[i*3+2]);}rm[i]=r;}
    const I2=w>65535?new Uint32Array(ni):new Uint16Array(ni);for(let i=0;i<ni;i++)I2[i]=rm[I[i]];
    const Pw=new Float32Array(wP),Nw=new Float32Array(wN);let Cw=null;if(C){Cw=new Uint8Array(w*4);for(let i=0;i<w;i++){Cw[i*4]=Math.round(Math.min(1,Math.max(0,wC[i*3]))*255);Cw[i*4+1]=Math.round(Math.min(1,Math.max(0,wC[i*3+1]))*255);Cw[i*4+2]=Math.round(Math.min(1,Math.max(0,wC[i*3+2]))*255);Cw[i*4+3]=255;}}
    const at={POSITION:this.acc(Pw,'VEC3',5126,w,34962,[mn,mx]),NORMAL:this.acc(Nw,'VEC3',5126,w,34962)};if(UV)at.TEXCOORD_0=this.acc(new Float32Array(wU),'VEC2',5126,w,34962);
    if(Cw){const ai=this.acc(Cw,'VEC4',5121,w,34962);this.j.accessors[ai].normalized=true;at.COLOR_0=ai;}
    this.stats.tris+=ni/3;this.stats.verts+=w;this.stats.rawVerts=(this.stats.rawVerts||0)+nv;return {attributes:at,indices:this.acc(I2,'SCALAR',I2 instanceof Uint32Array?5125:5123,ni,34963),material:mi,mode:4};}
  node(name,prims,extra){const n={name};if(prims&&prims.length){this.j.meshes.push({name,primitives:prims});n.mesh=this.j.meshes.length-1;}Object.assign(n,extra||{});this.j.nodes.push(n);return this.j.nodes.length-1;}
  gltf(binName){if(this.ext.size)this.j.extensionsUsed=[...this.ext];this.j.buffers=[{byteLength:this.len,uri:binName}];for(const k of ['images','textures','samplers','materials','meshes'])if(!this.j[k].length)delete this.j[k];
    const bin=new Uint8Array(this.len);let o=0;for(const c of this.chunks){bin.set(c,o);o+=c.byteLength;}return {json:JSON.stringify(this.j),bin};}
  glb(){if(this.ext.size)this.j.extensionsUsed=[...this.ext];this.j.buffers=[{byteLength:this.len}];for(const k of ['images','textures','samplers','materials','meshes'])if(!this.j[k].length)delete this.j[k];
    let js=new TextEncoder().encode(JSON.stringify(this.j));const jp=(4-js.length%4)%4;if(jp){const t=new Uint8Array(js.length+jp);t.set(js);t.fill(32,js.length);js=t;}
    const bin=new Uint8Array(this.len+((4-this.len%4)%4));let o=0;for(const c of this.chunks){bin.set(c,o);o+=c.byteLength;}
    const total=12+8+js.length+8+bin.length,out=new Uint8Array(total),dv=new DataView(out.buffer);dv.setUint32(0,0x46546C67,true);dv.setUint32(4,2,true);dv.setUint32(8,total,true);
    dv.setUint32(12,js.length,true);dv.setUint32(16,0x4E4F534A,true);out.set(js,20);dv.setUint32(20+js.length,bin.length,true);dv.setUint32(24+js.length,0x004E4942,true);out.set(bin,28+js.length);return out;}
}

/* one mesh (or one instance) → baked parts per material, in the space of `rootInv` */
const _m=new THREE.Matrix4(),_n=new THREE.Matrix3(),_v=new THREE.Vector3(),_c=new THREE.Color();
function bake(o,mat4,geo,mat,group,instColor){const pa=geo.attributes.position;if(!pa)return null;const na=geo.attributes.normal,ua=geo.attributes.uv,ca=geo.attributes.color,ix=geo.index;
  let s=0,e=ix?ix.count:pa.count;if(group){s=group.start;e=Math.min(e,group.start+group.count);}
  const flip=mat4.determinant()<0;_n.getNormalMatrix(mat4);
  const tex=mat.map||mat.normalMap||mat.emissiveMap||mat.alphaMap||mat.roughnessMap;let uvM=null;if(tex&&ua){tex.updateMatrix();uvM=tex.matrix;}
  const la=geo.attributes.livColor;const vc=!!(mat.vertexColors&&ca),useC=vc||!!instColor||!!la;
  /* re-index the used range */const remap=new Map(),P=[],N=[],UV=[],C=[],I=[];
  const get=i=>{let r=remap.get(i);if(r!==undefined)return r;r=P.length/3;remap.set(i,r);
    _v.fromBufferAttribute(pa,i).applyMatrix4(mat4);P.push(_v.x,_v.y,_v.z);
    if(na){_v.fromBufferAttribute(na,i).applyMatrix3(_n).normalize();N.push(_v.x,_v.y,_v.z);}else N.push(0,1,0);
    if(ua){let u=ua.getX(i),v=ua.getY(i);if(uvM){const e=uvM.elements,uu=e[0]*u+e[3]*v+e[6],vv=e[1]*u+e[4]*v+e[7];u=uu;v=vv;}UV.push(u,v);}
    if(useC){let r=1,g=1,b=1;if(vc){r=ca.getX(i);g=ca.getY(i);b=ca.getZ(i);}if(instColor){r*=instColor.r;g*=instColor.g;b*=instColor.b;}if(la){r*=la.getX(i);g*=la.getY(i);b*=la.getZ(i);}C.push(r,g,b);}return r;};
  for(let t=s;t+2<e;t+=3){const a=ix?ix.getX(t):t,b=ix?ix.getX(t+1):t+1,c=ix?ix.getX(t+2):t+2;if(flip)I.push(get(a),get(c),get(b));else I.push(get(a),get(b),get(c));}
  if(!na){/* flat normals from faces */for(let t=0;t<I.length;t+=3){const ia=I[t]*3,ib=I[t+1]*3,ic=I[t+2]*3;const ux=P[ib]-P[ia],uy=P[ib+1]-P[ia+1],uz=P[ib+2]-P[ia+2],vx=P[ic]-P[ia],vy=P[ic+1]-P[ia+1],vz=P[ic+2]-P[ia+2];let nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;const l=Math.hypot(nx,ny,nz)||1;for(const q of [ia,ib,ic]){N[q]=nx/l;N[q+1]=ny/l;N[q+2]=nz/l;}}}
  return {P:new Float32Array(P),N:new Float32Array(N),UV:UV.length?new Float32Array(UV):null,C:useC?new Float32Array(C):null,I:new Uint32Array(I)};}

function shaded(m){return m&&(m.isMeshStandardMaterial||m.isMeshBasicMaterial||m.isMeshLambertMaterial||m.isMeshPhongMaterial);}
const visUp=(o,stop)=>{for(let p=o;p&&p!==stop;p=p.parent)if(!p.visible)return false;return true;};

/* collect: objects under `root`; cellOf(meshOrInstancePosition)→cell key; bucket per material+cell+shadow */
function collect(G,root,space,opts){opts=opts||{};const buckets=new Map(),inv=new THREE.Matrix4().copy(space).invert();root.updateMatrixWorld(true);
  const add=(key,mi,useUV,part,meta)=>{let b=buckets.get(key);if(!b){b={mi,useUV,useC:false,parts:[],meta};buckets.set(key,b);}if(part.C)b.useC=true;if(!part.UV)b.useUV=b.useUV&&false;b.parts.push(part);};
  root.traverse(o=>{if(!o.isMesh)return;if(opts.skip&&opts.skip(o))return;if(!visUp(o,opts.visStop))return;
    const mats=Array.isArray(o.material)?o.material:[o.material],groups=Array.isArray(o.material)&&o.geometry.groups.length?o.geometry.groups:[null];
    for(const gr of groups){const mat=gr?mats[gr.materialIndex]:mats[0];if(!shaded(mat)||mat.visible===false){G.stats.skipped[(mat&&mat.type)||'none']=(G.stats.skipped[(mat&&mat.type)||'none']||0)+1;continue;}
      if(mat.colorWrite===false||mat.opacity<.02)continue;
      const inst=o.isInstancedMesh?o.count:1;
      for(let i=0;i<inst;i++){_m.copy(o.matrixWorld);if(o.isInstancedMesh){const im=new THREE.Matrix4();o.getMatrixAt(i,im);_m.multiply(im);}const W=new THREE.Matrix4().multiplyMatrices(inv,_m);
        let ic=null;if(o.isInstancedMesh&&o.instanceColor){ic=new THREE.Color();o.getColorAt(i,ic);}
        const part=bake(o,W,o.geometry,mat,gr,ic);if(!part||!part.I.length)continue;
        const vc=!!part.C,mi=G.material(mat,vc),cx=W.elements[12],cz=W.elements[14],cell=opts.cell?opts.cell(o,cx,cz):'all',cs=o.castShadow?1:0;
        add(mi+'|'+cell+'|'+cs+'|'+(part.UV?1:0),mi,!!part.UV,part,{cell,cs});}}});
  return buckets;}

window.__exportTrack=function(name){const G=new GLB();G.extDir=name+'_tex';
  /* show every scenery cell the distance culling hid */for(const ch of (typeof detailChunks!=='undefined'?detailChunks:[]))for(const m of ch.ms)m.visible=true;
  const kartSet=new Set(karts.map(k=>k.m&&k.m.g).filter(Boolean));
  /* things that move are drawn by the game, not baked into the track: traffic, walkers, the train's wagons, rolling meatballs, item boxes */
  const hz=__hazSet();
  const skip=o=>{for(let p=o;p;p=p.parent){if(kartSet.has(p)||hz.has(p))return true;if(p.userData&&(p.userData.isBox||p.userData.box||p.userData.fx||p.userData.dyn||p.userData.hdProp))return true;}return false;};
  /* the ground gets its own material name, so the PC can give it a finished surface */
  try{if(typeof TERR!=='undefined'&&TERR&&TERR.chunks)for(const c of TERR.chunks)if(c.material)c.material.name='terrain';}catch(e){}
  const CELL=700,DSET=new Set();for(const ch of (typeof detailChunks!=='undefined'?detailChunks:[]))for(const m of ch.ms)DSET.add(m);
  const cellOf=(o,x,z)=>Math.floor(x/CELL)+'_'+Math.floor(z/CELL)+(DSET.has(o)?'_d':'');
  const buckets=collect(G,world,new THREE.Matrix4(),{skip,cell:cellOf,visStop:null});
  /* nodes: one per cell+material, named so Godot can read cell and shadow flags */
  const cells=new Map();for(const [k,b] of buckets){const pr=G.primitive(b.parts,b.mi,b.useUV,b.useC);if(!pr)continue;const nm='c'+b.meta.cell+(b.meta.cs?'':'_noshadow')+'_m'+b.mi;const ni=G.node(nm,[pr]);
    let c=cells.get(b.meta.cell);if(!c){c=[];cells.set(b.meta.cell,c);}c.push(ni);}
  for(const [cell,list] of cells){const ni=G.node('cell_'+cell,null,{children:list});G.j.scenes[0].nodes.push(ni);}
  const out=G.gltf(name+'.bin');return {json:out.json,bin:u8ToB64(out.bin),files:G.files||[],stats:Object.assign(G.stats,{nodes:G.j.nodes.length,materials:(G.j.materials||[]).length,images:(G.j.images||[]).length,binBytes:out.bin.length,cells:cells.size})};};

/* run a livery material's shader once per vertex (one point per pixel) and read the colours back */
function bakeLivery(mesh){const m=mesh.material;if(!m||Array.isArray(m)||!m.userData||!m.userData.livA||!m.onBeforeCompile)return false;
  const fake={uniforms:{},vertexShader:'',fragmentShader:''};m.onBeforeCompile(fake);const U=fake.uniforms;if(!U.uLA)return false;
  const geo=mesh.geometry,pa=geo.attributes.position,na=geo.attributes.normal,n=pa.count,W=1024,H=Math.ceil(n/W);
  const g=new THREE.BufferGeometry();g.setAttribute('position',pa);if(na)g.setAttribute('normal',na);const vid=new Float32Array(n);for(let i=0;i<n;i++)vid[i]=i;g.setAttribute('vid',new THREE.BufferAttribute(vid,1));
  const decl='vec3 vNormal=vec3(0.,0.,1.);\n';/* view-independent: the paint sheen is left to the renderer */
  const mat=new THREE.ShaderMaterial({uniforms:Object.assign({rtSize:{value:new THREE.Vector2(W,H)}},U),
    vertexShader:'attribute float vid;uniform vec2 rtSize;varying vec3 vLivP;varying vec3 vLivN;\nvoid main(){vLivP=position;vLivN=normal;float x=mod(vid,rtSize.x),y=floor(vid/rtSize.x);gl_Position=vec4((x+.5)/rtSize.x*2.-1.,(y+.5)/rtSize.y*2.-1.,0.,1.);gl_PointSize=1.;}',
    fragmentShader:LIV_FRAG+'\n'+decl+'vec3 vViewPosition=vec3(0.,0.,-30.);\nvoid main(){vec4 diffuseColor=vec4(1.);\n'+LIV_BODY+'\ngl_FragColor=vec4(diffuseColor.rgb,1.);}',depthTest:false,depthWrite:false});
  const pts=new THREE.Points(g,mat);pts.frustumCulled=false;const sc=new THREE.Scene();sc.add(pts);
  const rt=new THREE.WebGLRenderTarget(W,H,{type:THREE.FloatType,minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter,depthBuffer:false});
  const prev=renderer.getRenderTarget(),pa2=renderer.autoClear;renderer.setRenderTarget(rt);renderer.setClearColor(0xff00ff,1);renderer.clear();renderer.render(sc,new THREE.Camera());
  const px=new Float32Array(W*H*4);renderer.readRenderTargetPixels(rt,0,0,W,H,px);renderer.setRenderTarget(prev);rt.dispose();mat.dispose();
  const out=new Float32Array(n*3);let bad=0;for(let i=0;i<n;i++){out[i*3]=px[i*4];out[i*3+1]=px[i*4+1];out[i*3+2]=px[i*4+2];if(px[i*4]===1&&px[i*4+1]===0&&px[i*4+2]===1)bad++;}
  geo.setAttribute('livColor',new THREE.BufferAttribute(out,3));return {n,bad};}

window.__bakeLivery=bakeLivery;
/* ================= garage: every body, wheel, glider and driver as separate parts ================= */
/* Bodies are built with marker colours (a paint and a stripe nobody else uses) and the game's bake() is
   patched for the export (see __garageBegin) so the paint, the darker trim and the stripe stay separate,
   named materials (g_paint, g_dark, g_stripe). The PC build recolours them for any paint or livery. */
const GM={paint:'#fe01fd',stripe:'#01fe03'};
const ctag=c=>Math.round(c.r*1000)+','+Math.round(c.g*1000)+','+Math.round(c.b*1000);
const parts=(G,root,space,skip)=>{const b=collect(G,root,space,{skip,visStop:null});const pr=[];for(const [k,bk] of b){const p=G.primitive(bk.parts,bk.mi,bk.useUV,bk.useC);if(p)pr.push(p);}return pr;};
const under=(o,root)=>{for(let p=o;p;p=p.parent)if(p===root)return true;return false;};
const rel=(o,g)=>new THREE.Matrix4().copy(g.matrixWorld).invert().multiply(o.matrixWorld);
function reset(m){const g=m.g;g.position.set(0,0,0);g.rotation.set(0,0,0);g.scale.set(1,1,1);if(m.gl){m.gl.visible=false;}if(m.lo)m.lo.visible=false;if(m.bub)m.bub.visible=false;if(m.ice)m.ice.visible=false;(m.flames||[]).forEach(f=>f.visible=false);m.tilt.visible=true;g.updateMatrixWorld(true);}
window.__garageInfo=function(){
  const mkCol=new THREE.Color(GM.paint),stCol=new THREE.Color(GM.stripe),dkCol=new THREE.Color(shade(GM.paint,-.45));
  return {mark:{paint:GM.paint,stripe:GM.stripe,dark:shade(GM.paint,-.45),tags:{paint:ctag(mkCol),stripe:ctag(stCol),dark:ctag(dkCol)}},
    bodies:BODIES.map(b=>({id:b.id,name:b.name,desc:b.desc,st:b.st,sf:b.sf||1,bike:!!b.bike,bw:b.bw||null,car:CAR_BODIES.includes(b.id)})),
    wheels:WHEELS.map(w=>({id:w.id,name:w.name,desc:w.desc,st:w.st,r:w.r,wz:w.wz,pack:w.pack||null})),
    gliders:GLIDERS.map(g=>({id:g.id,name:g.name,desc:g.desc,st:g.st,sink:g.sink,air:g.air})),
    paints:PAINTS,paintNames:PAINT_NAMES,liveries:LIVERIES.map(l=>Object.assign({},l)),livCats:LIV_CATS,statW:STAT_W,statNames:STAT_NAMES,statShort:STAT_SHORT,
    racers:RACERS.map(r=>({name:r.name,color:r.color,stripe:r.stripe,top:r.top,iris:r.iris})),shadeDark:-.45};};
/* the patched bake: paint, dark trim and stripe (marker colours) keep their own named materials */
window.__garageBake=function(S){const mk=new THREE.Color(GM.paint),st=new THREE.Color(GM.stripe),dk=new THREE.Color(shade(GM.paint,-.45));const near=(a,b)=>Math.abs(a.r-b.r)+Math.abs(a.g-b.g)+Math.abs(a.b-b.b)<.004;
  S.traverse(o=>{if(!o.isMesh)return;for(const m of (Array.isArray(o.material)?o.material:[o.material])){if(!m||!m.color||m.map)continue;
    if(near(m.color,mk)){m.vertexColors=true;m.name='g_paint';}else if(near(m.color,dk)){m.vertexColors=true;m.name='g_dark';}else if(near(m.color,st)){m.vertexColors=true;m.name='g_stripe';}}});};
/* one body: its geometry without wheels, driver or glider, plus the pack wheels of cars and bikes */
window.__exportBody=function(b){const G=new GLB();const pi=PAINTS.length-1;const m=buildKart({ri:0,b,w:0,g:0,p:pi,t:'',hq:1});reset(m);const g=m.g;
  const yaws=m.wheels.map(w=>w.spin.parent),front=new Set(m.front||[]);
  const skip=o=>yaws.some(y=>under(o,y))||under(o,m.drv)||(m.lo&&under(o,m.lo))||(m.gl&&under(o,m.gl))||(m.bub&&under(o,m.bub))||(m.ice&&under(o,m.ice))||(m.flames||[]).some(f=>under(o,f))||(m.hglow&&o===m.hglow);
  const top=[G.node('body',parts(G,g,g.matrixWorld,skip))];
  /* where the livery pattern is computed: the paint mesh's own space */
  let paintM=null,box=null;g.traverse(o=>{if(!paintM&&o.isMesh&&!skip(o)&&o.material&&o.material.name==='g_paint'){paintM=o;}});
  /* the imported cars keep their own paint mesh (not baked): it wears the marker paint colour */
  if(!paintM){const mk=new THREE.Color(GM.paint);g.traverse(o=>{if(!paintM&&o.isMesh&&!skip(o)&&o.material&&!Array.isArray(o.material)&&o.material.color&&Math.abs(o.material.color.r-mk.r)+Math.abs(o.material.color.g-mk.g)+Math.abs(o.material.color.b-mk.b)<.004)paintM=o;});}
  let liv=null;if(paintM){const a=paintM.geometry.attributes.position.array;let x0=1e9,x1=-1e9,zw=0,yt=-1e9,y0=1e9;for(let i=0;i<a.length;i+=3){x0=Math.min(x0,a[i]);x1=Math.max(x1,a[i]);zw=Math.max(zw,Math.abs(a[i+2]));yt=Math.max(yt,a[i+1]);y0=Math.min(y0,a[i+1]);}
    let cfg={};try{const dm=new Proxy({},{get:(t,k)=>k in t?t[k]:(t[k]=new THREE.MeshStandardMaterial())});cfg=BODY_FN[BODIES[b].id](new THREE.Group(),dm,RACERS[0],0,new THREE.Group())||{};}catch(e){}
    const car=!!cfg.car;liv={box:car?carDims(cfg.car):[x0,x1,zw,yt],belt:car?(cfg.belt||1.5):y0+(yt-y0)*.5,numPos:car?(cfg.numPos||[0,1]):[(x0+x1)/2,y0+(yt-y0)*.5],xf:rel(paintM,g).invert().toArray(),car};}
  /* cars on their standard wheels and bikes: their own wheel models */
  const pw=[];m.wheels.forEach((w,i)=>{const yaw=w.spin.parent,sp=w.spin;const ch=sp.children[0];const packed=ch&&ch.isMesh&&ch.geometry&&ch.material&&!(ch.scale.x!==1&&ch.scale.y!==1);
    const pr=parts(G,sp,sp.matrixWorld,null);if(pr.length){const nm='pw'+i;top.push(G.node(nm,pr));pw.push(nm);}});
  const root=G.node('kart',null,{children:top});G.j.scenes[0].nodes.push(root);const bytes=G.glb();
  return {b64:u8ToB64(bytes),liv,pw,stats:Object.assign(G.stats,{bytes:bytes.length})};};
/* every wheel type, both sides, unscaled, in the wheel's own space */
window.__exportWheel=function(w){const G=new GLB();const pi=PAINTS.length-1;const m=buildKart({ri:0,b:0,w,g:0,p:pi,t:'',hq:1});reset(m);const top=[];
  const done={};m.wheels.forEach(q=>{const sp=q.spin,yaw=sp.parent,side=yaw.position.z<0?'L':'R';if(done[side])return;done[side]=1;const wh=sp.children[0];if(!wh)return;
    const pr=parts(G,wh,wh.matrixWorld,null);if(pr.length)top.push(G.node('wheel_'+side,pr));});
  const root=G.node('wheels',null,{children:top});G.j.scenes[0].nodes.push(root);const bytes=G.glb();return {b64:u8ToB64(bytes),stats:Object.assign(G.stats,{bytes:bytes.length})};};
window.__exportGlider=function(gi){const G=new GLB();const pi=PAINTS.length-1;const m=buildKart({ri:0,b:0,w:0,g:gi,p:pi,t:'',hq:1});reset(m);const gl=m.gl;gl.visible=true;gl.scale.setScalar(1);gl.updateMatrixWorld(true);
  const pr=parts(G,gl,gl.matrixWorld,null);const root=G.node('glider',pr);G.j.scenes[0].nodes.push(root);const bytes=G.glb();return {b64:u8ToB64(bytes),stats:Object.assign(G.stats,{bytes:bytes.length})};};
window.__exportDriver=function(ri){const G=new GLB();const m=buildKart({ri,b:0,w:0,g:0,p:0,t:'',hq:1});reset(m);const d=m.drv;
  const pr=parts(G,d,d.matrixWorld,null);const root=G.node('driver',pr);G.j.scenes[0].nodes.push(root);const bytes=G.glb();return {b64:u8ToB64(bytes),stats:Object.assign(G.stats,{bytes:bytes.length})};};
/* where things go for one body with one wheel type: wheels, lift, glider, bubble, effects */
window.__placeBW=function(b,w){const m=buildKart({ri:0,b,w,g:0,p:0,t:'',hq:0});reset(m);const g=m.g,front=new Set(m.front||[]);const B=m.drv.parent.parent;
  const wl=m.wheels.map((q,i)=>{const sp=q.spin,yaw=sp.parent,wh=sp.children[0];const ys=yaw.getWorldPosition(new THREE.Vector3());
    const ax=[];yaw.children.forEach(c=>{if(c!==sp&&c.isMesh)ax.push({p:c.position.toArray(),s:c.scale.toArray(),r:c.rotation.toArray().slice(0,3)});});
    return {i,front:front.has(yaw),x:ys.x,y:ys.y,z:ys.z,r:q.r,s:wh?wh.scale.toArray():[1,1,1],axle:ax};});
  const v=a=>a?(a.isVector3?a.toArray():a):null;
  return {L:B.position.y,glY:m.gl?m.gl.position.y:0,bub:m.bub?{x:m.bub.position.x,y:m.bub.position.y,z:m.bub.position.z,s:m.bub.scale.x}:null,wheels:wl,top:m.top,axF:m.axF,axR:m.axR,axW:m.axW,sf:m.sf,hover:m.hover,bike:m.bike,
    fxL:(m.fxL||[]).map(v),fxP:(m.fxP||[]).map(v),smoke:v(m.smoke),flames:(m.flames||[]).map((f,i)=>({i,inner:i%2===1,x:f.position.x,y:f.position.y,z:f.position.z,fl:f.userData.fl}))};};
/* the driver's seat for one body and one racer (a 4x4 matrix in kart space) */
window.__placeDrv=function(b,ri){const m=buildKart({ri,b,w:0,g:0,p:0,t:'',hq:0});reset(m);return rel(m.drv,m.g).toArray();};
/* the shared livery textures: race numbers and decals */
window.__livTex=async function(){const out={};for(const [k,t] of [['num',numTex],['dec',decTex]]){const im=t.image;const c=document.createElement('canvas');c.width=im.width;c.height=im.height;c.getContext('2d').drawImage(im,0,0);out[k+'.png']=c.toDataURL('image/png').split(',')[1];}
  /* wrap liveries painted from a picture (the Onyx's race wrap): the picture itself, as the web loads it */
  for(const lv of LIVERIES){if(!lv.tex||out[lv.tex+'.jpg'])continue;const r=await fetch(texSrc(PROP_TEX[lv.tex]));out[lv.tex+'.jpg']=u8ToB64(new Uint8Array(await r.arrayBuffer()));}
  return out;};

window.__exportKart=function(spec){const G=new GLB();const m=buildKart(spec);const g=m.g;g.position.set(0,0,0);g.rotation.set(0,0,0);g.scale.set(1,1,1);g.updateMatrixWorld(true);
  m.tilt.visible=true;if(m.lo)m.lo.visible=false;if(m.gl)m.gl.visible=false;if(m.bub)m.bub.visible=false;if(m.ice)m.ice.visible=false;(m.flames||[]).forEach(f=>{if(f&&f.visible!==undefined)f.visible=false;});
  const livStats=[];g.traverse(o=>{if(o.isMesh){const r=bakeLivery(o);if(r)livStats.push(r);}});
  const wheelOf=new Map();m.wheels.forEach((w,i)=>wheelOf.set(w.spin,i));const front=new Set(m.front||[]);
  const findWheel=o=>{for(let p=o;p&&p!==g;p=p.parent)if(wheelOf.has(p))return wheelOf.get(p);return -1;};
  const top=[];
  /* body: everything not under a wheel spin group, in kart space */
  const body=collect(G,g,g.matrixWorld,{skip:o=>findWheel(o)>=0||(m.lo&&(()=>{for(let p=o;p;p=p.parent)if(p===m.lo)return true;return false;})()),visStop:null});
  const bp=[];for(const [k,b] of body){const pr=G.primitive(b.parts,b.mi,b.useUV,b.useC);if(pr)bp.push(pr);}top.push(G.node('body',bp));
  const wheels=[];m.wheels.forEach((w,i)=>{const yaw=w.spin.parent,ys=yaw.getWorldPosition(new THREE.Vector3());const sp=new THREE.Matrix4().makeTranslation(ys.x,ys.y,ys.z);
    const bk=collect(G,w.spin,sp,{visStop:null});const pr=[];for(const [k,b] of bk){const p=G.primitive(b.parts,b.mi,b.useUV,b.useC);if(p)pr.push(p);}
    const isF=front.has(yaw);const nm='wheel_'+(isF?'F':'R')+(ys.z<0?'L':'R');top.push(G.node(nm,pr,{translation:[ys.x,ys.y,ys.z]}));wheels.push({name:nm,front:isF,x:ys.x,y:ys.y,z:ys.z,r:w.r});});
  const root=G.node('kart',null,{children:top});G.j.scenes[0].nodes.push(root);
  const bytes=G.glb();return {livery:livStats,b64:u8ToB64(bytes),meta:{scale:KS*(m.sf||1),sf:m.sf||1,KS,wheels,axF:m.axF,axR:m.axR,axW:m.axW,top:m.top,bike:!!m.bike,hover:m.hover||0,drvY:m.drvY||0,
      fxL:(m.fxL||[]).map(v=>[v.x,v.y,v.z]),fxP:(m.fxP||[]).map(v=>[v.x,v.y,v.z]),smoke:m.smoke?[m.smoke.x,m.smoke.y,m.smoke.z]:null,
      bub:m.bub?{x:m.bub.position.x,y:m.bub.position.y,z:m.bub.position.z,s:m.bub.scale.x}:null,
      flames:(m.flames||[]).map((f,i)=>{const w=new THREE.Vector3();f.getWorldPosition(w);return {i,inner:i%2===1,x:w.x,y:w.y,z:w.z,fl:f.userData.fl||null,lx:f.position.x};}),
      tiltPos:[m.tilt.position.x,m.tilt.position.y,m.tilt.position.z]},stats:Object.assign(G.stats,{bytes:bytes.length})};};

window.__exportData=function(step){step=step||10;const def=MAPS[mapIdx];const R=def.R;
  const tr=track.map(p=>[+p.x.toFixed(3),+p.y.toFixed(3),+p.nx.toFixed(5),+p.ny.toFixed(5),+p.tx.toFixed(5),+p.ty.toFixed(5),+p.ang.toFixed(5),p.wall|0,p.pond|0,p.open?1:0,+(p.ey||0).toFixed(3),p.flo===undefined?null:+p.flo.toFixed(2),p.fhi===undefined?null:+p.fhi.toFixed(2)]);
  const n=Math.ceil(2*R/step)+1,H=new Int16Array(n*n);let hmin=1e9,hmax=-1e9;for(let j=0;j<n;j++)for(let i=0;i<n;i++){const x=-R+i*step,z=-R+j*step,h=groundAt(x,z);if(h<hmin)hmin=h;if(h>hmax)hmax=h;H[j*n+i]=Math.max(-32767,Math.min(32767,Math.round(h*20)));}
  const sunDir=new THREE.Vector3().subVectors(sun.position,sun.target.position).normalize();
  const hemi=(()=>{let h=null;scene.traverse(o=>{if(o.isHemisphereLight&&!h)h=o;});return h;})();
  const amb=(()=>{let h=null;scene.traverse(o=>{if(o.isAmbientLight&&!h)h=o;});return h;})();
  const fog=scene.fog;const bg=scene.background&&scene.background.isColor?scene.background:null;
  return {map:def.id,name:def.name,R,RIM,N,RW,CURB,WALLD,KS,BASE0,ACCEL,TURN,LAPS:3,KERB_H,STEP,classMul:CLASSES.medium.mul,
    track:tr,ramps:ramps.map(r=>({j:r.j,len:r.len,h:r.h,w:r.w,glide:!!r.glide})),pads:pads.map(p=>({j:p.j,lat:p.lat,w:p.w||16})),
    obstacles:obstacles.filter(o=>!o.ghost&&!o.mesh?.userData?.dyn).map(o=>({x:+o.x.toFixed(2),y:+o.y.toFixed(2),r:o.r,h:o.h})),
    grid:karts.map(k=>({x:+k.x.toFixed(3),y:+k.y.toFixed(3),a:+k.a.toFixed(5),wy:+k.wy.toFixed(3),player:k===player})),
    height:{x0:-R,z0:-R,step,n,scale:20,min:hmin,max:hmax,b64:u8ToB64(new Uint8Array(H.buffer))},
    light:{sunDir:sunDir.toArray(),sunColor:'#'+sun.color.getHexString(),sunI:sun.intensity,hemiSky:hemi?'#'+hemi.color.getHexString():null,hemiGround:hemi?'#'+hemi.groundColor.getHexString():null,hemiI:hemi?hemi.intensity:0,ambColor:amb?'#'+amb.color.getHexString():null,ambI:amb?amb.intensity:0,
      fog:fog?{color:'#'+fog.color.getHexString(),near:fog.near,far:fog.far,density:fog.density}:null,bg:bg?'#'+bg.getHexString():null,exposure:renderer.toneMappingExposure},
    sky:(()=>{let u=null;world.traverse(o=>{const m=o.material;if(!u&&m&&m.isShaderMaterial&&m.uniforms&&m.uniforms.top&&m.uniforms.hor)u=m.uniforms;});if(!u)return null;const c=x=>x&&x.value&&x.value.isColor?'#'+x.value.getHexString():null;return {top:c(u.top),hor:c(u.hor),bot:c(u.bot),sunCol:c(u.sunCol),sunDir:u.sunDir&&u.sunDir.value&&u.sunDir.value.toArray?u.sunDir.value.toArray():null};})(),
    gridProg:karts.map(k=>k.prog),
    glide:(typeof GLIDE!=='undefined'&&GLIDE)?{j0:GLIDE.j0,j1:GLIDE.j1,rj:GLIDE.rj,long:!!GLIDE.long,gy:(()=>{const n=Math.ceil(2*R/step)+1,A=new Int16Array(n*n);for(let j=0;j<n;j++)for(let i=0;i<n;i++){let v=-32768;try{const g=glideY(-R+i*step,-R+j*step);if(isFinite(g))v=Math.max(-32767,Math.min(32767,Math.round(g*20)));}catch(e){}A[j*n+i]=v;}return u8ToB64(new Uint8Array(A.buffer));})()}:null,
    pit:(typeof PITS!=='undefined'&&PITS.length)?(()=>{const n=Math.ceil(2*R/step)+1,A=new Int16Array(n*n);for(let j=0;j<n;j++)for(let i=0;i<n;i++)A[j*n+i]=Math.max(0,Math.min(32767,Math.round(pitAt(-R+i*step,-R+j*step)*20)));return u8ToB64(new Uint8Array(A.buffer));})():null,
    loopsD:(typeof LOOPS!=='undefined'?LOOPS:[]).map(L=>({j:L.j,full:!!L.full,lat0:L.lat0,W:L.W,S:L.S})),
    shortsD:(typeof SHORTS!=='undefined'?SHORTS:[]).map(c=>({a:c.a,b:c.b,s:c.s,route:!!c.route,n:c.n,w:c.w||SCW,pts:c.pts.map(p=>[+p.x.toFixed(2),+p.y.toFixed(2),+p.tx.toFixed(4),+p.ty.toFixed(4),+p.nx.toFixed(4),+p.ny.toFixed(4)])})),
    pondLim:(typeof POND!=='undefined'&&POND)?CURB+2*POND.GR*POND.SZ+30:null,
    statMods:(()=>{try{return statMods({ri:1,b:BODIES.findIndex(b=>b.id==='hyper'),w:0,g:0,p:0,t:''});}catch(e){return null;}})(),
    hasGlide:typeof GLIDE!=='undefined'&&!!GLIDE,loops:typeof LOOPS!=='undefined'?LOOPS.length:0,shorts:typeof SHORTS!=='undefined'?SHORTS.length:0,multi:typeof MULTI!=='undefined'?!!MULTI:false,relief:typeof RELIEF!=='undefined'&&!!RELIEF,pits:typeof PITS!=='undefined'?PITS.length:0};};


/* ---- racers, items and icons for the native build ---- */
window.__exportRoster=function(seed){let s=seed||20261110;const rnd=()=>{s=(Math.imul(s,1103515245)+12345)&0x7fffffff;return s/0x7fffffff;};
  const R0=Math.random;Math.random=rnd;let builds;try{builds=RACERS.map(randomBuild);}finally{Math.random=R0;}
  return RACERS.map((r,ri)=>{const b=builds[ri];return {ri,name:r.name,color:r.color,stripe:r.stripe,build:b,body:BODIES[b.b].id,bodyName:BODIES[b.b].name,sm:statMods(b),glider:{id:GLIDERS[b.g].id,sink:GLIDERS[b.g].sink,air:GLIDERS[b.g].air}};});};
window.__statsFor=function(b){return {sm:statMods(b),glider:{id:GLIDERS[b.g].id,sink:GLIDERS[b.g].sink,air:GLIDERS[b.g].air}};};
window.__exportItems=function(){const G=new GLB();const top=[],names=[];
  const add=(name,o)=>{o.position.set(0,0,0);o.rotation.set(0,0,0);o.scale.set(1,1,1);o.updateMatrixWorld(true);const b=collect(G,o,new THREE.Matrix4(),{visStop:null});const pr=[];for(const [k,bk] of b){const p=G.primitive(bk.parts,bk.mi,bk.useUV,bk.useC);if(p)pr.push(p);}if(pr.length){top.push(G.node(name,pr));names.push(name);}};
  for(const k of Object.keys(ITEM_BUILD)){try{const o=itemProto(k).clone();o.traverse(m=>{if(m.isMesh&&m.material&&(m.material.blending===THREE.AdditiveBlending))m.visible=false;});add(k,o);}catch(e){console.warn('item',k,e);}}
  if(typeof IBX!=='undefined'&&IBX){const g=new THREE.Group();for(const q of IBX.parts)g.add(new THREE.Mesh(q[0],q[1]));add('itembox',g);const g2=new THREE.Group();for(const q of IBX.parts)g2.add(new THREE.Mesh(q[0],q[2]));add('itembox2',g2);}
  const root=G.node('items',null,{children:top});G.j.scenes[0].nodes.push(root);const bytes=G.glb();return {b64:u8ToB64(bytes),names,stats:Object.assign(G.stats,{bytes:bytes.length})};};
window.__exportIcons=function(){try{renderItemIcons();}catch(e){}const o={};for(const k of ITEM_KEYS){const m=/src="(data:image\/png;base64,[^"]+)"/.exec(SVG[k]||'');if(m)o[k]=m[1].slice(m[1].indexOf(',')+1);}return o;};
window.__exportRace=function(){return {
  boxes:boxes.map(b=>({x:+b.x.toFixed(2),y:+b.y.toFixed(2),gy:+(b.gy||0).toFixed(2),dbl:!!b.dbl,air:!!b.air,train:!!b.trainCar})),
  obstacles:obstacles.filter(o=>!o.ghost&&!o.mesh?.userData?.dyn).map(o=>({x:+o.x.toFixed(2),y:+o.y.toFixed(2),r:o.r,h:o.h,j:o.j==null?null:o.j,lat:o.lat==null?null:+(+o.lat).toFixed(2)})),
  loops:LOOPS.map(L=>({j:L.j,full:!!L.full,lat0:L.lat0,W:L.W,S:L.S,shift:L.shift,g0:L.g0,p:{x:L.p.x,y:L.p.y,tx:L.p.tx,ty:L.p.ty,nx:L.p.nx,ny:L.p.ny,ang:L.p.ang}})),
  loopK:{DIV:LOOP_DIV,DH:LOOP_DH,TAP:LOOP_TAP,R:LOOPR},
  haz:{traffic:(HAZ.traffic||[]).length,walk:(HAZ.walk||[]).length,rollers:(typeof rollers!=='undefined'?rollers.length:0),train:!!HAZ.train},
  L:T.L,racers:RACERS.map(r=>({name:r.name,color:r.color,stripe:r.stripe})),
  diffs:DIFFS,itemPower:ITEM_POWER,
  bend:track.map(p=>p.bend==null?null:+p.bend.toFixed(4))};};

function __hazSet(){const hz=new Set();try{HAZ.traffic.forEach(c=>hz.add(c.m.g));HAZ.walk.forEach(w=>hz.add(w.g));if(HAZ.train)HAZ.train.cars.forEach(c=>hz.add(c.g));}catch(e){}try{rollers.forEach(r=>hz.add(r.m));}catch(e){}return hz;}
/* moving hazards: models (glb) + where they start and how they move */
window.__exportHaz=function(){const G=new GLB();const top=[];const data={traffic:[],rollers:[],walk:[],train:null};
  const prims=b=>{const out=[];for(const [k,bk] of b){const p=G.primitive(bk.parts,bk.mi,bk.useUV,bk.useC);if(p)out.push(p);}return out;};
  const under=(o,root)=>{for(let p=o;p;p=p.parent)if(p===root)return true;return false;};
  const reset=g=>{const sv=[g.position.clone(),g.rotation.clone(),g.scale.clone(),g.visible];g.position.set(0,0,0);g.rotation.set(0,0,0);g.scale.set(1,1,1);g.visible=true;g.updateMatrixWorld(true);return ()=>{g.position.copy(sv[0]);g.rotation.copy(sv[1]);g.scale.copy(sv[2]);g.visible=sv[3];g.updateMatrixWorld(true);};};
  HAZ.traffic.forEach((c,i)=>{const g=c.m.g,undo=reset(g);const kids=[];
    kids.push(G.node('body',prims(collect(G,g,g.matrixWorld,{skip:o=>c.m.wh.some(w=>under(o,w.sp)),visStop:null}))));
    c.m.wh.forEach((w,j)=>{const sp=new THREE.Matrix4().makeTranslation(w.sp.position.x,w.sp.position.y,w.sp.position.z);kids.push(G.node('w'+j,prims(collect(G,w.sp,sp,{visStop:null})),{translation:w.sp.position.toArray()}));});
    top.push(G.node('traffic'+i,null,{children:kids}));undo();
    data.traffic.push({s0:c.s0,lat:c.latT,laneT:c.laneT,v:c.v,len:c.m.len,scale:g.scale.x,wheels:c.m.wh.map(w=>({x:w.sp.position.x,y:w.sp.position.y,z:w.sp.position.z,r:w.r}))});});
  (typeof rollers!=='undefined'?rollers:[]).forEach((r,i)=>{if(i>0)return;const m=r.m,undo=reset(m);top.push(G.node('roller',prims(collect(G,m,new THREE.Matrix4(),{visStop:null}))));undo();});
  data.rollers=(typeof rollers!=='undefined'?rollers:[]).map(r=>({j:r.j,ph:r.ph}));
  HAZ.walk.forEach((w,i)=>{const g=w.g,undo=reset(g);const kids=[];
    kids.push(G.node('body',prims(collect(G,g,g.matrixWorld,{skip:o=>w.legs.some(l=>under(o,l)),visStop:null}))));
    w.legs.forEach((l,j)=>{const sp=new THREE.Matrix4().makeTranslation(l.position.x,l.position.y,l.position.z);kids.push(G.node('leg'+j,prims(collect(G,l,sp,{visStop:null})),{translation:l.position.toArray()}));});
    top.push(G.node('walk'+i,null,{children:kids}));undo();
    data.walk.push({j:w.j,lat:w.lat,v:w.v,ph:w.ph,pause:w.pause,H:w.H,legs:w.legs.length});});
  if(HAZ.train){const tr=HAZ.train;tr.cars.forEach((c,i)=>{const g=c.g,undo=reset(g);top.push(G.node('wagon'+i,prims(collect(G,g,g.matrixWorld,{visStop:null}))));undo();});
    data.train={p:{x:tr.p.x,y:tr.p.y},ux:tr.ux,uy:tr.uy,span:tr.span,len:tr.len,v:tr.v,j:tr.j,cars:tr.cars.map(c=>({off:c.off,L:c.L,scale:c.g.scale.x})),lamps:tr.lamps.length};}
  const root=G.node('haz',null,{children:top});G.j.scenes[0].nodes.push(root);const bytes=G.glb();return {b64:u8ToB64(bytes),data,stats:Object.assign(G.stats,{bytes:bytes.length})};};
window.__sceneSurvey=function(){const out={top:[],types:{}};world.children.forEach(c=>{let n=0,t=0;c.traverse(o=>{if(o.isMesh){n++;const g=o.geometry;t+=((g.index?g.index.count:g.attributes.position.count)/3)*(o.isInstancedMesh?o.count:1);}});out.top.push([c.type,c.name||'',Object.keys(c.userData).slice(0,3).join(','),n,Math.round(t/1000),c.visible]);});
  scene.children.forEach(c=>{out.types[c.type]=(out.types[c.type]||0)+1;});
  const mats={};world.traverse(o=>{if(o.isMesh){const ms=Array.isArray(o.material)?o.material:[o.material];for(const m of ms)mats[m.type]=(mats[m.type]||0)+1;}});out.mats=mats;out.sceneTop=scene.children.filter(c=>c!==world).map(c=>[c.type,c.name||'',Object.keys(c.userData).slice(0,3).join(',')]).slice(0,30);return out;};
})();
