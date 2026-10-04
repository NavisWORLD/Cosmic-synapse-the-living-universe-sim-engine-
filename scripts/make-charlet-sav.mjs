/**
 * The owner's cage save: Phera, traits 30/30/30, recorded run 635, 40 XP.
 * admit() may change the growth trailer. The LCX1 body stays the cage record.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { buildGenome } from '../arcade/spark-beasts/genome.mjs';
import { sparkRecord } from '../arcade/spark-beasts/trade.mjs';
import { admit, cageSave, emptyLedger } from '../arcade/lost-cosmos/synapse-os.mjs';
import { attachGrowth, buildGrowth, buildSave } from '../arcade/lost-cosmos/mailbox.mjs';

const table = JSON.parse(readFileSync(new URL('../arcade/spark-beasts/data/quantum-runs.json', import.meta.url), 'utf8'));
const run = table.runs[635];
const genome = buildGenome({ focus: 30, calm: 30, spark: 30 }, run, 'Phera');
const record = sparkRecord(genome, 635, 40);
await admit(emptyLedger(), record, 'local');
const bytes = cageSave(record, buildSave, buildGrowth, attachGrowth);
writeFileSync(process.argv[2], bytes);
process.stdout.write(`${JSON.stringify({ callsign: record.callsign, species: record.speciesName, bytes: bytes.length })}\n`);
