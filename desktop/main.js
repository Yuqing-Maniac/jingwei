/* 经纬织图 桌面版 — 主进程（Electron 22：支持 Windows 7～11、银河麒麟 V10 x86／飞腾） */
'use strict';
const { app, BrowserWindow, ipcMain, dialog, shell, Menu, screen, nativeImage, nativeTheme } = require('electron');
const path = require('path');
const fs = require('fs');
const recentLib = require('./recent');

const isLinux = process.platform === 'linux', isWin = process.platform === 'win32';
// 国产 GPU 驱动差异大：Linux 默认软件渲染，避免黑屏／花屏；可用 --gpu 强制开启
if (isLinux && !process.argv.includes('--gpu')) app.disableHardwareAcceleration();
app.commandLine.appendSwitch('disable-features', 'HardwareMediaKeyHandling,MediaSessionService');
if (isWin) app.setAppUserModelId('cn.ycq.jingwei-zhitu');

const T = process.env.JW_TEST_DIR || '';   // 自动化测试：跳过系统对话框
const OPENABLE = /\.(json|png|jpe?g|pptx|vsdx|drawio|xml)$/i;
const DATA = app.getPath('userData');
const STORE = path.join(DATA, 'desk.json');
let store = { recent: [], lastDir: '', win: null };
try { store = Object.assign(store, JSON.parse(fs.readFileSync(STORE, 'utf8'))); } catch (_) { }
const saveStore = () => { try { fs.mkdirSync(DATA, { recursive: true }); fs.writeFileSync(STORE, JSON.stringify(store)); } catch (_) { } };
const ICON = path.join(__dirname, isWin ? 'icon.ico' : 'icon.png');

let win = null, splash = null, pendingOpen = [], forceClose = false;
const fileArgs = argv => argv.slice(1).filter(a => !a.startsWith('-') && OPENABLE.test(a) && fs.existsSync(a)).map(a => path.resolve(a));

if (!app.requestSingleInstanceLock()) { app.quit(); }
else app.on('second-instance', (_e, argv) => {
  if (!win) return;
  if (win.isMinimized()) win.restore(); win.show(); win.focus();
  for (const f of fileArgs(argv)) win.webContents.send('jw:open-path', f);
});

function addRecent(p) {
  if (!p) return;
  store.recent = [p, ...store.recent.filter(x => x !== p)].slice(0, 12);
  if (isWin) app.addRecentDocument(p);
  saveStore();
}

function createSplash() {
  splash = new BrowserWindow({ width: 520, height: 320, frame: false, resizable: false, movable: true, center: true, show: false,
    skipTaskbar: false, backgroundColor: '#081a3a', icon: ICON, alwaysOnTop: false, webPreferences: { sandbox: true, spellcheck: false } });
  splash.setMenu(null);
  splash.loadFile(path.join(__dirname, 'splash.html'));
  splash.once('ready-to-show', () => splash && splash.show());
}

function createMain() {
  const wa = screen.getPrimaryDisplay().workAreaSize;
  const st = store.win || {};
  const W = Math.min(st.w || 1440, wa.width), H = Math.min(st.h || 900, wa.height);
  win = new BrowserWindow({
    width: Math.max(1024, W), height: Math.max(640, H), x: st.x, y: st.y, minWidth: 980, minHeight: 600,
    frame: false, show: false, backgroundColor: '#0b2148', icon: ICON, title: '经纬织图',
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: false, spellcheck: false, devTools: !app.isPackaged || process.argv.includes('--dev') },
  });
  win.setMenu(null);
  win.loadFile(path.join(__dirname, 'app', 'index.html'));
  win.once('ready-to-show', () => {
    if (st.max) win.maximize();
    win.show();
    setTimeout(() => { if (splash) { splash.destroy(); splash = null; } }, 120);
  });
  const sendState = () => win && win.webContents.send('jw:win-state', { max: win.isMaximized(), full: win.isFullScreen() });
  win.on('maximize', sendState); win.on('unmaximize', sendState); win.on('enter-full-screen', sendState); win.on('leave-full-screen', sendState);
  win.on('close', e => {
    const b = win.getNormalBounds(); store.win = { x: b.x, y: b.y, w: b.width, h: b.height, max: win.isMaximized() }; saveStore();
    if (forceClose) return;
    e.preventDefault(); win.webContents.send('jw:before-close');
  });
  win.on('closed', () => { win = null; });
  // 外部链接用系统程序打开；禁止页面跳转
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/i.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', e => e.preventDefault());
  // 兜底：页面仍走 <a download> 时用系统保存对话框
  win.webContents.session.on('will-download', (_e, item) => {
    item.setSaveDialogOptions({ title: '保存', defaultPath: path.join(store.lastDir || app.getPath('documents'), item.getFilename()) });
    item.once('done', (_e2, state) => { if (state === 'completed') { store.lastDir = path.dirname(item.getSavePath()); saveStore(); } });
  });
  win.webContents.on('render-process-gone', (_e, d) => {
    dialog.showMessageBox({ type: 'error', title: '经纬织图', message: '绘图窗口异常退出（' + d.reason + '），将重新加载。', buttons: ['确定'] }).then(() => win && win.reload());
  });
}

