/* Run after build_web.py --desk and stage.py. PW_MODULE and JW_ELECTRON select local runtimes. */
const assert = require('assert');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
const { chromium, _electron } = require(process.env.PW_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '_work', 'qa-results');
fs.mkdirSync(out, { recursive: true });
async function skins(page, desk) {
  const initial = await page.evaluate(() => projectJSON());
  for (const key of ['light', 'jade', 'paper', 'dark']) {
    await page.locator('header .jw-skin-select').selectOption(key);
    assert.equal(await page.locator('html').getAttribute('data-theme'), key);
    const colors = await page.evaluate(() => ({ panel: getComputedStyle(document.querySelector('#props')).backgroundColor, fg: getComputedStyle(document.querySelector('#props')).color }));
    assert.notEqual(colors.panel, colors.fg);
    assert.equal(await page.evaluate(() => projectJSON()), initial, 'skin must not change document');
    if (desk) {
      const close = await page.locator('header [data-w=close]').boundingBox();
      assert(close.x + close.width <= await page.evaluate(() => innerWidth), 'toolbar fits desktop screen');
    }
    await page.screenshot({ path: path.join(out, (desk ? 'desktop-' : 'web-') + key + '.png') });
  }
  await page.reload();
  await page.waitForSelector('header .jw-skin-select');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark', 'skin survives restart/reload');
}
(async () => {
  const errors = [];
  const browser = await chromium.launch({ executablePath: process.env.JW_CHROME });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, colorScheme: 'dark' });
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(pathToFileURL(path.join(root, 'dist', 'offline.html')).href);
  await skins(page, false);
  await page.evaluate(() => { setTheme('command'); undo(); });
  assert.equal(await page.locator('#b-theme').inputValue(), await page.evaluate(() => doc.theme));
  for (const kind of ['svg', 'png', 'pptx', 'vsdx']) {
    await page.locator('#b-export').click();
    const download = page.waitForEvent('download');
    await page.locator('[data-exp="' + kind + '"]').click();
    const d = await download; await d.saveAs(path.join(out, 'demo.' + kind));
    assert(fs.statSync(path.join(out, 'demo.' + kind)).size > 100);
  }
  await page.goto(pathToFileURL(path.join(root, 'desktop', 'splash.html')).href);
  await page.waitForTimeout(1100);
  await page.setViewportSize({ width: 520, height: 320 });
  await page.screenshot({ path: path.join(out, 'splash.png') });
  await browser.close();
  const env = { ...process.env, JW_TEST_DIR: out, JW_TEST_CLOSE: 'cancel' }; delete env.ELECTRON_RUN_AS_NODE;
  const app = await _electron.launch({ executablePath: process.env.JW_ELECTRON, args: [path.join(root, '_work/stage/app'), '--user-data-dir=' + path.join(out, 'profile')], env });
  try {
    let editor;
    for (let i = 0; i < 100; i++) {
      editor = app.windows().find(p => p.url().endsWith('/app/index.html'));
      if (editor) break; await new Promise(r => setTimeout(r, 100));
    }
    assert(editor, 'desktop editor opens');
    editor.on('pageerror', e => errors.push(String(e)));
    await editor.waitForSelector('#jw-go');
    await editor.waitForTimeout(400);
    assert(await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows().find(w => w.getTitle().includes('经纬织图')).isFullScreen()), 'starts fullscreen');
    await editor.locator('#jw-go').click();
    await skins(editor, true);
    await editor.locator('#jw-go').click();
    await editor.evaluate(() => saveProject());
    await editor.evaluate(() => { checkpoint(); doc.name = 'Unsaved regression'; render(); });
    await editor.evaluate(() => saveProject());
    await editor.evaluate(() => undo());
    assert(await editor.locator('#jw-file').evaluate(el => el.classList.contains('dirty')), 'undo after save is dirty');
    await editor.evaluate(() => saveProject());
    await editor.evaluate(() => redo());
    assert(await editor.locator('#jw-file').evaluate(el => el.classList.contains('dirty')), 'redo after save is dirty');
    const before = await editor.evaluate(() => projectJSON());
    await editor.locator('#b-new').click();
    await editor.waitForTimeout(100);
    assert.equal(await editor.evaluate(() => projectJSON()), before, 'cancel new keeps edits');
    await app.evaluate(() => { process.env.JW_TEST_CLOSE = 'discard'; });
    await editor.locator('#b-new').click();
    await editor.waitForTimeout(150);
    assert(await editor.locator('#jw-file').evaluate(el => el.classList.contains('dirty')), 'new document needs saving');
    await app.evaluate(() => { process.env.JW_TEST_CLOSE = 'cancel'; process.env.JW_TEST_OPEN = process.env.JW_TEST_DIR + '/missing.json'; });
    const newDoc = await editor.evaluate(() => projectJSON());
    await editor.locator('#b-open').click();
    await editor.waitForTimeout(100);
    assert.equal(await editor.evaluate(() => projectJSON()), newDoc, 'cancel open keeps edits');
    await editor.locator('header [data-w=full]').click();
    await editor.waitForTimeout(200);
    await editor.waitForFunction(() => document.querySelector('header [data-w=full]').textContent === '全屏', null, { timeout: 3000 });
    await editor.keyboard.press('F11'); await editor.waitForTimeout(200);
    assert.equal(await editor.locator('header [data-w=full]').innerText(), '退出全屏');
    // Saving must retain edits made while the asynchronous write is outstanding.
    await app.evaluate(({ ipcMain }) => {
      ipcMain.removeHandler('jw:save');
      ipcMain.handle('jw:save', async () => { await new Promise(r => setTimeout(r, 150)); return process.env.JW_TEST_DIR + '/delayed.jingwei.json'; });
    });
    await editor.evaluate(async () => { const p = saveProject(); checkpoint(); doc.name = 'Edited during save'; await p; });
    assert(await editor.locator('#jw-file').evaluate(el => el.classList.contains('dirty')), 'concurrent edit remains dirty');
    await editor.locator('#jw-home').click();
    await editor.locator('#jw-start .jw-skin-select').selectOption('jade');
    await editor.waitForTimeout(350);
    await editor.screenshot({ path: path.join(out, 'desktop-home.png') });
    // Narrow window must keep the close button reachable.
    await app.evaluate(({ BrowserWindow }) => { const w = BrowserWindow.getAllWindows()[0]; w.setFullScreen(false); w.setSize(1024, 720); });
    await editor.waitForTimeout(300);
    await editor.locator('#jw-go').click();
    await editor.screenshot({ path: path.join(out, 'desktop-narrow.png') });
    const box = await editor.locator('header [data-w=close]').boundingBox();
    assert(box && box.x + box.width <= await editor.evaluate(() => innerWidth), 'window controls fit narrow screen');
  } finally { await app.evaluate(({ app }) => app.exit(0)).catch(() => {}); }
  assert.deepEqual(errors, []);
  console.log('PASS skins, persistence, export, fullscreen, dirty-state and unsaved-work protection');
})().catch(e => { console.error(e); process.exit(1); });
