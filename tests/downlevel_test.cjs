const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'jw-downlevel-'));
const script = path.resolve(__dirname, '../build/downlevel.js');
try {
  for (const newline of ['\n', '\r\n']) {
    const file = path.join(dir, 'page.html');
    fs.writeFileSync(file, '<script>' + newline + 'var value = source?.value ?? 1;' + newline + '</script><script>var inline = source?.value;</script>');
    const result = spawnSync(process.execPath, [script, file], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert(result.stdout.includes('scripts 2 es2019-fail 0'));
    assert(!fs.readFileSync(file, 'utf8').includes('?.'));
  }
  const empty = path.join(dir, 'empty.html'); fs.writeFileSync(empty, '<html></html>');
  assert.notEqual(spawnSync(process.execPath, [script, empty]).status, 0, 'empty matches must fail');
  console.log('PASS CRLF/LF/inline scripts and empty-build rejection');
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
