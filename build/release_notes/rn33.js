const {P,H,TBL,build,Packer,Paragraph,TextRun,AlignmentType,rf,CNH,CN,rich}=require('./lib.js');
const body=[]; const add=(...a)=>a.forEach(x=>Array.isArray(x)?body.push(...x):body.push(x));
const LI=(t)=>new Paragraph({children:rich(t,{}),numbering:{reference:'bul',level:0},spacing:{line:330,lineRule:'auto',after:40},alignment:AlignmentType.LEFT});
const C=(t,size,font,bold,after)=>new Paragraph({alignment:AlignmentType.CENTER,indent:{firstLine:0},spacing:{after:after||120},children:[new TextRun({text:t,size,bold:!!bold,font:rf(font)})]});
const cover=[new Paragraph({spacing:{before:3200},children:[]}),C('经纬织图',52,CNH,true,200),C('V3.3 桌面版　安装与使用说明',36,CNH,true,1600),C(require('./lib.js').BRAND.org,30,CN,false,120),C('2026 年 10 月 19 日',28,CN,false,120)];
add(P('**v3.3 起经纬织图提供独立桌面版：自带运行环境，双击即用，不依赖系统浏览器，不需要联网；同时支持 Windows 7～11 与银河麒麟 V10（飞腾 arm64、x86_64）。绘图功能与 v3.2.1 一致，工程文件完全通用。**'));
add(H('一、安装包选择',1));
add(TBL('安装包清单',['系统','文件','说明'],[
 ['Windows 10／11（64 位）','经纬织图_v3.3.0_Windows_x64_安装包.exe','推荐。安装到当前用户目录，无需管理员权限'],
 ['Windows 7 SP1／8（64 位）','同上','同上'],
 ['Windows 7（32 位）','经纬织图_v3.3.0_Windows_x86_安装包.exe','32 位系统专用'],
 ['Windows 免安装','经纬织图_v3.3.0_Windows_x64（或 x86）_绿色版.zip','解压后双击 JingWeiZhiTu.exe，可放 U 盘'],
 ['银河麒麟 V10（飞腾）','经纬织图_v3.3.0_银河麒麟_飞腾arm64.deb','适用飞腾 D2000 等 arm64 机型'],
 ['银河麒麟 V10（x86）','经纬织图_v3.3.0_银河麒麟_x86_64.deb','适用海光、兆芯、Intel 等 x86 机型'],
],[2300,3700,2600]));
add(P('查看 Windows 是 32 位还是 64 位：右键“计算机”（或“此电脑”）→ 属性 → 系统类型。查看麒麟机型：开始菜单 → 设置 → 关于，处理器为 Phytium（飞腾）选 arm64 包。'));
add(H('二、Windows 安装',1));
['**安装包**：双击安装包 → 下一步 → 安装。默认装到“C:\\Users\\用户名\\AppData\\Local\\Programs\\JingWeiZhiTu”，自动创建桌面和开始菜单快捷方式“经纬织图”。全程不需要管理员权限。','**绿色版**：把 zip 解压到任意位置（整个 JingWeiZhiTu 文件夹一起拷贝），双击 JingWeiZhiTu.exe。可右键“发送到 → 桌面快捷方式”。','**卸载**：开始菜单 → 经纬织图 → 卸载 经纬织图；或“控制面板 → 程序和功能”。','**右键打开**：安装版会把经纬织图加入 .vsdx、.pptx、.drawio、.json 文件的“打开方式”列表，不改变原有默认程序。'].forEach(t=>add(LI(t)));
add(H('三、银河麒麟安装',1));
['**图形界面**：双击 deb 文件，用“软件安装器”安装（需输入当前用户密码）。安装后在开始菜单“图形”或“办公”分类中找到“经纬织图”。','**命令行**：sudo dpkg -i 经纬织图_v3.3.0_银河麒麟_飞腾arm64.deb；启动命令 jingwei-zhitu；卸载 sudo dpkg -r jingwei-zhitu。','**离线安装**：安装包已内置全部运行组件，不需要联网下载依赖。若提示缺少系统运行库（极少见，通常是精简安装的系统），启动时会弹窗列出缺少的库名，请联系系统管理员补装。','**显示异常**：默认关闭显卡加速以兼容国产显卡；如需开启，在终端运行 jingwei-zhitu --gpu。'].forEach(t=>add(LI(t)));
add(H('四、桌面版新增',1));
add(TBL('桌面版功能',['功能','说明'],[
 ['首页','启动后显示首页：新建空白图、打开文件、从模板新建、文字成图、格式转换、打开示例，以及最近打开的文件'],
 ['保存','Ctrl+S 直接保存到当前文件；Ctrl+S 首次保存或 Ctrl+Shift+S 另存为时弹出系统保存对话框'],
 ['未保存提醒','标题栏文件名前出现橙色圆点表示有未保存修改；关闭窗口时提示是否保存'],
 ['打开文件','系统打开对话框；可把文件直接拖进窗口；可双击 .jingwei.json 文件或用“打开方式”启动'],
 ['导出','PNG、PPT、Visio、draw.io、SVG、规范表格均弹出系统保存对话框，并记住上次保存的文件夹'],
 ['批量转换','格式转换时先选一次保存文件夹，全部结果写入该文件夹，完成后自动打开'],
 ['窗口','深蓝标题栏，最小化／最大化／关闭；双击标题栏最大化；F11 全屏；窗口大小与位置自动记忆'],
],[1800,6800]));
add(H('五、说明',1));
['**与网页版的关系**：桌面版内置独立的运行环境，与网页版（单个 html 文件）功能相同、工程文件通用，两者可同时保留。','**数据位置**：设置与最近文件记录保存在用户目录（Windows：%APPDATA%\\经纬织图；麒麟：~/.config/经纬织图），不写入安装目录。','**大模型功能**：参照生成、文字成图的“大模型”模式需内网 OpenAI 兼容接口（如 DeepSeek），在对话框设置中填写；不配置时使用离线规则。'].forEach(t=>add(LI(t)));
(async()=>{require('fs').writeFileSync('Guide_v3.3.docx',await Packer.toBuffer(build({title:'经纬织图 V3.3 桌面版 安装与使用说明',header:'经纬织图　V3.3 桌面版 安装与使用说明',cover,body})));console.log('ok')})();
