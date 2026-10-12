import React,{useEffect,useRef,useState,useLayoutEffect} from 'react';
import {createRoot} from 'react-dom/client';
import motion from './timeline.js';
import LightPillar from './LightPillar.jsx';
import {flushSync} from 'react-dom';
import {paintFilm,MOTION} from './motion.js';
import Visuals from './Visuals.jsx';
import story from './story.json';
import captions from './captions.json';
import './base.css';
import './footer-fixed.css';
import './full.css';
import './directed.css';
function findIndex(array,t){let l=0,r=array.length-1;while(l<=r){const m=(l+r)>>1;if(array[m].start<=t)l=m+1;else r=m-1;}return Math.max(0,r);}
function fit(text){return Math.min(100,Math.floor(605/[...text].reduce((n,c)=>n+(c.charCodeAt(0)<128?.55:1),0)));}
function App(){
 const [frame,setFrame]=useState({time:0,si:0,ci:0});const lastUpdate=useRef(-1);const contentRef=useRef(null);const transitionRef=useRef(null);
 const s=story.scenes[frame.si],chapter=story.chapters[s.chapter];const caption=captions[frame.ci];const isWide=s.wide;
 let visualIndex=frame.si;
 if(s.kind==='sphere')while(visualIndex>0&&story.scenes[visualIndex-1].kind==='sphere'&&story.scenes[visualIndex-1].chapter===s.chapter)visualIndex--;
 const visualScene=story.scenes[visualIndex];
 useEffect(()=>{
  const tl=motion.timeline({paused:true});tl.to('.presenter',{x:1496,y:292,width:342,duration:1.2,ease:'power3.inOut'},6.42).to('.portrait',{height:500,duration:1.2,ease:'power3.inOut'},6.42).to('.intro-label',{opacity:0,duration:.3},6.2).to('.portraitshade',{opacity:1,duration:.8},6.8).to('.speaker,.live,.presenter-foot',{opacity:1,duration:.7},7.3);
  tl.to('.content-layer,.inputs',{opacity:1,duration:.8,stagger:.12},7.2);
  window.__filmClock=0;window.__story=story;
  function seek(t,sync=false){window.__filmClock=t;tl.seek(t);const si=findIndex(story.scenes,t),ci=findIndex(captions,t);const update=()=>setFrame({time:t,si,ci});if(sync)flushSync(update);else update();window.__sceneTl?.seek(Math.max(0,t-story.scenes[si].start));window.__visualTl?.seek(Math.max(0,t-(window.__visualStart??0)));window.__transitionTl?.seek(Math.max(0,t-story.scenes[si].start));for(const animation of document.getAnimations()){animation.pause();animation.currentTime=t*1000;}paintFilm();}
  let fastScene=-1;
  window.__film={duration:story.duration,seek,
   async renderFast(t){
    const video=document.querySelector('#speaker');video.pause();video.muted=true;
    if(Math.abs(video.currentTime-t)>.0001){await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>{cleanup();reject(Error('视频解码超时'))},20000);function cleanup(){clearTimeout(timeout);video.removeEventListener('seeked',done);video.removeEventListener('error',fail)}function done(){cleanup();resolve()}function fail(){cleanup();reject(Error('视频解码失败'))}video.addEventListener('seeked',done);video.addEventListener('error',fail);video.currentTime=Math.min(t,video.duration-.001);});}
    seek(t,true);
    const si=findIndex(story.scenes,t);
    if(si!==fastScene){await document.fonts.ready;await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));paintFilm();fastScene=si;}
    return {scene:si,time:t};
   },
   async render(t){const video=document.querySelector('#speaker');video.pause();video.muted=true;if(Math.abs(video.currentTime-t)>.0001){await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>{cleanup();reject(Error('视频解码超时'))},20000);function cleanup(){clearTimeout(timeout);video.removeEventListener('seeked',done);video.removeEventListener('error',fail)}function done(){cleanup();resolve()}function fail(){cleanup();reject(Error('视频解码失败'))}video.addEventListener('seeked',done);video.addEventListener('error',fail);video.currentTime=Math.min(t,video.duration-.001);});}seek(t,true);await document.fonts.ready;await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));paintFilm();return {scene:findIndex(story.scenes,t),time:t};},
   getScene(){return story.scenes[findIndex(story.scenes,window.__filmClock)]}};window.demoReady=true;
  return()=>{tl.kill();delete window.__film;delete window.__sceneTl;delete window.__visualTl;delete window.__visualStart;delete window.__transitionTl;};
 },[]);
 useLayoutEffect(()=>{
  const content=contentRef.current;if(!content)return;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const tl=motion.timeline({paused:true});
  tl.set(content.querySelector('.headline'),{opacity:1,y:0,filter:'none'});
  tl.fromTo(content.querySelectorAll('.title-line>span'),{y:reduced?0:MOTION.distance,opacity:0},{y:0,opacity:1,duration:reduced?.01:MOTION.title,stagger:MOTION.lineGap,ease:'power4.out'},Math.max(0,(s.titleAt??s.start)-s.start));
  window.__sceneTl=tl;tl.seek(Math.max(0,(window.__filmClock||0)-s.start));
  const transit=motion.timeline({paused:true});if(s.kind==='chapter'&&!reduced)transit.fromTo(transitionRef.current,{x:-1920,opacity:1},{x:1920,duration:.95,ease:'power2.inOut'});else motion.set(transitionRef.current,{opacity:0});window.__transitionTl=transit;transit.seek(Math.max(0,(window.__filmClock||0)-s.start));return()=>{tl.kill();transit.kill();};
 },[s.id]);
 useLayoutEffect(()=>{
  const visual=contentRef.current?.querySelector('.scene-visual');if(!visual)return;
  const v=visualScene,reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const offset=Math.max(.14,(v.visualAt??v.start)-v.start);
  const from=v.kind==='sphere'?{scale:reduced?1:.86,y:reduced?0:18,opacity:0}:v.motion==='scale'?{scale:reduced?1:.94,opacity:0}:v.motion==='slide'?{x:reduced?0:28,opacity:0}:v.motion==='extract'?{clipPath:'inset(0 0 100% 0)',opacity:1}:v.motion==='trace'?{opacity:0}:{clipPath:'inset(0 100% 0 0)',opacity:1};
  const tl=motion.timeline({paused:true});
  tl.fromTo(visual,{x:0,y:0,scale:1,clipPath:'inset(0 0 0 0)',...from},{x:0,y:0,scale:1,opacity:1,clipPath:'inset(0 0 0 0)',duration:reduced?.01:v.kind==='sphere'?1.25:.8,ease:'power3.out'},offset);
  window.__visualStart=v.start;window.__visualTl=tl;tl.seek(Math.max(0,(window.__filmClock||0)-v.start));
  return()=>tl.kill();
 },[visualScene.id]);
 const subtitle=caption&&frame.time>=caption.start&&frame.time<caption.end?caption.text:'';
 return <main className={`stage full-stage theme-${chapter.theme} ${isWide?'wide-scene':''}`} style={{'--accent':chapter.accent}}>
 <div className="light"><LightPillar topColor={chapter.beam[0]} bottomColor={chapter.beam[1]} intensity={.85} rotationSpeed={.12} pillarRotation={38} pillarWidth={2.8} pillarHeight={.38} glowAmount={.003} noiseIntensity={.15} quality="high"/></div><div className="veil"/>
 <header><div className="brand"><span className="brandmark">{(story.brand||"V")[0]}</span>{story.brand||"视频笔记"}</div><div className="chapter"><span/>{story.topic||"VIDEO NOTES"}<b>/</b>{chapter.short}</div><div className="lesson"><span>{chapter.short}</span></div></header>
 <div className="content-layer" ref={contentRef}>
 <section className="headline"><div className="eyebrow"><i/>{chapter.short} · AI VIDEO NOTES</div><h1 style={{fontSize:isWide?58:Math.min(fit(s.a),fit(s.b))}}><span className="title-line"><span>{s.a}</span></span><span className="title-line accent-line"><span>{s.b}<span className="period">.</span></span></span></h1><p>{s.desc}</p>{s.note&&<div className="scene-note">{s.note}</div>}</section>
 <section className={'scene-visual kind-'+s.kind}><Visuals s={s.kind==='sphere'?{...s,start:visualScene.start}:s} time={frame.time} chapter={chapter}/></section>
 </div>
 <div className="inputs"><div className="input-label">{chapter.summary||""}</div><div className="input-flow">{(chapter.labels||[]).map((label,i)=><React.Fragment key={i}><span>{label}</span>{i<(chapter.labels||[]).length-1&&<b>→</b>}</React.Fragment>)}</div></div>
 <aside className="presenter"><div className="portrait"><video id="speaker" src="./source.mp4" playsInline preload="metadata"/><div className="portraitshade"/><div className="live"><i/>口播讲解</div><div className="speaker">{story.speaker||"讲解"}<span>{story.tagline||""}</span></div></div><div className="presenter-foot"><div className="wave">{Array.from({length:23},(_,i)=><i key={i} style={{height:7+(Math.sin(i*1.8+frame.time*7)+1)*13,'--i':i}}/>)}</div><span>{story.tagline||""}</span></div></aside>
 <div className="intro-label">{story.introTitle||story.topic}<span>{story.introSubtitle||""}</span></div>
 <div className="bottom"><span className="caption">{subtitle}</span><span className="progress">{chapter.short}</span></div><div className="edge">VIDEO NOTES</div>
 <div className="chapter-wipe" ref={transitionRef}/>
 </main>
}
document.fonts.load('700 120px SourceHan').then(()=>createRoot(document.getElementById('root')).render(<App/>));
