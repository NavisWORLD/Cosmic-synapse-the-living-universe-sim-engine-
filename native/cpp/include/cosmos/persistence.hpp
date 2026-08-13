#pragma once
#include "types.hpp"
#include <filesystem>
#include <string>
namespace cosmos{bool saveWorld(const std::filesystem::path&,const Simulation&);bool loadWorld(const std::filesystem::path&,Simulation&);void appendLedger(const std::filesystem::path&,const std::string&,const std::string&,const Simulation&);}
