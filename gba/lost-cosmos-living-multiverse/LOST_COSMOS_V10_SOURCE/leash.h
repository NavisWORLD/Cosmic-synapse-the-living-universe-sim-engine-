/* V11.8 "remove the leash": the field companion roams on its own.
 *
 * LEASH OFF (default): the beast picks its own field goal from what it can
 * see (enemies, NPCs, visible points of interest, map cells it has not
 * walked), walks there along a breadth-first path over the real collision
 * map (walls and hazards are never entered), and comes back when called
 * (SYSTEM > CALL BEAST, or A on its FIELD RECORD page). It has no collision
 * with Arin, never uses a trigger, never sets a story/quest flag, and only
 * helps in a fight when it is within 72px of Arin.
 * LEASH ON: the original V11.7 follow behaviour (buddy_tick) is used.
 *
 * The LCL1 record counts what happened; it is a log, not a mind. */
#ifndef LC_LEASH_H
#define LC_LEASH_H
static u16 lf_dist[4096] LF_EWRAM;
static u16 lf_q[4096] LF_EWRAM;
static u8 lf_goal=LFG_IDLE,lf_called=0,lf_loc=255,lf_layer=255,lf_slot=0,lf_poi_n=0,lf_npc=255,lf_moving=0,lf_stepping=0,lf_greeted=0;
static u16 lf_alerted=0,lf_wait=0,lf_far=0,lf_goal_t=0,lf_target=0,lf_poi_pick=0,lf_frames=0,lf_poi_done[16];
static s16 lf_nx,lf_ny;
static u32 lf_rng=0x2545F491u;
#ifdef QA_AUTORUN
static u32 qa_lf_wall_frames=0,qa_lf_ticks=0;
#endif
static u8 lf_rand(void){lf_rng=lf_rng*1664525u+1013904223u;return (u8)(lf_rng>>24);}
static int lf_pass(int t){return collision[t]==C_FREE;}
static int lf_tile(void){return ((cosmos.y>>3)<<6)|((cosmos.x>>3)&63);}
static int lf_ptile(void){return ((player.y>>3)<<6)|((player.x>>3)&63);}
static int lf_cell(int t){return (((t>>6)>>3)<<3)|((t&63)>>3);}
static u8 lf_loc_id(void){return current_world?(u8)(128+((current_world-1)<<4)+(current_room&15)):(u8)(current_room&127);}
static int lf_pdist(void){return iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y);}
static int leash_autonomous(void){return !leash_on&&!BH_IS_ROOM&&game_mode==MODE_SURFACE;}
static void lf_bfs(int r){int h=0,t=0,i;
 for(i=0;i<4096;i++)lf_dist[i]=0xFFFF;lf_dist[r]=0;lf_q[t++]=(u16)r;
 while(h<t){int c=lf_q[h++],x=c&63;u16 d=(u16)(lf_dist[c]+1);
  if(x>0&&lf_dist[c-1]==0xFFFF&&lf_pass(c-1)){lf_dist[c-1]=d;lf_q[t++]=(u16)(c-1);}
  if(x<63&&lf_dist[c+1]==0xFFFF&&lf_pass(c+1)){lf_dist[c+1]=d;lf_q[t++]=(u16)(c+1);}
  if(c>=64&&lf_dist[c-64]==0xFFFF&&lf_pass(c-64)){lf_dist[c-64]=d;lf_q[t++]=(u16)(c-64);}
  if(c<4032&&lf_dist[c+64]==0xFFFF&&lf_pass(c+64)){lf_dist[c+64]=d;lf_q[t++]=(u16)(c+64);}}}
static int lf_bits(const u8*m){int n=0,i;u8 b;for(i=0;i<8;i++)for(b=m[i];b;b&=(u8)(b-1))n++;return n;}
static void lf_enter_loc(u8 loc){int i,best=0,bn=999;
 for(i=0;i<LF_SLOTS;i++)if(lf_rec.slot_loc[i]==loc){lf_slot=(u8)i;return;}
 for(i=0;i<LF_SLOTS;i++){int n=lf_rec.slot_loc[i]==255?-1:lf_bits(lf_rec.slot_mask[i]);if(n<bn){bn=n;best=i;}}
 lf_slot=(u8)best;lf_rec.slot_loc[best]=loc;for(i=0;i<8;i++)lf_rec.slot_mask[best][i]=0;}
