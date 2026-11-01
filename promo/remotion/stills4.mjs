import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'fs';
// usage: node stills4.mjs OUTDIR 'Comp:f1,f2:{props}' ...
const [,, out, ...jobs] = process.argv;
const B = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const serveUrl = await bundle({entryPoint: './src/index.ts', publicDir: './public'});
fs.mkdirSync(out, {recursive: true});
for (const j of jobs) {
  const [id, frames, ...rest] = j.split(':');
  const ps = rest.join(':');
  const inputProps = ps ? JSON.parse(ps) : {};
  const comp = await selectComposition({serveUrl, id, inputProps, browserExecutable: B});
  const tag = inputProps.num ? '_' + inputProps.num : '';
  for (const fr of frames.split(',').map(Number)) {
    await renderStill({composition: comp, serveUrl, frame: fr, inputProps, imageFormat: 'jpeg', jpegQuality: 80, scale: 0.5, output: `${out}/${id}${tag}_${String(fr).padStart(3, '0')}.jpg`, browserExecutable: B});
  }
}
console.log('done');
