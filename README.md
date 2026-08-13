# 🌍 COSMIC SYNAPSE // THE LIVING UNIVERSE SIM ENGINE

<p align="center">
  <img src="docs/assets/hero.svg" alt="SIM EARTH — Cosmic Synapse Living Universe Simulation Engine" width="100%">
</p>

<p align="center">
  <strong>SIM EARTH 7.08 // REALITY BODY</strong><br>
  A persistent living-universe simulation with a self-contained WebGL2 world body, Luna field explorer, and LUNA-ARC survey vessel — while the canonical engine still fits in one HTML file.
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/SIM%20EARTH-7.08-62f6ff">
  <img alt="Renderer" src="https://img.shields.io/badge/renderer-WebGL2%20%2B%20Canvas%20fallback-8a8cff">
  <img alt="State Engine" src="https://img.shields.io/badge/state-12D%E2%86%9242D%E2%86%9254D-b7ff77">
  <img alt="Standalone" src="https://img.shields.io/badge/canonical-one%20HTML-f7d66d">
  <img alt="Native" src="https://img.shields.io/badge/package-PWA%20%2F%20iOS%20%2F%20Android%20%2F%20Desktop-74b9ff">
  <img alt="License" src="https://img.shields.io/badge/software-Apache--2.0-white">
</p>

> **One engine. One file. Persistent worlds. 3D surface presence. Luna. LUNA-ARC. 12D → 42D → 54D live state fusion.**

SIM EARTH is the focused living-universe game/simulation branch of the Cosmic Synapse project. Version **7.08 Reality Body** keeps the previous procedural world, ecology, persistence, sensor, audio, orbital, Reality Lens, and CST/state systems, then gives the surface a lightweight raw-WebGL2 3D body.

The renderer is intentionally self-contained: no Three.js CDN is required at runtime. When WebGL2 is unavailable, the existing Canvas renderer remains the fallback.

## 🚀 Run it

### Standalone — no install

Download:

[`standalone/SIM_EARTH_7_08_REALITY_BODY.html`](standalone/SIM_EARTH_7_08_REALITY_BODY.html)

Open it in a modern browser and initiate SIM EARTH.

For camera, microphone, motion, geolocation, PWA installation, and more consistent browser permissions, use an HTTPS deployment or the included local server:

```bash
python tools/serve.py
```

Then open `http://localhost:7070/`.

### iPhone / iPad

The easiest unsigned Apple route is the PWA: open the deployed site in Safari → **Share** → **Add to Home Screen**. The repository also contains the Capacitor iOS path for Xcode/Simulator/TestFlight/App Store builds. A physical-device/App Store `.ipa` requires the publisher's Apple Developer signing identity.

### Android

Use the PWA or the Android GitHub Actions workflow / Capacitor path to generate the Android package from the same web engine.

### Windows / macOS / Linux

Use the PWA or Electron packaging. Desktop workflows target Windows NSIS, macOS DMG/ZIP, and Linux AppImage/DEB.

## 👽 What changed in 7.08?

### Reality Body renderer

`RealityRenderer708` renders the surface using raw WebGL2 while reusing the old procedural renderer as the authoritative terrain/biome model.

- real generated 3D terrain mesh;
- derived terrain normals;
- biome-dependent ground color;
- procedural soil/rock/micro-material breakup;
- sun + hemispheric lighting;
- atmospheric fog;
- procedural sky, clouds, storms and lightning;
- daylight-correct star visibility;
- animated translucent water;
- adaptive mobile/desktop render density;
- Canvas fallback when WebGL2 is unavailable.

The final desktop Earth QA scene generated **112,614 terrain indices**, roughly **5,000 grass instances**, and more than **200 trees** while retaining the one-file architecture.

### 🌿 Living surface

The existing ecology system still derives appearance from temperature, moisture, elevation, atmosphere, water, wind, biosphere and deterministic world noise. WebGL2 adds lightweight GPU vegetation: tapered wind-responsive grass and crossed multi-layer tree canopies for depth.

### 👩‍🚀 Luna // field explorer

Third-person mode gives the player an actual in-world explorer body:

- rounded procedural EVA anatomy;
- white/graphite suit;
- backpack;
- helmet + blue visor;
- cyan suit/chest illumination.

This is generated game geometry, not a downloaded or externally licensed character asset.

### 🚀 LUNA-ARC // survey vessel

The LUNA-ARC is physically present in the scene and can be approached, boarded, flown, landed and exited. Its procedural design includes a pale ceramic/metal hull, dark underside, cockpit canopy, atmospheric wings, glowing engine pods, dorsal structure and landing gear.

## 🎮 Controls

| Action | Desktop | Mobile |
|---|---|---|
| Move / thrust | WASD | virtual stick |
| Look | mouse / arrows | drag view |
| Sprint / fast flight | Shift | SPRINT |
| Jump / ascend | Space | JUMP → ASCEND |
| Descend ship | Ctrl | SCAN → DESCEND while boarded |
| Scan | E | SCAN |
| First / third person | V | VIEW |
| Board / exit LUNA-ARC | F | SHIP / EXIT |
| Orbit / surface | G / mode controls | ORBIT / mode controls |
| Reality Lens | R | mode controls |
| HUD | H | HUD control |
| Audio | M | AUDIO |
| Time warp | T | TIME control |

The ship will not let the explorer exit while it is too high above the terrain.

## 🧠 12D → 42D → 54D

The original computational state stack remains intact.