static int lf_cell_seen(int t){int c=lf_cell(t);return (lf_rec.slot_mask[lf_slot][c>>3]>>(c&7))&1;}
static void lf_mark(int t){int c=lf_cell(t);u8 b=(u8)(1u<<(c&7));
 if(!(lf_rec.slot_mask[lf_slot][c>>3]&b)){lf_rec.slot_mask[lf_slot][c>>3]|=b;lf_rec.cells++;leash_obs.cell_new=1;}}
static void lf_fav(void){int c=lf_cell(lf_tile()),i,low=0;
 for(i=0;i<LF_FAV;i++)if(lf_rec.fav_n[i]&&lf_rec.fav_loc[i]==lf_loc&&lf_rec.fav_cell[i]==c){if(lf_rec.fav_n[i]<65535u)lf_rec.fav_n[i]++;return;}
 for(i=1;i<LF_FAV;i++)if(lf_rec.fav_n[i]<lf_rec.fav_n[low])low=i;
 lf_rec.fav_loc[low]=lf_loc;lf_rec.fav_cell[low]=(u8)c;lf_rec.fav_n[low]=(u16)(lf_rec.fav_n[low]+1);}
static int lf_poi(int t){u8 v=trigger[t];return v&&v!=TR_SECRET&&v!=TR_ANOMALY;}
static int lf_poi_was(int p){int i;for(i=0;i<lf_poi_n;i++)if(lf_poi_done[i]==p)return 1;return 0;}
static void leash_room_reset(void){lf_goal=LFG_IDLE;lf_moving=lf_stepping=0;lf_poi_n=0;lf_greeted=0;lf_alerted=0;lf_wait=30;lf_far=0;lf_npc=255;}
static void leash_reset(void){u8*p=(u8*)&lf_rec;unsigned i;for(i=0;i<sizeof(lf_rec);i++)p[i]=0;
 for(i=0;i<LF_SLOTS;i++)lf_rec.slot_loc[i]=255;leash_on=0;lf_called=0;lf_loc=lf_layer=255;leash_room_reset();}
