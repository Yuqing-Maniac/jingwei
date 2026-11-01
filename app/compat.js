/* 兼容层（ES5）：旧版 Chromium／火狐（国产系统常见）补齐运行时接口，并在浏览器过旧时给出提示 */
(function () {
  var BP = window.Blob && Blob.prototype;
  function rd(b, how) { return new Promise(function (ok, no) { var r = new FileReader(); r.onload = function () { ok(r.result); }; r.onerror = function () { no(r.error); }; r[how](b); }); }
  if (BP && !BP.arrayBuffer) BP.arrayBuffer = function () { return rd(this, 'readAsArrayBuffer'); };
  if (BP && !BP.text) BP.text = function () { return rd(this, 'readAsText'); };
  if (!Object.fromEntries) Object.fromEntries = function (it) { var o = {}; Array.from(it).forEach(function (kv) { o[kv[0]] = kv[1]; }); return o; };
  if (!String.prototype.trimStart) String.prototype.trimStart = String.prototype.trimLeft;
  if (!String.prototype.trimEnd) String.prototype.trimEnd = String.prototype.trimRight;
  if (!Array.prototype.flat) Array.prototype.flat = function (d) { d = d === undefined ? 1 : d; return d < 1 ? this.slice() : this.reduce(function (a, v) { return a.concat(Array.isArray(v) ? v.flat(d - 1) : v); }, []); };
  if (!Array.prototype.flatMap) Array.prototype.flatMap = function (f, t) { return this.map(f, t).flat(); };
  if (!String.prototype.padStart) String.prototype.padStart = function (n, c) { var s = String(this); c = c === undefined ? ' ' : String(c); while (s.length < n) s = c + s; return s.slice(-Math.max(n, String(this).length)); };
  var ok = true; try { new Function('async function f(){await 0}; var {a, ...b} = {a:1}; return [...[1]]'); } catch (e) { ok = false; }
  function warn() {
    if (document.getElementById('compat-warn')) return;
    var d = document.createElement('div'); d.id = 'compat-warn';
    d.style.cssText = 'position:fixed;left:0;right:0;top:0;z-index:2147483647;background:#B3261E;color:#fff;font:16px/1.7 sans-serif;padding:14px 20px;text-align:center';
    d.innerHTML = '当前浏览器版本过低，经纬织图无法正常运行。请改用 Chromium 内核 69 以上（奇安信可信浏览器、360 安全浏览器信创版、Chromium 等）或 Firefox 68 以上版本打开本文件。';
    (document.body || document.documentElement).appendChild(d);
  }
  if (!ok) { if (document.body) warn(); else document.addEventListener('DOMContentLoaded', warn); }
  window.addEventListener('error', function (e) { if (e && e.error && e.error.name === 'SyntaxError') warn(); });
})();
