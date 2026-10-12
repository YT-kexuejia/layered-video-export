// Original analytic ribbon shader. No React Bits component or shader code is used.
import React,{useEffect,useRef} from 'react';
import * as THREE from 'three';
import {registerDraw} from './motion.js';
const fragment=`precision highp float;
varying vec2 vUv;
uniform float time;uniform vec3 cold;uniform vec3 warm;
void main(){
 vec2 p=(vUv-.5)*2.;float beam=0.;float haze=0.;
 for(int i=0;i<5;i++){
  float n=float(i);float lane=p.x-.56*p.y;
  float center=.15*sin(p.y*2.8+time*.09+n*.83)+.065*sin(p.y*8.1-time*.07+n*1.3)+(n-2.)*.18;
  float d=abs(lane-center);float width=.016+.008*sin(p.y*3.+n);
  beam+=exp(-d*d/(width*width))*(.38+.08*cos(p.y*4.+n));
  haze+=exp(-d*d/.08)*.23;
 }
 float field=clamp((beam+haze)*1.3,0.,1.);float taper=1.-smoothstep(.25,1.4,length(p*vec2(.75,.55)));
 vec3 color=mix(cold,warm,clamp(.5+.45*sin(p.y*1.7+time*.04),0.,1.));
 gl_FragColor=vec4(color*(.65+beam*.8),field*taper);
}`;
export default function LightPillar({topColor='#9bc5ff',bottomColor='#deeaff'}){
 const host=useRef();
 useEffect(()=>{
  const renderer=new THREE.WebGLRenderer({alpha:true,antialias:false,preserveDrawingBuffer:true});renderer.setSize(1330,1330);host.current.append(renderer.domElement);
  const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{time:{value:0},cold:{value:new THREE.Color(topColor)},warm:{value:new THREE.Color(bottomColor)}},vertexShader:'varying vec2 vUv;void main(){vUv=position.xy*.5+.5;gl_Position=vec4(position,1.);}',fragmentShader:fragment});
  const scene=new THREE.Scene(),geometry=new THREE.PlaneGeometry(2,2);scene.add(new THREE.Mesh(geometry,material));
  const off=registerDraw(()=>{material.uniforms.time.value=matchMedia('(prefers-reduced-motion: reduce)').matches?0:window.__filmClock||0;renderer.render(scene,new THREE.Camera());});
  return()=>{off();geometry.dispose();material.dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();};
 },[topColor,bottomColor]);
 return <div ref={host} style={{width:'100%',height:'100%'}}/>;
}
