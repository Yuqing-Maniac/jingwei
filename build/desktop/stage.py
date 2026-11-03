"""组装桌面版应用目录：desktop/ 外壳 + dist/desk.html → _work/stage/app"""
import shutil, os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(ROOT, 'desktop'); W = os.environ.get('JW_WORK', os.path.join(ROOT, '_work')); O = os.path.join(W, 'stage', 'app')
shutil.rmtree(O, ignore_errors=True); os.makedirs(O + '/app')
for f in ['package.json', 'main.js', 'recent.js', 'preload.js', 'splash.html', 'icon.png', 'icon.ico']: shutil.copy(f'{S}/{f}', O)
sys.path.insert(0, os.path.join(ROOT, 'build')); import brand
pk = json.load(open(f'{O}/package.json', encoding='utf-8')); pk['author'] = brand.load(quiet=True)['org']   # 机构标识：brand.local.json（不入库）
json.dump(pk, open(f'{O}/package.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
shutil.copy(os.path.join(ROOT, 'dist', 'desk.html'), O + '/app/index.html')
print('staged', sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(O) for f in fs) // 1024, 'KB ->', O)