static void lf_go(u8 g,int target){lf_goal=g;lf_target=(u16)target;lf_goal_t=0;lf_bfs(target);lf_moving=1;}
static void lf_beside_player(void){int t=lf_ptile();cosmos.x=(s16)(((t&63)<<3)+4);cosmos.y=(s16)(((t>>6)<<3)+4);lf_stepping=0;}
static void lf_choose(void){int b=lf_tile(),i,d,best=-1;u16 bd=0xFFFF;
 if(lf_called){lf_go(LFG_RETURN,lf_ptile());return;}
 for(i=0;i<10;i++)if(enemies[i].active&&!(lf_alerted&(1u<<i))&&iabs(enemies[i].x-cosmos.x)+iabs(enemies[i].y-cosmos.y)<96){
  lf_alerted|=(u16)(1u<<i);lf_rec.encounters++;lf_go(LFG_ALERT,lf_ptile());return;}
 if(lf_far>=1200){lf_far=0;lf_go(LFG_CHECKIN,lf_ptile());return;}
 for(i=0;i<npc_count&&i<8;i++)if(npc_runtime[i].active&&!(lf_greeted&(1u<<i))&&iabs(npc_runtime[i].x-cosmos.x)+iabs(npc_runtime[i].y-cosmos.y)<96){
  lf_npc=(u8)i;lf_go(LFG_NPC,((npc_runtime[i].y>>3)<<6)|((npc_runtime[i].x>>3)&63));return;}
 lf_bfs(b);
 if(lf_poi_n<16){for(i=0;i<4096;i++){int p=-1;d=lf_dist[i];if(d==0xFFFF||d>40||d>=bd)continue;
   if(lf_poi(i))p=i;else if((i&63)>0&&lf_poi(i-1))p=i-1;else if((i&63)<63&&lf_poi(i+1))p=i+1;else if(i>=64&&lf_poi(i-64))p=i-64;else if(i<4032&&lf_poi(i+64))p=i+64;
   if(p<0||lf_poi_was(p))continue;bd=(u16)d;best=i;lf_poi_pick=(u16)p;}
  if(best>=0){lf_poi_done[lf_poi_n++]=lf_poi_pick;lf_go(LFG_POI,best);return;}}
 if(cosmos.energy<60){int fi=-1;
  for(i=0;i<LF_FAV;i++)if(lf_rec.fav_n[i]&&lf_rec.fav_loc[i]==lf_loc&&(fi<0||lf_rec.fav_n[i]>lf_rec.fav_n[fi]))fi=i;
  if(fi>=0){int c=lf_rec.fav_cell[fi],x0=(c&7)<<3,y0=(c>>3)<<3,x,y;
   for(y=y0;y<y0+8;y++)for(x=x0;x<x0+8;x++){d=lf_dist[(y<<6)|x];if(d<bd){bd=(u16)d;best=(y<<6)|x;}}}
  lf_go(LFG_REST,best>=0?best:b);return;}
 for(i=0;i<4096;i++){d=lf_dist[i];if(d==0xFFFF||d<3||d>48||d>=bd||lf_cell_seen(i))continue;bd=(u16)d;best=i;}
 if(best>=0){lf_go(LFG_EXPLORE,best);return;}
 {int n=0,pick=lf_rand()&31;for(i=0;i<4096;i++){d=lf_dist[i];if(d>=4&&d<=12){best=i;if(n++>=pick)break;}}}
 if(best>=0)lf_go(LFG_IDLE,best);else{lf_goal=LFG_IDLE;lf_moving=0;lf_wait=90;}}
static void lf_complete(void){u8 g=lf_goal;lf_rec.done[g]++;lf_moving=0;lf_wait=40;
 if(g==LFG_POI){lf_rec.pois++;lf_fav();lf_wait=60;}
 else if(g==LFG_NPC){lf_rec.npcs++;lf_greeted|=(u8)(1u<<lf_npc);lf_fav();lf_wait=90;}
 else if(g==LFG_RETURN){if(lf_called){lf_rec.returns++;lf_called=0;}lf_wait=180;}
 else if(g==LFG_CHECKIN){lf_rec.checkins++;lf_wait=90;}
 else if(g==LFG_REST){lf_fav();lf_wait=180;}
 else if(g==LFG_EXPLORE)lf_wait=12;
 lf_goal=g==LFG_REST?LFG_REST:LFG_IDLE;}
static void lf_observe(void){int i,d,bt=lf_tile(),bx=bt&63,by=bt>>6,x,y;volatile LfObs*o=&leash_obs;
 o->version=1;o->leash_on=leash_on;o->called=lf_called;o->goal=lf_goal;o->loc=lf_loc;o->energy=cosmos.energy;
 o->beast_tx=(u8)bx;o->beast_ty=(u8)by;o->player_tx=(u8)((player.x>>3)&63);o->player_ty=(u8)((player.y>>3)&63);
 o->enemy_dist=o->npc_dist=255;
 for(i=0;i<10;i++)if(enemies[i].active){d=(iabs(enemies[i].x-cosmos.x)+iabs(enemies[i].y-cosmos.y))>>3;if(d<=12&&d<o->enemy_dist)o->enemy_dist=(u8)d;}
 for(i=0;i<npc_count;i++)if(npc_runtime[i].active){d=(iabs(npc_runtime[i].x-cosmos.x)+iabs(npc_runtime[i].y-cosmos.y))>>3;if(d<=12&&d<o->npc_dist)o->npc_dist=(u8)d;}
 if((frame&7)==0){o->poi_dist=255;for(y=by-12;y<=by+12;y++)for(x=bx-12;x<=bx+12;x++){if(x<0||y<0||x>63||y>63)continue;d=iabs(x-bx)+iabs(y-by);if(d<=12&&d<o->poi_dist&&lf_poi((y<<6)|x))o->poi_dist=(u8)d;}}
 for(i=0;i<25;i++){x=bx+(i%5)-2;y=by+(i/5)-2;o->sight[i]=(u8)((x<0||y<0||x>63||y>63)?1:collision[(y<<6)|x]);}}
