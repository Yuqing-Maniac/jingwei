"""生成 desktop/splash.html（启动画面，内嵌图标与得意黑子集字体）与 desktop/brand.woff。
需要 fonttools（pip install fonttools）。"""
import base64, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, 'desktop')
TEXT = "经纬织图体系架构绘图桌面版正在启动…新建打开最近模板文字成图格式转换示例欢迎使用纵横织网成首页JingWei ZhiTu0123456789.v"
if '--reuse-font' not in sys.argv:
    subprocess.run([sys.executable, '-m', 'fontTools.subset', os.path.join(ROOT, 'assets', 'fonts', 'SmileySans-Oblique.ttf'), '--text=' + TEXT, '--flavor=woff',
                    '--output-file=' + os.path.join(D, 'brand.woff')], check=True)
ic = base64.b64encode(open(os.path.join(ROOT, 'assets', 'brand', 'icon.svg'), 'rb').read()).decode()
ft = base64.b64encode(open(os.path.join(D, 'brand.woff'), 'rb').read()).decode()
html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>经纬织图</title><style>
@font-face{{font-family:Brand;src:url(data:font/woff;base64,{ft}) format('woff')}}
html,body{{margin:0;height:100%;overflow:hidden;user-select:none;-webkit-app-region:drag}}
body{{background:radial-gradient(ellipse 90% 80% at 30% 35%,#17407e 0%,#0b2148 55%,#061430 100%);font-family:'Noto Sans SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif;color:#fff;position:relative}}
.grid{{position:absolute;top:0;right:0;bottom:0;left:0;background-image:linear-gradient(rgba(110,180,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(110,180,255,.07) 1px,transparent 1px);background-size:26px 26px}}
.wrap{{position:absolute;left:44px;top:80px;display:flex;align-items:center;gap:26px}}
.logo{{width:100px;height:100px;filter:drop-shadow(0 10px 22px rgba(0,0,0,.45)) drop-shadow(0 0 18px rgba(76,168,255,.35));animation:pop .7s cubic-bezier(.2,1.4,.4,1) both}}
.t{{font-family:Brand,sans-serif;font-size:48px;letter-spacing:.08em;line-height:1;background:linear-gradient(180deg,#fff 15%,#cfe9ff 55%,#62b4ff);-webkit-background-clip:text;color:transparent;animation:up .6s .12s both}}
.s{{margin-top:12px;font-size:16px;letter-spacing:.3em;color:#bcd6f3;animation:up .6s .22s both}}
.foot{{position:absolute;left:44px;right:44px;bottom:42px;font-size:12px;color:#8fb2d8;letter-spacing:.08em;display:flex;justify-content:space-between}}
.bar{{position:absolute;left:44px;right:44px;bottom:28px;height:3px;border-radius:2px;background:rgba(255,255,255,.1);overflow:hidden}}
.bar i{{position:absolute;top:0;bottom:0;width:38%;border-radius:2px;background:linear-gradient(90deg,transparent,#2bd4c4,#4ca8ff,transparent);animation:run 1.1s linear infinite}}
@keyframes run{{from{{left:-40%}}to{{left:100%}}}}
@keyframes pop{{from{{transform:scale(.6);opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes up{{from{{transform:translateY(14px);opacity:0}}to{{transform:none;opacity:1}}}}
.weave{{position:absolute;top:0;left:0;width:100%;height:100%;opacity:.5}}
.weave path{{fill:none;stroke-width:1.5;stroke-dasharray:700;stroke-dashoffset:700;animation:weave 1.2s ease-out forwards}}
.weave .lat{{stroke:#65c9ff;animation-delay:.12s}}
.weave .lon{{stroke:#5ce5c0;animation-delay:.3s}}
.weave circle{{fill:#ffcf83;animation:pop .45s .9s both;transform-origin:center;transform-box:fill-box}}
@keyframes weave{{to{{stroke-dashoffset:0}}}}
@media(prefers-reduced-motion:reduce){{.logo,.t,.s,.weave path,.weave circle,.bar i{{animation:none}}.weave path{{stroke-dashoffset:0}}.bar i{{left:31%}}}}
</style></head><body><div class="grid"></div>
<svg class="weave" viewBox="0 0 520 320" aria-hidden="true"><g class="lat"><path class="lat" d="M0 50 H520 M0 270 H520"/></g><g><path class="lon" d="M28 0 V320 M492 0 V320"/></g><circle cx="28" cy="50" r="4"/><circle cx="492" cy="270" r="4"/></svg>
<div class="wrap"><img class="logo" src="data:image/svg+xml;base64,{ic}"><div><div class="t">经纬织图</div><div class="s">纵横经纬　织网成图</div></div></div>
<div class="foot"><span>体系架构绘图 · 桌面版</span><span>正在启动…</span></div><div class="bar"><i></i></div></body></html>'''
open(os.path.join(D, 'splash.html'), 'w', encoding='utf-8').write(html)
print('ok')
