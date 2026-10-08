/* Boot the actual vendored core, import the public QBEAST and resume its battery. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path');
const root=process.argv[2]||'http://127.0.0.1:3000',out=process.argv[3]||'artifacts/sol-spark-core';
(async()=>{
 await fs.mkdir(out,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage(),errors=[];
 await page.addInitScript(()=>{
  let ready;
  Object.defineProperty(window,'EJS_ready',{configurable:true,get:()=>ready,set(fn){ready=()=>{
   fn();EJS_emulator.on('saveDatabaseLoaded',fs=>{
    const name=EJS_gameName.replace(/\.gba$/,'');window.__preparedBattery=Array.from(fs.readFile('/data/saves/mGBA/'+name+'.srm'));
   });
  };}});
 });
 page.on('pageerror',e=>errors.push(e.message));
 const fixtureText=await fs.readFile(path.join(__dirname,'fixtures/vercel-spark.qbeast'),'utf8');
 async function open(){
  await page.goto(root+'/arcade/sol-spark-gate/?mode=handheld');
  await page.waitForFunction(()=>!document.querySelector('#status').textContent.includes('Loading'));
  await page.evaluate(text=>{
   window.__cloudEvents=[];
   window.addEventListener('message',event=>{if(event.source===window&&['sol-spark-admitted','sol-spark-running','sol-spark-input-ack','sol-spark-return','sol-spark-return-error','sol-spark-observation'].includes(event.data?.type))window.__cloudEvents.push(event.data);});
   window.postMessage({type:'sol-spark-qbeast',text},location.origin);
  },fixtureText);
  await page.waitForFunction(()=>window.__cloudEvents.some(event=>event.type==='sol-spark-admitted'),null,{timeout:30000});
  const hand=page.frameLocator('#handheld');await hand.locator('#status').filter({hasText:'cartridge mailbox'}).waitFor();
  await page.evaluate(()=>window.postMessage({type:'sol-spark-start'},location.origin));
  await page.waitForFunction(()=>window.__cloudEvents.some(event=>event.type==='sol-spark-running'),null,{timeout:90000});
  await hand.locator('#status').filter({hasText:/Cartridge running|Journey restored/}).waitFor({timeout:90000});
  return page.frames().find(f=>f.url().includes('/handheld.html'));
 }
 try{
  const hand=await open();
  const initial=await hand.evaluate(()=>{const gm=EJS_emulator.gameManager,s=gm.getSaveFile(false);return {path:gm.getSaveFilePath(),name:EJS_gameName,files:gm.FS.readdir('/data/saves'),save:s?Array.from(s):null}});
  console.log('Native battery admission:',JSON.stringify({...initial,save:initial.save?.length}));
  assert.equal(initial.save.length,32768);assert.equal(Buffer.from(initial.save).toString('ascii',24704,24708),'SPK1');
  assert.ok(initial.path.includes(initial.name.replace('.gba','')),'native battery uses the selected identity namespace');
  console.log('Native core battery path:',initial.path);
  // Actual frame observations cross both trust-checked iframe boundaries.
  const selected=await page.evaluate(()=>window.__cloudEvents.find(x=>x.type==='sol-spark-admitted').id);
  await page.evaluate(({id})=>window.postMessage({type:'sol-spark-observe-request',requestId:'native-vision-001',qbeast_id:id},location.origin),{id:selected});
  await page.waitForFunction(()=>window.__cloudEvents.some(x=>x.type==='sol-spark-observation'&&x.requestId==='native-vision-001'),null,{timeout:8000});
  const seen=await page.evaluate(()=>window.__cloudEvents.find(x=>x.type==='sol-spark-observation'&&x.requestId==='native-vision-001'));
  assert.equal(seen.qbeast_id,selected);
  assert.ok(['observed','unavailable'].includes(seen.observation?.status));
  if(seen.observation.status==='observed'){
   assert.equal(seen.observation.source,'native-emulator-display');
   for(const k of ['brightness','contrast','frameChange'])assert.ok(Number.isInteger(seen.observation[k])&&seen.observation[k]>=0&&seen.observation[k]<=100);
   assert.ok(['red','green','blue','mixed'].includes(seen.observation.dominant));
  }
  // A mismatched Beast must not get even a bounded pixel response.
  await page.evaluate(()=>window.postMessage({type:'sol-spark-observe-request',requestId:'native-vision-forged',qbeast_id:'bb-not-this-beast'},location.origin));
  await page.waitForTimeout(300);
  assert.equal(await page.evaluate(()=>window.__cloudEvents.some(x=>x.requestId==='native-vision-forged')),false);
  console.log('Native optical relay:',seen.observation.status,'same verified Beast; no forged response');
  // A speaker diagnostic is distinct from emulator-generated native game sound.
  await hand.locator('#test-audio').click();
  assert.match(await hand.locator('#audio-status').innerText(),/Speaker test sent|Speaker test could not start|Speaker resume was blocked/);

  await hand.evaluate(()=>{const gm=EJS_emulator.gameManager,original=gm.simulateInput.bind(gm);window.__bridgedInputs=[];gm.simulateInput=(player,index,value)=>{window.__bridgedInputs.push([player,index,value]);return original(player,index,value);};});
  const bridgeInput=async(button,down)=>page.evaluate(({button,down})=>window.postMessage({type:'sol-spark-input',button,down},location.origin),{button,down});
  const expected={up:4,down:5,left:6,right:7,a:8,b:0,start:3,select:2};
  for(const [button,index] of Object.entries(expected)){
   await bridgeInput(button,true);await bridgeInput(button,false);await page.waitForTimeout(40);
   assert.deepEqual(await hand.evaluate(()=>window.__bridgedInputs.slice(-2)),[[0,index,1],[0,index,0]],`parent ${button} reaches the actual mounted EmulatorJS core`);
   const ack=await page.evaluate(button=>window.__cloudEvents.filter(event=>event.type==='sol-spark-input-ack'&&event.button===button).slice(-1)[0],button);
   assert.equal(ack?.applied,true,`parent ${button} is acknowledged by the mounted core`);
  }
  const beforeInvalid=await hand.evaluate(()=>window.__bridgedInputs.length);await bridgeInput('not-a-control',true);await page.waitForTimeout(40);
  assert.equal(await hand.evaluate(()=>window.__bridgedInputs.length),beforeInvalid,'invalid forwarded controls are rejected');
  await hand.locator('#game canvas').first().screenshot({path:out+'/native-title.png'});
  async function pressParent(button){await bridgeInput(button,true);await page.waitForTimeout(150);await bridgeInput(button,false);await page.waitForTimeout(650);}
  // Advance the real native title flow through the exact parent bridge under test.
  // The LCR1 roster appearing in SRAM below is the native-game effect receipt.
  await page.waitForTimeout(1800);await pressParent('a');await page.waitForTimeout(900);await pressParent('start');
  await hand.waitForFunction(()=>{const gm=EJS_emulator.gameManager;gm.saveSaveFiles();const s=gm.getSaveFile(false);return s&&String.fromCharCode(...s.subarray(1024,1028))==='LCR1'},null,{timeout:90000});
  // A boot/title screen may be black or cleared; sample again after native gameplay begins.
  await page.evaluate(({id})=>window.postMessage({type:'sol-spark-observe-request',requestId:'native-vision-play-002',qbeast_id:id},location.origin),{id:selected});
  await page.waitForFunction(()=>window.__cloudEvents.some(x=>x.type==='sol-spark-observation'&&x.requestId==='native-vision-play-002'),null,{timeout:8000});
  const gameplayView=await page.evaluate(()=>window.__cloudEvents.find(x=>x.type==='sol-spark-observation'&&x.requestId==='native-vision-play-002'));
  assert.equal(gameplayView.qbeast_id,selected);
  assert.ok(['observed','unavailable'].includes(gameplayView.observation?.status));
  console.log('Native gameplay optical status:',gameplayView.observation.status);

  await page.evaluate(()=>window.postMessage({type:'sol-spark-return-request'},location.origin));
  await page.waitForFunction(()=>window.__cloudEvents.some(event=>event.type==='sol-spark-return'),null,{timeout:15000});
  const returned=await page.evaluate(()=>window.__cloudEvents.filter(event=>event.type==='sol-spark-return').slice(-1)[0]?.payload);
  assert.equal(returned?.schema,'lost-cosmos-return-v1');
  assert.match(returned?.qbeast_id||'',/^bb-/);
  assert.match(returned?.event_id||'',/^native-[0-9a-f]{64}$/);
  assert.ok(Number(returned?.game_level)>=1);
  assert.ok(Number(returned?.game_xp)>=0);
  assert.equal(Buffer.from(returned?.native_save||'','base64').length,32768,'native return contains the actual 32 KB battery');
  // Pause the CPU before taking the battery snapshot: journal initialization
  // otherwise legitimately continues between export and pagehide checkpoint.
  await hand.evaluate(()=>EJS_emulator.pause());
  const downloadPromise=page.waitForEvent('download');await hand.locator('#save-journey').click();
  const download=await downloadPromise;await download.saveAs(out+'/PUBLIC_SPARK_JOURNEY.sav');
  const earned=Array.from(await fs.readFile(out+'/PUBLIC_SPARK_JOURNEY.sav'));
  assert.equal(Buffer.from(earned).toString('ascii',0,4),'LCV5');
  assert.deepEqual(earned.slice(24704,24832),initial.save.slice(24704,24832));
  await hand.locator('#game canvas').first().screenshot({path:out+'/native-companion.png'});
  const resumed=await open();assert.match(await resumed.locator('#status').innerText(),/Journey restored/);
  // Observe exact admission before the CPU initializes its journal banks.
  const reopened=await resumed.evaluate(()=>window.__preparedBattery);assert.deepEqual(reopened,earned);
  const running=await resumed.evaluate(()=>Array.from(EJS_emulator.gameManager.getSaveFile(false)));
  assert.deepEqual(running.slice(1024,1276),earned.slice(1024,1276),'native roster and earned progress survive boot');
  assert.deepEqual(running.slice(25600),earned.slice(25600),'manual slots and Spark forms survive boot');
  assert.deepEqual(errors,[]);await fs.writeFile(out+'/report.json',JSON.stringify({passed:true,nativeCore:true,publicQbeast:true,parentStartBootsCore:true,sameIdentityBattery:true,earnedBatterySurvivesReopen:true,allEightParentControlsHitNativeCore:true,parentControlsAdvanceNativeGame:true,nativeSaveReturnPayload:true,opticalReplyStatus:seen.observation.status,gameplayOpticalStatus:gameplayView.observation.status,forgedObservationRejected:true,speakerProbeTriggered:true,consoleErrors:errors},null,2));
  console.log('PASS: parent Start Lost COSMOS booted the native core, all eight controls reached it, and the actual native battery returned as lost-cosmos-return-v1');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
