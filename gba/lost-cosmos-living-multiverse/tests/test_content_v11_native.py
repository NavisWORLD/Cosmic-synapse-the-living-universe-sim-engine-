#!/usr/bin/env python3
"""Exercise actual C content rules with simulated MMIO; separate from mGBA QA."""
from pathlib import Path
import os,subprocess
R=Path(__file__).resolve().parents[1];G=R/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=G,check=True,capture_output=True)
pre=(G/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
body=r'''
#include <assert.h>
#include <stdio.h>
static void fresh(void){init_new_game();intro=0;v10_opening=0;cinema_active=0;init_graphics();}
int main(void){int i,j,w,n;u8 prefix[256];fresh();
 assert(sizeof(Enemy)==16&&sizeof(NPC)==12);assert(v11_capacity()==40);
 for(i=0;i<100;i++)v11_qty[i]=0;
 for(i=0;i<40;i++)assert(v11_inventory_add(i,1));
 assert(!v11_inventory_add(40,1));assert(v11_inventory_add(0,1));assert(v11_qty[0]==2);
 v11_learn(69);v11_passives[0]=69;assert(v11_capacity()==60);assert(v11_inventory_add(40,1));
 fresh();v11_enter(0);assert(v11_qty[99]&&v11_equipment[0]==0);assert(v11_str()==5);
 v11_inventory_add(12,1);v11_equipment[0]=12;assert(v11_str()==10&&v11_mag()==6);
 for(w=0;w<8;w++){v11_enter(w);assert(current_room==70+w);int counts[10]={0};
  for(i=0;i<4096;i++)if(trigger[i]>=110&&trigger[i]<=119)counts[trigger[i]-110]++;
  fprintf(stderr,"world%d cache%d echo%d beacon%d camp%d exit%d next%d\n",w,counts[5],counts[7],counts[4],counts[3],counts[1],counts[2]);assert(counts[5]==4&&counts[7]==1&&counts[4]==1&&counts[3]==1&&counts[1]==1&&counts[2]==1);
  assert(counts[6]==(w==0||w==2||w==5||w==6?2:1));if(w==5)assert(counts[8]==3);
  /* Flood every legal 2px actor position, including the native 10px footprint. */
  static u8 seen[256*256];static u16 queue[256*256];for(i=0;i<65536;i++)seen[i]=0;
  int head=0,tail=1;queue[0]=(54*4)*256+32*4;seen[queue[0]]=1;
  while(head<tail){int q=queue[head++],x=(q%256)*2,y=(q/256)*2;int xs[4]={x-2,x+2,x,x},ys[4]={y,y,y-2,y+2};
   for(j=0;j<4;j++)if(xs[j]>=8&&xs[j]<=502&&ys[j]>=8&&ys[j]<=502&&can_stand(xs[j],ys[j])&&tile_collision_at(xs[j],ys[j])!=C_HAZARD){int at=(ys[j]/2)*256+xs[j]/2;if(!seen[at]){seen[at]=1;queue[tail++]=(u16)at;}}}
  for(i=0;i<4096;i++)if(trigger[i]>=111&&trigger[i]<=119){int tx=i%64,ty=i/64,ok=0,x,y;
   for(y=maxi(8,(ty-1)*8);y<mini(504,(ty+2)*8);y+=2)for(x=maxi(8,(tx-1)*8);x<mini(504,(tx+2)*8);x+=2)ok|=seen[(y/2)*256+x/2];assert(ok);}
  for(i=0;i<v11_npc_count;i++){int ok=0,x,y;for(y=maxi(8,v11_npc_y[i]-16);y<=mini(502,v11_npc_y[i]+16);y+=2)for(x=maxi(8,v11_npc_x[i]-16);x<=mini(502,v11_npc_x[i]+16);x+=2)if(iabs(x-v11_npc_x[i])+iabs(y-v11_npc_y[i])<28)ok|=seen[(y/2)*256+x/2];assert(ok);}
 }
 puts("PASS all eight regions retain every pickup, camp, beacon and reachable NPC");
 v11_enter(5);near_trigger_x=28;v11_field_interact(TR_V11_FORGE);n=v11_scrap;v11_field_interact(TR_V11_FORGE);assert(v11_scrap==n);
 v11_enter(0);near_trigger_x=32;near_trigger_y=10;v11_field_interact(TR_V11_CORE);n=v11_qty[93];v11_field_interact(TR_V11_CORE);assert(v11_qty[93]==n);
 fresh();v11_enter(0);v11_enemy_id[9]=90;v11_enemy_hp[9]=v11_enemy_max[9]=600;enemies[9].active=1;v11_start_battle(9);assert(v11_enemy_hp[9]==600);v11_damage_target(100,0,0,0);assert(v11_enemy_hp[9]==500);
 v11_learn(1);v11_mp=0;v11_free_cast=1;v11_status=VS_SILENCE;assert(!v11_use_skill(1)&&v11_free_cast);v11_status=0;assert(v11_use_skill(1)&&!v11_free_cast&&v11_mp==0);
 v11_learn(33);v11_mp=10;v11_fetch_used=0;assert(v11_use_skill(33));n=v11_qty[70];assert(!v11_use_skill(33)&&v11_qty[70]==n);
 v11_learn(86);v11_mp=100;v11_ult_charge=100;v11_hp=17;assert(v11_use_skill(86));v11_take_hit(10);assert(v11_hp==7);v11_take_hit(999);assert(v11_hp==1);
 v11_enemy_id[9]=95;v11_enemy_hp[9]=200;v11_enemy_max[9]=620;v11_phase=0;v11_status=0;v11_hp=100;v11_turn_end();assert(v11_status&VS_FREEZE);
 game_mode=MODE_SURFACE;v11_hp=17;v11_credits=444;v11_cosmos_stage=1;copystr(v11_cosmos_name,"STAY",12);save_game();
 for(i=0;i<256;i++)prefix[i]=SRAM[i];v11_save();for(i=0;i<256;i++)assert(SRAM[i]==prefix[i]);v11_hp=1;v11_credits=0;v11_restore();assert(v11_hp==17&&v11_credits==444&&v11_cosmos_stage==1&&!v11_compare_name(v11_cosmos_name,"STAY"));
 v11_slot_save(0);assert(v11_slot_valid(0));v11_credits=666;v11_slot_save(1);assert(v11_slot_valid(1));assert(v11_slot_load(0)&&v11_credits==444);assert(v11_slot_load(1)&&v11_credits==666);
 SRAM[25600+32+400]^=1;assert(!v11_slot_valid(0));n=v11_credits;assert(!v11_slot_load(0)&&v11_credits==n);
 SRAM[25600+2048+31]=0;assert(!v11_slot_valid(1));v11_slot_save(2);assert(v11_slot_valid(2));
 SRAM[6400+30]^=1;v11_restore();assert(current_room==2&&v11_credits==credits);
 fresh();assert(v11_prepare_export(0));assert(v11_export_valid());u8 profile[64];for(i=0;i<64;i++)profile[i]=SRAM[6224+i];LcProfile p;assert(lc_parse_bcp1(profile,64,&p)==LC_OK);assert(p.public_id==0x43534d53u);SRAM[6250]^=1;assert(!v11_export_valid());
#if defined(LC_IMPORT_HAS_BCP1)
 fresh();assert(v11_snapshot_valid());assert(lc_party.count==1&&lc_party.slots[0].identity==0xf5a4cb6du);
 lc_party.slots[0].bond=75;lc_party.slots[0].level=12;assert(v11_prepare_export(1));assert(v11_export_valid());
 for(i=0;i<64;i++)profile[i]=SRAM[6224+i];assert(lc_parse_bcp1(profile,64,&p)==LC_OK&&p.public_id==0xf5a4cb6du);
 assert(lc_release_wild(&lc_party,0)!=LC_OK);assert(v11_import_snapshot());assert(lc_party.count==1&&lc_party.slots[0].bond==75);
#endif
 puts("PASS finite resources, wide boss HP, ability limits, frozen saves, three CRC slots, public export");
 return 0;
}
'''
src=G/'content_v11_test_host.c';src.write_text(pre+body)
exe=G/'content_v11_test_host'
subprocess.run([os.environ.get('LC_HOST_CC','gcc'),'-DQA_AUTORUN','-DHOST_QA','-O2',str(src),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
subprocess.run([os.environ.get('LC_HOST_CC','gcc'),'-DQA_AUTORUN','-DHOST_QA','-DLC_IMPORTED_COMPANION','-O2',str(src),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
