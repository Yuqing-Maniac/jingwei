// 机构标识（Node 侧）：读 jingwei/brand.example.json，本地有 brand.local.json（不入库）时覆盖。与 build/brand.py 一致。
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const b = JSON.parse(fs.readFileSync(path.join(ROOT, 'brand.example.json'), 'utf8'));
const p = path.join(ROOT, 'brand.local.json');
if (fs.existsSync(p)) Object.assign(b, JSON.parse(fs.readFileSync(p, 'utf8')));
else if (!process.env.JW_BRAND_QUIET) console.error('提示：未找到 brand.local.json，使用通用机构标识：' + b.org);
module.exports = b;