static void leash_tick(void){int t,c,d,i,speed;u8 loc=lf_loc_id();
 if(loc!=lf_loc||current_layer!=lf_layer){lf_loc=loc;lf_layer=current_layer;lf_enter_loc(loc);leash_room_reset();
  if(!lf_pass(lf_tile())||lf_pdist()>48)lf_beside_player();}
 leash_obs.cell_new=0;
 if(++lf_frames>=60){lf_frames=0;lf_rec.secs++;}
 if(lf_pdist()>160)lf_far++;else lf_far=0;
 if(lf_moving&&(frame&31)==0&&cosmos.energy)cosmos.energy--;
 t=lf_tile();
 if(!lf_stepping&&((cosmos.x&7)!=4||(cosmos.y&7)!=4)){
  if(lf_pass(t)){lf_nx=(s16)(((t&63)<<3)+4);lf_ny=(s16)(((t>>6)<<3)+4);lf_stepping=1;}else lf_beside_player();}
 if(lf_stepping){speed=lf_called?2:1;
  if(cosmos.x<lf_nx)cosmos.x=(s16)mini(lf_nx,cosmos.x+speed);else if(cosmos.x>lf_nx)cosmos.x=(s16)maxi(lf_nx,cosmos.x-speed);
  else if(cosmos.y<lf_ny)cosmos.y=(s16)mini(lf_ny,cosmos.y+speed);else if(cosmos.y>lf_ny)cosmos.y=(s16)maxi(lf_ny,cosmos.y-speed);
  if(cosmos.x==lf_nx&&cosmos.y==lf_ny){lf_stepping=0;lf_rec.moves_ok++;lf_mark(lf_tile());}
  lf_observe();return;}
 if(lf_wait){lf_wait--;if(lf_goal==LFG_REST&&(frame&1)&&cosmos.energy<240)cosmos.energy++;if(lf_called){lf_wait=0;}lf_observe();return;}
 if(!lf_moving){lf_choose();lf_observe();return;}
 lf_goal_t++;
 if(lf_goal==LFG_RETURN||lf_goal==LFG_ALERT||lf_goal==LFG_CHECKIN){
  if(lf_pdist()<=20){lf_complete();lf_observe();return;}
  if((lf_goal_t&15)==0&&lf_ptile()!=lf_target){lf_target=(u16)lf_ptile();lf_bfs(lf_target);}
  if(lf_called&&lf_goal_t>=300){lf_beside_player();lf_rec.catchups++;lf_complete();lf_observe();return;}}
 else if(lf_goal==LFG_NPC){NPC*n=&npc_runtime[lf_npc<6?lf_npc:0];
  if(lf_npc>=npc_count||!n->active){lf_moving=0;lf_goal=LFG_IDLE;lf_observe();return;}
  if(iabs(n->x-cosmos.x)+iabs(n->y-cosmos.y)<=16){lf_complete();lf_observe();return;}
  c=((n->y>>3)<<6)|((n->x>>3)&63);if((lf_goal_t&31)==0&&c!=lf_target){lf_target=(u16)c;lf_bfs(c);}}
 else if(t==lf_target){lf_complete();lf_observe();return;}
 if(lf_goal_t>900){lf_moving=0;lf_goal=LFG_IDLE;lf_wait=30;lf_observe();return;}
 d=lf_dist[t];
 if(d==0xFFFF){lf_rec.no_path++;
  if(lf_called&&lf_goal==LFG_RETURN){if(lf_goal_t>=120){lf_beside_player();lf_rec.catchups++;lf_complete();}}
  else{lf_moving=0;lf_goal=LFG_IDLE;lf_wait=30;}
  lf_observe();return;}
 {static const s8 ox[4]={1,-1,0,0},oy[4]={0,0,1,-1};int s=lf_rand()&3,k;c=-1;
  for(k=0;k<4;k++){int j=(s+k)&3,x=(t&63)+ox[j],y=(t>>6)+oy[j],n;if(x<0||y<0||x>63||y>63)continue;n=(y<<6)|x;
   if(lf_dist[n]==d-1){c=n;break;}}
  if(c<0||(!lf_pass(c)&&c!=lf_target)){lf_rec.moves_blocked++;lf_bfs(lf_target);}
  else if(!lf_pass(c)){lf_complete();} /* the goal tile itself is solid: standing next to it is arriving */
  else{lf_nx=(s16)(((c&63)<<3)+4);lf_ny=(s16)(((c>>6)<<3)+4);lf_stepping=1;}}
 (void)i;lf_observe();}
