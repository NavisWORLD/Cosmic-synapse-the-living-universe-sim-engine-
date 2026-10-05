/**
 * Play in Lost Cosmos. Builds the same 32 KB starter battery that Spark Gate
 * and the Beast Box dock hand to the V11.2 handheld: the LCX1 mailbox with the
 * beast's BCP1 profile, its LCG1 growth record, and SPK1 art for all three forms.
 * Nothing here is new cartridge format. It only chains the existing pieces.
 */
import { buildGenome } from './genome.mjs';
import { renderSprite } from './render.mjs';
import { spriteToGba } from './gba-tiles.mjs';
import { shownName, stageFromXp } from './store.mjs';
import { bindCage, stampRecord } from './care.mjs';
import { admit, attachGrowth, buildGrowth, buildSave, cageSave, sparkRecord, xpFromGrowth } from './trade.mjs';
import { attachFieldArt } from '../lost-cosmos/mailbox.mjs';
import { attachSparkArt, verifySparkArt } from '../sol-spark-gate/cartridge.mjs';

/** Link from a beast card or the spark result to the in-browser player. */
export function playPath(seed) {
  return `play.html?beast=${encodeURIComponent(String(seed || ''))}`;
}

export function pickBeast(store, seed) {
  const key = seed || store?.active;
  const beast = key && store?.beasts?.[key];
  if (!beast) throw new Error('That beast is not in the Spark ledger on this device. Spark or pick one on the Spark Beasts page first.');
  return beast;
}

/**
 * Rebuild the beast from its saved recipe, hold it in the shared cage ledger
 * (the same check as "Send to handheld"), then build the verified starter save.
 */
export async function preparePlay({ store, ledger, table, seed }) {
  const beast = pickBeast(store, seed);
  const run = table.runs[beast.runIndex];
  if (!run) throw new Error('This beast names a recorded run that is not in this copy of the table.');
  const genome = buildGenome(beast.traits, run, beast.userId);
  if (genome.seed !== beast.seed) throw new Error('This beast could not be rebuilt from its saved recipe.');
  const fresh = sparkRecord(genome, beast.runIndex, beast.xp);
  const id = fresh.publicId.toString(16).padStart(8, '0');
  const row = ledger.identities[id];
  if (row && !row.held) throw new Error(`${fresh.callsign} is out for trade. Import that share on the Spark Beasts page to bring the same beast back first.`);
  const admitted = await admit(ledger, fresh, 'local');
  if (!admitted.transfer) throw new Error('The cage did not accept this beast.');
  const carried = xpFromGrowth(admitted.growth);
  if (carried > (beast.xp || 0)) {
    beast.xp = carried;
    beast.stage = stageFromXp(beast.xp);
  }
  bindCage(store, genome.seed, admitted.publicHex || id);
  const record = stampRecord(admitted, beast);
  const stage = beast.stage || 1;
  let bytes = cageSave(record, buildSave, buildGrowth, attachGrowth);
  bytes = attachFieldArt(bytes, spriteToGba(renderSprite(genome, stage, { shadow: false })));
  bytes = attachSparkArt(bytes, genome, beast.runIndex, table);
  verifySparkArt(bytes);
  const species = genome.names[String(stage)] || genome.names['1'];
  return {
    beast,
    genome,
    record,
    bytes,
    stage,
    species,
    label: shownName(beast, species),
    callsign: record.callsign,
  };
}
