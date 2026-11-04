'use strict';
/* 增量包：zip 根目录 jingwei-patch.json，files 列出相对应用目录的覆盖路径。 */
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

function readZip(buf) {
  let eocd = -1;
  const min = Math.max(0, buf.length - 22 - 65535);
  for (let i = buf.length - 22; i >= min; i--) {
    if (buf.readUInt32LE(i) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error('不是 zip');
  const count = buf.readUInt16LE(eocd + 10);
  let off = buf.readUInt32LE(eocd + 16);
  const files = {};
  for (let n = 0; n < count; n++) {
    if (buf.readUInt32LE(off) !== 0x02014b50) throw new Error('zip 目录损坏');
    const method = buf.readUInt16LE(off + 10);
    const compSize = buf.readUInt32LE(off + 20);
    const nameLen = buf.readUInt16LE(off + 28);
    const extraLen = buf.readUInt16LE(off + 30);
    const commentLen = buf.readUInt16LE(off + 32);
    const localOff = buf.readUInt32LE(off + 42);
    const name = buf.slice(off + 46, off + 46 + nameLen).toString('utf8').replace(/\\/g, '/');
    off += 46 + nameLen + extraLen + commentLen;
    if (name.endsWith('/')) continue;
    if (buf.readUInt32LE(localOff) !== 0x04034b50) throw new Error('zip 本地头损坏');
    const ln = buf.readUInt16LE(localOff + 26);
    const le = buf.readUInt16LE(localOff + 28);
    const data = buf.slice(localOff + 30 + ln + le, localOff + 30 + ln + le + compSize);
    if (method === 0) files[name] = Buffer.from(data);
    else if (method === 8) files[name] = zlib.inflateRawSync(data);
    else throw new Error('不支持的压缩方式');
  }
  return files;
}

function safeRel(p) {
  const n = String(p || '').replace(/\\/g, '/');
  if (!n || n.startsWith('/') || /^[A-Za-z]:/.test(n) || n.split('/').includes('..')) throw new Error('路径不允许');
  return n;
}

function applyPatch(zipPath, root) {
  const files = readZip(fs.readFileSync(zipPath));
  if (!files['jingwei-patch.json']) throw new Error('缺少 jingwei-patch.json');
  const meta = JSON.parse(files['jingwei-patch.json'].toString('utf8'));
  if (meta.format !== 'jingwei-patch' || !Array.isArray(meta.files) || !meta.files.length) throw new Error('增量包标记不正确');
  const base = path.resolve(root);
  const written = [];
  for (const rel0 of meta.files) {
    const rel = safeRel(rel0);
    if (!Object.prototype.hasOwnProperty.call(files, rel)) throw new Error('增量包缺少文件');
    const dest = path.resolve(base, ...rel.split('/'));
    if (dest !== base && dest.indexOf(base + path.sep) !== 0) throw new Error('路径越界');
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, files[rel]);
    written.push(rel);
  }
  return { from: meta.from || '', to: meta.to || '', files: written, restart: true };
}

module.exports = { applyPatch, readZip };
