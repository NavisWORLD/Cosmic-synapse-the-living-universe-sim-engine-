import test from 'node:test';
import assert from 'node:assert/strict';
import {isTrustedCloudOrigin} from './cloud-origin.mjs';

test('production and local Beast Box origins remain trusted',()=>{
 for(const origin of [
  'https://beastboxcosmos.xyz',
  'https://www.beastboxcosmos.xyz',
  'http://127.0.0.1:3000',
  'http://localhost:3000',
 ]) assert.equal(isTrustedCloudOrigin(origin),true,origin);
});

test('only this Beast Box Vercel project preview pattern is trusted',()=>{
 assert.equal(isTrustedCloudOrigin('https://the-beast-box-op840rza5-zerefs-end.vercel.app'),true);
 assert.equal(isTrustedCloudOrigin('https://the-beast-box-git-main-zerefs-end.vercel.app'),true);
 assert.equal(isTrustedCloudOrigin('https://other-project-op840rza5-zerefs-end.vercel.app'),false);
 assert.equal(isTrustedCloudOrigin('http://the-beast-box-op840rza5-zerefs-end.vercel.app'),false);
 assert.equal(isTrustedCloudOrigin('https://the-beast-box-op840rza5-zerefs-end.vercel.app.evil.example'),false);
 assert.equal(isTrustedCloudOrigin('https://evil.example'),false);
 assert.equal(isTrustedCloudOrigin('not-an-origin'),false);
});
