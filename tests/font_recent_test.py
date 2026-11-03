import json, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
OUT = os.environ.get('JW_SHOT_DIR', '/opt/cursor/artifacts/screenshots')
os.makedirs(OUT, exist_ok=True)
CHROME = '/usr/bin/google-chrome'

EXPECT = {
    '初号': 42, '小初': 36, '一号': 26, '小一': 24, '二号': 22, '小二': 18,
    '三号': 16, '小三': 15, '四号': 14, '小四': 12, '五号': 10.5, '小五': 9,
    '六号': 7.5, '小六': 6.5, '七号': 5.5, '八号': 5,
}

def launch(pw):
    return pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])

def main():
    offline = os.path.join(DIST, 'offline.html')
    desk = os.path.join(DIST, 'desk.html')
    assert os.path.isfile(offline), offline
    with sync_playwright() as pw:
        b = launch(pw)
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + offline)
        pg.wait_for_timeout(400)
        got = pg.evaluate("""() => {
          const map = {};
          for (const s of CN_SIZES) map[s.name] = parseSize(s.name);
          return { map, n: CN_SIZES.length, num: parseSize('18'), junk: parseSize('不是字号'), eight: parseSize('八号') };
        }""")
        assert got['n'] == 16, got
        assert got['map'] == EXPECT, got['map']
        assert got['num'] == 18 and got['eight'] == 5 and got['junk'] is None

        pg.evaluate("""() => {
          const n = P().nodes.find(x => x.text && x.type !== 'band' && x.type !== 'lane' && x.type !== 'group');
          sel = new Set([n.id]); n.font = 'fangsong'; n.size = parseSize('五号'); render();
        }""")
        face = pg.evaluate("""() => {
          const n = nodeById([...sel][0]);
          const svg = exportSVGString(P(), false).str;
          const blob = JSON.parse(JSON.stringify({ format: 'hongtu', version: 1, doc }));
          const back = JSON.parse(JSON.stringify(blob));
          loadDoc(back.doc);
          const n2 = P().nodes.find(x => x.font === 'fangsong');
          return { size: n2 && n2.size, font: n2 && n2.font, svg: svg.indexOf('FangSong') >= 0, css: fontCSS(n2) };
        }""")
        assert face['size'] == 10.5 and face['font'] == 'fangsong' and face['svg'], face
        assert 'FangSong' in face['css'] and 'STFangsong' in face['css']

        pg.evaluate("""() => { const n = P().nodes.find(x => x.font === 'fangsong'); sel = new Set([n.id]); render(); }""")
        pg.wait_for_selector('#p-font')
        assert pg.input_value('#p-font') == 'fangsong'
        assert pg.input_value('#p-size') == '五号'
        pg.locator('#props').screenshot(path=os.path.join(OUT, 'font-panel.png'))
        pg.fill('#p-size', '18')
        pg.dispatch_event('#p-size', 'input')
        assert pg.evaluate("() => nodeById([...sel][0]).size") == 18

        office = pg.evaluate("""async () => {
          window.__saved = [];
          window.saveFile = saveFile = async (name, data) => { window.__saved.push({ name, data }); };
          const plain = mkNode({ type: 'text', text: '默认样本', x: 40, y: 40, w: 180, h: 40 });
          const song = mkNode({ type: 'text', text: '仿宋样本', font: 'fangsong', size: 16, x: 40, y: 100, w: 180, h: 40 });
          loadDoc({ name: '字体', theme: 'report', statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' }, custom: {}, pages: { root: { id: 'root', name: '总图', nodes: [plain, song], links: [] } } });
          await exportPPTX();
          const z = await JSZip.loadAsync(await window.__saved[0].data.arrayBuffer());
          const slide = await z.file('ppt/slides/slide1.xml').async('string');
          window.__saved = [];
          await exportVSDX();
          const z2 = await JSZip.loadAsync(await window.__saved[0].data.arrayBuffer());
          const page = await z2.file('visio/pages/page1.xml').async('string');
          const docxml = await z2.file('visio/document.xml').async('string');
          const near = (xml, text, face) => {
            const i = xml.indexOf(text);
            if (i < 0) return false;
            return xml.slice(Math.max(0, i - 2500), i + 400).indexOf(face) >= 0;
          };
          return {
            pptPlain: near(slide, '默认样本', 'Microsoft YaHei'),
            pptSong: near(slide, '仿宋样本', 'FangSong'),
            vsdPlain: near(page, '默认样本', 'Microsoft YaHei'),
            vsdSong: near(page, '仿宋样本', 'FangSong'),
            faces: docxml.indexOf("NameU='FangSong'") >= 0 && docxml.indexOf("NameU='Microsoft YaHei'") >= 0
          };
        }""")
        assert office['pptPlain'] and office['pptSong'] and office['vsdPlain'] and office['vsdSong'] and office['faces'], office

        pg.evaluate("() => localStorage.removeItem('hongtu.shelf')")
        pg.reload()
        pg.wait_for_timeout(300)
        assert pg.locator('#jw-webhist').count() == 0 or not pg.locator('#jw-webhist').is_visible()

        pg.evaluate("""() => {
          const d = buildDemo();
          d.name = '巡逻甲';
          localStorage.setItem('hongtu.shelf', JSON.stringify([{ id: 'a', name: '巡逻甲', path: '浏览器本地存储', t: Date.UTC(2026, 10, 3, 8, 30), doc: d }]));
        }""")
        pg.reload()
        pg.wait_for_timeout(400)
        assert pg.locator('#jw-webhist').is_visible()
        assert '巡逻甲' in pg.locator('#jw-webhist .nm').inner_text()
        assert '浏览器本地存储' in pg.locator('#jw-webhist .dir').inner_text()
        pg.locator('#jw-webhist').screenshot(path=os.path.join(OUT, 'welcome-web-with-history.png'))
        pg.click('#jw-webhist .nm')
        pg.fill('#jw-webhist input', '巡逻乙')
        pg.keyboard.press('Enter')
        pg.wait_for_timeout(150)
        stored = json.loads(pg.evaluate("() => localStorage.getItem('hongtu.shelf')"))
        assert stored[0]['name'] == '巡逻乙', stored[0]['name']
        assert stored[0]['doc']['name'] == '巡逻乙'
        pg.evaluate("() => localStorage.removeItem('hongtu.shelf')")
        pg.reload()
        pg.wait_for_timeout(300)
        assert not pg.locator('#jw-webhist').is_visible()
        assert not errs, errs[:3]
        pg.close()

        def desk_shot(recent):
            p = b.new_page(viewport={'width': 1440, 'height': 900})
            payload = json.dumps(recent)
            p.add_init_script("""(() => {
              const recent = %s;
              window.jwDesk = {
                on() {},
                info: async () => ({ version: '3.3.4', platform: 'linux', arch: 'x64' }),
                pending: async () => [],
                recent: async () => recent,
                recentRemove: async () => true,
                rename: async (file, nm) => { window.__ren = [file, nm]; return { path: '/tmp/proj/' + nm + '.jingwei.json', name: nm + '.jingwei.json', dir: '/tmp/proj', t: Date.now() }; },
                title() {}, win() {}, read: async () => { throw new Error('no read'); }
              };
            })();""" % payload)
            p.goto('file://' + desk)
            p.wait_for_selector('#jw-start.on', timeout=20000)
            p.wait_for_timeout(400)
            return p

        with_hist = desk_shot([{
            'path': '/tmp/proj/patrol.jingwei.json', 'name': 'patrol.jingwei.json',
            'dir': '/tmp/proj', 't': 1762158600000,
        }])
        assert with_hist.locator('#jw-hist').is_visible()
        assert 'patrol' in with_hist.locator('#jw-hist .nm').inner_text()
        assert '/tmp/proj/patrol.jingwei.json' in with_hist.locator('#jw-hist .dir').inner_text()
        with_hist.screenshot(path=os.path.join(OUT, 'welcome-with-history.png'))
        with_hist.click('#jw-hist .nm')
        with_hist.fill('#jw-hist input', 'renamed-patrol')
        with_hist.keyboard.press('Enter')
        with_hist.wait_for_timeout(200)
        assert with_hist.evaluate('() => window.__ren') == ['/tmp/proj/patrol.jingwei.json', 'renamed-patrol']
        with_hist.close()

        empty = desk_shot([])
        assert not empty.locator('#jw-hist').is_visible()
        assert empty.locator('#jw-start .cards').is_visible()
        empty.screenshot(path=os.path.join(OUT, 'welcome-without-history.png'))
        empty.close()
        b.close()
    print('font recent ok')

if __name__ == '__main__':
    main()
