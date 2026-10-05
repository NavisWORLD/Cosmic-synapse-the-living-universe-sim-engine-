import { buildGenome } from '../spark-beasts/genome.mjs';
import { importPayload, cageSave, buildSave, buildGrowth, attachGrowth } from '../spark-beasts/trade.mjs';
import { attachSparkArt } from './cartridge.mjs';

/** Accept the public Spark card exported by the current Vercel generator.
 * Existing QBEAST validation owns identity, digest and unsigned-progress rules. */
export async function readSparkFile(bytes,table) {
 if(!(bytes instanceof Uint8Array)||bytes.length>524288)throw new Error('Spark file is too large.');
 const value=JSON.parse(new TextDecoder().decode(bytes));
 const summary=value.events?.[0]?.payload?.summary;
 const card=/^Spark Beasts v1\. Recorded quantum seed, game companion\. traits=(\d+),(\d+),(\d+) bucket=10 run=([A-Za-z0-9:_#-]+) name=([A-Za-z0-9]+)(?: keeper=([A-Za-z0-9 ._-]{1,24}))?$/.exec(summary||'');
 if(value.format!=='QBEAST1'||!card)throw new Error('Choose a Spark Beasts .qbeast from the current generator.');
 const traits={focus:Number(card[1]),calm:Number(card[2]),spark:Number(card[3])};
 if(Object.values(traits).some(v=>v<0||v>100))throw new Error('Spark traits are outside 0–100.');
 const runIndex=table.runs.findIndex(r=>r.key===card[4]);if(runIndex<0)throw new Error('Recorded run is not in this cartridge table.');
 const genome=buildGenome(traits,table.runs[runIndex],card[6]||null);
 if(genome.seed!==value.profile?.seed||genome.names['2']!==card[5])throw new Error('The Spark card does not reproduce this creature.');
 const record=await importPayload(bytes,traits);
 if(record.seed!==genome.seed)throw new Error('Spark identity was rejected.');
 return {genome,record,runIndex};
}
export function checkedSparkSave({genome,record,runIndex},table){
 return attachSparkArt(cageSave(record,buildSave,buildGrowth,attachGrowth),genome,runIndex,table,record.seed===genome.seed?{record}:{});
}
