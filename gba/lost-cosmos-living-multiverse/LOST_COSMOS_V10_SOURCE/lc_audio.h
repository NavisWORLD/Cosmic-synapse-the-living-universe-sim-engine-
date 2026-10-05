/* Lost Cosmos sound: an original PSG chiptune sequencer and effect set.
   Square 1 carries the melody, the wave channel the bass, noise the drums.
   Square 2 carries effects and seeded beast voices; effect noise borrows the
   drum channel for a few frames. Work per frame is a handful of compares and
   at most a few register writes, so it costs well under one scanline. */
#ifdef HOST_QA
static volatile u16 HOST_SND_EXTRA[32];
#define LC_SNDREG(off) HOST_SND_EXTRA[((off)-0x60)>>1]
#else
#define LC_SNDREG(off) (*(volatile u16*)(0x04000000u+(off)))
#endif
#define REG_SOUND3CNT_L LC_SNDREG(0x70)
#define REG_SOUND3CNT_H LC_SNDREG(0x72)
#define REG_SOUND3CNT_X LC_SNDREG(0x74)
#define REG_SOUND4CNT_L LC_SNDREG(0x78)
#define REG_SOUND4CNT_H LC_SNDREG(0x7C)
#define LC_WAVE_RAM(i) LC_SNDREG(0x90+(i)*2)

typedef struct{const u8*lead;const u8*bass;const u8*drum;u8 tempo,duty,env,bass_vol;}LcTrack;
#include "lc_music_data.h"

enum{SFX_NONE,SFX_MOVE,SFX_CONFIRM,SFX_CANCEL,SFX_ATTACK,SFX_HIT,SFX_CRIT,SFX_BEFRIEND,SFX_POTION,SFX_RUN,SFX_LEVELUP,SFX_CRY,SFX_COUNT};
/* One effect step: note byte (0 silences square 2), frames, control, noise preset.
   control: bits 7-6 duty, bits 5-3 envelope step, bits 2-0 volume/2. */
