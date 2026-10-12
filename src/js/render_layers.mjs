import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
const opt=Object.fromEntries(process.argv.slice(2).map(a=>{const i=a.indexOf('=');return [a.slice(2,i),a.slice(i+1)]}));
const C=JSON.parse(fs.readFileSync(process.env.LVE_RESOLVED_CONFIG,'utf8'));const work=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1')),root=path.resolve(opt.dir),src=path.resolve(C.projectDir);
const start=Number(opt.start),N=Number(opt.frames),fps=24,cancel=opt.cancel;
if(!Number.isFinite(start)||!Number.isInteger(N)||N<1||N>7200||!root.startsWith(path.resolve(C.outputDir)+path.sep))throw Error('Invalid segment');
const req=createRequire(import.meta.url),pp=req('puppeteer-core'),puppeteer=pp.default||pp;
const story=JSON.parse(fs.readFileSync(path.join(src,'story.json'),'utf8'));
fs.mkdirSync(path.join(root,'ui'),{recursive:true});
const progress=(phase,done,total)=>fs.writeFileSync(path.join(root,'layer-progress.json'),JSON.stringify({phase,done,total}));
function check(){if(fs.existsSync(cancel))throw Error('Paused');const disk=fs.statfsSync(root);if(disk.bavail*disk.bsize<1024**3)throw Error('磁盘剩余空间不足 1GB 已生成素材保留');}
if(C.uiEntry)await req('esbuild').build({entryPoints:[path.join(src,C.uiEntry)],bundle:true,jsx:'automatic',outfile:path.join(root,'ui-bundle.js'),nodePaths:[path.resolve('node_modules'),...(C.nodeModules||[])],loader:{'.otf':'file','.ttf':'file'},assetNames:'ui-bundle-fonts/[name]-[hash]',define:{'process.env.NODE_ENV':'"production"'},minify:true,plugins:[{name:'no-ui-webgl',setup(b){b.onLoad({filter:/\.jsx$/},a=>(C.gpuModules||['Scene3D.jsx','Objects3D.jsx','LightPillar.jsx']).includes(path.basename(a.path))?({contents:`import React from 'react';export default function Empty(){return <div className=${JSON.stringify(a.path.includes('Objects3D')?'object3d':'scene3d')}/>}`,loader:'jsx'}):null)}}]});
let gpuHandle;
const server=http.createServer(async(r,res)=>{
 try{
  if(r.url==='/cancel'){res.end(fs.existsSync(cancel)?'1':'0');return;}
  if(r.url==='/gpu-chunk'&&r.method==='POST'){
   check();for await(const block of r)await gpuHandle.write(block);res.end('ok');return;
  }
  let name=decodeURIComponent(r.url.split('?')[0]);
  if(name==='/ui-film.html'){res.setHeader('Content-Type','text/html');res.end(C.uiEntry?fs.readFileSync(path.join(src,C.filmFile),'utf8').replaceAll('bundle.css','ui-bundle.css').replaceAll('bundle.js','ui-bundle.js'):fs.readFileSync(path.join(src,C.uiFile),'utf8'));return;}
  if(name==='/film.html')name='/'+C.filmFile;const file=name.startsWith('/ui-bundle')?path.resolve(root,'.'+name):path.resolve(src,'.'+name);
  if(!file.startsWith(src+path.sep)&&!file.startsWith(root+path.sep))return res.writeHead(403).end();
  if(!fs.existsSync(file))return res.writeHead(404).end();
  res.setHeader('Content-Type',({'.js':'text/javascript','.css':'text/css','.html':'text/html','.otf':'font/otf','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);
 }catch(e){res.writeHead(500).end(e.message);}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port;
let browser;
async function page(ui){const p=await browser.newPage();await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});const c=await p.createCDPSession();await c.send('Network.enable');await c.send('Network.setBlockedURLs',{urls:['*source.mp4*']});await p.goto(url+(ui?'/ui-film.html':'/film.html'),{waitUntil:'networkidle0',timeout:60000});await p.waitForFunction(()=>window.__film?.seek);await p.evaluate(()=>document.fonts.ready);return p;}
try{
 browser=await puppeteer.launch({executablePath:C.chrome,headless:true,args:['--no-sandbox','--use-angle=d3d11','--force-high-performance-gpu','--enable-gpu-rasterization','--disable-background-timer-throttling']});
 if(!fs.existsSync(path.join(root,'gpu.ready'))){
  check();const p=await page(false);await p.exposeFunction('reportGPU',n=>progress('gpu',n,N));
  gpuHandle=await fs.promises.open(path.join(root,'gpu.partial.h264'),'w');
  const result=await p.evaluate(async({start,N,fps})=>{
   const canvas=document.createElement('canvas');canvas.width=1920;canvas.height=1080;const ctx=canvas.getContext('2d',{alpha:false});
   const lc=document.createElement('canvas');lc.width=1330;lc.height=1330;const lx=lc.getContext('2d');
   const mask=lx.createLinearGradient(0,0,1330,0);for(const [at,a]of[[0,0],[.20,1],[.82,1],[1,0]])mask.addColorStop(at,`rgba(0,0,0,${a})`);
   let pending=[],bytes=0,error;const positions=[];
   const enc=new VideoEncoder({output:c=>{const b=new Uint8Array(c.byteLength);c.copyTo(b);pending.push(b);bytes+=b.length;},error:e=>error=String(e)});
   const conf={codec:'avc1.640028',width:1920,height:1080,framerate:24,bitrate:20000000,hardwareAcceleration:'prefer-hardware',avc:{format:'annexb'}};
   if(!(await VideoEncoder.isConfigSupported(conf)).supported)throw Error('AVC 编码不可用');enc.configure(conf);
   async function drain(){if(!pending.length)return;const data=new Blob(pending);pending=[];const r=await fetch('/gpu-chunk',{method:'POST',body:data});if(!r.ok)throw Error(await r.text());}
   const palettes={blue:['#161c23','#0b0d10','#08090b','8,9,11'],cyan:['#102c34','#07151e','#061016','6,16,22'],violet:['#2e2446','#141022','#0e0b18','14,11,24'],amber:['#382c22','#181412','#100d0b','16,13,11'],ice:['#dce7f5','#eaf0f7','#f3f6fa','243,246,250']};
   let previousScene;
   try{for(let i=0;i<N;i++){
    const t=start+i/fps;window.__film.seek(t,true);const s=window.__film.getScene();
    if(s.id!==previousScene){await Promise.all([...document.images].map(im=>im.decode().catch(()=>{})));window.__film.seek(t,true);previousScene=s.id;}
    const theme=window.__story.chapters[s.chapter].theme,colors=palettes[theme]||palettes.blue;
    // CSS radial-gradient(ellipse farthest-corner at 52% 48%): account for aspect ratio.
    ctx.save();ctx.translate(998.4,518.4);ctx.scale(1,1080/1920);const radius=Math.hypot(998.4,561.6*1920/1080);
    const bg=ctx.createRadialGradient(0,0,0,0,0,radius);bg.addColorStop(0,colors[0]);bg.addColorStop(.45,colors[1]);bg.addColorStop(.85,colors[2]);ctx.fillStyle=bg;ctx.fillRect(-998.4,-518.4*1920/1080,1920,1920);ctx.restore();
    const light=document.querySelector('.light canvas'),ls=getComputedStyle(document.querySelector('.light'));
    lx.clearRect(0,0,1330,1330);lx.globalCompositeOperation='source-over';lx.drawImage(light,0,0,1330,1330);lx.globalCompositeOperation='destination-in';lx.fillStyle=mask;lx.fillRect(0,0,1330,1330);lx.globalCompositeOperation='source-over';
    ctx.globalAlpha=Number(ls.opacity);ctx.globalCompositeOperation=ls.mixBlendMode==='multiply'?'multiply':'source-over';ctx.drawImage(lc,340,-200);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';
    const veil=ctx.createLinearGradient(0,0,1920,0);for(const [at,a]of[[0,1],[.24,128/255],[.52,0],[.77,112/255],[1,1]])veil.addColorStop(at,`rgba(${colors[3]},${a})`);ctx.fillStyle=veil;ctx.fillRect(0,0,1920,1080);
    for(const c of document.querySelectorAll('.scene-visual canvas')){
     const r=c.getBoundingClientRect();let opacity=1;ctx.save();
     for(let e=c;e&&e!==document.body;e=e.parentElement){const st=getComputedStyle(e);opacity*=Number(st.opacity);const clip=st.clipPath.match(/^inset\(([^)]+)\)/);if(clip){const z=e.getBoundingClientRect(),a=clip[1].split(' ').map(v=>parseFloat(v));const four=a.length===1?[a[0],a[0],a[0],a[0]]:a.length===2?[a[0],a[1],a[0],a[1]]:a;ctx.beginPath();ctx.rect(z.x+z.width*four[3]/100,z.y+z.height*four[0]/100,z.width*(1-(four[1]+four[3])/100),z.height*(1-(four[0]+four[2])/100));ctx.clip();}}
     ctx.globalAlpha=opacity;ctx.drawImage(c,r.x,r.y,r.width,r.height);ctx.restore();
    }
    if(t<7.63){const r=document.querySelector('.portrait').getBoundingClientRect();positions.push({frame:i,x:r.x,y:r.y,w:r.width,h:r.height,radius:parseFloat(getComputedStyle(document.querySelector('.portrait')).borderRadius)});}
    const f=new VideoFrame(canvas,{timestamp:Math.round(i*1e6/fps),duration:Math.round(1e6/fps)});enc.encode(f,{keyFrame:i%48===0});f.close();
    if(enc.encodeQueueSize>5)await new Promise(r=>enc.addEventListener('dequeue',r,{once:true}));
    if(i%48===0){if(await(await fetch('/cancel')).text()==='1')throw Error('Paused');await drain();await window.reportGPU(i+1);}
    if(error)throw Error(error);
   }await enc.flush();await drain();return {bytes,positions};}finally{enc.close();}
  },{start,N,fps});
  await gpuHandle.sync();await gpuHandle.close();gpuHandle=null;fs.renameSync(path.join(root,'gpu.partial.h264'),path.join(root,'gpu.h264'));fs.writeFileSync(path.join(root,'presenter-positions.json'),JSON.stringify(result.positions));fs.writeFileSync(path.join(root,'gpu.ready'),String(result.bytes));await p.close();
 }
 // Include every actual motion interval, preserving subsequent UI zooms and moving playheads.
 const active=new Set([0]);function range(a,b){for(let i=Math.max(0,Math.floor((a-start)*fps));i<Math.min(N,Math.ceil((b-start)*fps));i++)active.add(i);}
 range(6.2,8.9);
 for(const s of story.scenes){if(s.start>=start+N/fps)break;if(s.end<=start)continue;
  range(s.start,s.start+2);range(s.titleAt??s.start,(s.titleAt??s.start)+1.1);range(s.visualAt??s.start,(s.visualAt??s.start)+1.5);
  const rows=s.items||s.rows||s.labels||s.bars||s.scores||[];for(let j=0;j<Math.max(rows.length,s.reveal?.length||0);j++){const at=s.reveal?.[j]??s.start+.2+j*1.6;range(at,at+(s.kind==='bars'||s.kind==='score'?1.25:.7));}
  if(['control-desk','chapter','timeline','workflow','loop','prompt'].includes(s.kind))range(s.start,s.end);
  if(s.kind==='ui')range(s.start,Math.min(s.end,s.start+17));
  if(s.kind==='optimize')range(s.start,s.start+3.1);
  if(['filmcut','edit-bay'].includes(s.kind))range(s.start,s.start+10.1);
 }
 const indices=[...active].sort((a,b)=>a-b);fs.writeFileSync(path.join(root,'ui-index.json'),JSON.stringify(indices));
 if(!fs.existsSync(path.join(root,'ui.ready'))){const p=await page(true);await p.addStyleTag({content:`html,body,.stage{background:transparent!important}.light,.veil,.scene-visual canvas,#speaker,.caption,.wave{visibility:hidden!important}.portrait{background:transparent!important;box-shadow:none!important}.portraitshade{visibility:hidden!important}`});await p.evaluate(()=>window.__filmDraws?.clear());
  let prior;for(let j=0;j<indices.length;j++){check();const i=indices[j],file=path.join(root,'ui',String(i).padStart(5,'0')+'.png');
   if(!fs.existsSync(file)){await p.evaluate(t=>window.__film.seek(t,true),start+i/fps);const si=await p.evaluate(()=>window.__film.getScene().id);if(si!==prior){await p.evaluate(()=>Promise.all([...document.images].map(im=>im.decode().catch(()=>{}))));prior=si;}
    await p.screenshot({path:file+'.tmp',type:'png',omitBackground:true,optimizeForSpeed:true,captureBeyondViewport:false});fs.renameSync(file+'.tmp',file);
   }if(j%24===0)progress('ui',j+1,indices.length);
  }fs.writeFileSync(path.join(root,'ui.ready'),'ok');await p.close();
 }
 progress('ready',N,N);
}finally{await gpuHandle?.close();await browser?.close();await new Promise(r=>server.close(r));}
