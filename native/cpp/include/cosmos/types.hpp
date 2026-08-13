#pragma once
#include <array>
#include <cstdint>
#include <string>
#include <vector>
namespace cosmos {
struct Vec3{double x{},y{},z{};};
struct Planet{std::string name{"Earth"};std::uint64_t seed{};bool known{true};double gravityG{1},gravity{9.80665},escapeKmS{11.2},temperatureC{15},atmosphereAtm{1},pressurePa{101325},rotationHours{23.934},wind{.2},water{.71},radiation{.05},magnetic{1},terrain{.55},hue{205},saturation{62},lightness{42};bool rings{false};};
struct Outpost{double x{},z{};std::int64_t createdMs{};};
struct WorldState{double biosphere{.22},storm{0};int anomalies{0};double cycles{0};int lifeEvents{0};double globalEvolution{0};std::vector<Outpost> outposts;};
struct PlayerState{double x{},y{2},z{},vy{},heading{},pitch{},speed{};bool onGround{true},sprint{false};};
struct SensorState{double audioAvg{},bass{},mid{},treble{},spectralFlatness{.25},spectralCentroid{},dominantHz{},visionLuminance{.35},visionMotion{},visionEntropy{.30},latitude{},longitude{},ambientLux{100};bool locationOk{false};};
struct LiveData{std::string apodTitle{"Offline sky"},apodExplanation,apodCopyright,apodMediaType,apodLocalPath,apodUrl;int neoCount{},solarFlareCount{};double latestQuakeMagnitude{};std::int64_t updatedMs{};bool stale{true};};
struct SimClock{double simUnixMs{},localDay{.5},timeWarp{1};};
using State12=std::array<float,12>;using State42=std::array<float,42>;using State54=std::array<float,54>;
struct StateBundle{State12 d12{};State42 d42{};State54 d54{};};
struct Simulation{Planet planet;WorldState world;PlayerState player;SensorState sensors;LiveData live;SimClock clock;StateBundle state;};
}
