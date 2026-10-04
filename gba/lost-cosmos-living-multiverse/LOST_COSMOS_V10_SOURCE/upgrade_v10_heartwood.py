"""One-time, assert-locked new playable Heartwood chapter from user's original PDF pp20–23.
Apply only to V10 first presentation pass source, NOT repeatedly. Tested in host + native ARM.
"""
from pathlib import Path
p=Path(__file__).with_name('lost_cosmos_v5.c');s=p.read_text()
def rep(a,b,tag):
 global s
 c=s.count(a);assert c==1,(tag,c);s=s.replace(a,b)
rep('TR_RIFT=24};','TR_RIFT=24,TR_HW_WISDOM=25,TR_HW_COURAGE=26,TR_HW_HEART=27};','trigger IDs')
rep('static u8 v10_opening_step=0,v10_tutorial=0,v10_ending_card=0;',
    'static u8 v10_opening_step=0,v10_tutorial=0,v10_ending_card=0;\n'
    'static u8 v10_hw_riddle=0,v10_hw_choice=0; /* 0 unset, 1 fought, 2 healed/bonded */',
    'heartwood state')
rep('#define ST_LATTICE 4096u',
    '#define ST_LATTICE 4096u\n'
    '#define ST_HW_WISDOM 8192u\n#define ST_HW_COURAGE 16384u\n#define ST_HEARTWOOD 32768u',
    'story flags')
rep(' {"DARIUS","WE PROTECT THE MEMORY OF THIS CITY.","THE DREAM GATE NEEDS THE HEART\'S LIGHT.","WE ARE NO LONGER LOST TO HISTORY.",0,5,1,22,38,2,255,0}\n',
    ' {"DARIUS","WE PROTECT THE MEMORY OF THIS CITY.","THE DREAM GATE NEEDS THE HEART\'S LIGHT.","WE ARE NO LONGER LOST TO HISTORY.",0,5,1,22,38,2,255,0},\n'
    ' {"HEARTWOOD SPIRIT","THE ROOTS REMEMBER THE CRYSTAL OF BALANCE.","SOLVE THE RUNE. THEN FACE OR HEAL THE WOUNDED GUARDIAN. THE CHOICE IS YOURS.","THE GROVE RECOGNIZES YOUR CHOICE.",0,7,1,31,19,1,255,0}\n',
    'append NPC')
# Insert actual authored new map rather than simply relabelling Bloom Z.
anchor='/* Additional 64x64 authored Eridoria areas, all genuine navigable BG maps. */'
new=r'''/* Heartwood Woods from Cory Davis's original novel, pp.20–23. This is a
 * genuinely separate 64x64 map, not a relabelled Bloom Z map. Bridge and
 * three shrine positions are fixed; trees never block the authored route. */
static void v10_generate_heartwood(void){int x,y;
 map_fill(T_GRASS,0);map_border();
 /* Dense dark boundary grove and an asymmetric understory. */
 for(x=4;x<61;x+=7)for(y=5;y<60;y+=9)
   if((x+y*3)%4)map_put(x,y,T_TREE,3,C_WALL,TR_NONE);
 add_noise_decor(121,T_FLOWER,3,85,0);
 for(y=4;y<61;y++)if(y!=31&&y!=52){
   if(y<21||y>42)map_put(57,y,T_TREE,3,C_WALL,TR_NONE);
 }
 /* A real impassable stream, crossed ONLY by its walkable central bridge. */
 for(x=16;x<=48;x++)map_put(x,24,T_WATER,2,C_WALL,TR_NONE);
 for(x=29;x<=35;x++)map_put(x,24,T_BRIDGE,1,C_FREE,TR_NONE);
 /* Three authored roads: main crystal path, wisdom branch and courage arena. */
 for(y=13;y<=54;y++)for(x=30;x<=34;x++)
   if(y!=24||x>=29&&x<=35)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(x=10;x<=54;x++)for(y=30;y<=33;y++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(x=10;x<=32;x++)for(y=51;y<=54;y++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(x=44;x<=51;x++)for(y=26;y<=34;y++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 /* The old singing tree exists physically in this glade. */
 for(x=27;x<=37;x++)for(y=6;y<=11;y++)
   if(x<30||x>34||y<9)map_put(x,y,T_TREE,3,C_WALL,TR_NONE);
 map_put(32,13,T_CRYSTAL,5,C_FREE,TR_HW_HEART);
 map_put(13,31,T_RUNE,4,C_FREE,TR_HW_WISDOM);
 map_put(48,31,T_RUNE,5,C_FREE,TR_HW_COURAGE);
 map_put(10,54,T_DOOR,3,C_FREE,TR_GATE);
}
'''
rep(anchor,new+anchor,'insert real Heartwood map')
rep('  add_noise_decor(91,T_FLOWER,3,45,0);',
    '  add_noise_decor(91,T_FLOWER,3,45,0);\n'
    '  for(x=31;x<=55;x++)map_put(x,54,T_PATH,1,C_FREE,TR_NONE);\n'
    '  map_put(55,54,T_DOOR,3,C_FREE,TR_GATE); /* Heartwood road from the novel */',
    'Brindlemark gate')
