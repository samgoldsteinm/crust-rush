import sys
from PIL import Image
SP='/tmp/claude-0/-home-claude/009aa3b6-e96f-505b-b230-9e07dd3a3292/scratchpad'
tag=sys.argv[1]; n=int(sys.argv[2]); cols=int(sys.argv[3]) if len(sys.argv)>3 else 2
ims=[Image.open(SP+'/neon_%s_%d.png'%(tag,i)).convert('RGB') for i in range(n)]
w,h=ims[0].size; rows=(n+cols-1)//cols
s=Image.new('RGB',(w*cols,h*rows))
for i,im in enumerate(ims): s.paste(im,((i%cols)*w,(i//cols)*h))
sc=min(1,1900/(w*cols)); s=s.resize((int(w*cols*sc),int(h*rows*sc))); s.save(SP+'/neon_%s_sheet.jpg'%tag,quality=86)
