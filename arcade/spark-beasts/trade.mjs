/**
 * Spark beasts travel in the existing Lost Cosmos .qbeast share.
 * The recipe fits the 64-character seed. Stats and the public id are rebuilt
 * by the cage. Anti-dupe stays in the Synapse OS ledger.
 */
import { beastProfile, buildGrowth, buildSave, attachGrowth } from '../lost-cosmos/mailbox.mjs';
import { encodeTicket, importPayload, openShare, sealShare, ticketLink } from '../lost-cosmos/qbeast.mjs?sites=digest43';
import { admit, cageSave, emptyLedger, loadLedger, releaseForTrade, saveLedger } from '../lost-cosmos/synapse-os.mjs';
import { buildGenome } from './genome.mjs';
import { stageFromXp } from './store.mjs';

export const ISLAND_FAMILY = {
  'Eridoria Prime': 'aurora',
  'Hollow Verdance': 'memory',
  'The Crown': 'starlight',
  'The Pale Expanse': 'nebula',
  'Rust Meridian': 'signal',
  'Cinder Drift': 'plasma',
  'Umbral Deep': 'void',
  'The Shattered Reef': 'aurora',
};

export function sanitizeName(name) {
  const clean = String(name || '').toUpperCase().replace(/[^A-Z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 16);
  return clean || null;
}

export function recipeFor({ traits, runIndex, name }) {
  const base = `sb2|${traits.focus}|${traits.calm}|${traits.spark}|${runIndex}`;
  const recipe = name ? `${base}|${sanitizeName(name)}` : base;
  if (recipe.length > 64) throw new Error('That player name is too long for a trade ticket');
  return recipe;
}

export function parseRecipe(seed) {
  if (typeof seed !== 'string' || !seed.startsWith('sb2|')) return null;
  const parts = seed.split('|');
  if (parts.length < 5 || parts.length > 6) return null;
  const focus = Number(parts[1]);
  const calm = Number(parts[2]);
  const spark = Number(parts[3]);
  const runIndex = Number(parts[4]);
  if (![focus, calm, spark, runIndex].every((n) => Number.isInteger(n))) return null;
  return { focus, calm, spark, runIndex, name: parts[5] ? sanitizeName(parts[5]) : null };
}

export function xpFromGrowth(growth) {
  return Math.max(0, (growth?.layer || 0) * 1000 + (growth?.points || 0));
}

export function sparkRecord(genome, runIndex, xp = 0) {
  const traits = genome.inputs.traits;
  const name = sanitizeName(genome.inputs.user_id);
  const recipe = recipeFor({ traits, runIndex, name });
  const familyName = ISLAND_FAMILY[genome.island] || 'starlight';
  const hue = Math.max(-32, Math.min(31, Math.round((genome.genes.hue - 0.5) * 64)));
  const profile = beastProfile({ seed: recipe, familyName, hue, ...traits });
  const callsign = genome.names['1'].toUpperCase().replace(/[^A-Z0-9 ]/g, '').slice(0, 12) || profile.callsign;
  const kept = Math.max(0, xp | 0);
  return {
    origin: 'beast',
    seed: recipe,
    family: profile.family,
    familyName,
    speciesName: profile.speciesName,
    hue: profile.hue,
    ...traits,
    callsign,
    note: 'SPARK BEAST. RECORDED QUANTUM SEED.',
    profile: { ...profile, callsign },
    publicId: profile.publicId,
    growth: {
      epoch: '0',
      layer: Math.min(999, Math.floor(kept / 1000)),
      points: kept % 1000,
      trade: false,
      grown: kept > 0,
      memoryCrc: 0,
      chainCrc: 0,
    },
    memories: [`ISLAND ${genome.island}`.slice(0, 48)],
    transfer: null,
  };
}

export function genomeFromRecipe(seed, table) {
  const recipe = parseRecipe(seed);
  if (!recipe) return null;
  const run = table.runs[recipe.runIndex];
  if (!run) throw new Error('This spark ticket names a quantum run that is not in the local table');
  const genome = buildGenome({ focus: recipe.focus, calm: recipe.calm, spark: recipe.spark }, run, recipe.name);
  return { genome, recipe, run };
}

export function loadCage(storage) {
  return loadLedger(storage);
}

export function saveCage(ledger, storage) {
  saveLedger(ledger, storage);
}

export { emptyLedger, admit, releaseForTrade, sealShare, openShare, importPayload, encodeTicket, ticketLink, cageSave, buildSave, buildGrowth, attachGrowth };

export function stageOf(xp) {
  return stageFromXp(xp);
}
