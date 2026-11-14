"""网页版构建：把 app/ 下的模块拼成单文件 html。
用法：python3 build/build_web.py [--desk] [--modern] [--no-artifact]
输出（均在仓库 dist/ 下）：
  offline.html   离线单文件网页版（内联 jszip / pptxgenjs / milsymbol，脚本降级到 Chrome 69 / Firefox 68）
  artifact.html  在线预览版（三方库走 CDN，不降级）
  desk.html      桌面版界面（offline.html + app/desk/desk.css、desk.js），--desk 时生成
依赖：仓库根目录先 npm ci（node_modules 中需有 jszip、pptxgenjs、milsymbol、esbuild、acorn）。"""
import sys, glob, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app'); DIST = os.path.join(ROOT, 'dist'); NM = os.path.join(ROOT, 'node_modules')
os.makedirs(DIST, exist_ok=True)
rd = lambda p: open(os.path.join(APP, p), encoding='utf-8').read()
body = rd('app_body.html')
body = ('<script>try { var skin = localStorage.getItem("hongtu.uiSkin"); '
        'document.documentElement.setAttribute("data-theme", /^(light|jade|paper|dark)$/.test(skin) ? skin : "light"); '
        '} catch (_) { document.documentElement.setAttribute("data-theme", "light"); }</script>\n'
        + body + '<style>\n' + rd('skins.css') + '\n</style>\n')
parts = [rd('icons.js')] + [rd(os.path.basename(p)) for p in sorted(glob.glob(os.path.join(APP, 'icons_*.js')))]
MODS = ['app.js', 'skins.js', 'glyphbook.js', 'imgimport.js', 'backup.js', 'compact.js', 'combo.js', 'standards.js', 'xlsxexport.js', 'templates.js', 'std_templates.js', 'textgen.js',
        'importers.js', 'vsdxraw.js', 'drawio.js', 'refgen.js', 'convert.js']
if os.path.exists(os.path.join(APP, 'redrawn.js')):
    parts.append(rd('redrawn.js'))
mods = [rd(m) for m in MODS]
own = "<script>\n" + "\n".join(parts) + "\n</script>\n<script>\n" + "\n".join(mods) + "\n" + rd('demo.js') + "\nloadDoc(buildDemo());\nif (!window.jwDesk) Backup.offer();\n</script>\n"
cdn = ('<script src="https://cdn.jsdelivr.net/npm/dompurify@3.4.17/dist/purify.min.js"></script>\n'
       '<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>\n'
       '<script src="https://cdnjs.cloudflare.com/ajax/libs/pptxgenjs/3.12.0/pptxgen.bundle.js"></script>\n'
       '<script src="https://cdn.jsdelivr.net/npm/milsymbol@2.2.0/dist/milsymbol.js"></script>\n')
if '--no-artifact' not in sys.argv:
    open(os.path.join(DIST, 'artifact.html'), 'w', encoding='utf-8').write(body + cdn + own)
def inl(p):
    return '<script>\n' + open(os.path.join(NM, p), encoding='utf-8').read().replace('</script', '<\\/script') + '\n</script>\n'
off = body.replace('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap">', '')
off = ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       '<style>*{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style></head><body>\n'
       + '<script>\n' + rd('compat.js') + '\n</script>\n' + off
       + inl('dompurify/dist/purify.min.js') + inl('jszip/dist/jszip.min.js') + inl('pptxgenjs/dist/pptxgen.bundle.js') + inl('milsymbol/dist/milsymbol.js') + own + '</body></html>')
out = os.path.join(DIST, 'offline.html')
open(out, 'w', encoding='utf-8').write(off)
if '--modern' not in sys.argv:
    subprocess.run(['node', os.path.join(ROOT, 'build', 'downlevel.js'), out], check=True)
print(os.path.getsize(out) // 1024, 'KB -> dist/offline.html')
if '--desk' in sys.argv:
    d = open(out, encoding='utf-8').read()
    css = '<style>\n' + rd('desk/desk.css') + '\n</style>\n'
    js = '<script>\n' + rd('desk/desk.js') + '\n</script>\n'
    d = d.replace('</head>', css + '</head>', 1)
    # A bundled library may contain the literal closing tags in a JS string.
    # Inject only at the document's final closing tags, never inside that library.
    end = d.rfind('</body></html>')
    if end < 0:
        raise RuntimeError('missing document closing tags')
    d = d[:end] + js + d[end:]
    d = d.replace('<title>经纬织图</title>', '<title>经纬织图</title><meta http-equiv="Content-Security-Policy" content="default-src \'self\' data: blob: \'unsafe-inline\' \'unsafe-eval\'; connect-src *; img-src * data: blob:">', 1)
    open(os.path.join(DIST, 'desk.html'), 'w', encoding='utf-8').write(d); print('desk.html', len(d) // 1024, 'KB -> dist/desk.html')
