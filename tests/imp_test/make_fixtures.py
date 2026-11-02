"""生成导入测试用的 PPTX 夹具（python-pptx）。输出到 imp_test/fx/。
a_layered.pptx  四层架构：整宽圆角层 + 独立左侧标签文字框、肘形连接线（含双向）、组合(grpSp)
b_swimlane.pptx 泳道流程：泳道 + 菱形判断 + 无 stCxn 的连线（端点只是靠近形状）+ 线上标注
c_pic_table.pptx 图片＋题注、表格、标题占位符
"""
import os, io, copy
from pptx import Presentation
from pptx.util import Emu, Pt, Cm
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'fx'); os.makedirs(OUT, exist_ok=True)

def new_prs():
    p = Presentation(); p.slide_width = Cm(33.867); p.slide_height = Cm(19.05); return p
def blank(p): return p.slides.add_slide(p.slide_layouts[6])
def text(sh, s, size=12, bold=False, color=None):
    tf = sh.text_frame; tf.clear(); lines = s.split('\n')
    for i, l in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = para.add_run(); r.text = l; r.font.size = Pt(size); r.font.bold = bold
        if color: r.font.color.rgb = RGBColor.from_string(color)
def box(shapes, kind, x, y, w, h, s='', fill=None, line=None, size=11, bold=False):
    sh = shapes.add_shape(kind, Cm(x), Cm(y), Cm(w), Cm(h))
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    if line: sh.line.color.rgb = RGBColor.from_string(line)
    if s: text(sh, s, size, bold, '1B2433' if fill else None)
    return sh
def tbox(shapes, x, y, w, h, s, size=12, bold=False, vert=False):
    tb = shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)); text(tb, s, size, bold)
    if vert: tb.text_frame._txBody.find(qn('a:bodyPr')).set('vert', 'eaVert')
    return tb
def arrow(conn, head=False, tail=True, dash=None):
    ln = conn.line._get_or_add_ln()
    if head: etree.SubElement(ln, qn('a:headEnd')).set('type', 'triangle')
    if tail: etree.SubElement(ln, qn('a:tailEnd')).set('type', 'triangle')
    if dash: conn.line.dash_style = dash
def connect(shapes, a, b, kind=MSO_CONNECTOR.ELBOW, ai=2, bi=0, **kw):
    c = shapes.add_connector(kind, 0, 0, 0, 0); c.begin_connect(a, ai); c.end_connect(b, bi); arrow(c, **kw); return c

# ---------------- (a) layered architecture ----------------
p = new_prs(); s = blank(p); S = s.shapes
tbox(S, 9, 0.3, 16, 1.2, '某体系总体架构图', 24, True)
layers = [('应用层', ['态势展示', '任务规划', '指挥决策', '效能评估', '训练仿真']),
          ('服务层', ['数据服务', '消息服务', '模型服务', '认证服务']),
          ('数据层', ['业务数据库', '情报数据库', '地理信息库']),
          ('基础设施层', ['计算资源', '存储资源', '网络资源', '安全防护', '运维监控', '机房环境'])]
Y = 2.0; LH = 3.6; X0 = 1.0; LW = 31.5
boxes = {}
for li, (name, items) in enumerate(layers):
    y = Y + li * (LH + 0.6)
    box(S, MSO_SHAPE.ROUNDED_RECTANGLE, X0, y, LW, LH, fill='EAF1FB', line='5B7DB1')
    tbox(S, X0 - 0.2, y + 0.4, 2.6, LH - 0.8, name, 14, True)        # 独立标签，压在左缘
    n = len(items); avail = (16.0 if li == 2 else LW - 4.0); bw = min(4.2, avail / n - 0.6); gap = (avail - n * bw) / max(1, n - 1) if n > 1 else 0
    if li == 1:   # 服务层前两个放进一个组合 grpSp（带底框）
        pass
    for i, it in enumerate(items):
        x = X0 + 3.4 + i * (bw + gap)
        b = box(S, MSO_SHAPE.RECTANGLE, x, y + 0.9, bw, 1.6, it, fill='FFFFFF', line='4A5A70', size=12)
        boxes[it] = b
