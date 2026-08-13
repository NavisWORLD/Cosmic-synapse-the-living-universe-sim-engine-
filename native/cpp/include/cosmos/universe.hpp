#pragma once
#include "types.hpp"
#include <string>
namespace cosmos{Planet makePlanet(const std::string&);double terrainHeight(const Planet&,double,double);void resetPlayerToSpawn(Simulation&);void foldTo(Simulation&,const std::string&);void updatePlayer(Simulation&,double,double,double,bool,bool);void updateWorld(Simulation&,double);void seedLife(Simulation&);void addOutpost(Simulation&);void injectStorm(Simulation&);void manifestAnomaly(Simulation&);double scanResource(const Simulation&);}
