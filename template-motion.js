export const MOTION=Object.freeze({title:.65,lineGap:.09,distance:36,item:.65,hover:200});
export const clamp=x=>Math.max(0,Math.min(1,x));
export const ease=x=>1-Math.pow(1-clamp(x),4);
export function reveal(s,time,i=0){return ease((time-(s.reveal?.[i]??s.start+.2+i*1.6))/MOTION.item)}
export function itemStyle(s,time,i=0){const p=reveal(s,time,i);return {opacity:p,transform:`translateY(${(1-p)*12}px)`}}
export function paintFilm(){for(const draw of window.__filmDraws||[])draw();}
export function registerDraw(draw){(window.__filmDraws??=new Set()).add(draw);draw();return()=>window.__filmDraws.delete(draw);}