# grpSp: a "子系统" group with its own frame + title + two boxes, placed in 应用层? put inside 服务层 right side
grp = S.add_group_shape()
gy = Y + 1 * (LH + 0.6)
# move service boxes? create a separate grouped cluster in 数据层 right part
dy = Y + 2 * (LH + 0.6)
fr = grp.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(21), Cm(dy + 0.3), Cm(10.5), Cm(3.0)); fr.fill.solid(); fr.fill.fore_color.rgb = RGBColor.from_string('FFF4E0'); fr.line.color.rgb = RGBColor.from_string('D4861A')
t = grp.shapes.add_textbox(Cm(21.1), Cm(dy + 0.35), Cm(4), Cm(0.7)); text(t, '大数据平台', 11, True)
g1 = grp.shapes.add_shape(MSO_SHAPE.CAN, Cm(21.6), Cm(dy + 1.1), Cm(4.2), Cm(1.9)); text(g1, '数据湖', 11)
g2 = grp.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(26.8), Cm(dy + 1.2), Cm(4.2), Cm(1.6)); text(g2, '流式计算', 11)
boxes['数据湖'] = g1; boxes['流式计算'] = g2
# scale the group to test chOff/chExt composition: python-pptx sets chOff=off; simulate by scaling ext & off
xfrm = grp._element.grpSpPr.find(qn('a:xfrm'))
off = xfrm.find(qn('a:off')); ext = xfrm.find(qn('a:ext'))
# shrink group horizontally to 90% around same origin -> children must be composed
ext.set('cx', str(int(int(ext.get('cx')) * 0.9)))
# links
connect(S, boxes['态势展示'], boxes['数据服务'])
connect(S, boxes['任务规划'], boxes['消息服务'], both=None) if False else None
connect(S, boxes['指挥决策'], boxes['模型服务'], head=True, tail=True)      # 双向
connect(S, boxes['效能评估'], boxes['认证服务'])
connect(S, boxes['数据服务'], boxes['业务数据库'])
connect(S, boxes['模型服务'], boxes['数据湖'])
connect(S, boxes['消息服务'], boxes['情报数据库'], dash=7)   # dash
connect(S, boxes['业务数据库'], boxes['计算资源'])
connect(S, boxes['地理信息库'], boxes['存储资源'], head=True, tail=False)   # 只有头箭头 → 反向
connect(S, boxes['数据湖'], boxes['流式计算'], kind=MSO_CONNECTOR.STRAIGHT, ai=3, bi=1)
p.save(os.path.join(OUT, 'a_layered.pptx'))

# ---------------- (b) swimlane flow ----------------
p = new_prs(); s = blank(p); S = s.shapes
tbox(S, 1, 0.3, 20, 1.1, '目标处置流程（泳道图）', 22, True)
lanes = ['侦察分队', '指挥所', '火力分队']
LY = 1.8; LH = 5.2
for i, nme in enumerate(lanes):
    y = LY + i * LH
    box(S, MSO_SHAPE.RECTANGLE, 1, y, 31.5, LH, fill='F7F9FC', line='8EA2BB')
    lb = box(S, MSO_SHAPE.RECTANGLE, 1, y, 1.4, LH, fill='2E3B4E', line='2E3B4E')   # 竖排标签条
    text(lb, nme, 13, True, 'FFFFFF'); lb.text_frame._txBody.find(qn('a:bodyPr')).set('vert', 'eaVert')
