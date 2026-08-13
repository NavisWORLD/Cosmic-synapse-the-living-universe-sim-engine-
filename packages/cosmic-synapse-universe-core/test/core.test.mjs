import test from'node:test';import assert from'node:assert/strict';import{seeded,universeDNA,normalizeSensorSummary}from'../src/index.js';
test('seeded generator deterministic',()=>{const a=seeded('world','707'),b=seeded('world','707');for(let i=0;i<20;i++)assert.equal(a(),b())});
test('DNA changes with world seed',()=>assert.notEqual(universeDNA({worldSeed:'a'}).hash,universeDNA({worldSeed:'b'}).hash));
test('sensor normalization clamps channels',()=>{const p=normalizeSensorSummary({audioAvg:2,motion:-3,luminance:.5});assert.equal(p.audioAvg,1);assert.equal(p.motion,0);assert.equal(p.luminance,.5)});