/* ---------------- IPC ---------------- */
const FILTERS = {
  json: [{ name: '经纬织图工程', extensions: ['json'] }], pptx: [{ name: 'PowerPoint 演示文稿', extensions: ['pptx'] }], vsdx: [{ name: 'Visio 绘图', extensions: ['vsdx'] }],
  drawio: [{ name: 'draw.io 图', extensions: ['drawio'] }], png: [{ name: 'PNG 图片', extensions: ['png'] }], svg: [{ name: 'SVG 矢量图', extensions: ['svg'] }],
  xlsx: [{ name: 'Excel 工作簿', extensions: ['xlsx'] }],
};
const filtersFor = name => { const ext = (name.match(/\.([^.]+)$/) || [])[1]; return [...(FILTERS[(ext || '').toLowerCase()] || []), { name: '所有文件', extensions: ['*'] }]; };
const toBuf = d => Buffer.from(d instanceof ArrayBuffer ? new Uint8Array(d) : d);

ipcMain.handle('jw:save', async (_e, { name, data, path: target, title }) => {
  let p = target;
  if (!p && T) p = path.join(T, name);
  if (!p) {
    const r = await dialog.showSaveDialog(win, { title: title || '保存', defaultPath: path.join(store.lastDir || app.getPath('documents'), name), filters: filtersFor(name) });
    if (r.canceled || !r.filePath) return null;
    p = r.filePath;
  }
  fs.writeFileSync(p, toBuf(data));
  store.lastDir = path.dirname(p); saveStore();
  if (/\.json$/i.test(p)) addRecent(p);
  return p;
});
ipcMain.handle('jw:pick-dir', async (_e, title) => {
  if (T) return T;
  const r = await dialog.showOpenDialog(win, { title: title || '选择保存文件夹', defaultPath: store.lastDir || app.getPath('documents'), properties: ['openDirectory', 'createDirectory'] });
  if (r.canceled || !r.filePaths[0]) return null;
  store.lastDir = r.filePaths[0]; saveStore(); return r.filePaths[0];
});
ipcMain.handle('jw:write-in', async (_e, { dir, name, data }) => {
  let p = path.join(dir, name.replace(/[\\/:*?"<>|]/g, '_'));
  const ext = path.extname(p), base = p.slice(0, p.length - ext.length); let k = 2;
  while (fs.existsSync(p)) p = `${base}(${k++})${ext}`;
  fs.writeFileSync(p, toBuf(data)); return p;
});
ipcMain.handle('jw:read', async (_e, p) => {
  const b = fs.readFileSync(p); addRecent(p);
  return { name: path.basename(p), path: p, data: b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) };
});
ipcMain.handle('jw:open-dialog', async () => {
  if (T) return process.env.JW_TEST_OPEN || null;
  const r = await dialog.showOpenDialog(win, { title: '打开', defaultPath: store.lastDir || app.getPath('documents'), properties: ['openFile'],
    filters: [{ name: '可打开的文件', extensions: ['json', 'png', 'jpg', 'jpeg', 'pptx', 'vsdx', 'drawio', 'xml'] }, { name: '经纬织图工程', extensions: ['json'] }, { name: '框图图片', extensions: ['png', 'jpg', 'jpeg'] }, { name: 'PowerPoint', extensions: ['pptx'] }, { name: 'Visio', extensions: ['vsdx'] }, { name: 'draw.io', extensions: ['drawio', 'xml'] }] });
  if (r.canceled || !r.filePaths[0]) return null;
  store.lastDir = path.dirname(r.filePaths[0]); saveStore(); return r.filePaths[0];
});
function projectDirs() {
  const dirs = [];
  const add = d => { if (d && dirs.indexOf(d) < 0) dirs.push(d); };
  add(store.lastDir);
  for (const k of ['documents', 'desktop', 'downloads', 'home']) { try { add(app.getPath(k)); } catch (_) { } }
  return dirs;
}
ipcMain.handle('jw:recent', () => recentLib.scanProjects(fs, store.recent, projectDirs()));
ipcMain.handle('jw:recent-remove', (_e, p) => { store.recent = store.recent.filter(x => x !== p); saveStore(); return true; });
ipcMain.handle('jw:rename', (_e, p, name) => {
  const r = recentLib.renameProject(fs, p, name);
  if (r && r.path) {
    const was = path.resolve(p);
    store.recent = store.recent.map(x => { try { return path.resolve(x) === was ? r.path : x; } catch (_) { return x; } });
    if (!store.recent.some(x => { try { return path.resolve(x) === r.path; } catch (_) { return false; } })) store.recent.unshift(r.path);
    store.recent = store.recent.slice(0, 12);
    saveStore();
  }
  return r;
});
ipcMain.handle('jw:pending', () => { const a = pendingOpen; pendingOpen = []; return a; });
ipcMain.handle('jw:info', () => ({ version: app.getVersion(), platform: process.platform, arch: process.arch, electron: process.versions.electron, chrome: process.versions.chrome }));
ipcMain.handle('jw:confirm-close', async (_e, name) => {
  if (T) return process.env.JW_TEST_CLOSE || 'discard';
  const r = await dialog.showMessageBox(win, { type: 'question', title: '经纬织图', message: `“${name}”有未保存的修改，是否保存？`, buttons: ['保存', '不保存', '取消'], defaultId: 0, cancelId: 2, noLink: true });
  return ['save', 'discard', 'cancel'][r.response];
});
ipcMain.on('jw:close-now', () => { forceClose = true; win && win.close(); });
ipcMain.on('jw:win', (_e, op) => {
  if (!win) return;
  if (op === 'min') win.minimize();
  else if (op === 'max') win.isMaximized() ? win.unmaximize() : win.maximize();
  else if (op === 'close') win.close();
  else if (op === 'full') win.setFullScreen(!win.isFullScreen());
});
ipcMain.on('jw:title', (_e, t) => win && win.setTitle(t));
ipcMain.on('jw:reveal', (_e, p) => p && shell.showItemInFolder(p));

function backupNop() { return { suppressed: true, projects: [] }; }
function canonDoc(d) {
  const copy = JSON.parse(JSON.stringify(d));
  const pages = (copy && copy.pages) || {};
  for (const id of Object.keys(pages)) delete pages[id].cam;
  return copy;
}
function backupDirOf(projectPath) {
  if (projectPath == null) return path.join(app.getPath('userData'), 'backups', 'untitled');
  return projectPath + '.bak';
}
function assertSlot(slot) {
  if (typeof slot !== 'number' || !isFinite(slot) || slot < 1 || slot > 5 || Math.floor(slot) !== slot) throw new Error('slot');
}
function slotFile(projectPath, slot) {
  assertSlot(slot);
  const dir = path.resolve(backupDirOf(projectPath));
  const name = 'bak-' + slot + '.json';
  const file = path.join(dir, name);
  if (path.basename(file) !== name || path.resolve(file) !== path.join(dir, name)) throw new Error('target');
  return { dir, file, name };
}
function resolveProject(projectPath) {
  if (projectPath == null) return null;
  if (typeof projectPath !== 'string' || !projectPath) throw new Error('path');
  const resolved = path.resolve(projectPath);
  let st;
  try { st = fs.statSync(resolved); }
  catch (e) { if (e.code === 'ENOENT') return resolved; throw e; }
  if (st.isDirectory()) throw new Error('path');
  return resolved;
}
function readSlotFile(file, n) {
  let raw;
  try { raw = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { return null; }
  if (!raw || !raw.doc || !raw.doc.pages || !raw.doc.pages.root) return null;
  const at = raw.backup && raw.backup.backedAt;
  const slot = raw.backup && raw.backup.slot;
  if (typeof at !== 'number' || !isFinite(at) || at <= 0) return null;
  if (slot !== n || n < 1 || n > 5) return null;
  return { slot: n, backedAt: at, doc: raw.doc };
}
function slotsIn(dir) {
  const out = [];
  for (let n = 1; n <= 5; n++) {
    const file = path.join(dir, 'bak-' + n + '.json');
    let st;
    try { st = fs.statSync(file); } catch (e) { continue; }
    if (!st.isFile()) continue;
    const slot = readSlotFile(file, n);
    if (slot) out.push(slot);
  }
  return out;
}
function saveInfo(projectPath) {
  if (!projectPath) return { saveTime: 0, saveText: null };
  let st;
  try { st = fs.statSync(projectPath); } catch (e) { return { saveTime: 0, saveText: null }; }
  if (!st.isFile()) return { saveTime: 0, saveText: null };
  let text = null;
  try {
    const o = JSON.parse(fs.readFileSync(projectPath, 'utf8'));
    const d = o && o.doc && o.doc.pages ? o.doc : o;
    if (d && d.pages && d.pages.root) text = JSON.stringify(canonDoc(d));
  } catch (e) { text = null; }
  return { saveTime: st.mtimeMs || 0, saveText: text };
}
function backupProject(projectPath) {
  const info = saveInfo(projectPath);
  return { projectPath: projectPath, saveTime: info.saveTime, saveText: info.saveText, slots: slotsIn(backupDirOf(projectPath)) };
}
function replaceFile(tmp, dest) {
  try { fs.renameSync(tmp, dest); }
  catch (e) {
    try { fs.unlinkSync(dest); fs.renameSync(tmp, dest); }
    catch (e2) { try { fs.unlinkSync(tmp); } catch (_) { } throw e2; }
  }
}
ipcMain.handle('jw:backup-list', async (_e, arg) => {
  if (T) return backupNop();
  const scope = arg && arg.scope;
  if (scope === 'all') {
    const projects = [];
    for (const p of store.recent) if (/\.json$/i.test(p)) projects.push(backupProject(p));
    projects.push(backupProject(null));
    return { suppressed: false, projects };
  }
  if (scope === 'untitled') return { suppressed: false, projects: [backupProject(null)] };
  const projectPath = resolveProject(arg && arg.projectPath);
  return { suppressed: false, projects: [backupProject(projectPath)] };
});
ipcMain.handle('jw:backup-write', async (_e, arg) => {
  if (T) return null;
  const projectPath = resolveProject(arg && arg.projectPath);
  const slot = arg && arg.slot;
  const doc = arg && arg.doc;
  const backedAt = arg && arg.backedAt;
  assertSlot(slot);
  if (!doc || typeof doc !== 'object' || !doc.pages || !doc.pages.root) throw new Error('doc');
  if (typeof backedAt !== 'number' || !isFinite(backedAt) || backedAt <= 0) throw new Error('time');
  const loc = slotFile(projectPath, slot);
  fs.mkdirSync(loc.dir, { recursive: true });
  const tmp = path.join(loc.dir, loc.name + '.tmp');
  const body = JSON.stringify({ format: 'hongtu', version: 1, backup: { backedAt: backedAt, slot: slot }, doc: doc });
  fs.writeFileSync(tmp, body);
  replaceFile(tmp, loc.file);
  return true;
});
ipcMain.handle('jw:backup-drop', async (_e, arg) => {
  if (T) return null;
  const projectPath = resolveProject(arg && arg.projectPath);
  const loc = slotFile(projectPath, arg && arg.slot);
  try { fs.unlinkSync(loc.file); } catch (e) { if (e.code !== 'ENOENT') throw e; }
  return true;
});

/* ---------------- lifecycle ---------------- */
pendingOpen = fileArgs(process.argv);
app.on('open-file', (e, p) => { e.preventDefault(); if (win) win.webContents.send('jw:open-path', p); else pendingOpen.push(p); });
app.whenReady().then(() => {
  nativeTheme.themeSource = 'light';   // 不跟随系统深色模式：图面与面板统一浅色，保证对比度
  Menu.setApplicationMenu(null);
  try { const ses = require('electron').session.defaultSession; ses.setSpellCheckerEnabled(false); ses.setSpellCheckerDictionaryDownloadURL('http://127.0.0.1:9/'); } catch (_) { }
  createSplash();
  createMain();
});
app.on('window-all-closed', () => app.quit());
