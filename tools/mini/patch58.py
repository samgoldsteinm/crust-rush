"""Patch 58 (web v215): no scenery standing in a shortcut's or a paved route's lane, on any track.
Following patch 55 (Margherita's causeway posts), scratch/scvert.js went through the Sandbox places: Midnight Mozzarella had a street
lamp (the instanced scenery, userData.cullOK) standing on its paved fast lane near the edge (27 from the lane's middle, the lane 34 wide);
its generator's own check measured from the plain shortcut width. Rather than mend generator after generator, scClear() runs as a race
or a place is set up (resetRace, before warmScene): any instanced scenery detail (cullOK) whose foot is inside a shortcut's lane (its
own width, less 3) is shrunk to nothing. Scenery never belongs on a road; nothing else is touched (pads, boxes, rails are not cullOK).
Run once: py.cmd tools/mini/patch58.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 58' not in s, 'already patched'
a = "NOITM=!demo&&mode!=='lss'&&mode!=='bb'&&mode!=='sb'&&(NET.cfg?!!NET.cfg.ni:!NET.role&&itemsOff());/* (patch 47) */\n  warmScene();\n}"
assert s.count(a) == 1
s = s.replace(a, a[:-len("  warmScene();\n}")] + "  try{scClear();}catch(e){console.warn('scClear',e);}/* (patch 58) */\n  warmScene();\n}\n"
    "/* (patch 58) no scenery detail standing in a shortcut's lane */\n"
    "function scClear(){if(!SHORTS||!SHORTS.length||!world)return;const M=new THREE.Matrix4(),P=new THREE.Vector3(),Z=new THREE.Matrix4().makeScale(0,0,0);\n"
    "  world.traverse(o=>{if(!o.isInstancedMesh||!o.userData||!o.userData.cullOK||o.userData.scClr)return;o.userData.scClr=1;o.updateWorldMatrix(true,false);let ch=false;\n"
    "    for(let i=0;i<o.count;i++){o.getMatrixAt(i,M);P.setFromMatrixPosition(M).applyMatrix4(o.matrixWorld);if(nearSC(P.x,P.z,SCW-3)){o.setMatrixAt(i,Z);ch=true;}}if(ch)o.instanceMatrix.needsUpdate=true;});}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 58 applied')
