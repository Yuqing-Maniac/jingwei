// 用法：node winexe.mjs in.exe out.exe icon.ico version
import * as ResEdit from 'resedit';
import * as PELibrary from 'pe-library';
import fs from 'fs';
import BRAND from '../brand.js';   // 机构标识：brand.local.json（不入库）> brand.example.json
const [,, inp, out, ico, ver] = process.argv;
const exe = PELibrary.NtExecutable.from(fs.readFileSync(inp), { ignoreCert: true });
const res = PELibrary.NtExecutableResource.from(exe);
const iconFile = ResEdit.Data.IconFile.from(fs.readFileSync(ico));
const groups = ResEdit.Resource.IconGroupEntry.fromEntries(res.entries);
const gid = groups.length ? groups[0].id : 1, lang = groups.length ? groups[0].lang : 1033;
ResEdit.Resource.IconGroupEntry.replaceIconsForResource(res.entries, gid, lang, iconFile.icons.map(i => i.data));
const vi = ResEdit.Resource.VersionInfo.fromEntries(res.entries)[0] || ResEdit.Resource.VersionInfo.createEmpty();
const [a, b, c] = ver.split('.').map(Number);
vi.setFileVersion(a, b, c, 0, 1033); vi.setProductVersion(a, b, c, 0, 1033);
for (const l of vi.getAllLanguagesForStringValues()) vi.removeAllStringValues(l);
const S = { CompanyName: BRAND.org, FileDescription: '经纬织图', ProductName: '经纬织图', InternalName: 'JingWeiZhiTu', OriginalFilename: 'JingWeiZhiTu.exe', LegalCopyright: BRAND.copyright, FileVersion: ver, ProductVersion: ver };
vi.setStringValues({ lang: 2052, codepage: 1200 }, S);
vi.outputToResourceEntries(res.entries);
res.outputResource(exe);
fs.writeFileSync(out, Buffer.from(exe.generate()));
console.log('ok', out);
