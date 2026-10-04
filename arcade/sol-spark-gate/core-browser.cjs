/* Boot the actual vendored core, import the public QBEAST and resume its battery. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path');
const root=process.argv[2]||'http://127.0.0.1:8765',out=process.argv[3]||'artifacts/sol-spark-core';
(async()=>{
 await fs.mkdir(out,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 async function open(){
  await page.goto(root+'/arcade/sol-spark-gate/?mode=handheld');
  await page.waitForFunction(()=>!document.querySelector('#status').textContent.includes('Loading'));
  await page.locator('#beast-file').setInputFiles(path.join(__dirname,'fixtures/vercel-spark.qbeast'));
  const hand=page.frameLocator('#handheld');await hand.locator('#status').filter({hasText:'cartridge mailbox'}).waitFor();
  await hand.locator('#play').click();assert.match(await hand.locator('#status').innerText(),/Allow the verified/);
  await hand.locator('#consent').check();await hand.locator('#play').click();
  await hand.getByText(/^start game$/i).click({timeout:60000});
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
  await hand.locator('#game canvas').first().screenshot({path:out+'/native-title.png'});
  async function press(button){await hand.evaluate(b=>EJS_emulator.gameManager.simulateInput(0,b,1),button);await page.waitForTimeout(150);await hand.evaluate(b=>EJS_emulator.gameManager.simulateInput(0,b,0),button);await page.waitForTimeout(650);}
  await page.waitForTimeout(1800);await press(8);await page.waitForTimeout(900);await press(3);
  await hand.waitForFunction(()=>{const gm=EJS_emulator.gameManager;gm.saveSaveFiles();const s=gm.getSaveFile(false);return s&&String.fromCharCode(...s.subarray(1024,1028))==='LCR1'},null,{timeout:90000});
  const earned=await hand.evaluate(async()=>{const gm=EJS_emulator.gameManager;gm.saveSaveFiles();await new Promise((resolve,reject)=>gm.FS.syncfs(false,e=>e?reject(e):resolve()));return Array.from(gm.getSaveFile(false))});
  assert.equal(Buffer.from(earned).toString('ascii',0,4),'LCV5');
  assert.deepEqual(earned.slice(24704,24832),initial.save.slice(24704,24832));
  await fs.writeFile(out+'/PUBLIC_SPARK_JOURNEY.sav',Buffer.from(earned));await hand.locator('#game canvas').first().screenshot({path:out+'/native-companion.png'});
  const resumed=await open();assert.match(await resumed.locator('#status').innerText(),/Journey restored/);
  const reopened=await resumed.evaluate(()=>Array.from(EJS_emulator.gameManager.getSaveFile(false)));assert.deepEqual(reopened,earned);
  assert.deepEqual(errors,[]);await fs.writeFile(out+'/report.json',JSON.stringify({passed:true,nativeCore:true,publicQbeast:true,gestureImport:true,sameIdentityBattery:true,earnedBatterySurvivesReopen:true,consoleErrors:errors},null,2));
  console.log('PASS: actual mobile Chromium core, public Spark import, exact native battery resume');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
