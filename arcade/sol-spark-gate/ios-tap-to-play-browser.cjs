/* WebKit regression: a START message (no gesture in this frame) must not throw on missing
   MediaRecorder, must show the in-frame TAP TO PLAY target, and one tap must keep the
   cartridge booting to sol-spark-running. Audio is unlocked by that tap, not by a new context. */
const {webkit}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path');
const root=process.argv[2]||'http://127.0.0.1:3000';
(async()=>{
 const browser=await webkit.launch();const page=await (await browser.newContext({viewport:{width:390,height:844}})).newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const text=await fs.readFile(path.join(__dirname,'fixtures/vercel-spark.qbeast'),'utf8');
 try{
  await page.goto(root+'/arcade/sol-spark-gate/?mode=handheld&player=shell45');
  await page.waitForFunction(()=>!document.querySelector('#status').textContent.includes('Loading'));
  await page.evaluate(text=>{window.__ev=[];window.addEventListener('message',e=>{if(e.source===window)window.__ev.push(e.data?.type);});window.postMessage({type:'sol-spark-qbeast',text},location.origin);},text);
  await page.waitForFunction(()=>window.__ev.includes('sol-spark-admitted'),null,{timeout:30000});
  const hand=page.frameLocator('#handheld');await hand.locator('#status').filter({hasText:'cartridge mailbox'}).waitFor();
  await page.evaluate(()=>window.postMessage({type:'sol-spark-start'},location.origin));
  await hand.locator('#tap-gate').waitFor({state:'visible',timeout:30000});
  assert.match(await hand.locator('#tap-gate').textContent(),/TAP/);
  await hand.locator('#tap-gate').click();
  await page.waitForFunction(()=>window.__ev.includes('sol-spark-running'),null,{timeout:90000});
  assert.ok(!errors.some(e=>/MediaRecorder/.test(e)),'no MediaRecorder start failure: '+errors.join(' | '));
  console.log('WebKit tap-to-play: running after one in-frame tap',JSON.stringify({errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
