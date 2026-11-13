'use strict';
const assert = require('assert');
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const acorn = require('acorn');

const root = path.join(__dirname, '..');
const stage = path.join(process.env.JW_WORK || path.join(root, '_work'), 'stage', 'app');
const staged = spawnSync('python3', [path.join(root, 'build', 'desktop', 'stage.py')], {
  encoding: 'utf8',
  env: process.env,
});
assert.strictEqual(staged.status, 0, staged.stderr || staged.stdout);
const html = fs.readFileSync(path.join(stage, 'app', 'index.html'), 'utf8');
let scripts = 0;
for (const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) {
  acorn.parse(match[1], { ecmaVersion: 'latest' });
  scripts++;
}
assert(scripts > 0, 'staged HTML contains no scripts');

const pkg = JSON.parse(fs.readFileSync(path.join(stage, 'package.json'), 'utf8'));
const mainRel = pkg.main || 'index.js';
const mainPath = path.join(stage, mainRel);
assert.ok(fs.existsSync(mainPath) && fs.statSync(mainPath).isFile() && fs.statSync(mainPath).size > 0,
  'staged package main ' + mainRel + ' is missing');

const reqRe = /require\(\s*['"](\.[^'"]+)['"]\s*\)/g;
function relativeRequires(file) {
  const text = fs.readFileSync(file, 'utf8');
  const specs = [];
  let match;
  while ((match = reqRe.exec(text))) specs.push(match[1]);
  return specs;
}
function resolveRelative(fromFile, spec) {
  const base = path.resolve(path.dirname(fromFile), spec);
  const candidates = [base, base + '.js', base + '.json', path.join(base, 'index.js')];
  return candidates.find(candidate => {
    try { return fs.statSync(candidate).isFile(); } catch (_) { return false; }
  }) || null;
}

const queue = [mainPath];
const seen = new Set();
while (queue.length) {
  const file = queue.pop();
  if (seen.has(file)) continue;
  seen.add(file);
  for (const spec of relativeRequires(file)) {
    const hit = resolveRelative(file, spec);
    assert.ok(hit, path.basename(file) + ' requires ' + spec + ', and the staged app does not contain it');
    if (hit.endsWith('.js')) queue.push(hit);
  }
}
console.log('staged', mainRel, 'resolves', seen.size, 'scripts');
