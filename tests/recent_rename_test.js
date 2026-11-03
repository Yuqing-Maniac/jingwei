'use strict';
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { scanProjects, renameProject } = require('../desktop/recent');

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'jw-recent-'));
const docs = path.join(root, 'docs');
const desk = path.join(root, 'desk');
fs.mkdirSync(docs);
fs.mkdirSync(desk);
const kept = path.join(docs, 'patrol.jingwei.json');
const other = path.join(desk, 'notes.txt');
const gone = path.join(docs, 'missing.jingwei.json');
fs.writeFileSync(kept, '{"format":"hongtu"}\n');
fs.writeFileSync(other, 'x');
const old = new Date('2020-01-02T03:04:00Z');
fs.utimesSync(kept, old, old);

let list = scanProjects(fs, [gone, kept], [docs, desk]);
assert.strictEqual(list.length, 1, 'missing recent file is dropped and non-project files stay out');
assert.strictEqual(list[0].path, path.resolve(kept));
assert.strictEqual(list[0].name, 'patrol.jingwei.json');
assert.ok(list[0].t > 0, 'mtime is present');

const renamed = renameProject(fs, kept, '边防巡逻');
assert.strictEqual(renamed.error, undefined);
assert.strictEqual(renamed.name, '边防巡逻.jingwei.json');
assert.ok(fs.existsSync(renamed.path), 'renamed file is on disk');
assert.ok(!fs.existsSync(kept), 'old name is gone');

list = scanProjects(fs, [kept, renamed.path], [docs]);
assert.deepStrictEqual(list.map(x => x.name), ['边防巡逻.jingwei.json']);

const clash = renameProject(fs, renamed.path, '边防巡逻');
assert.strictEqual(clash.path, renamed.path, 'same name is a no-op');

fs.writeFileSync(path.join(docs, 'taken.jingwei.json'), '{}');
const blocked = renameProject(fs, renamed.path, 'taken');
assert.strictEqual(blocked.error, '已有同名文件');
assert.ok(fs.existsSync(renamed.path));

const empty = scanProjects(fs, [gone], [path.join(root, 'empty-nope')]);
assert.deepStrictEqual(empty, []);

console.log('recent rename ok', renamed.path);
fs.rmSync(root, { recursive: true, force: true });
