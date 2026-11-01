import sys, os, subprocess, glob, shutil
from PIL import Image, ImageDraw
from jw_paths import DRAWTOOL
# usage: cmp.py src.vsdx [more...]  -> out/<name>_cmp_p<N>.png
OUT=str(DRAWTOOL/'raw_test'/'out'); R=OUT+'/r'; os.makedirs(R,exist_ok=True)
def render(path, tag):
    d=f'{R}/{tag}'; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',d,path],capture_output=True,timeout=180)
    pdf=glob.glob(d+'/*.pdf')
    if not pdf: return []
    subprocess.run(['pdftoppm','-png','-r','60',pdf[0],d+'/p'],capture_output=True)
    return sorted(glob.glob(d+'/p*.png'))
for src in sys.argv[1:]:
    name=os.path.splitext(os.path.basename(src))[0]
    a=render(src,name+'_src'); b=render(f'{OUT}/{name}.pptx',name+'_ppt')
    for i in range(max(len(a),len(b))):
        ims=[Image.open(x[i]) if i<len(x) else Image.new('RGB',(200,200),'red') for x in (a,b)]
        h=max(i.height for i in ims); W=sum(i.width for i in ims)+30
        c=Image.new('RGB',(W,h+20),'#888'); x=0
        for k,im in enumerate(ims): c.paste(im,(x,20)); ImageDraw.Draw(c).text((x+4,4),['Visio(LO)','PPTX(LO)'][k],fill='white'); x+=im.width+30
        c.save(f'{OUT}/{name}_cmp_p{i+1}.png')
    print(name,len(a),len(b))
