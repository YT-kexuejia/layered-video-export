// Project adapter around MIT-licensed Anime.js; time is always provided in seconds.
import {createTimeline,utils,stagger} from 'animejs';
const easings={'power3.inOut':'inOutQuart','power3.out':'outQuart','power4.out':'outQuint','power2.inOut':'inOutCubic'};
function params(to,from){
 const out={duration:(to.duration??.5)*1000,ease:easings[to.ease]||'outQuart'};
 for(const [k,v]of Object.entries(to))if(!['duration','ease','stagger'].includes(k))out[k]=from&&k in from?{from:from[k],to:v}:v;
 if(to.stagger)out.delay=stagger(to.stagger*1000);
 return out;
}
export default {
 set(target,values){if(target)utils.set(target,values);},
 timeline(){const tl=createTimeline({autoplay:false});return {
  to(target,to,at=0){if(target)tl.add(target,params(to),at*1000);return this;},
  fromTo(target,from,to,at=0){if(target){utils.set(target,from);tl.add(target,params(to,from),at*1000);}return this;},
  set(target,values){if(target)utils.set(target,values);return this;},
  seek(seconds){tl.seek(Math.max(0,seconds)*1000,true);},
  kill(){tl.cancel();}
 };}
};
