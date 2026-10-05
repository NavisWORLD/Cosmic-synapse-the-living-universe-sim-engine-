import test from 'node:test';
import assert from 'node:assert/strict';
import {handleOptionalWakeLock} from './wake-lock.mjs';

test('optional native wake lock tolerates permission denial and preserves real success', async () => {
  const denied = {request: async () => { throw new DOMException('Denied', 'NotAllowedError'); }};
  handleOptionalWakeLock(denied);
  assert.equal(await denied.request('screen'), null);
  const sentinel = {release() {}}, allowed = {request: async type => { assert.equal(type, 'screen'); return sentinel; }};
  handleOptionalWakeLock(allowed);
  assert.equal(await allowed.request('screen'), sentinel);
  const broken = {request: async () => { throw new TypeError('Unexpected core failure'); }};
  handleOptionalWakeLock(broken);
  await assert.rejects(broken.request('screen'), /Unexpected core failure/);
  handleOptionalWakeLock(undefined);
});
