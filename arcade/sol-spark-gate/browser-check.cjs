const {chromium}=require('playwright');const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const base=process.argv[2]||'http://127.0.0.1:8765',out=path.resolve(process.argv[3]||'artifacts/sol-spark-browser');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.SOL_CHROME?{executablePath:process.env.SOL_CHROME}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1400,height:1100},acceptDownloads:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(base+'/arcade/sol-spark-gate/');await page.waitForFunction(()=>!document.getElementById('status').textContent.includes('Loading'));
  const fixture=path.join(__dirname,'fixtures/vercel-spark.qbeast');await page.locator('#beast-file').setInputFiles(fixture);
  await page.waitForFunction(()=>!document.getElementById('download').disabled);const original=await page.locator('#companion').innerText();
  const player=page.frameLocator('#handheld');await player.locator('#status').filter({hasText:'cartridge mailbox'}).waitFor();
  const pending=page.waitForEvent('download');await page.locator('#download').click();const download=await pending;await download.saveAs(path.join(out,'VERCEL_SPARK_STARTER.sav'));assert.equal(fs.statSync(path.join(out,'VERCEL_SPARK_STARTER.sav')).size,32768);
  const bytes=fs.readFileSync(path.join(out,'VERCEL_SPARK_STARTER.sav'));assert.equal(bytes[24837]&2,2);assert.equal(bytes.toString('ascii',24704,24708),'SPK1');
  await page.locator('#beast-file').setInputFiles({name:'bad.qbeast',mimeType:'application/json',buffer:Buffer.from('{}')});await page.waitForFunction(()=>document.getElementById('status').textContent.includes('Choose a Spark'));
  assert.equal(await page.locator('#companion').innerText(),original);assert.equal(await page.locator('#download').isEnabled(),true);
  const r=page.waitForEvent('download');await page.locator('#receipt').click();await(await r).saveAs(path.join(out,'SPARK_RECEIPT.json'));
  await page.reload();await page.waitForFunction(()=>!document.getElementById('status').textContent.includes('Loading'));await page.locator('#beast-file').setInputFiles(path.join(out,'SPARK_RECEIPT.json'));await page.waitForFunction(()=>!document.getElementById('download').disabled);assert.equal(await page.locator('#companion').innerText(),original);
  // Drive Grok's real page through its existing, admitted Send to handheld path.
  const spark=page.frameLocator('#spark');await spark.locator('#consent').check();await spark.locator('#player-name').fill('CORY');await spark.locator('#spark-btn').click();await spark.locator('#portrait').waitFor({state:'visible'});
  await spark.locator('[data-view="trade"]').click();await spark.locator('#send').click();await page.waitForFunction(()=>!document.getElementById('companion').textContent.startsWith('Aurlet'));
  await player.locator('#status').filter({hasText:'cartridge mailbox'}).waitFor();
  const s=page.waitForEvent('download');await page.locator('#download').click();await(await s).saveAs(path.join(out,'GROK_SPARK_STARTER.sav'));assert.equal(fs.readFileSync(path.join(out,'GROK_SPARK_STARTER.sav')).toString('ascii',24704,24708),'SPK1');
  await page.screenshot({path:path.join(out,'SPARK_GATE_DESKTOP.png'),fullPage:true});
  for(const width of [320,390]){await page.setViewportSize({width,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.screenshot({path:path.join(out,`SPARK_GATE_MOBILE_${width}.png`),fullPage:true});}
  assert.deepEqual(errors,[]);const report={passed:true,checks:['public Vercel QBEAST1 import','actual art mailbox forwarding','32 KB save download','invalid file is atomic','receipt restore preserves identity','unmodified Grok Spark UI and admitted handheld send','320px and 390px layout','no page errors']};fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