static void leash_call(void){if(leash_on)return;lf_rec.calls++;lf_called=1;lf_wait=0;lf_moving=0;lf_goal=LFG_IDLE;}
static void leash_toggle(void){leash_on^=1;if(leash_on){cosmos.x=(s16)(player.x+14);cosmos.y=(s16)(player.y-10);lf_called=0;}else{lf_loc=255;}save_game();}
static void lf_w16(u8*b,int o,u16 v){b[o]=(u8)v;b[o+1]=(u8)(v>>8);}
static void lf_w32(u8*b,int o,u32 v){lf_w16(b,o,(u16)v);lf_w16(b,o+2,(u16)(v>>16));}
static u16 lf_r16(const u8*b,int o){return (u16)(b[o]|(b[o+1]<<8));}
static u32 lf_r32(const u8*b,int o){return (u32)lf_r16(b,o)|((u32)lf_r16(b,o+2)<<16);}
static u32 lf_crc(const u8*b){u32 c=0xffffffffu;int i;for(i=0;i<LF_BYTES;i++)c=(c>>8)^journal_crc_table[(c^b[i])&255u];return c^0xffffffffu;}
static void leash_save(void){u8 b[LF_BYTES];int i;const u16*w=&lf_rec.cells;
 for(i=0;i<LF_BYTES;i++)b[i]=0;
 b[0]='L';b[1]='C';b[2]='L';b[3]='1';b[4]=1;b[5]=(u8)((leash_on&1)|(lf_rec.flags&2));
 lf_w32(b,8,lf_rec.moves_ok);lf_w32(b,12,lf_rec.moves_blocked);
 for(i=0;i<10;i++)lf_w16(b,16+i*2,w[i]);
 for(i=0;i<LFG_COUNT;i++)lf_w16(b,36+i*2,lf_rec.done[i]);
 for(i=0;i<LF_FAV;i++){b[52+i]=lf_rec.fav_loc[i];b[60+i]=lf_rec.fav_cell[i];lf_w16(b,68+i*2,lf_rec.fav_n[i]);}
 for(i=0;i<LF_SLOTS;i++){int j;b[88+i]=lf_rec.slot_loc[i];for(j=0;j<8;j++)b[136+i*8+j]=lf_rec.slot_mask[i][j];}
 lf_w32(b,84,lf_crc(b));
 for(i=0;i<LF_BYTES;i++)SRAM[LF_SRAM+i]=b[i];}
static void leash_restore(void){u8 b[LF_BYTES];int i;u32 got;u16*w=&lf_rec.cells;
 for(i=0;i<LF_BYTES;i++)b[i]=SRAM[LF_SRAM+i];
 got=lf_r32(b,84);b[84]=b[85]=b[86]=b[87]=0;
 leash_reset();
 if(b[0]!='L'||b[1]!='C'||b[2]!='L'||b[3]!='1'||b[4]!=1||lf_crc(b)!=got){lf_rec.flags=2;return;} /* older save: new empty record, LEASH OFF */
 leash_on=b[5]&1;lf_rec.flags=b[5]&2;
 lf_rec.moves_ok=lf_r32(b,8);lf_rec.moves_blocked=lf_r32(b,12);
 for(i=0;i<10;i++)w[i]=lf_r16(b,16+i*2);
 for(i=0;i<LFG_COUNT;i++)lf_rec.done[i]=lf_r16(b,36+i*2);
 for(i=0;i<LF_FAV;i++){lf_rec.fav_loc[i]=b[52+i];lf_rec.fav_cell[i]=b[60+i];lf_rec.fav_n[i]=lf_r16(b,68+i*2);}
 for(i=0;i<LF_SLOTS;i++){int j;lf_rec.slot_loc[i]=b[88+i];for(j=0;j<8;j++)lf_rec.slot_mask[i][j]=b[136+i*8+j];}}
