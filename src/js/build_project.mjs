import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
const req=createRequire(import.meta.url),C=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
await req('esbuild').build({entryPoints:[path.join(C.projectDir,C.uiEntry||'main.jsx')],bundle:true,jsx:'automatic',outfile:path.join(C.projectDir,'bundle.js'),nodePaths:[path.resolve('node_modules'),...(C.nodeModules||[])],loader:{'.otf':'file','.ttf':'file'},assetNames:'fonts/[name]-[hash]',define:{'process.env.NODE_ENV':'"production"'},minify:true});
console.log('Built deterministic Anime.js + Three.js composition');
