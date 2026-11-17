(()=>{/* (patch 76) one Sandbox place's driving distances: between every two of its gates, and from each gate to the start line.
  A road place: along the lap (the shorter way round); an open place or a room: straight across, x1.15 */
  const id=SB.regId,road=SB.kind==='road',cum=[0];for(let j=1;j<=N;j++){const a=track[j-1],b=track[j%N];cum.push(cum[j-1]+Math.hypot(b.x-a.x,b.y-a.y));}const L=cum[N];
  const near=(x,z)=>{let bj=0,bd=1e18;for(let j=0;j<N;j++){const d=(track[j].x-x)**2+(track[j].y-z)**2;if(d<bd){bd=d;bj=j;}}return bj;};
  const pts=SB.gates.map(g=>({k:g.to,x:g.x,z:g.z,j:g.j!=null?g.j:near(g.x,g.z)}));if(SB.flag)pts.push({k:'@flag',x:SB.flag.x,z:SB.flag.z,j:near(SB.flag.x,SB.flag.z)});
  const d=(a,b)=>road?Math.min(Math.abs(cum[a.j]-cum[b.j]),L-Math.abs(cum[a.j]-cum[b.j])):Math.hypot(a.x-b.x,a.z-b.z)*1.15;const out={};
  for(const a of pts)for(const b of pts)if(a!==b&&a.k!=='@flag')out[a.k+'>'+b.k]=Math.round(d(a,b));return {id,kind:SB.kind,c:out};})()
