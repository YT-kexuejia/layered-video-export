import React,{useLayoutEffect,useRef} from 'react';
import * as T from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {registerDraw,ease} from './motion.js';
export default function Objects3D({kind,start=0}){
 const host=useRef();
 useLayoutEffect(()=>{
  const el=host.current,w=el.clientWidth,h=el.clientHeight;
  const r=new T.WebGLRenderer({alpha:true,antialias:true});r.setSize(w,h);r.setPixelRatio(1);r.outputColorSpace=T.SRGBColorSpace;r.toneMapping=T.ACESFilmicToneMapping;r.toneMappingExposure=1.05;el.append(r.domElement);
  const scene=new T.Scene(),camera=new T.PerspectiveCamera(33,w/h,.1,100);camera.position.set(4,3,7);camera.lookAt(0,0,0);
  const pm=new T.PMREMGenerator(r),room=new RoomEnvironment(),env=pm.fromScene(room,.06);scene.environment=env.texture;
  scene.add(new T.HemisphereLight(0xc4e8ff,0x173047,1.1));const key=new T.DirectionalLight(0xffffff,4);key.position.set(-4,6,5);scene.add(key);
  const g=new T.Group();scene.add(g);
  const navy=new T.MeshStandardMaterial({color:0x17324d,metalness:.7,roughness:.34}),silver=new T.MeshStandardMaterial({color:0xc5d4df,metalness:.6,roughness:.3}),blue=new T.MeshStandardMaterial({color:0x71b9eb,metalness:.45,roughness:.3}),black=new T.MeshStandardMaterial({color:0x0b1625,metalness:.5,roughness:.45});
  function mesh(geo,mat,x=0,y=0,z=0,parent=g){const o=new T.Mesh(geo,mat);o.position.set(x,y,z);parent.add(o);return o}
  const box=(x,y,z,a,b,c,mat=navy,parent=g)=>mesh(new RoundedBoxGeometry(a,b,c,2,Math.min(.045,a/4,b/4,c/4)),mat,x,y,z,parent);
  const cyl=(x,y,z,rad,len,mat=silver,parent=g)=>mesh(new T.CylinderGeometry(rad,rad,len,40),mat,x,y,z,parent);
  const fans=[],layers=[];let rotate=null,cart=null,beam=null;
  function human(x=0,z=0,parent=g){const p=new T.Group();p.position.set(x,-.2,z);parent.add(p);mesh(new T.CapsuleGeometry(.24,.65,8,24),silver,0,.2,0,p);mesh(new T.SphereGeometry(.21,24,16),silver,0,.96,0,p);for(const side of [-1,1]){mesh(new T.CapsuleGeometry(.08,.66,8,16),silver,side*.13,-.57,0,p);const arm=mesh(new T.CapsuleGeometry(.065,.56,8,16),silver,side*.36,.21,0,p);arm.rotation.z=side*.12;}return p;}
  function cameraBody(parent){box(0,.35,0,.65,.46,.46,navy,parent);const lens=cyl(0,.35,-.34,.19,.35,black,parent);lens.rotation.x=Math.PI/2;const glass=cyl(0,.35,-.53,.16,.035,blue,parent);glass.rotation.x=Math.PI/2;box(0,.64,0,.3,.13,.2,silver,parent);}
  if(kind==='server'){
   for(let col=0;col<2;col++){box((col-.5)*1.9,0,0,1.55,3.2,1.25);for(let i=0;i<6;i++){box((col-.5)*1.9,-1.26+i*.5,.66,1.37,.38,.08,black);for(let j=0;j<9;j++)box((col-.5)*1.9-.54+j*.11,-1.26+i*.5,.72,.025,.2,.035,silver);mesh(new T.SphereGeometry(.035,10,8),blue,(col-.5)*1.9+.59,-1.26+i*.5,.74);}}
  }else if(['assembly','deployment','cache'].includes(kind)){
   for(let i=0;i<4;i++){const l=new T.Group();g.add(l);l.position.y=-1.05+i*.65;box(0,0,0,2.7,.13,2,navy,l);box(0,.13,0,1.2,.12,.8,i===3?blue:black,l);for(let j=0;j<7;j++)box(-1+j*.34,.09,.78,.19,.08,.19,silver,l);layers.push(l);}
  }else if(kind==='gpu-board'){
   camera.position.set(1.7,3.3,7);camera.lookAt(0,0,0);box(0,0,0,4.3,.32,1.9);box(0,.2,0,4.05,.2,1.72,black);for(let i=0;i<2;i++){const f=new T.Group();f.position.set((i-.5)*2,.36,0);g.add(f);cyl(0,0,0,.76,.08,silver,f);cyl(0,.055,0,.68,.075,black,f);for(let j=0;j<9;j++){const blade=box(Math.cos(j*Math.PI*2/9)*.4,.11,Math.sin(j*Math.PI*2/9)*.4,.52,.055,.17,navy,f);blade.rotation.y=-j*Math.PI*2/9+.5;}cyl(0,.16,0,.18,.08,blue,f);fans.push(f);}for(let i=0;i<15;i++)box(-1.5+i*.16,-.02,1.07,.09,.1,.28,silver);box(-2.2,.15,0,.12,.8,2.2,silver);
  }else if(kind==='film-reel'){
   camera.position.set(2,2,8);camera.lookAt(0,0,0);for(let n=0;n<2;n++){const reel=new T.Group();reel.position.set((n-.5)*2.2,0,n*.4);g.add(reel);const disk=cyl(0,0,0,1.17,.14,silver,reel);disk.rotation.x=Math.PI/2;for(let i=0;i<6;i++){const hole=cyl(Math.cos(i*Math.PI/3)*.69,Math.sin(i*Math.PI/3)*.69,.09,.24,.03,black,reel);hole.rotation.x=Math.PI/2;}const hub=cyl(0,0,.12,.2,.16,blue,reel);hub.rotation.x=Math.PI/2;fans.push(reel);}box(0,-1.4,0,4,.25,.7,navy);
  }else if(kind==='turntable'){
   cyl(0,-1.38,0,1.65,.16,navy);rotate=human();const ring=mesh(new T.TorusGeometry(1.72,.017,8,120),blue,0,-1.28,0);ring.rotation.x=Math.PI/2;camera.position.set(3,1.6,7);camera.lookAt(0,0,0);
  }else if(kind==='scales'){
   cyl(0,-1.35,0,1.25,.15);cyl(0,-.15,0,.07,2.4);beam=new T.Group();beam.position.y=1;g.add(beam);box(0,0,0,3.7,.09,.09,silver,beam);for(const side of [-1,1]){for(const z of [-.3,.3])cyl(side*1.5,-.55,z,.014,1.05,silver,beam);cyl(side*1.5,-1.1,0,.64,.06,navy,beam);box(side*1.5,-.87,0,.45,.4,.4,blue,beam);}
  }else{
   const floor=box(0,-1.36,0,5,.09,3.8,black);const grid=new T.GridHelper(5,10,0x6c8dab,0x233c54);grid.position.y=-1.3;g.add(grid);human(1.2,0);cart=new T.Group();g.add(cart);cameraBody(cart);cyl(0,-.45,0,.035,1.25,silver,cart);for(const side of [-1,1]){box(-.6,-1.19,side*.6,3.6,.06,.06,silver);const foot=box(side*.25,-1.05,0,.05,.45,.06,silver,cart);foot.rotation.z=side*.45;}box(0,-1.21,0,.85,.1,.8,navy,cart);camera.position.set(4,3.3,7);camera.lookAt(0,0,0);
  }
  const off=registerDraw(()=>{const t=Math.max(0,(window.__filmClock||0)-start),still=window.matchMedia('(prefers-reduced-motion: reduce)').matches;const tt=still?0:t;
   g.rotation.y=['server','gpu-board','film-reel'].includes(kind)?Math.sin(tt*.13)*.12:0;
   layers.forEach((l,i)=>{l.position.y=-1.05+i*(.31+.36*ease(tt/2));l.rotation.y=(i-1.5)*.025;});
   fans.forEach((f,i)=>{if(kind==='film-reel')f.rotation.z=tt*.14;else f.rotation.y=tt*.8;});
   if(rotate)rotate.rotation.y=tt*.28;if(cart){cart.position.x=-1.15+Math.sin(tt*.27)*.75;cart.rotation.y=-Math.PI/2;}if(beam)beam.rotation.z=Math.sin(tt*.35)*.065;
   r.render(scene,camera);
  });
  return()=>{off();scene.traverse(o=>{o.geometry?.dispose();if(o.material)for(const m of [o.material].flat())m.dispose();});env.dispose();room.dispose();pm.dispose();r.dispose();r.forceContextLoss();el.replaceChildren();};
 },[kind,start]);
 return <div className={'object3d object-'+kind} ref={host} aria-label={kind+' 三维示意'}/>;
}
