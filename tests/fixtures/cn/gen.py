# 生成中文测试 Visio：基于真实 Visio 文件（含主题、样式表），替换页面内容
import zipfile, shutil, re, sys
SRC='/home/claude/vfx/poi/test-data/diagram/test.vsdx'
OUT=sys.argv[1] if len(sys.argv)>1 else 'cn_arch.vsdx'
sid=[100]
def nid(): sid[0]+=1; return sid[0]
def C(n,v,f=None,u=None): return f"<Cell N='{n}' V='{v}'"+(f" U='{u}'" if u else '')+(f" F='{f}'" if f else '')+"/>"
def rectgeom(nofill=0,noline=0):
    return (f"<Section N='Geometry' IX='0'>{C('NoFill',nofill)}{C('NoLine',noline)}{C('NoShow',0)}"
     "<Row T='RelMoveTo' IX='1'><Cell N='X' V='0'/><Cell N='Y' V='0'/></Row><Row T='RelLineTo' IX='2'><Cell N='X' V='1'/><Cell N='Y' V='0'/></Row>"
     "<Row T='RelLineTo' IX='3'><Cell N='X' V='1'/><Cell N='Y' V='1'/></Row><Row T='RelLineTo' IX='4'><Cell N='X' V='0'/><Cell N='Y' V='1'/></Row>"
     "<Row T='RelLineTo' IX='5'><Cell N='X' V='0'/><Cell N='Y' V='0'/></Row></Section>")
def ellgeom(w,h): return f"<Section N='Geometry' IX='0'>{C('NoFill',0)}{C('NoLine',0)}<Row T='Ellipse' IX='1'>{C('X',w/2)}{C('Y',h/2)}{C('A',w)}{C('B',h/2)}{C('C',w/2)}{C('D',h)}</Row></Section>"
def chars(rows):
    # rows: list of dict(size pt, bold, color, font, asian)
    out="<Section N='Character'>"
    for i,r in enumerate(rows):
        out+=f"<Row IX='{i}'>"
        if 'font' in r: out+=C('Font',r['font'])
        if 'asian' in r: out+=C('AsianFont',r['asian'])
        if 'color' in r: out+=C('Color',r['color'])
        if 'size' in r: out+=C('Size',r['size']/72,u='PT')
        if 'bold' in r: out+=C('Style',1 if r['bold'] else 0)
        out+="</Row>"
    return out+"</Section>"
def paras(rows):
    out="<Section N='Paragraph'>"
    for i,r in enumerate(rows):
        out+=f"<Row IX='{i}'>"+''.join(C(k,v) for k,v in r.items())+"</Row>"
    return out+"</Section>"
def esc(t): return t.replace('&','&amp;').replace('<','&lt;')
def shape(x,y,w,h,text='',fill='#FFFFFF',line='#2F5597',lw=0.75,ch=None,pa=None,geom=None,extra='',style=None,txt=None,tb=None,name=None,angle=0,rounding=0,fillpat=1,linepat=1):
    i=nid()
    st=f" LineStyle='{style}' FillStyle='{style}' TextStyle='{style}'" if style else " LineStyle='3' FillStyle='3' TextStyle='3'"
    s=f"<Shape ID='{i}' Type='Shape'{st}"+(f" NameU='{name}' Name='{name}'" if name else '')+">"
    s+=C('PinX',x+w/2)+C('PinY',y+h/2)+C('Width',w)+C('Height',h)+C('LocPinX',w/2)+C('LocPinY',h/2)+C('Angle',angle)
    s+=C('FillForegnd',fill)+C('FillPattern',fillpat)+C('LineColor',line)+C('LineWeight',lw/72,u='PT')+C('LinePattern',linepat)
    if rounding: s+=C('Rounding',rounding)
    if tb: s+=''.join(C(k,v) for k,v in tb.items())
    s+=extra
    if ch: s+=chars(ch)
    if pa: s+=paras(pa)
    s+=geom if geom is not None else rectgeom()
    if txt is not None: s+=f"<Text>{txt}</Text>"
    elif text: s+=f"<Text>{esc(text)}</Text>"
    return s+"</Shape>", i