**12D sensory/CST core:** `frequency_mass`, `geometric_phase`, `spectral_flatness`, `phase_velocity`, `entanglement`, `valence`, `arousal`, `dominance`, `audio_psi`, `phi_harmonics`, `av_coherence`, `quantum_entropy`.

**42D** extends that state with Lorenz/chaos proxies, spectral/vision signals, location/solar phase, planetary/environmental fields, memory/novelty/instability/coherence and related context.

**54D** adds adaptive channels including Hebbian strength, plasticity, attention, curiosity, avoidance, flora/black-hole biases, memory depth, prediction error, learning rate, resonance and a singularity channel.

These are computational state-space dimensions/channels in the simulator. They are **not presented as proof of additional physical spacetime dimensions**.

See [`docs/PHYSICS_AND_54D_STATE.md`](docs/PHYSICS_AND_54D_STATE.md).

## 🛠 Build

The canonical game itself has no Node runtime dependency. Packaging requires Node.js 20+.

```bash
npm install
npm run verify
npm run prepare:web
```

Native wrappers:

```bash
npm run native:android
npm run native:ios
```

Desktop:

```bash
npm run desktop
npm run dist:desktop
```

See [`docs/BUILD_AND_DISTRIBUTION.md`](docs/BUILD_AND_DISTRIBUTION.md).

## ✅ Verification

The canonical LF-normalized SHA-256 for SIM EARTH 7.08 Reality Body is:

```text
68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295
```

The release was checked with:

- JavaScript syntax checks across active scripts;
- duplicate-ID and literal DOM-reference audits;
- 12D/42D/54D ancestry/state preservation checks;
- hostile mocked DOM/WebGL runtime tests;
- mobile view/ship/ascend/descend interaction tests;
- genuine Chromium WebGL2 shader compilation and rendering using the final source;
- final `gl.getError() === 0` in the Chromium QA path;
- exact-hash reconstruction on a GitHub-hosted runner before the canonical branch file was accepted.

The real-browser pass caught and fixed an actual GLSL reserved-word defect before publication.

Run the repository verifier yourself:

```bash
npm run verify
```

## 📦 Repository map

```text
standalone/     canonical one-file SIM EARTH game
app/            PWA manifest/service worker + generated index
desktop/        Electron desktop shell
scripts/        hostile verification + packaging preparation
tools/          local server
docs/           player, teacher, engineering, validation and distribution guides
paper/          7.07 technical manuscript + Zenodo metadata template
.github/        validation and cross-platform build workflows
```

## 📚 Documentation

- [Reality Body 7.08 Engineering Guide](docs/REALITY_BODY_7_08.md)
- [Visual Realism Ecology](docs/VISUAL_REALISM.md)
- [Player Manual](docs/PLAYER_MANUAL.md)
- [Teacher Guide](docs/TEACHER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Physics + 54D State](docs/PHYSICS_AND_54D_STATE.md)
- [Build & Distribution](docs/BUILD_AND_DISTRIBUTION.md)
- [Research & Validation](docs/RESEARCH_GUIDE.md)
- [IP & Attribution](docs/IP_AND_ATTRIBUTION.md)
- [7.07 Technical Paper](paper/SIM_EARTH_7_07_TECHNICAL_PAPER.md)

The 7.07 manuscript is preserved as historical research documentation rather than silently relabeled as a 7.08 publication.

## 📖 Research lineage

**Creator:** Cory Shane Davis  
**Foundational CST publication:** *The 12-Dimensional Cosmic Synapse Theory: Audio-Driven Deterministic Cosmological Simulation with Adaptive Memory and Light Particle Mapping*  
**DOI:** `10.5281/zenodo.17574447`

That DOI is cited as lineage for the foundational CST work. It is not represented as a DOI minted specifically for SIM EARTH 7.08.

## ⚖️ Licensing

- **Software:** Apache License 2.0 — [`LICENSE`](LICENSE)
- **Documentation/paper:** CC BY 4.0 — [`LICENSE-DOCS.md`](LICENSE-DOCS.md)
- [`NOTICE`](NOTICE) preserves project attribution and CST lineage.
- See [`docs/IP_AND_ATTRIBUTION.md`](docs/IP_AND_ATTRIBUTION.md) for practical provenance/licensing notes.

## 🔬 Scientific + visual boundary

“Alien control center” and “Reality Body” are game/engineering metaphors. The software does not physically actuate Earth, remote planets or spacecraft. Procedural worlds are not live remote planetary imagery. Sensor channels are not medical, deception, emotion or consciousness diagnostics.

The 7.08 renderer is a substantial 3D upgrade, but it is still a compact procedural WebGL implementation. It should **not** be represented as a literal survey-derived digital twin or cinematic UE5-class photorealism. The interesting engineering claim is narrower and reproducible: the project carries a persistent multi-system planetary explorer, 3D surface renderer, procedural character and flyable vessel inside a single inspectable HTML engine.

## 🌌 Design rule

> **Preserve ancestry. Add capability. Label simulations honestly. Let the universe remember.**
## 🛠 7.0.9 Reality Body hotfix

The 7.08 engine now includes a closable/minimizable control HUD and active Reality Body visual controls. Use the panel `×` to close the control deck, `× UI` for a clean immersive view, and `☰ RESTORE UI` to bring the HUD back. The new **VISUALS** tab directly controls the WebGL/Canvas renderer, quality, look and brightness. Day/night, biosphere growth and renderer-state changes now propagate into the graphics immediately. See [`docs/HOTFIX_7_08_UI_GRAPHICS.md`](docs/HOTFIX_7_08_UI_GRAPHICS.md).

