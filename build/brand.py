"""机构标识（单位名称、版权、维护者邮箱）。仓库只含通用值 jingwei/brand.example.json；
正式构建时在本地放置 jingwei/brand.local.json（不入库，已在 .gitignore）覆盖。
用于：deb 维护者、exe 公司名与版权、NSIS 卸载信息发布者、桌面版 package.json author、发布说明与宣传素材的“出品”。
命令行：python3 build/brand.py [字段]  → 打印整份 JSON 或单个字段"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(quiet=False):
    b = json.load(open(os.path.join(ROOT, 'brand.example.json'), encoding='utf-8'))
    p = os.path.join(ROOT, 'brand.local.json')
    if os.path.exists(p): b.update(json.load(open(p, encoding='utf-8')))
    elif not quiet: print('提示：未找到 brand.local.json，使用通用机构标识：' + b['org'], file=sys.stderr)
    return b
if __name__ == '__main__':
    b = load()
    print(b[sys.argv[1]] if len(sys.argv) > 1 else json.dumps(b, ensure_ascii=False, indent=2))