def conn(pts, label='', color='#404040', lw=1, end=13, begin=0, pat=1, lsize=9):
    i=nid()
    (bx,by),(ex,ey)=pts[0],pts[-1]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    x0,y0=min(xs),min(ys); w=max(max(xs)-x0,0.0001); h=max(max(ys)-y0,0.0001)
    s=f"<Shape ID='{i}' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>"
    s+=C('PinX',x0+w/2)+C('PinY',y0+h/2)+C('Width',w)+C('Height',h)+C('LocPinX',w/2)+C('LocPinY',h/2)
    s+=C('BeginX',bx)+C('BeginY',by)+C('EndX',ex)+C('EndY',ey)
    s+=C('LineColor',color)+C('LineWeight',lw/72,u='PT')+C('LinePattern',pat)+C('EndArrow',end)+C('BeginArrow',begin)+C('EndArrowSize',2)+C('FillPattern',0)
    if label:
        mx,my=pts[len(pts)//2-1] if len(pts)>2 else ((bx+ex)/2,(by+ey)/2)
        if len(pts)>2:
            a,b=pts[len(pts)//2-1],pts[len(pts)//2]; mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
        tw=0.9
        s+=C('TxtPinX',mx-x0)+C('TxtPinY',my-y0)+C('TxtWidth',tw)+C('TxtHeight',0.22)+C('TxtLocPinX',tw/2)+C('TxtLocPinY',0.11)+C('TextBkgnd','#FFFFFF')
        s+=chars([{'size':lsize,'color':color,'asian':'微软雅黑','font':'微软雅黑'}])
    s+=f"<Section N='Geometry' IX='0'>{C('NoFill',1)}{C('NoLine',0)}"
    for k,(px,py) in enumerate(pts): s+=f"<Row T='{'MoveTo' if k==0 else 'LineTo'}' IX='{k+1}'>{C('X',px-x0)}{C('Y',py-y0)}</Row>"
    s+="</Section>"
    if label: s+=f"<Text>{esc(label)}</Text>"
    return s+"</Shape>"
PW,PH=16.54,11.69   # A3 横
S=[]
YH='微软雅黑'
# 标题、副标题
s,_=shape(3.27,10.7,10,0.6,'某型无人集群体系总体架构',fill='#FFFFFF',fillpat=0,linepat=0,ch=[{'size':24,'bold':1,'font':YH,'asian':'黑体','color':'#1F2D3D'}]); S.append(s)
s,_=shape(3.27,10.25,10,0.4,'面向跨域协同的“感知—决策—行动”三层结构（示例）',fillpat=0,linepat=0,ch=[{'size':12,'font':YH,'asian':'楷体','color':'#666666'}]); S.append(s)
layers=[('感知层',8.0,'#EAF1FB','#2F5597'),('决策层',5.5,'#FFF4E5','#C55A11'),('行动层',3.0,'#EAF6EA','#548235')]
for name,y,f,l in layers:
    # 容器：标题在左上角
    s,_=shape(1.2,y,14.6,2.2,'',fill=f,line=l,lw=1.25); S.append(s)
    # 竖排层名（TextDirection=1）
    s,_=shape(0.6,y,0.6,2.2,name,fill=l,line=l,ch=[{'size':16,'bold':1,'color':'#FFFFFF','font':YH,'asian':'微软雅黑'}],tb={'TextDirection':1}); S.append(s)
# 感知层里的框：多种字号
boxes=[
 (1.6,8.6,2.2,1.0,'光电侦察吊舱',[{'size':10.5,'font':YH,'asian':YH}],None),
 (4.2,8.6,2.2,1.0,'合成孔径雷达',[{'size':9,'font':YH,'asian':YH}],None),
 (6.8,8.4,2.6,1.4,None,[{'size':14,'bold':1,'font':YH,'asian':YH,'color':'#2F5597'},{'size':8,'font':YH,'asian':'宋体','color':'#595959'}],"<cp IX='0'/>电子侦察\n<cp IX='1'/>频段 0.5～18 GHz，测向精度≤2°"),
 (9.8,8.6,2.2,1.0,'ADS-B 接收机',[{'size':12,'font':'Arial','asian':'仿宋'}],None),
]
for x,y,w,h,t,ch,txt in boxes:
    s,_=shape(x,y,w,h,t or '',fill='#FFFFFF',line='#2F5597',ch=ch,txt=esc(txt).replace('&lt;','<') if txt else None); S.append(s)
# 圆角框 + 样式继承字号（无 Character，继承自定义样式 ID=20，字号 11）
s,_=shape(12.4,8.6,2.6,1.0,'气象水文传感',fill='#DDEBF7',line='#2F5597',rounding=0.12,style='20'); S.append(s)
# 决策层：椭圆、带项目符号的说明框、旋转文字
s,_=shape(1.8,6.0,2.6,1.2,'任务规划',geom=ellgeom(2.6,1.2),fill='#FCE4D6',line='#C55A11',ch=[{'size':13,'bold':1,'font':YH,'asian':YH}]); S.append(s)
txt="<pp IX='0'/>态势融合\n<pp IX='1'/><cp IX='1'/>• 多源目标关联\n• 威胁评估\n• 航迹预测"
s,_=shape(5.2,5.8,3.4,1.6,None,fill='#FFFFFF',line='#C55A11',ch=[{'size':12,'bold':1,'font':YH,'asian':YH},{'size':9,'font':YH,'asian':YH}],pa=[{'HorzAlign':1},{'HorzAlign':0,'IndLeft':0.1,'SpLine':-1.5}],txt=txt,tb={'VerticalAlign':0}); S.append(s)
s,_=shape(9.4,6.1,2.4,0.9,'协同分配',fill='#FFFFFF',line='#C55A11',ch=[{'size':11,'font':YH,'asian':YH}]); S.append(s)
s,_=shape(12.4,6.0,2.6,1.0,'人在回路确认',fill='#FFFFFF',line='#C55A11',ch=[{'size':10,'font':YH,'asian':YH,'bold':1}],angle=0.0); S.append(s)
# 行动层：组合（两个子框 + 组合文字）
gid=nid()
g=f"<Shape ID='{gid}' Type='Group' LineStyle='3' FillStyle='3' TextStyle='3' NameU='编队' Name='编队'>"+C('PinX',4.0)+C('PinY',4.1)+C('Width',4.4)+C('Height',1.6)+C('LocPinX',2.2)+C('LocPinY',0.8)
g+=C('FillPattern',0)+C('LinePattern',2)+C('LineColor','#548235')+C('TxtPinX',2.2)+C('TxtPinY',1.75)+C('TxtWidth',4.4)+C('TxtHeight',0.3)+C('TxtLocPinX',2.2)+C('TxtLocPinY',0.15)
g+=chars([{'size':10,'bold':1,'font':YH,'asian':YH,'color':'#548235'}])+rectgeom()+"<Shapes>"
for k,nm in enumerate(['察打无人机 ×3','巡飞弹 ×6']):
    i=nid(); x=0.2+k*2.2
    g+=f"<Shape ID='{i}' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>"+C('PinX',x+0.9)+C('PinY',0.7)+C('Width',1.8)+C('Height',0.9)+C('LocPinX',0.9)+C('LocPinY',0.45)
    g+=C('FillForegnd','#E2F0D9')+C('FillPattern',1)+C('LineColor','#548235')+C('LineWeight',0.75/72)+chars([{'size':10.5,'font':YH,'asian':YH}])+rectgeom()+f"<Text>{esc(nm)}</Text></Shape>"
g+="</Shapes><Text>编队一（组合）</Text></Shape>"
S.append(g)
s,_=shape(7.0,3.5,2.4,1.0,'无人艇集群',fill='#FFFFFF',line='#548235',ch=[{'size':10.5,'font':YH,'asian':YH}]); S.append(s)
s,_=shape(10.0,3.5,2.4,1.0,'地面无人车',fill='#FFFFFF',line='#548235',ch=[{'size':10.5,'font':YH,'asian':YH}]); S.append(s)
s,_=shape(12.9,3.3,2.2,1.4,'旋转 30° 标注',fill='#FFF2CC',line='#BF9000',ch=[{'size':9,'font':YH,'asian':YH}],angle=0.5235987756); S.append(s)
# 连线（带标签、正交折线、虚线双向）
S.append(conn([(2.7,8.6),(2.7,7.2)],'目标指示',lsize=9))
S.append(conn([(5.3,8.6),(5.3,8.0),(6.9,8.0),(6.9,7.4)],'雷达点迹',color='#2F5597',lsize=8))
S.append(conn([(4.4,6.6),(5.2,6.6)],'',color='#C55A11',lw=1.5))
S.append(conn([(8.6,6.55),(9.4,6.55)],'方案迭代',color='#C55A11',end=13,begin=13,pat=2,lsize=10))
S.append(conn([(10.6,6.1),(10.6,5.0),(8.2,5.0),(8.2,4.5)],'指令下达',color='#7030A0',lw=1,lsize=9))
S.append(conn([(11.8,6.55),(12.4,6.55)],'',color='#C55A11'))
# 图例说明（左对齐、多段、小字）
s,_=shape(1.2,0.6,9.0,1.6,None,fill='#F2F2F2',line='#BFBFBF',ch=[{'size':10,'bold':1,'font':YH,'asian':YH},{'size':8,'font':YH,'asian':'宋体','color':'#404040'}],pa=[{'HorzAlign':0}],tb={'VerticalAlign':0,'LeftMargin':0.1,'TopMargin':0.08},
  txt="<cp IX='0'/>说明：\n<cp IX='1'/>1. 本图为测试样例，字号 8～24 磅混排，用于检验格式转换的字号还原。\n2. 连线标签 8～10 磅，带白底；虚线为迭代关系。\n3. 竖排层名 16 磅，旋转标注 30°。"); S.append(s)
fid=nid()
S.append(f"<Shape ID='{fid}' Type='Foreign' LineStyle='3' FillStyle='3' TextStyle='3' NameU='图片' Name='图片'>"+C('PinX',13.2)+C('PinY',1.4)+C('Width',2.4)+C('Height',1.6)+C('LocPinX',1.2)+C('LocPinY',0.8)+C('ImgOffsetX',0)+C('ImgOffsetY',0)+C('ImgWidth',2.4)+C('ImgHeight',1.6)+"<ForeignData ForeignType='EnhMetaFile' CompressionType=''><Rel r:id='rId1'/></ForeignData></Shape>")
pid=nid()
S.append(f"<Shape ID='{pid}' Type='Foreign' LineStyle='3' FillStyle='3' TextStyle='3'>"+C('PinX',11.2)+C('PinY',1.4)+C('Width',1.2)+C('Height',1.2)+C('LocPinX',0.6)+C('LocPinY',0.6)+C('ImgOffsetX',0)+C('ImgOffsetY',0)+C('ImgWidth',1.2)+C('ImgHeight',1.2)+"<ForeignData ForeignType='Bitmap' CompressionType='PNG'><Rel r:id='rId2'/></ForeignData></Shape>")
page=("<?xml version='1.0' encoding='utf-8' ?><PageContents xmlns='http://schemas.microsoft.com/office/visio/2012/main' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' xml:space='preserve'><Shapes>"+''.join(S)+"</Shapes></PageContents>")
zin=zipfile.ZipFile(SRC); zout=zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d=zin.read(it.filename)
    if it.filename=='visio/pages/page1.xml': d=page.encode('utf-8')
    elif it.filename=='visio/pages/pages.xml':
        t=d.decode('utf-8'); t=re.sub(r"<Cell N='PageWidth' V='[^']*'",f"<Cell N='PageWidth' V='{PW}'",t); t=re.sub(r"<Cell N='PageHeight' V='[^']*'",f"<Cell N='PageHeight' V='{PH}'",t); t=t.replace("Name='Page-1'","Name='总体架构'"); d=t.encode('utf-8')
    elif it.filename=='visio/document.xml':
        t=d.decode('utf-8')
        sty=("<StyleSheet ID='20' NameU='CN Box' Name='CN Box' LineStyle='3' FillStyle='3' TextStyle='3'>"+chars([{'size':11,'font':YH,'asian':'微软雅黑','color':'#1F3864','bold':1}])+"</StyleSheet>")
        t=t.replace('</StyleSheets>',sty+'</StyleSheets>'); d=t.encode('utf-8')
    elif it.filename=='visio/pages/_rels/page1.xml.rels':
        d=b"<?xml version='1.0' encoding='utf-8' ?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'><Relationship Id='rId1' Type='http://schemas.microsoft.com/visio/2010/relationships/image' Target='../media/image1.emf'/><Relationship Id='rId2' Type='http://schemas.microsoft.com/visio/2010/relationships/image' Target='../media/image2.png'/></Relationships>"
    zout.writestr(it,d)
zout.writestr('visio/media/image1.emf', open('thumb.emf','rb').read())
zout.writestr('visio/media/image2.png', open('/home/claude/drawtool/icon_sheet.png','rb').read())
zout.close()
# 补内容类型
import os
z=zipfile.ZipFile(OUT); items=[(i,z.read(i.filename)) for i in z.infolist()]; z.close()
z=zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED)
for i,d in items:
    if i.filename=='[Content_Types].xml':
        t=d.decode()
        for e,m in (('emf','image/x-emf'),('png','image/png')):
            if f'Extension="{e}"' not in t and f"Extension='{e}'" not in t: t=t.replace('<Default ',f'<Default Extension="{e}" ContentType="{m}"/><Default ',1)
        d=t.encode()
    z.writestr(i,d)
z.close(); print('ok',OUT)
