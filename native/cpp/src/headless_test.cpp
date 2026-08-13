#include "cosmos/cst_state.hpp"
#include "cosmos/universe.hpp"
#include <cassert>
#include <iostream>
int main(){cosmos::Simulation sim;sim.planet=cosmos::makePlanet("Earth");cosmos::resetPlayerToSpawn(sim);sim.clock.simUnixMs=1770000000000.0;cosmos::CSTStateEngine st;auto x0=sim.player.x,z0=sim.player.z;for(int i=0;i<600;i++){cosmos::updatePlayer(sim,1.0/60,1,0,false,false);cosmos::updateWorld(sim,1.0/60);sim.state=st.update(1.0/60,sim);}assert(sim.player.x!=x0||sim.player.z!=z0);assert(sim.state.d54[41]>=0&&sim.state.d54[41]<=1);auto a=cosmos::makePlanet("Cory Prime"),b=cosmos::makePlanet("Cory Prime");assert(a.gravityG==b.gravityG&&a.hue==b.hue);std::cout<<"LIVING UNIVERSE HEADLESS OK\nplanet="<<sim.planet.name<<" coherence="<<sim.state.d54[41]<<"\n";}
