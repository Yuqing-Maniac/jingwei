const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('经纬织图',52,CNH,true,200),C('V3.1.1　发布说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 18 日',28,CN,false,120)];
add(P('**v3.1.1 在 v3.1 基础上完成银河麒麟（飞腾）等国产环境适配，旧版国产浏览器可直接运行。**'));
add(P('**v3.1 起软件定名为“经纬织图”，取“纵横经纬，织网成图”之意，并启用新图标；配套视频教程同步重录。功能与 v3.0 一致，工程文件完全兼容。**'));
add(H('一、名称',1));
['**中文名**：经纬织图；副题“体系架构绘图”。','**英文名**：JingWei ZhiTu，程序文件为“JingWeiZhiTu_v3.1.1.html”。','**沿革**：鸿图体系绘图（v2.x）→ 经纬体系绘图（v3.0）→ 经纬织图（v3.1）。'].forEach(t=>add(LI(t)));
add(H('二、图标',1));
add(P('图标以两经两纬交织成网：青色竖线为“经”，蓝色横线为“纬”，上下交叠体现“织”；交点即体系节点，左上琥珀色为主节点，右下白色节点表示协同单元。底色为深蓝圆角方块。'));
add(TBL('图标文件（icon 文件夹）',['文件','用途'],[
 ['JingWeiZhiTu.ico','Windows 快捷方式图标（含 16～256 像素）'],
 ['icon_16～1024.png','各尺寸位图，用于文档、汇报材料'],
 ['icon.svg','矢量原稿，可任意缩放'],
],[2600,6000]));
['程序内已内置：浏览器标签页图标、左上角标识。','**设置桌面快捷方式图标**：在 html 文件上右键 › 发送到 › 桌面快捷方式；在快捷方式上右键 › 属性 › 更改图标，选择 JingWeiZhiTu.ico。'].forEach(t=>add(LI(t)));
add(H('三、视频教程',1));
add(P('教程按新名称重录，新增四段演示：拖动吸附、连线避障、打开 PPT／Visio／draw.io 与批量格式转换（Visio 转 PPT 字号一致）、报告版心插图。'));
add(H('四、兼容',1));
['**工程文件**：.hongtu.json、.jingwei.json 均可直接打开；新保存仍为 .jingwei.json。','**本机设置**：大模型接口、转换选项、吸附开关等保留。','**运行环境**：Windows 7～11、麒麟（x86／飞腾）；建议使用 Chrome、Edge 或其他 Chromium 内核浏览器。'].forEach(t=>add(LI(t)));
add(H('五、国产环境适配（v3.1.1）',1));
add(P('**已按银河麒麟桌面操作系统（国防版）V10、飞腾 D2000、UKUI 桌面环境完成适配评估，程序可正常运行。**'));
['**语法降级**：程序脚本统一降级为 Chromium 69、Firefox 68 即可解析的语法，覆盖奇安信可信浏览器、360 安全浏览器信创版及系统自带 Chromium、Firefox 的较早版本。','**接口补齐**：旧版浏览器缺少的文件读取、对象构造等接口由程序内置兼容层补齐；Visio、PPT 文件解压在旧版浏览器上自动改用内置解压算法。','**界面兼容**：对话框遮罩、格式转换选项高亮、模板缩略图等样式改用旧版浏览器支持的写法。','**版本提示**：浏览器版本过低时，页面顶部给出明确提示及推荐浏览器。','**性能**：按飞腾 D2000 量级算力（约为主流桌面处理器的四分之一）模拟测试，打开约 3 秒，画布刷新约 36 毫秒，一键美化约 60 毫秒，内存占用约 22 MB。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('ReleaseNotes_v3.1.1.docx',await Packer.toBuffer(build({title:'经纬织图 V3.1.1 发布说明',header:'经纬织图　V3.1.1 发布说明',cover,body})));console.log('ok')})();
