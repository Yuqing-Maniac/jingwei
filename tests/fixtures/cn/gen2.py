# 流程图式 Visio：只有方框＋文字＋连线箭头，无容器（用户描述的典型场景）
import importlib.util,sys
spec=importlib.util.spec_from_file_location('g','gen.py')
src=open('gen.py',encoding='utf-8').read()
head=src[:src.index('PW,PH=')]
exec(head)
PW,PH=11.69,8.27
S=[]
YH='微软雅黑'
import os
FRAME=os.environ.get('FRAME')=='1'
def box(x,y,t,w=1.3,h=0.55,sz=10.5,fill='#FFFFFF',line='#000000'):
    s,i=shape(x,y,w,h,t,fill=fill,line=line,ch=[{'size':sz,'font':YH,'asian':'宋体'}]); S.append(s); return (x,y,w,h)
s,_=shape(3.5,7.4,5,0.5,'无人机任务处理流程',fillpat=0,linepat=0,ch=[{'size':18,'bold':1,'font':YH,'asian':'黑体'}]); S.append(s)
B={}
if FRAME:
    s,_=shape(0.4,2.2,10.6,4.9,'',fill='#F5F7FA',line='#7F7F7F'); S.append(s)
    s,_=shape(0.5,6.75,2.0,0.3,'任务处理子系统',fillpat=0,linepat=0,ch=[{'size':11,'bold':1,'font':YH,'asian':YH}]); S.append(s)
B['a']=box(0.8,6.2,'任务接收')
B['b']=box(3.1,6.25,'任务解析',w=1.2)
B['c']=box(5.5,6.15,'航路规划',h=0.62)
B['d']=box(8.0,6.2,'指令上注')
B['e']=box(0.9,4.4,'态势感知')
B['f']=box(3.2,4.5,'目标识别',w=1.45)
B['g']=box(5.45,4.35,'威胁评估')
B['h']=box(7.9,4.45,'打击决策',w=1.25)
B['i']=box(2.0,2.6,'效果评估')
B['j']=box(4.6,2.5,'信息回传')
B['k']=box(7.3,2.65,'归档')
def c(a,b,lab=''):
    ax,ay,aw,ah=B[a]; bx,by,bw,bh=B[b]
    if abs(ay-by)<0.5: S.append(conn([(ax+aw,ay+ah/2),(bx,by+bh/2)],lab))
    else: S.append(conn([(ax+aw/2,ay),(ax+aw/2,(ay+by+bh)/2),(bx+bw/2,(ay+by+bh)/2),(bx+bw/2,by+bh)],lab))
for a,b in [('a','b'),('b','c'),('c','d'),('a','e'),('e','f'),('f','g'),('g','h'),('d','h'),('f','i'),('i','j'),('j','k'),('h','k')]: c(a,b)
c('b','g','')   # 跨越中间框 f 的连线
page=("<?xml version='1.0' encoding='utf-8' ?><PageContents xmlns='http://schemas.microsoft.com/office/visio/2012/main' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' xml:space='preserve'><Shapes>"+''.join(S)+"</Shapes></PageContents>")
import zipfile,re
zin=zipfile.ZipFile(SRC); zout=zipfile.ZipFile('flow_frame.vsdx' if FRAME else 'flow.vsdx','w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d=zin.read(it.filename)
    if it.filename=='visio/pages/page1.xml': d=page.encode()
    elif it.filename=='visio/pages/pages.xml':
        t=d.decode(); t=re.sub(r"<Cell N='PageWidth' V='[^']*'",f"<Cell N='PageWidth' V='{PW}'",t); t=re.sub(r"<Cell N='PageHeight' V='[^']*'",f"<Cell N='PageHeight' V='{PH}'",t); d=t.encode()
    elif it.filename=='visio/pages/_rels/page1.xml.rels': d=b"<?xml version='1.0' encoding='utf-8' ?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'></Relationships>"
    zout.writestr(it,d)
zout.close(); print('ok')
