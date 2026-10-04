/* SOL nursery art, Cory Davis / NavisWORLD. Pure integer 32px renderer.
 * Matches arcade/sol-beast-lab/sprites.mjs. Palette 13..15 carry the nursery
 * signature and visual genes; visible pixels use only indices 0..12.
 * Stage is earned by lc_evolve, never authored by a host-side roster patch. */
#ifndef SOL_BEAST_ART_H
#define SOL_BEAST_ART_H
#include <stdint.h>
static int sol_ellipse(int x,int y,int cx,int cy,int rx,int ry){
 int dx=x-cx,dy=y-cy;return dx*dx*ry*ry+dy*dy*rx*rx<=rx*rx*ry*ry;
}
static int sol_rect(int x,int y,int l,int t,int r,int b){return x>=l&&x<=r&&y>=t&&y<=b;}
static int sol_abs(int x){return x<0?-x:x;}
static int sol_shape(int x,int y,uint32_t seed,unsigned meta,int s){
 int i=meta&7,calm=(meta>>5)&3,spark=(meta>>7)&3,w=(seed>>2)&1;
 if(sol_ellipse(x,y,15,18-s,7+s+w,7+s+(calm>=2)))return 1;
 if(sol_rect(x,y,10-s,24+s,13,26+s)||sol_rect(x,y,17,24+s,20+s,26+s))return 1;
 if(i==0&&((y>=5-s&&y<=12&&sol_abs(x-9)<=(y-4+s)/2)||(y>=5-s&&y<=12&&sol_abs(x-21)<=(y-4+s)/2)||sol_ellipse(x,y,5,22,3+s,2+spark)))return 1;
 if(i==1&&(sol_ellipse(x,y,10,9-s,3,4)||sol_ellipse(x,y,20,9-s,3,4)||sol_rect(x,y,14,4-s,15,9)||sol_ellipse(x,y,17,5-s,3+s,2)))return 1;
 if(i==2&&(sol_ellipse(x,y,9,9-s,3,4)||sol_ellipse(x,y,21,9-s,3,4)||sol_rect(x,y,11,5-s,19,7)||sol_rect(x,y,11,3-s,12,6)||sol_rect(x,y,15,2,16,6)||sol_rect(x,y,18,3-s,19,6)))return 1;
 if(i==3&&(sol_ellipse(x,y,10,7,2+s,5+s)||sol_ellipse(x,y,20,7,2+s,5+s)||sol_ellipse(x,y,24,22,3,3)))return 1;
 if(i==4&&(sol_ellipse(x,y,9,9-s,3+s,3+s)||sol_ellipse(x,y,21,9-s,3+s,3+s)||sol_rect(x,y,4-s,16,7,21)||sol_rect(x,y,24,16,26+s,21)))return 1;
 if(i==5&&(sol_ellipse(x,y,6,20-s,3+s,4+s)||sol_ellipse(x,y,24,20-s,3+s,4+s)||sol_ellipse(x,y,15,7-s,2+s,3)||sol_rect(x,y,14,26,16,28)))return 1;
 if(i==6&&(sol_ellipse(x,y,7,17,4+s,6+s)||sol_ellipse(x,y,23,17,4+s,6+s)||sol_rect(x,y,10,5-s,11,10)||sol_rect(x,y,19,5-s,20,10)||sol_ellipse(x,y,9,5-s,2,2)||sol_ellipse(x,y,21,5-s,2,2)))return 1;
 if(i==7&&(sol_rect(x,y,3-s,12,7,14)||sol_rect(x,y,2,17,7,19)||sol_rect(x,y,4-s,22,8,24)||sol_rect(x,y,23,12,27+s,14)||sol_rect(x,y,23,17,28,19)||sol_rect(x,y,22,22,26+s,24)||sol_ellipse(x,y,15,7-s,2+s,3)))return 1;
 return 0;
}
static uint8_t sol_beast_pixel(int x,int y,uint32_t seed,unsigned meta,int stage,int blink){
 int s=stage<0?0:(stage>2?2:stage),i=meta&7,focus=(meta>>3)&3,eyeY=14-s;
 if(!sol_shape(x,y,seed,meta,s))return 0;
 if(!sol_shape(x-1,y,seed,meta,s)||!sol_shape(x+1,y,seed,meta,s)||!sol_shape(x,y-1,seed,meta,s)||!sol_shape(x,y+1,seed,meta,s))return 1;
 if(y<10-s)return i==1?10:(i==2?8:3);
 if(((x>=11&&x<=12)||(x>=18&&x<=19))&&y>=eyeY&&y<=eyeY+2)
  return blink?(y==eyeY+1?7:2):((y==eyeY&&(x==11||x==18))?4:7);
 if(y==eyeY+3&&(x==9||x==10||x==20||x==21))return 6;
 if((x==15||x==16)&&y==eyeY+4)return 7;
 if(i==5&&sol_rect(x,y,14,eyeY+3,16,eyeY+3))return 8;
 if(s==2&&y==21&&x>=13&&x<=17)return focus>=2?9:8;
 if(sol_ellipse(x,y,15,23-s,4+s,3+s))return 12;
 if(x<10||x>21)return i==6?10:5;
 if(((seed>>4)&1)&&x==14&&y==11-s)return 8;
 return x+y<30-s?3:2;
}
#endif
