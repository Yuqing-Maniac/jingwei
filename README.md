# 经纬织图 JingWei ZhiTu

体系架构图／泳道图绘制工具：分层框架、拟物化装备图标、文字成图、一键美化，PowerPoint／Visio／draw.io 打开与互转。全部组件内置，离线运行。

## 两种形态

| 形态 | 文件 | 运行方式 |
|---|---|---|
| 网页版（单文件） | `JingWeiZhiTu_v<版本>.html` | 用 Chromium 69+／Firefox 68+ 内核浏览器打开，无需安装 |
| 桌面版（自带运行环境，不需要浏览器） | Windows 绿色版 zip；银河麒麟免安装 zip | 解压后双击或执行启动脚本，无需安装 |

## 支持平台

- Windows 7 SP1、8、10、11（x64 与 32 位 x86）
- 银河麒麟桌面操作系统 V10（含国防版）：飞腾 arm64（D2000 已实测）、x86_64
- 网页版另可在任何 Chromium 69+／Firefox 68+ 浏览器中使用

## 主要功能

- **绘图**：分组带、层（泳道）、子容器；基础形状、流程图形、箭头；三百多个拟物化图标（无人、反无人、指控、感知通信等）与编队复合图标。
- **文字成图**（Ctrl+Shift+G）：粘贴文字或 Markdown，自动生成分层架构图。
- **参照生成**（Ctrl+Shift+L）：以一张好图为参照，填入新项目内容生成同款新图；可接内网 OpenAI 兼容大模型，也可离线。
- **一键美化**（Ctrl+Shift+F）：对齐、等距；连线从框边中点出入、同边多线对称排布、绕开中间的框且拐弯最少；拖动吸附。
- **规范视图**：DoDAF（OV-1、OV-2、OV-5b、SV-1、SV-4）与信息系统六类架构视图，自动编号、规范检查、标题栏、规范表格（xlsx）。
- **格式互通**（Ctrl+Shift+O）：打开 .pptx／.vsdx／.drawio；导出 PNG（透明、报告插图）、PPT、Visio、draw.io、SVG；Visio 批量转 PPT 时字体字号原样还原。
- **报告版心**：按版心宽与图内字号排版，插入 Word 即为版心宽。

## 下载

到仓库 **Releases** 页面下载标签为 `jingwei-v<版本>` 的正式版。页面只挂免安装包、网页离线包、增量包和 `SHA256SUMS.txt`。下载文件名是 ASCII，例如 `jingwei_v3.3.14_windows_x64_portable.zip`；中文名只作显示名。不提供 deb 与 Windows 安装包。

## 使用

- **Windows 绿色版**：解压 `jingwei_v<版本>_windows_x64_portable.zip` 或 `windows_x86_portable.zip`，双击 `JingWeiZhiTu/JingWeiZhiTu.exe`。
- **银河麒麟免安装**：解压 `kylin_arm64_portable.zip` 或 `kylin_x86_64_portable.zip`，在目录里执行 `sh start.sh`。
- **网页版**：解压 `web_offline.zip`，双击 html 文件。
- **增量升级**：桌面版标题栏「增量升级」选择 `incremental.zip`。见 `docs/INCREMENT.md`。

详细说明见 `docs/release-notes/Guide_v3.3.pdf`。

## 常用快捷键

Ctrl+S 保存（桌面版直接写回当前文件），Ctrl+Shift+S 另存为（桌面版），Ctrl+O 打开，Ctrl+E 导出，F1 全部快捷键，F11 全屏（桌面版）。

## 从源码构建

见 `CLAUDE.md` 第 5 节。一句话：`npm ci && bash build/build_all.sh`，产物在 `_work/dist/`。