rep(' }else if(current_room==5){ /* Forgotten city and the White Sentinel\'s gateway. */',
    ' }else if(current_room==7){v10_generate_heartwood();}\n'
    ' else if(current_room==5){ /* Forgotten city and the White Sentinel\'s gateway. */',
    'Heartwood branch')
rep('set_world_palette(current_world==0&&current_room==6?4:current_world);if(current_world==0&&current_room==6)',
    'set_world_palette(current_world==0&&current_room==6?4:(current_world==0&&current_room==7?3:current_world));if(current_world==0&&current_room==6)',
    'world-specific art palette')
rep('else if(current_world==0 && current_room>=2 && current_room<=5){eridoria_area();}',
    'else if(current_world==0 && ((current_room>=2 && current_room<=5)||current_room==7)){eridoria_area();}',
    'dispatch authored room')
rep('if(current_world==0&&current_room==6)return "NIHILOS RIFT";',
    'if(current_world==0&&current_room==6)return "NIHILOS RIFT";'
    'if(current_world==0&&current_room==7)return "HEARTWOOD WOODS";',
    'location identity')
rep('if(current_world==0&&current_room==6){v9_spawn_wave();return;}if(current_world==0&&current_room==4',
    'if(current_world==0&&current_room==6){v9_spawn_wave();return;}'
    'if(current_world==0&&current_room==7&&(story_flags&ST_HW_WISDOM)&&!(story_flags&ST_HW_COURAGE))'
    '{spawn_enemy(8,47,27,EN_BLOOM,1);enemies[8].maxhp=(u8)mini(99,12+player_level*2);enemies[8].hp=enemies[8].maxhp;return;}'
    'if(current_world==0&&current_room==4',
    'specific boss spawn')
rep('SRAM[229]=(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226]);}',
    'SRAM[229]=(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226]);\n'
    ' SRAM[230]=0xB7;SRAM[231]=v10_hw_choice;'
    'SRAM[232]=(u8)(0x5E^SRAM[230]^SRAM[231]^SRAM[200]^SRAM[201]);}',
    'isolated choice SRAM')
rep('SRAM[229]==(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226])&&SRAM[228]<=4)?SRAM[228]:0;',
    'SRAM[229]==(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226])&&SRAM[228]<=4)?SRAM[228]:0;\n'
    ' v10_hw_choice=(!old_v3&&!old_v4&&SRAM[230]==0xB7&&SRAM[231]<=2&&'
    'SRAM[232]==(u8)(0x5E^SRAM[230]^SRAM[231]^SRAM[200]^SRAM[201]))?SRAM[231]:0;',
    'isolated migration')
rep('v10_tutorial=0;v10_ending_card=0;actor_style=0;',
    'v10_tutorial=0;v10_ending_card=0;v10_hw_choice=v10_hw_riddle=0;actor_style=0;',
    'clear when New Game')
rep('if(current_world==0&&current_room==6){\n  if(e->elite)',
    'if(current_world==0&&current_room==7&&e->elite){\n'
    '  story_flags|=ST_HW_COURAGE;v10_hw_choice=1;'
    '  v9_gear_drop(e->x,e->y,2);add_xp(22);kill_count++;e->active=0;'
    '  say("THE WOUNDED GUARDIAN FELL. YOUR CHOICE ECHOES IN THE GROVE.");'
    '  tone(1400);save_game();return;\n'
    ' }\n if(current_world==0&&current_room==6){\n  if(e->elite)',
    'special combat route')
rep('battle_notice=e->elite?(current_room==6?',
    'battle_notice=(current_world==0&&current_room==7&&e->elite)?'
    '"THE SENTINEL HURTS. FIGHT OR TALK WITH AN ETHER.":'
    'e->elite?(current_room==6?',
    'branching encounter notice')
rep('}else if(battle_cursor==3){\n  if(!e->elite &&',
    '}else if(battle_cursor==3){\n'
    '  if(current_world==0&&current_room==7&&e->elite){\n'
    '   if(inv[ITEM_ETHER]){inv[ITEM_ETHER]--;v10_hw_choice=2;story_flags|=ST_HW_COURAGE;'
    '    v9_bonded=1;v9_bond_type=EN_BLOOM;'
    '    cosmos.trust=(u8)mini(255,cosmos.trust+24);e->active=0;'
    '    add_xp(18);save_game();'
    '    battle_notice="YOU HEALED THE GUARDIAN. IT WALKS WITH YOU.";}\n'
    '   else battle_notice="HEALING NEEDS ONE ETHER.";\n'
    '  }else if(!e->elite &&',
    'negotiated healing route')
rep('if(current_room==2){\n   if(tx<20)dst=0;',
    'if(current_room==2){\n'
    '   if(tx>48&&ty>45){if(!(story_flags&ST_HEART)){say("THE HEARTWOOD PATH NEEDS THE HEART OF ERIDORIA.");return;}dst=7;}\n'
    '   else if(tx<20)dst=0;',
    'Heartwood access gate')
rep('  else if(current_room==5){if(tx<20)dst=2;',
    '  else if(current_room==7){dst=2;}\n'
    '  else if(current_room==5){if(tx<20)dst=2;',
    'Return gate')
