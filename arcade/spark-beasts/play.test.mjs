import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { buildGenome } from './genome.mjs';
import { emptyStore, rememberBeast } from './store.mjs';
import { emptyLedger, releaseForTrade, sparkRecord } from './trade.mjs';
import { pickBeast, playPath, preparePlay } from './play-save.mjs';
import { verifySparkArt } from '../sol-spark-gate/cartridge.mjs';
import { batteryName } from '../sol-spark-gate/battery.mjs';
import { MAILBOX_OFFSET } from '../lost-cosmos/mailbox.mjs';

const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const table = JSON.parse(read('./data/quantum-runs.json'));

function sparked(traits = { focus: 65, calm: 72, spark: 48 }, runIndex = 0, keeper = 'CORY') {
  const genome = buildGenome(traits, table.runs[runIndex], keeper);
  const store = emptyStore();
  rememberBeast(store, {
    seed: genome.seed, traits: genome.inputs.traits, runIndex, runKey: genome.inputs.quantum_run,
    userId: genome.inputs.user_id, origin: 'spark', island: genome.island, name: genome.names['1'], xp: 0, bond: 0,
  });
  return { genome, store, ledger: emptyLedger() };
}

test('Play in Lost Cosmos builds the verified Spark Gate starter save for that beast', async () => {
  const { genome, store, ledger } = sparked();
  store.beasts[genome.seed].displayName = 'Ember';
  const out = await preparePlay({ store, ledger, table, seed: genome.seed });
  assert.equal(out.bytes.length, 32768);
  assert.ok(verifySparkArt(out.bytes));
  const profile = sparkRecord(genome, 0).profile;
  assert.deepEqual([...out.bytes.subarray(MAILBOX_OFFSET + 32, MAILBOX_OFFSET + 96)], [...profile.bcp1]);
  assert.equal(new DataView(out.bytes.buffer).getUint32(MAILBOX_OFFSET + 10, true), profile.gameSeed);
  assert.equal(String.fromCharCode(...out.bytes.subarray(MAILBOX_OFFSET + 14, MAILBOX_OFFSET + 19)), 'EMBER');
  assert.match(batteryName(out.bytes), /^lost-cosmos-[0-9a-f]{8}-[0-9a-f]{8}$/);
  assert.equal(out.label, 'Ember');
  assert.ok(store.beasts[genome.seed].cageId);
  const again = await preparePlay({ store, ledger, table, seed: genome.seed });
  assert.equal(batteryName(again.bytes), batteryName(out.bytes));
});

test('Play in Lost Cosmos refuses a missing beast and a beast out for trade', async () => {
  const { genome, store, ledger } = sparked({ focus: 40, calm: 70, spark: 15 }, 1, null);
  assert.throws(() => pickBeast(store, 'nope'), /not in the Spark ledger/);
  const held = await preparePlay({ store, ledger, table, seed: genome.seed });
  await releaseForTrade(ledger, held.record);
  await assert.rejects(preparePlay({ store, ledger, table, seed: genome.seed }), /out for trade/);
});

test('the spark result and each bestiary card link to the player', () => {
  assert.equal(playPath('a|b'), 'play.html?beast=a%7Cb');
  const page = read('./app.mjs');
  const html = read('./index.html');
  const play = read('./play.html');
  assert.match(page, /Play in Lost Cosmos/);
  assert.match(page, /play\.html\?beast=/);
  assert.match(page, /cell\.append\(card, playLink\(beast\.seed\)\)/);
  assert.match(html, /id="play-lc"/);
  assert.match(html, /id="rare-gallery"/);
  assert.match(play, /Back to Spark Beasts/);
  assert.match(play, /sol-spark-gate|play\.mjs/);
  assert.match(play, /no live quantum link/);
  assert.doesNotMatch(play, /src="https?:/);
  assert.match(read('./play.mjs'), /\.\.\/sol-spark-gate\/handheld\.html/);
});
