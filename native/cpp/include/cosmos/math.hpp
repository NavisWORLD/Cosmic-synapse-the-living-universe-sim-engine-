#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <string_view>
namespace cosmos {
constexpr double PI=3.14159265358979323846,PHI=1.6180339887498948482;
template<class T>inline T clamp(T v,T lo=T(0),T hi=T(1)){return std::max(lo,std::min(hi,v));}
inline double lerp(double a,double b,double t){return a+(b-a)*t;}inline double fract(double x){return x-std::floor(x);}inline double normAngle(double a){while(a>PI)a-=2*PI;while(a<-PI)a+=2*PI;return a;}
inline std::uint64_t fnv1a64(std::string_view s){std::uint64_t h=1469598103934665603ull;for(unsigned char c:s){h^=c;h*=1099511628211ull;}return h;}
inline std::uint64_t splitmix64(std::uint64_t&x){std::uint64_t z=(x+=0x9e3779b97f4a7c15ull);z=(z^(z>>30))*0xbf58476d1ce4e5b9ull;z=(z^(z>>27))*0x94d049bb133111ebull;return z^(z>>31);}inline double rand01(std::uint64_t&s){return(splitmix64(s)>>11)*(1.0/9007199254740992.0);}
inline double valueNoise(std::uint64_t seed,int x,int z){std::uint64_t s=seed^(std::uint64_t(std::uint32_t(x))*0x9E3779B185EBCA87ull)^(std::uint64_t(std::uint32_t(z))*0xC2B2AE3D27D4EB4Full);return rand01(s)*2-1;}inline double smoothstep(double t){t=clamp(t);return t*t*(3-2*t);}inline double noise2(std::uint64_t seed,double x,double z){int x0=(int)std::floor(x),z0=(int)std::floor(z),x1=x0+1,z1=z0+1;double tx=smoothstep(x-x0),tz=smoothstep(z-z0);return lerp(lerp(valueNoise(seed,x0,z0),valueNoise(seed,x1,z0),tx),lerp(valueNoise(seed,x0,z1),valueNoise(seed,x1,z1),tx),tz);}inline double fbm(std::uint64_t seed,double x,double z){double sum=0,amp=.5,freq=.018,norm=0;for(int i=0;i<5;i++){sum+=noise2(seed+i*101,x*freq,z*freq)*amp;norm+=amp;amp*=.5;freq*=2.03;}return sum/std::max(1e-9,norm);}
}