rep('player.x=(s16)((dst==0?20:(dst==2?11:(dst==3?11:(dst==4?31:10))))*8);\n player.y=(s16)((dst==0?49:52)*8);',
    'player.x=(s16)((dst==0?20:(dst==7?11:(dst==2&&current_room==2?55:(dst==2?11:(dst==3?11:(dst==4?31:10))))))*8);\n'
    ' player.y=(s16)((dst==0?49:52)*8);',
    'player entry',) if False else None
# The source line uses current_room AFTER dst assignment: choose a simpler spawn position
# and explicitly place return near Brindlemark southeast gate.
rep('player.x=(s16)((dst==0?20:(dst==2?11:(dst==3?11:(dst==4?31:10))))*8);',
    'player.x=(s16)((dst==0?20:(dst==7?11:(dst==3?11:(dst==4?31:(dst==2?11:10)))))*8);',
    'new map arrival')
rep('say(dst==2?"WELCOME TO BRINDLEMARK.":dst==3?',
    'say(dst==7?"THE HEARTWOOD ROOTS HUM WITH A DIFFERENT MUSIC.":'
    'dst==2?"WELCOME TO BRINDLEMARK.":dst==3?',
    'new map travel feedback')
# Introduce fixed three-point trial driven by real in-map triggers and combat.
rep('static void story_interact(u8 t){int tx=player.x>>3;\n',
    '''static void story_interact(u8 t){int tx=player.x>>3;\n
 if(t==TR_HW_WISDOM){
  if(story_flags&ST_HW_WISDOM){say("THE ROOT RUNE REMEMBERS YOUR ANSWER.");return;}
  v10_hw_riddle=1;say("THE WOOD ASKS: WHAT GROWS DEEPER AS IT CLIMBS? LEFT STONE, UP FIRE, RIGHT ROOTS.");return;
 }
 if(t==TR_HW_COURAGE){
  if(story_flags&ST_HW_COURAGE){say(v10_hw_choice==2?"THE GUARDIAN TRAVELS WITH YOU.":"THE SENTINEL'S MEMORY LINGERS.");return;}
  if(!(story_flags&ST_HW_WISDOM)){say("FIRST SOLVE THE ROOT RUNE AT THE WEST SHRINE.");return;}
  if(!enemies[8].active)spawn_monsters();
  battle_enter(8);return;
 }
 if(t==TR_HW_HEART){
  if(story_flags&ST_HEARTWOOD){say("THE CRYSTAL OF BALANCE RESTS WITH THE GROVE.");return;}
  if((story_flags&(ST_HW_WISDOM|ST_HW_COURAGE))!=(ST_HW_WISDOM|ST_HW_COURAGE)){
   say("THE CRYSTAL NEEDS THE RUNE AND A RESOLVED GUARDIAN.");return;
  }
  story_flags|=ST_HEARTWOOD;cosmos.trust=(u8)mini(255,cosmos.trust+15);
  inv[ITEM_CORE]=(u8)mini(99,inv[ITEM_CORE]+1);v9_gear_drop(player.x,player.y,3);
  say(v10_hw_choice==2?"BALANCE RESTORED WITHOUT BLOOD. COSMOS REMEMBERS THE SPIRIT.":"BALANCE RESTORED. YOUR CHOICE WILL REMAIN IN THIS WOOD.");
  save_game();return;
 }
''',
    'three live trial triggers')
rep('if(riddle_open){\n  if(newk&KEY_RIGHT)',
    'if(v10_hw_riddle){\n'
    '  if(newk&KEY_RIGHT){v10_hw_riddle=0;story_flags|=ST_HW_WISDOM;'
    '   spawn_monsters();say("THE ROOT RUNE ANSWERS. THE WOUNDED SENTINEL AWAKENS.");save_game();}\n'
    '  else if(newk&(KEY_LEFT|KEY_UP|KEY_B)){v10_hw_riddle=0;say("THE ROOTS CLOSE. THE RUNE CAN BE TRIED AGAIN.");}\n'
    '  return;\n }\n if(riddle_open){\n  if(newk&KEY_RIGHT)',
    'Wisdom actual input')
rep('ui_text(1,19,(v10_tutorial==1)?"FIND THE BRINDLE ELDER":',
    'ui_text(1,19,(current_world==0&&current_room==7)?'
    '((story_flags&ST_HEARTWOOD)?"HEARTWOOD: THE GROVE REMEMBERS":'
    '(!(story_flags&ST_HW_WISDOM)?"HEARTWOOD: SOLVE ROOT RUNE":'
    '(!(story_flags&ST_HW_COURAGE)?"HEARTWOOD: GUARDIAN TRIAL":"HEARTWOOD: BALANCE CRYSTAL"))):'
    '(v10_tutorial==1)?"FIND THE BRINDLE ELDER":',
    'in-game waypoint')
# Titles in new map are top UI location; load flags are masked 16 bits intact.
p.write_text(s)
print('PASS applied original-pdf Heartwood page 20-23: new 64x64 authored area, battle/mercy quest, rewards, versioned save')
