'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const zlib = require('zlib');
const assert = require('assert');
const { applyPatch } = require('../desktop/patch');

function zip(entries) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const [name, body] of entries) {
    const nb = Buffer.from(name);
    const raw = zlib.deflateRawSync(body);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(8, 8);
    local.writeUInt32LE(raw.length, 18);
    local.writeUInt32LE(body.length, 22);
    local.writeUInt16LE(nb.length, 26);
    const chunk = Buffer.concat([local, nb, raw]);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(8, 10);
    central.writeUInt32LE(raw.length, 20);
    central.writeUInt32LE(body.length, 24);
    central.writeUInt16LE(nb.length, 28);
    central.writeUInt32LE(offset, 42);
    locals.push(chunk);
    centrals.push(Buffer.concat([central, nb]));
    offset += chunk.length;
  }
  const cd = Buffer.concat(centrals);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(entries.length, 8);
  eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(cd.length, 12);
  eocd.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, cd, eocd]);
}

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'jw-patch-'));
const root = path.join(dir, 'app');
fs.mkdirSync(path.join(root, 'resources'), { recursive: true });
fs.writeFileSync(path.join(root, 'resources', 'app.asar'), 'old-asar');
const mark = JSON.stringify({ format: 'jingwei-patch', version: 1, from: '3.3.13', to: '3.3.14', files: ['resources/app.asar'] });
const zpath = path.join(dir, 'patch.zip');
fs.writeFileSync(zpath, zip([['jingwei-patch.json', Buffer.from(mark)], ['resources/app.asar', Buffer.from('new-asar')]]));
const r = applyPatch(zpath, root);
assert.strictEqual(fs.readFileSync(path.join(root, 'resources', 'app.asar'), 'utf8'), 'new-asar');
assert.strictEqual(r.to, '3.3.14');
assert.strictEqual(r.restart, true);
let threw = false;
try { applyPatch(zpath, root); } catch (_) { threw = false; }
const bad = path.join(dir, 'bad.zip');
fs.writeFileSync(bad, zip([['jingwei-patch.json', Buffer.from(JSON.stringify({ format: 'jingwei-patch', version: 1, files: ['../x'] }))], ['../x', Buffer.from('no')]]));
try { applyPatch(bad, root); } catch (e) { threw = true; }
assert.strictEqual(threw, true);
assert.strictEqual(fs.existsSync(path.join(dir, 'x')), false);
console.log('patch_apply ok', r.files.join(','));
