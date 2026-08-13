#pragma once
#include "types.hpp"
#include <array>
namespace cosmos{class CSTStateEngine{public:StateBundle update(double,const Simulation&);private:double prevPhase_{0},lx_{.1},ly_{.2},lz_{.3};std::array<float,12>weights_{{.5f,.5f,.5f,.5f,.5f,.5f,.5f,.5f,.5f,.5f,.5f,.5f}};std::array<float,12>memory_{};};}
