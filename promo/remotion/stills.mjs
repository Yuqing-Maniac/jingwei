import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'fs';
const [,, id, frames, props, out] = process.argv;
const serveUrl = await bundle({entryPoint: './src/index.ts', publicDir: './public'});
fs.mkdirSync(out, {recursive: true});
const inputProps = JSON.parse(props || '{}');
const comp = await selectComposition({serveUrl, id, inputProps, browserExecutable: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
for (const fr of frames.split(',').map(Number)) {
  await renderStill({composition: comp, serveUrl, frame: fr, inputProps, output: `${out}/${id}_${String(fr).padStart(3,'0')}.png`, browserExecutable: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
}
console.log('done');
