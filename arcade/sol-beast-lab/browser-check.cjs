/* Run against a served repository: NODE_PATH=<playwright node_modules> node
 * arcade/sol-beast-lab/browser-check.cjs [base URL] [output directory].
 * An optional SOL_CHROME points at a locally installed Chrome executable. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const base=process.argv[2]||'http://127.0.0.1:8765',out=path.resolve(process.argv[3]||'artifacts/sol-browser');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.SOL_CHROME?{executablePath:process.env.SOL_CHROME}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1280,height:1000},reducedMotion:'reduce',acceptDownloads:true}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(base+'/arcade/sol-beast-lab/');await page.waitForSelector('html[data-ready="true"]');
  assert.equal(await page.locator('#creature-name').innerText(),'Cinderkip');
  const originalId=await page.locator('#identity').innerText(),originalSeed=await page.locator('#seed').inputValue();
  const receiptDownload=page.waitForEvent('download');await page.getByRole('button',{name:'↓ Companion receipt',exact:true}).click();
  const receipt=await receiptDownload;await receipt.saveAs(path.join(out,'companion.json'));const json=JSON.parse(fs.readFileSync(path.join(out,'companion.json'),'utf8'));
  const bad={...json,islandIndex:2,nonce:'REJECTED',traits:{focus:1,calm:2,spark:3},source:'muse-derived'};
  await page.locator('#read-receipt').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(bad))});
  await page.waitForFunction(()=>document.getElementById('status').textContent.includes('does not match'));
  assert.equal(await page.locator('#identity').innerText(),originalId);assert.equal(await page.locator('#seed').inputValue(),originalSeed);
  assert.equal(await page.locator('#source-label').innerText(),'MANUAL CUES');assert.equal(await page.locator('#save').isEnabled(),true);
  const missing=await page.evaluate(async()=>{const{createBeast,publicReceipt}=await import('./design.mjs');const archive=new Uint8Array((await(await fetch('archive.json')).json()).bytes);const r=publicReceipt(createBeast({island:2,nonce:'DEFAULT-CASE',focus:50,calm:50,spark:50},archive));delete r.traits;return r;});
  await page.locator('#read-receipt').setInputFiles({name:'missing.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(missing))});
  await page.waitForFunction(()=>document.getElementById('status').textContent.includes('all three'));
  assert.equal(await page.locator('#identity').innerText(),originalId);assert.equal(await page.locator('#seed').inputValue(),originalSeed);assert.equal(await page.locator('#save').isEnabled(),true);
  await page.locator('#seed').fill('');await page.getByRole('button',{name:'Preview Hearthpaw',exact:true}).click();
  assert.equal(await page.locator('#hatch').isDisabled(),true);assert.equal(await page.locator('#save').isDisabled(),true);
  await page.locator('#seed').fill(originalSeed);assert.equal(await page.locator('#save').isEnabled(),true);
  await page.locator('#read-save-button').focus();assert.equal(await page.evaluate(()=>document.activeElement.id),'read-save-button');
  await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'read-receipt-button');
  const starterDownload=page.waitForEvent('download');await page.locator('#save').click();const starter=await starterDownload;
  await starter.saveAs(path.join(out,'starter.sav'));assert.equal(fs.statSync(path.join(out,'starter.sav')).size,32768);
  await page.getByRole('button',{name:'The Shattered Reef',exact:true}).click();assert.equal(await page.locator('#creature-name').innerText(),'Bubblefin');assert.equal(await page.locator('#save').isDisabled(),true);
  await page.locator('#hatch').click();await page.waitForFunction(()=>!document.getElementById('save').disabled);assert.notEqual(await page.locator('#identity').innerText(),originalId);
  await page.locator('#read-receipt').setInputFiles(path.join(out,'companion.json'));await page.waitForFunction(()=>document.getElementById('creature-name').textContent==='Cinderkip');
  await page.reload();await page.waitForSelector('html[data-ready="true"]');assert.equal(await page.locator('#identity').innerText(),originalId);
  await page.screenshot({path:path.join(out,'SOL_NURSERY_DESKTOP.png'),fullPage:true});
  for(const width of [320,390]){await page.setViewportSize({width,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.equal(await page.evaluate(()=>{const panel=document.querySelector('.evolution').getBoundingClientRect();return[...document.querySelectorAll('.stage')].every(card=>{const r=card.getBoundingClientRect(),c=card.querySelector('canvas').getBoundingClientRect();return r.left>=panel.left&&r.right<=panel.right&&c.left>=r.left&&c.right<=r.right;});}),true);await page.screenshot({path:path.join(out,`SOL_NURSERY_MOBILE_${width}.png`),fullPage:true});}
  await page.locator('#simulate').click();assert.equal(await page.locator('#source-label').innerText(),'SIMULATED CUES');
  assert.equal(await page.locator('#save').isDisabled(),true);
  const context=await browser.newContext({reducedMotion:'reduce'});await context.addInitScript(()=>{Storage.prototype.setItem=function(){throw new Error('blocked for test')};});
  const privatePage=await context.newPage();await privatePage.goto(base+'/arcade/sol-beast-lab/');await privatePage.waitForSelector('html[data-ready="true"]');
  assert.match(await privatePage.locator('#status').innerText(),/could not save your shelf/);await context.close();
  assert.deepEqual(errors,[]);
  const report={passed:true,checks:['load','no page errors','rejected receipt is atomic','invalid draft remains gated','keyboard file actions','32768-byte download','island hatch','receipt restore','shelf reload','320px and 390px mobile layout','explicit simulation','storage failure warning']};
  fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
