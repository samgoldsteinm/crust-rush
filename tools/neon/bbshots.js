//shot start
(()=>{/* the start of a round, as the player sees it (the others drive on) */return {t:Math.round(BB.t),left:BB.left,bal:player.bal};})()
----
//shot overview
(()=>{__solo();__put(-100,-40,0);window.__cam=[-40,1180,520,-10,0,40];return 'from above';})()
----
//shot overview_w
(()=>{window.__cam=[-1150,620,300,-60,0,20];return 'from the open west side';})()
----
//shot overview_ne
(()=>{window.__cam=[620,520,-520,60,20,60];return 'from the north-east, over the walls';})()
----
//wait 700 //shot five
(()=>{window.__cam=null;player.bbL=0;player.bal=5;__put(-60,-200,0);bbHud();return 'five balloons';})()
----
//wait 700 //shot three
(()=>{player.bbL=1;player.bal=3;bbHud();return 'three';})()
----
//wait 700 //shot one
(()=>{player.bbL=2;player.bal=1;bbHud();return 'one';})()
----
//wait 700 //shot ramp_lid
(()=>{player.bbL=0;player.bal=5;__put(-545,310,0);return 'the lid, from the table';})()
----
//wait 700 //shot ledge_boxes
(()=>{__put(-330,310,0);return 'on the box stacks, looking east to the baking sheet';})()
----
//wait 700 //shot ramp_sheet
(()=>{__put(170,310,0);return 'the baking sheet up to the top';})()
----
//wait 700 //shot top
(()=>{__put(420,330,-1.5708);return 'on the top, looking north down the cheese';})()
----
//wait 700 //shot ramp_cheese
(()=>{__put(465,-40,1.5708);return 'the cheese wedge, from the block';})()
----
//wait 700 //shot ramp_bread
(()=>{__put(465,-300,1.5708);return 'the bread board up to the block';})()
----
//wait 700 //shot isle_east
(()=>{__put(10,-90,3.14159);return 'the island: the baking sheet up its east side';})()
----
//wait 700 //shot isle_south
(()=>{__put(-310,190,-1.5708);return 'the island: the bread board up its south side';})()
----
//wait 700 //shot isle_top
(()=>{__put(-400,-90,0);return 'on the island';})()
----
//wait 700 //shot isle_nw
(()=>{__put(-500,-250,.6);return 'the island from the north-west: its open edges and the crates';})()
----
//wait 700 //shot floor_mid
(()=>{__put(330,-250,2.6);return 'the open floor from the north-east: pans, sack, plates, mill, cans';})()
----
//wait 700 //shot floor_south
(()=>{__put(-120,200,-.5);return 'the rolling pin and the cans from the south';})()
----
//wait 700 //shot pans
(()=>{__put(-420,-300,0);return 'along the pans';})()