def at(lane, x, w=4.2, h=1.6): return (x, LY + lane * LH + (LH - h) / 2, w, h)
st = box(S, MSO_SHAPE.FLOWCHART_TERMINATOR, *at(0, 3.5), '发现目标', fill='FFFFFF', line='4A5A70')
rep = box(S, MSO_SHAPE.RECTANGLE, *at(0, 10), '上报目标信息', fill='FFFFFF', line='4A5A70')
ana = box(S, MSO_SHAPE.RECTANGLE, *at(1, 10), '研判目标性质', fill='FFFFFF', line='4A5A70')
dec = box(S, MSO_SHAPE.DIAMOND, *at(1, 16.5, 4.6, 2.8), '是否打击？', fill='FFF4E0', line='D4861A')
arc = box(S, MSO_SHAPE.RECTANGLE, *at(1, 24, 4.2), '持续监视', fill='FFFFFF', line='4A5A70')
fire = box(S, MSO_SHAPE.RECTANGLE, *at(2, 16.7), '实施打击', fill='FFFFFF', line='4A5A70')
bda = box(S, MSO_SHAPE.ROUNDED_RECTANGLE, *at(2, 24), '毁伤评估', fill='FFFFFF', line='4A5A70')
def free_line(x1, y1, x2, y2, label=None, **kw):
    # 普通直线（无 stCxn/endCxn），端点仅“靠近”形状（留 0.1~0.2cm 缝隙）
    c = S.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x1), Cm(y1), Cm(x2), Cm(y2)); arrow(c, **kw)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tbox(S, mx - 1.0, my - 0.45, 2.0, 0.8, label, 10)
    return c
def mid(sh, side):
    x, y, w, h = sh.left / 360000, sh.top / 360000, sh.width / 360000, sh.height / 360000
    return {'r': (x + w + 0.15, y + h / 2), 'l': (x - 0.15, y + h / 2), 'b': (x + w / 2, y + h + 0.15), 't': (x + w / 2, y - 0.15)}[side]
free_line(*mid(st, 'r'), *mid(rep, 'l'))
free_line(*mid(rep, 'b'), *mid(ana, 't'))
free_line(*mid(ana, 'r'), *mid(dec, 'l'))
free_line(*mid(dec, 'r'), *mid(arc, 'l'), label='否')
free_line(*mid(dec, 'b'), *mid(fire, 't'), label='是')
free_line(*mid(fire, 'r'), *mid(bda, 'l'))
c = free_line(*mid(bda, 't'), *mid(arc, 'b'), dash=7)  # 毁伤评估→持续监视（虚线）
p.save(os.path.join(OUT, 'b_swimlane.pptx'))

# ---------------- (c) picture + caption + table + title placeholder ----------------
from PIL import Image, ImageDraw
def png(color, shape='circle'):
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shape == 'circle': d.ellipse((10, 10, 150, 150), fill=color)
    else: d.polygon([(80, 8), (152, 150), (8, 150)], fill=color)
    b = io.BytesIO(); im.save(b, 'PNG'); b.seek(0); return b
p = new_prs(); s = p.slides.add_slide(p.slide_layouts[5])    # Title Only 版式（标题占位符，无 xfrm → 继承）
s.shapes.title.text = '装备组成与指标'
S = s.shapes
for i, (nm, col, shp) in enumerate([('侦察无人机', '2F80ED', 'circle'), ('地面控制站', 'D4861A', 'tri'), ('数据链终端', '27AE60', 'circle')]):
    x = 2 + i * 5.5
    S.add_picture(png('#' + col, shp), Cm(x), Cm(5), Cm(3), Cm(3))
    tbox(S, x - 0.5, 8.1, 4, 0.8, nm, 12)
S.add_picture(png('#2F80ED', 'circle'), Cm(2), Cm(11), Cm(3), Cm(3))   # 重复图片 → 去重
tbox(S, 1.5, 14.1, 4, 0.8, '侦察无人机（备份）', 12)
rows, cols = 4, 3
gf = S.add_table(rows, cols, Cm(19), Cm(5), Cm(13), Cm(5))
data = [['装备', '数量', '备注'], ['侦察无人机', '6', '含 2 架备份'], ['地面控制站', '2', '车载'], ['数据链终端', '8', '']]
for r in range(rows):
    for c_ in range(cols): gf.table.cell(r, c_).text = data[r][c_]
# 一条连线：图片→图片
cc = S.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(5.1), Cm(6.5), Cm(7.4), Cm(6.5)); arrow(cc, head=True, tail=True)
p.save(os.path.join(OUT, 'c_pic_table.pptx'))
print('ok', os.listdir(OUT))
