const {webkit}=require('playwright'),assert=require('node:assert/strict');
const root=process.argv[2]||'http://127.0.0.1:8765';
(async()=>{
 const browser=await webkit.launch({headless:true});
 const context=await browser.newContext({
  viewport:{width:390,height:844},isMobile:true,hasTouch:true,
  userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'
 });
 const page=await context.newPage();
 try{
  await page.goto(root+'/arcade/sol-spark-gate/handheld.html?controller=iphoneaudio40',{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{
   const fakeContext={state:'suspended',resumeCalls:0,resume(){this.resumeCalls++;this.state='running';return Promise.resolve();}};
   const source={gain:{context:fakeContext}};
   window.__iphoneAudio={fakeContext,volumes:[]};
   window.EJS_emulator={
    Module:{AL:{currentCtx:{sources:new Set([source])}}},
    setVolume(value){window.__iphoneAudio.volumes.push(value);}
   };
  });
  await page.locator('#audio').tap();
  await page.waitForFunction(()=>document.querySelector('#audio').textContent.includes('Game sound on'));
  const result=await page.evaluate(()=>({
   state:window.__iphoneAudio.fakeContext.state,
   resumeCalls:window.__iphoneAudio.fakeContext.resumeCalls,
   volumes:window.__iphoneAudio.volumes,
   pressed:document.querySelector('#audio').getAttribute('aria-pressed'),
   note:document.querySelector('#audio-status').textContent
  }));
  assert.equal(result.state,'running');
  assert.equal(result.resumeCalls,1);
  assert.ok(result.volumes.some(v=>v>0));
  assert.equal(result.pressed,'true');
  assert.match(result.note,/unlocked/i);
  console.log('PASS: iPhone WebKit trusted sound tap resumes the handheld audio context',result);
  // Some Emscripten builds put the native OpenAL state in window.AL,
  // outside EJS_emulator.Module. The same iPhone button must find it there.
  await page.evaluate(()=>{
   const context={state:'suspended',resumeCalls:0,resume(){this.resumeCalls++;this.state='running';return Promise.resolve();}};
   window.AL={currentCtx:{audioCtx:context}};
   window.EJS_emulator={setVolume(value){window.__iphoneAudio.volumes.push(value);}};
   window.__iphoneAudio.globalContext=context;
  });
  await page.locator('#audio').tap();
  await page.waitForFunction(()=>document.querySelector('#audio').textContent.includes('Game sound on'));
  const recovered=await page.evaluate(()=>({
   state:window.__iphoneAudio.globalContext.state,
   resumeCalls:window.__iphoneAudio.globalContext.resumeCalls,
   text:document.querySelector('#audio').textContent
  }));
  assert.equal(recovered.state,'running');
  assert.equal(recovered.resumeCalls,1);
  assert.match(recovered.text,/Game sound on/);
  console.log('PASS: iPhone WebKit native AL global-context audio resume',recovered);

 }finally{await browser.close();}
})().catch(err=>{console.error(err);process.exitCode=1});
