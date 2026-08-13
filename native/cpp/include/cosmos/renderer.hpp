#pragma once
#include "types.hpp"
#include <string>
namespace cosmos{class Renderer{public:Renderer(int,int);~Renderer();void setMode(int);int mode()const{return mode_;}void render(const Simulation&,double);void refreshApodTexture(const LiveData&);private:int mode_{0};std::string loadedApod_;unsigned int apodId_{0};int apodW_{0},apodH_{0};void drawOrbit(const Simulation&,double);void drawSurface(const Simulation&,double);void drawApod(const Simulation&,double);void drawHud(const Simulation&);};}