/* ---------- display ---------- */
static const char*const LF_GOAL_NAMES[LFG_COUNT]={"LOOKING AROUND","EXPLORING","SNIFFING A SPOT","MEETING SOMEONE","WARNING YOU","RESTING","COMING BACK","CHECKING IN"};
static void lf_fav_line(int row,int rank){int i,j,idx[3]={-1,-1,-1};
 for(j=0;j<3;j++)for(i=0;i<LF_FAV;i++){if(!lf_rec.fav_n[i]||i==idx[0]||i==idx[1])continue;if(idx[j]<0||lf_rec.fav_n[i]>lf_rec.fav_n[idx[j]])idx[j]=i;}
 i=idx[rank];if(i<0){ui_text(2,row,"-",15);return;}
 if(lf_rec.fav_loc[i]<128){ui_text(2,row,"ROOM",13);ui_num(7,row,lf_rec.fav_loc[i],15);}
 else{ui_text(2,row,"WORLD",13);ui_num(8,row,((lf_rec.fav_loc[i]-128)>>4)+1,15);}
 ui_text(12,row,"CELL",13);ui_num(17,row,lf_rec.fav_cell[i],15);ui_text(21,row,"X",13);ui_num(23,row,lf_rec.fav_n[i],15);}
static void leash_draw_record(void){
 ui_text(2,4,"LEASH",13);ui_text(8,4,leash_on?"ON  FOLLOWS ARIN":"OFF  ROAMS ALONE",15);
 ui_text(2,5,"NOW",13);ui_text(6,5,leash_on?"FOLLOWING":LF_GOAL_NAMES[lf_goal<LFG_COUNT?lf_goal:0],14);
 ui_text(2,6,"CELLS",13);ui_num(8,6,lf_rec.cells,15);ui_text(14,6,"STEPS",13);ui_num(20,6,(int)(lf_rec.moves_ok>60000u?60000u:lf_rec.moves_ok),15);
 ui_text(2,7,"BLOCKED",13);ui_num(10,7,(int)(lf_rec.moves_blocked>60000u?60000u:lf_rec.moves_blocked),15);ui_text(14,7,"NO PATH",13);ui_num(22,7,lf_rec.no_path,15);
 ui_text(2,8,"SPOTS",13);ui_num(8,8,lf_rec.pois,15);ui_text(12,8,"NPC",13);ui_num(16,8,lf_rec.npcs,15);ui_text(20,8,"ENC",13);ui_num(24,8,lf_rec.encounters,15);
 ui_text(2,9,"CALLS",13);ui_num(8,9,lf_rec.calls,15);ui_text(12,9,"BACK",13);ui_num(17,9,lf_rec.returns,15);ui_text(20,9,"HOP",13);ui_num(24,9,lf_rec.catchups,15);
 ui_text(2,10,"GOALS DONE",13);ui_num(13,10,lf_rec.done[LFG_EXPLORE]+lf_rec.done[LFG_POI]+lf_rec.done[LFG_NPC]+lf_rec.done[LFG_ALERT]+lf_rec.done[LFG_REST]+lf_rec.done[LFG_RETURN]+lf_rec.done[LFG_CHECKIN],15);
 ui_text(2,11,"FAVORITE SPOTS",14);lf_fav_line(12,0);lf_fav_line(13,1);lf_fav_line(14,2);
 ui_text(2,17,"A CALL BEAST  B BACK      ",13);}
#endif
