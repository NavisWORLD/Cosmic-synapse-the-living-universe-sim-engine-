#!/usr/bin/env python3
"""Cross-language contract: browser previews are exact native 4bpp sprites."""
from pathlib import Path
import json, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
js=r'''
import fs from 'node:fs';
import {createBeast} from './arcade/sol-beast-lab/design.mjs';
import {renderSprite} from './arcade/sol-beast-lab/sprites.mjs';
const archive=new Uint8Array(JSON.parse(fs.readFileSync('arcade/sol-beast-lab/archive.json')).bytes);
let cases=[];
for(let island=0;island<8;island++)for(let stage=0;stage<3;stage++)for(let variant=0;variant<4;variant++){
 const b=createBeast({island,nonce:'CORY-SOL-'+variant,focus:variant*33,calm:100-variant*25,spark:variant*25},archive);
 for(let blink=0;blink<2;blink++)cases.push({seed:b.gameSeed,meta:b.meta,stage,blink,pixels:[...renderSprite(b,stage,blink).pixels]});
}
console.log(JSON.stringify(cases));
'''
cases=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=REPO,text=True))
with tempfile.TemporaryDirectory(prefix='sol-art-') as d:
 p=Path(d); (p/'test.c').write_text('#include <stdio.h>\n#include <stdlib.h>\n#include "sol_beast_art.h"\nint main(int n,char**v){if(n!=5)return 2;unsigned seed=strtoul(v[1],0,10),meta=strtoul(v[2],0,10);int s=atoi(v[3]),b=atoi(v[4]);for(int y=0;y<32;y++)for(int x=0;x<32;x++)putchar(sol_beast_pixel(x,y,seed,meta,s,b));return 0;}\n')
 subprocess.run(['gcc','-std=c99','-Wall','-Wextra','-Werror','-O2','-I',str(ROOT/'LOST_COSMOS_V10_SOURCE'),str(p/'test.c'),'-o',str(p/'test')],check=True)
 for c in cases:
  actual=subprocess.check_output([str(p/'test'),str(c['seed']),str(c['meta']),str(c['stage']),str(c['blink'])])
  assert actual==bytes(c['pixels']),f'Native/browser mismatch: {c["seed"]}/{c["stage"]}/{c["blink"]}'
print(f'PASS: {len(cases)} browser/native frames match exactly across eight islands, three stages, four genomes and two expressions.')
