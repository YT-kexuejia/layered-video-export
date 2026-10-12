import React,{useEffect,useRef} from 'react';
import * as THREE from 'three';
import {registerDraw} from './motion.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

export default function Scene3D({kind='sphere',label='AI',start=0}){
 const host=useRef(null);
 useEffect(()=>{
 const container=host.current,w=container.clientWidth,h=container.clientHeight;
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(1);renderer.setSize(w,h);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;container.appendChild(renderer.domElement);
 const scene=new THREE.Scene();const camera=new THREE.PerspectiveCamera(33,w/h,.1,100);camera.position.set(0,0,8.4);
 const pmrem=new THREE.PMREMGenerator(renderer);const environment=new RoomEnvironment();const env=pmrem.fromScene(environment,.04);scene.environment=env.texture;
 scene.add(new THREE.AmbientLight(0xadcfff,.5));const key=new THREE.DirectionalLight(0xe7f4ff,4);key.position.set(-3,5,4);scene.add(key);const rim=new THREE.PointLight(0x3183ff,75,15);rim.position.set(3,1,-2);scene.add(rim);const fill=new THREE.PointLight(0xa9e5ff,25,15);fill.position.set(-4,-2,3);scene.add(fill);
 const group=new THREE.Group();scene.add(group);const art=new THREE.Group();group.add(art);
 const metal=new THREE.MeshPhysicalMaterial({color:0x182b42,metalness:.87,roughness:.34,clearcoat:1,clearcoatRoughness:.12});
 const rimMat=new THREE.MeshStandardMaterial({color:0x82baff,emissive:0x3179d5,emissiveIntensity:.5,metalness:.55,roughness:.28});
 function textPlane(text,width,y,z,size=190){const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=512;const c=canvas.getContext('2d');c.font=`700 ${size}px SourceHan`;c.textAlign='center';c.textBaseline='middle';c.fillStyle='#e1efff';c.shadowColor='#66aaff';c.shadowBlur=9;c.fillText(text,512,256);const tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;const plane=new THREE.Mesh(new THREE.PlaneGeometry(width,width/2),new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false}));plane.position.set(0,y,z);art.add(plane);return plane;}
 let movingCamera=null,pathCurve=null;
 if(kind==='sphere'){
  const globe=new THREE.Mesh(new THREE.SphereGeometry(1.66,96,64),metal);art.add(globe);
  const halo=new THREE.Mesh(new THREE.TorusGeometry(2.03,.012,12,180),rimMat);halo.rotation.set(.75,.23,-.22);group.add(halo);
  const halo2=new THREE.Mesh(new THREE.TorusGeometry(2.24,.007,8,180),new THREE.MeshBasicMaterial({color:0x7db8ff,transparent:true,opacity:.28}));halo2.rotation.set(-.5,.6,.36);group.add(halo2);
  textPlane(label,3.35,0,1.71,300);textPlane('MODEL',2.25,.92,1.47,64);textPlane('VIDEO ENGINE',2.1,-.95,1.43,49);
  for(let i=0;i<5;i++){const bead=new THREE.Mesh(new THREE.SphereGeometry(i===0?.036:.022,12,12),rimMat);const a=i*1.24;bead.position.set(2.03*Math.cos(a),1.54*Math.sin(a),.7*Math.sin(a));group.add(bead);}
 }else if(kind==='chip'){
  const board=new THREE.Mesh(new THREE.BoxGeometry(3.7,2.7,.13),metal);art.add(board);const chip=new THREE.Mesh(new THREE.BoxGeometry(1.85,1.55,.38),new THREE.MeshPhysicalMaterial({color:0x304966,metalness:.86,roughness:.24,clearcoat:1}));chip.position.z=.21;art.add(chip);textPlane(label,1.6,0,.43,140);
  for(let i=0;i<14;i++){for(const side of [-1,1]){const pin=new THREE.Mesh(new THREE.BoxGeometry(.09,.45,.06),rimMat);pin.position.set(-1.48+i*.226,side*1.37,.12);art.add(pin);}}
  for(let i=0;i<5;i++){const line=new THREE.Mesh(new THREE.BoxGeometry(.8,.025,.012),rimMat);line.position.set(-1.35,.6-i*.29,.082);art.add(line);const line2=line.clone();line2.position.x=1.35;art.add(line2);}
 }else if(kind==='camera'){
  camera.position.set(5,4.6,7);camera.lookAt(0,0,0);camera.fov=35;camera.updateProjectionMatrix();
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(7,6),new THREE.MeshStandardMaterial({color:0x182738,metalness:.3,roughness:.6}));floor.rotation.x=-Math.PI/2;floor.position.y=-1.03;art.add(floor);
  const grid=new THREE.GridHelper(7,14,0x6695be,0x294157);grid.position.y=-1.02;art.add(grid);
  const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.11,.16,1.35,16),metal);trunk.position.set(-1.15,-.35,0);art.add(trunk);
  for(let i=0;i<3;i++){const crown=new THREE.Mesh(new THREE.ConeGeometry(.72-i*.17,1.2,24),new THREE.MeshStandardMaterial({color:0x679aa1,metalness:.15,roughness:.6}));crown.position.set(-1.15,.2+i*.46,0);art.add(crown);}
  const person=new THREE.Group();person.position.x=1.13;const body=new THREE.Mesh(new THREE.CapsuleGeometry(.22,.64,10,20),new THREE.MeshStandardMaterial({color:0xd5dfe9,metalness:.3,roughness:.3}));body.position.y=-.15;person.add(body);const head=new THREE.Mesh(new THREE.SphereGeometry(.2,24,24),body.material);head.position.y=.65;person.add(head);for(const side of [-1,1]){const leg=new THREE.Mesh(new THREE.CapsuleGeometry(.072,.45,8,12),body.material);leg.position.set(side*.12,-.7,0);person.add(leg);const arm=new THREE.Mesh(new THREE.CapsuleGeometry(.065,.46,8,12),body.material);arm.position.set(side*.35,-.07,0);arm.rotation.z=side*.2;person.add(arm);}art.add(person);
  const pathPoints=[];for(let i=0;i<=8;i++){const a=Math.PI+i*Math.PI/4;pathPoints.push(new THREE.Vector3(-1.15+1.45*Math.cos(a),.68,1.45*Math.sin(a)));}for(let i=0;i<=8;i++){const a=Math.PI+i*Math.PI/4;pathPoints.push(new THREE.Vector3(1.13+1.08*Math.cos(a),.65,1.08*Math.sin(a)));}pathPoints.push(new THREE.Vector3(1.13,.65,.65));pathCurve=new THREE.CatmullRomCurve3(pathPoints);
  const path=new THREE.Mesh(new THREE.TubeGeometry(pathCurve,100,.012,8,false),rimMat);art.add(path);
  movingCamera=new THREE.Group();const box=new THREE.Mesh(new THREE.BoxGeometry(.34,.24,.28),rimMat);movingCamera.add(box);const lens=new THREE.Mesh(new THREE.CylinderGeometry(.11,.1,.16,16),metal);lens.rotation.x=Math.PI/2;lens.position.z=-.21;movingCamera.add(lens);art.add(movingCamera);
 }else{
  for(let i=0;i<3;i++){const block=new THREE.Mesh(new THREE.BoxGeometry(.99,1.18,.32),metal);block.position.set((i-1)*1.44,Math.sin(i*2)*.12,0);art.add(block);const wire=new THREE.Mesh(new THREE.BoxGeometry(.43,.018,.018),rimMat);wire.position.x=(i-.5)*1.44;if(i<2)art.add(wire);const edge=new THREE.LineSegments(new THREE.EdgesGeometry(block.geometry),new THREE.LineBasicMaterial({color:0x78b3fb,transparent:true,opacity:.65}));edge.position.copy(block.position);art.add(edge);}
 }
 const off=registerDraw(()=>{const t=window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:Math.max(0,(window.__filmClock??0)-start);if(kind==='sphere'){art.rotation.y=Math.sin(t*.24)*.11;group.rotation.z=Math.sin(t*.1)*.025;}else if(kind==='camera'){const progress=(t%16)/16;const p=pathCurve.getPoint(progress);movingCamera.position.copy(p);movingCamera.lookAt(progress<.48?-1.15:1.13,.4,0);}else{group.rotation.set(-.17+Math.sin(t*.22)*.055,-.33+Math.sin(t*.16)*.17,.04);}renderer.render(scene,camera);});window.__threeReady=true;
 return()=>{off();scene.traverse(o=>{o.geometry?.dispose();if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material]){m.map?.dispose();m.dispose();}}});env.dispose();environment.dispose();pmrem.dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();};
 },[kind,label,start]);
 return <div className={'scene3d '+kind} ref={host} aria-label={'3D '+label}/>;
}
