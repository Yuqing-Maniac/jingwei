'use strict';
const path = require('path');

const PROJECT_RE = /\.jingwei\.json$/i;

function safeName(name) {
  return String(name || '').replace(/[\\/:*?"<>|]/g, '').replace(/\s+/g, ' ').trim();
}

function displayName(filename) {
  return String(filename || '').replace(/\.jingwei\.json$/i, '');
}

function addFile(fs, found, p) {
  let st;
  try { st = fs.statSync(p); } catch (_) { return; }
  if (!st.isFile()) return;
  const abs = path.resolve(p);
  found.set(abs, { path: abs, name: path.basename(abs), dir: path.dirname(abs), t: st.mtimeMs });
}

function scanProjects(fs, recent, dirs) {
  const found = new Map();
  for (const p of recent || []) addFile(fs, found, p);
  for (const dir of dirs || []) {
    let names;
    try { names = fs.readdirSync(dir); } catch (_) { continue; }
    for (const n of names) if (PROJECT_RE.test(n)) addFile(fs, found, path.join(dir, n));
  }
  return [...found.values()].sort((a, b) => b.t - a.t).slice(0, 16);
}

function renameProject(fs, from, nextName) {
  const base = safeName(nextName);
  if (!base) return { error: '文件名不能为空' };
  let st;
  try { st = fs.statSync(from); } catch (_) { return { error: '文件不存在' }; }
  if (!st.isFile()) return { error: '文件不存在' };
  const ext = PROJECT_RE.test(from) ? '.jingwei.json' : path.extname(from);
  let stem = base;
  if (ext && stem.toLowerCase().endsWith(ext.toLowerCase())) stem = stem.slice(0, -ext.length);
  if (!stem) return { error: '文件名不能为空' };
  const dest = path.join(path.dirname(path.resolve(from)), stem + ext);
  const src = path.resolve(from);
  if (dest === src) return { path: src, name: path.basename(src), dir: path.dirname(src), t: st.mtimeMs };
  if (fs.existsSync(dest)) return { error: '已有同名文件' };
  fs.renameSync(src, dest);
  const st2 = fs.statSync(dest);
  return { path: dest, name: path.basename(dest), dir: path.dirname(dest), t: st2.mtimeMs };
}

module.exports = { scanProjects, renameProject, displayName, safeName };