typedef struct{u8 note,len,ctl,noise;}LcSfxStep;
#define LC_CTL(duty,env,vol) (u8)(((duty)<<6)|((env)<<3)|((vol)>>1))
static const LcSfxStep LC_SFX_MOVE[]={{60,3,LC_CTL(2,1,10),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_CONFIRM[]={{53,3,LC_CTL(2,1,12),0},{58,6,LC_CTL(2,2,12),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_CANCEL[]={{46,3,LC_CTL(2,1,12),0},{41,6,LC_CTL(2,2,10),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_HIT[]={{20,2,LC_CTL(1,1,14),5},{15,5,LC_CTL(1,2,12),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_CRIT[]={{61,2,LC_CTL(1,1,14),6},{65,2,LC_CTL(1,1,14),0},{68,2,LC_CTL(1,1,14),0},{73,8,LC_CTL(1,3,14),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_BEFRIEND[]={{49,4,LC_CTL(1,1,12),0},{53,4,LC_CTL(1,1,12),0},{56,4,LC_CTL(1,1,12),0},{61,4,LC_CTL(1,1,12),0},{65,4,LC_CTL(1,1,12),0},{68,12,LC_CTL(1,4,14),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_POTION[]={{56,3,LC_CTL(2,1,10),0},{63,3,LC_CTL(2,1,10),0},{58,3,LC_CTL(2,1,10),0},{65,3,LC_CTL(2,1,10),0},{60,8,LC_CTL(2,3,12),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_RUN[]={{56,2,LC_CTL(2,1,10),7},{53,2,LC_CTL(2,1,10),0},{49,2,LC_CTL(2,1,10),0},{44,2,LC_CTL(2,1,10),0},{39,6,LC_CTL(2,2,8),0},{0,0,0,0}};
static const LcSfxStep LC_SFX_LEVELUP[]={{49,4,LC_CTL(2,1,12),0},{53,4,LC_CTL(2,1,12),0},{56,4,LC_CTL(2,1,12),0},{61,4,LC_CTL(2,1,12),0},{56,4,LC_CTL(2,1,12),0},{61,14,LC_CTL(2,5,14),0},{0,0,0,0}};
static LcSfxStep lc_sfx_ram[6];
/* Noise presets: CNT_L (volume/envelope) and CNT_H (clock) for kick, snare, hat, crash, hit, crit, whoosh. */
static const u16 LC_NOISE_L[8]={0,0xB100,0x9200,0x5100,0x7300,0xD200,0xF400,0x8300};
static const u16 LC_NOISE_H[8]={0,0x0063,0x0031,0x0018,0x0021,0x0042,0x0030,0x0021};
static const u8 LC_SFX_PRIORITY[SFX_COUNT]={0,1,1,1,3,3,4,4,3,3,4,2};

static u8 snd_music=3,snd_sfx=3;
static u8 lc_song=255,lc_song_next=255,lc_song_done,lc_jingle;
static u8 lc_pos[3];static u16 lc_wait[3];
static u8 lc_sfx_id,lc_sfx_pos,lc_sfx_wait,lc_sfx_noise_wait,lc_sfx_queue[3],lc_sfx_qn;
static const LcSfxStep*lc_sfx_cur;
static u16 lc_snd_mask=0xFFFF;
static u8 lc_music_context(void);
static u8 lc_opt_row;
static const char*lc_level_name(u8 l){static const char*n[4]={"OFF","LOW","MID","HIGH"};return n[l&3];}
/* row 0 master sound, 1 music level, 2 effect level. dir 0 (A) cycles, -1/+1 step. */
static u8 lc_level_step(u8 l,int dir){return (u8)(dir?clampi(l+dir,0,3):(l+1)&3);}
static void lc_audio_option(int row,int dir){
 if(row==0)audio_on=(u8)!audio_on;
 else if(row==1)snd_music=lc_level_step(snd_music,dir);
 else snd_sfx=lc_level_step(snd_sfx,dir);
}

static u8 lc_audio_pack(void){
 if(snd_music==3&&snd_sfx==3)return audio_on?1:0; /* byte-identical with V11.2 */
 return (u8)(0x80|(audio_on?0x10:0)|(snd_music&3)|((snd_sfx&3)<<2));
}
static void lc_audio_unpack(u8 v){
 if(v&0x80){audio_on=(u8)((v>>4)&1);snd_music=(u8)(v&3);snd_sfx=(u8)((v>>2)&3);}
 else{audio_on=(u8)(v?1:0);snd_music=snd_sfx=3;}
}
static int lc_music_live(void){return audio_on&&snd_music;}
static int lc_sfx_live(void){return audio_on&&snd_sfx;}
static void lc_sound_mask(void){
 u16 m=0;
 if(lc_music_live())m|=1|4|8;
 if(lc_sfx_live())m|=2|8;
 if(m!=lc_snd_mask){lc_snd_mask=m;REG_SOUNDCNT_L=(u16)(0x0077|(m<<8)|(m<<12));}
}
static void sound_init(void){int i;
 static const u16 wave[8]={0x2301,0x6745,0xAB89,0xEFCD,0xDCFE,0x98BA,0x5476,0x1032}; /* soft triangle */
 REG_SOUNDCNT_X=0x0080;
 REG_SOUNDCNT_H=0x0002;REG_SOUND1CNT_L=0x0008;
 REG_SOUND1CNT_H=0;REG_SOUND2CNT_L=0;
 REG_SOUND3CNT_L=0x40;for(i=0;i<8;i++)LC_WAVE_RAM(i)=wave[i];REG_SOUND3CNT_L=0x80;REG_SOUND3CNT_H=0;
 REG_SOUND4CNT_L=0;
 lc_snd_mask=0xFFFF;lc_sound_mask();
 lc_song=255;lc_jingle=0;lc_sfx_id=0;lc_sfx_qn=0;
}
static u8 lc_scale(u8 vol,u8 level){return (u8)((vol*level+2)/3);}
/* ---- effects ---- */
static void lc_noise(u8 preset,u8 level){
 u16 l=LC_NOISE_L[preset&7];u8 vol=lc_scale((u8)(l>>12),level);
 if(!vol)return;
 REG_SOUND4CNT_L=(u16)((vol<<12)|(l&0x0FFF));REG_SOUND4CNT_H=(u16)(0x8000|LC_NOISE_H[preset&7]);
}
static void lc_sfx_apply(const LcSfxStep*s){
 if(s->note){u8 vol=lc_scale((u8)(((s->ctl&7)<<1)|1),snd_sfx);
  REG_SOUND2CNT_L=(u16)((vol<<12)|(((s->ctl>>3)&7)<<8)|((s->ctl>>6)<<6));
  REG_SOUND2CNT_H=(u16)(0x8000|LC_NOTE_RATE[s->note<85?s->note:84]);}
 else{REG_SOUND2CNT_L=0;REG_SOUND2CNT_H=0x8000;}
 if(s->noise){lc_noise(s->noise,snd_sfx);lc_sfx_noise_wait=(u8)(s->len+4);}
 lc_sfx_wait=s->len;
}
static const LcSfxStep*lc_sfx_table(u8 id){
 switch(id){case SFX_MOVE:return LC_SFX_MOVE;case SFX_CONFIRM:return LC_SFX_CONFIRM;case SFX_CANCEL:return LC_SFX_CANCEL;
  case SFX_HIT:return LC_SFX_HIT;case SFX_CRIT:return LC_SFX_CRIT;case SFX_BEFRIEND:return LC_SFX_BEFRIEND;
  case SFX_POTION:return LC_SFX_POTION;case SFX_RUN:return LC_SFX_RUN;case SFX_LEVELUP:return LC_SFX_LEVELUP;
  default:return lc_sfx_ram;}
}
static void lc_sfx_start(u8 id){
 lc_sfx_id=id;lc_sfx_cur=lc_sfx_table(id);lc_sfx_pos=0;lc_sfx_apply(lc_sfx_cur);
}
/* UI blips replace each other. Game effects queue behind a playing game effect. */
static void lc_sfx(u8 id){
 if(!lc_sfx_live()||id==SFX_NONE||id>=SFX_COUNT)return;
 if(lc_sfx_id&&LC_SFX_PRIORITY[lc_sfx_id]>=2&&LC_SFX_PRIORITY[id]>=2){if(lc_sfx_qn<3)lc_sfx_queue[lc_sfx_qn++]=id;return;}
 if(lc_sfx_id&&LC_SFX_PRIORITY[lc_sfx_id]>LC_SFX_PRIORITY[id])return;
 lc_sfx_start(id);
}
/* Seeded voices: a beast's seed bytes pick its pitch, contour and duty. */
static void lc_seed_steps(u32 seed,int attack){int i,base,step,duty=(int)(seed&3);
 base=attack?50+(int)((seed>>8)%9):44+(int)((seed>>8)%17);
 step=1+(int)((seed>>16)%4);if((seed>>20)&1)step=-step;
 for(i=0;i<5;i++){int n=attack?base-i*(2+(int)((seed>>24)&1)):base+(i&1?step:0)+i*((seed>>28)&1?1:-1);
  lc_sfx_ram[i].note=(u8)clampi(n,8,80);lc_sfx_ram[i].len=(u8)(attack?2:3+((seed>>(i*3))&1));
  lc_sfx_ram[i].ctl=LC_CTL(duty,1,attack?12:10);lc_sfx_ram[i].noise=(u8)(attack&&i==0?7:0);}
 lc_sfx_ram[5].len=0;
}
static void lc_sfx_attack(u32 seed){if(!lc_sfx_live())return;
 lc_seed_steps(seed?seed:0x5EED1234u,1);lc_sfx(SFX_ATTACK);}
static void lc_sfx_cry(u32 seed){if(!lc_sfx_live())return;
 if(lc_sfx_id&&LC_SFX_PRIORITY[lc_sfx_id]>2)return;
 lc_seed_steps(seed?seed:0x43534d53u,0);lc_sfx_start(SFX_CRY);}
static void lc_sfx_step(void){
 if(lc_sfx_noise_wait)lc_sfx_noise_wait--;
 if(!lc_sfx_id)return;
 if(!lc_sfx_live()){lc_sfx_id=0;lc_sfx_qn=0;REG_SOUND2CNT_L=0;return;}
 if(lc_sfx_wait&&--lc_sfx_wait)return;
 lc_sfx_pos++;
 if(lc_sfx_cur[lc_sfx_pos].len){lc_sfx_apply(&lc_sfx_cur[lc_sfx_pos]);return;}
 lc_sfx_id=0;
 if(lc_sfx_qn){u8 i,next=lc_sfx_queue[0];for(i=1;i<lc_sfx_qn;i++)lc_sfx_queue[i-1]=lc_sfx_queue[i];lc_sfx_qn--;lc_sfx_start(next);}
}
/* Legacy one-shot blip (dialogue, pickups). It never cuts a game effect. */
static void tone(u16 f){if(!lc_sfx_live()||(lc_sfx_id&&LC_SFX_PRIORITY[lc_sfx_id]>=2))return;
 REG_SOUND2CNT_L=(u16)((lc_scale(10,snd_sfx)<<12)|0x0680);REG_SOUND2CNT_H=(u16)(0x8000|(f&2047));}
/* ---- music ---- */
static void lc_music_play(u8 song){
 if(song==lc_song)return;
 lc_song=song;lc_pos[0]=lc_pos[1]=lc_pos[2]=0;lc_wait[0]=lc_wait[1]=lc_wait[2]=0;lc_song_done=0;
 REG_SOUND1CNT_H=0;REG_SOUND1CNT_X=0x8000;REG_SOUND3CNT_H=0;
}
static void lc_victory(void){lc_jingle=1;lc_music_play(LC_SONG_VICTORY);}
static void lc_voice(int ch,u8 note){const LcTrack*t=&LC_TRACKS[lc_song];
 if(ch==0){
  if(!note){REG_SOUND1CNT_H=0;REG_SOUND1CNT_X=0x8000;return;}
  REG_SOUND1CNT_H=(u16)((lc_scale(12,snd_music)<<12)|(t->env<<8)|(t->duty<<6));
  REG_SOUND1CNT_X=(u16)(0x8000|LC_NOTE_RATE[note]);
 }else if(ch==1){
  static const u8 vol[4][4]={{0,0,0,0},{0,3,3,3},{0,3,2,2},{0,2,2,1}}; /* level x track bass volume code */
  if(!note){REG_SOUND3CNT_H=0;return;}
  REG_SOUND3CNT_H=(u16)(vol[snd_music&3][t->bass_vol&3]<<13);
  REG_SOUND3CNT_X=(u16)(0x8000|LC_NOTE_RATE[note+12]);
 }else{
  if(note&&!lc_sfx_noise_wait)lc_noise(note,snd_music);
 }
}
static void music_step(void){int ch;const LcTrack*t;const u8*s;
 lc_sound_mask();lc_sfx_step();
 if(!lc_music_live()){if(lc_song!=255){lc_song=255;REG_SOUND1CNT_H=0;REG_SOUND1CNT_X=0x8000;REG_SOUND3CNT_H=0;}return;}
 if(lc_jingle&&lc_song==LC_SONG_VICTORY&&!lc_song_done){}else{lc_jingle=0;lc_music_play(lc_music_context());}
 if(lc_song>=sizeof(LC_TRACKS)/sizeof(LC_TRACKS[0])||lc_song_done)return;
 t=&LC_TRACKS[lc_song];
 for(ch=0;ch<3;ch++){
  if(lc_wait[ch]&&--lc_wait[ch])continue;
  s=ch==0?t->lead:ch==1?t->bass:t->drum;
  if(s[lc_pos[ch]]==0xFE)lc_pos[ch]=0;
  if(s[lc_pos[ch]]==0xFF){if(ch==0)lc_song_done=1;lc_wait[ch]=0;if(ch==1)REG_SOUND3CNT_H=0;continue;}
  lc_voice(ch,s[lc_pos[ch]]);
  lc_wait[ch]=(u16)(s[lc_pos[ch]+1]*t->tempo);
  lc_pos[ch]=(u8)(lc_pos[ch]+2);
 }
}
