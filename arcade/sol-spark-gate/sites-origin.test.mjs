import test from 'node:test';
import assert from 'node:assert/strict';
import {isTrustedCloudOrigin} from './cloud-origin.mjs';
test('the existing Cory Sites origin can hand the Beast to the native cartridge',()=>{
 assert.equal(isTrustedCloudOrigin('https://beast-box-control-deck-cory.pheras-king.chatgpt.site'),true);
 assert.equal(isTrustedCloudOrigin('http://terminal.local:4173'),true);
 assert.equal(isTrustedCloudOrigin('https://evil.chatgpt.site'),false);
 assert.equal(isTrustedCloudOrigin('http://beast-box-control-deck-cory.pheras-king.chatgpt.site'),false);
});
