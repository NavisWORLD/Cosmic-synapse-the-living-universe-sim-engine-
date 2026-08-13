# SIM EARTH 7.08 — Reality Body Build Verification Receipt

Release family: **SIM EARTH 7.08 // REALITY BODY**  
Canonical source: `standalone/SIM_EARTH_7_08_REALITY_BODY.html`  
Canonical LF SHA-256: `68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295`

This receipt records the validation and packaging evidence for the 7.08 Reality Body source. `BUILD_VERIFICATION_7.07.md` remains historical evidence for the previous release and is not overwritten.

## 1. Source/runtime validation

The exact 7.08 standalone was checked before publication with:

- all four active JavaScript script bodies parsed successfully with Node syntax checking;
- 119 DOM IDs audited with no duplicate IDs;
- literal `getElementById(...)` references audited with no unresolved IDs;
- `Universe`, `SensorFusion`, `CSTStateEngine`, `SimEarth707App`, and exact 12D/42D/54D state-array surfaces preserved;
- hostile mocked DOM/WebGL runtime exercised terrain/flora generation, surface rendering, first/third-person switching, LUNA-ARC boarding, flight, landing and exit;
- mobile runtime exercised `VIEW`, `SHIP`/`EXIT`, `JUMP`→`ASCEND`, and `SCAN`→`DESCEND` label/action transitions;
- genuine Chromium WebGL2 compiled and rendered the final source after QA fixes;
- final real-browser QA returned `gl.getError() === 0`.

Representative final mocked runtime result:

```json
{"pass":true,"terrainIndices":112614,"grass":5044,"trees":240,"shipMoved":19.773,"view":"third","status":"LUNA // FIELD WALKER // THIRD PERSON // WEBGL2","glError":0}
```

Representative final Chromium WebGL2 QA result:

```json
{"app":true,"reality":true,"version":"WebGL 2.0 (OpenGL ES 3.0 Chromium)","renderer":"WebKit WebGL","gl":0,"terrain":112614,"grass":5044,"trees":230,"view":"third","status":"LUNA // FIELD WALKER // THIRD PERSON // WEBGL2","oldUI":true}
```

Real Chromium QA caught and blocked a genuine GLSL defect during development because `patch` is a reserved identifier. The shader was corrected (`mottle`) and the final source was recompiled/rendered successfully before release.

## 2. Exact GitHub reconstruction

GitHub Actions run **31666105891** (`Apply SIM EARTH 7.08 Reality Body`) reconstructed the large standalone on a GitHub-hosted runner from readable source/apply chunks. The apply script refused to accept the output unless it matched the exact canonical SHA above.

Result: **success**.

The successful cleanup commit removed the temporary transfer directory, reconstruction script and reconstruction workflow from the final branch tree.

## 3. Fresh repository verifier

GitHub Actions run **31666407843** (`Verify engine`) ran from the same 7.08 source tree used to trigger native packaging.

Result: **success**.

The verifier checks the exact canonical SHA, original Genesis/12D→42D→54D surfaces, Reality Body WebGL2 class, Luna/LUNA-ARC controls, packaging surfaces and cleanup invariants. It also runs PWA preparation from the canonical standalone.

## 4. Cross-platform build run

GitHub Actions run **31666407908** (`Build SIM EARTH 7.08 Reality Body`) completed with overall result **success**.

Jobs:

- Android debug APK — job `94341800069` — **success**
- iOS Simulator — job `94341800151` — **success**
- Windows desktop — job `94341800170` — **success**
- Linux desktop — job `94341800229` — **success**
- macOS desktop — job `94341800232` — **success**
- one-shot cleanup — **success** (required for the workflow's overall successful completion)

Every platform job ran `npm run verify` and `npm run prepare:web` before native/desktop packaging, so all wrappers consumed the 7.08 Reality Body source rather than the prior 7.07 build.

## 5. GitHub artifact archives

| Target | Artifact ID | GitHub artifact digest |
|---|---:|---|
| Android debug APK | `9168104385` | `sha256:f4d1f81a6a3ba2f47f9b281a692e84c05361d9d6a583f698ce687980c5a8ef4e` |
| iOS Simulator | `9168098788` | `sha256:8bd912c7857f5ed8cbe77d8725f3b757d6a76f178a4a02635fac0763e404fa15` |
| Windows | `9168105063` | `sha256:49ee632bfa4c570553aafd504ab7a15dfaa0d9d7807a236684860f248385563f` |
| macOS | `9168094062` | `sha256:161f29318e14a2baf0f2d03700aa5860e200f1e011419c3eac2b50602b61261a` |
| Linux | `9168108030` | `sha256:c241e4e98b356dcf7761b6145b9ac942efb0e5c7abe8420f6da9dc316979be37` |

## 6. Extracted distributable payloads

The GitHub artifact archives were downloaded and the actual distributable payloads were independently hashed after extraction:

| Payload | Architecture/type | SHA-256 |
|---|---|---|
| `SIM_EARTH_7_08_Android_Debug.apk` | Android debug APK | `805acae7693a78f482106cffce4b76b63346d0663b1ed91d59bec5d0f3a484b8` |
| `SIM_EARTH_7_08_iOS_Simulator.zip` | iOS Simulator universal app (`x86_64` + `arm64`) | `05382e76fb32adb8f561449d5f6bb3de8b5fb19011ba3d159c688241de95fbe0` |
| `SIM_EARTH_7_08_Windows_Setup_7.0.8.exe` | Windows NSIS installer | `1eb63bc56d1e328d06352ca8097d4b7ae61a0b7381d22d29bb2c8e544e9a982b` |
| `SIM_EARTH_7_08_macOS_ARM64_7.0.8.dmg` | macOS Apple Silicon ARM64 DMG | `15461d092e8ca849b6a750af4a14116b43c84c486b27b046f5b1d6366ea85cc4` |
| `SIM_EARTH_7_08_macOS_ARM64_7.0.8.zip` | macOS Apple Silicon ARM64 ZIP | `f745ec4419b5aa9dd28aa526d4173cd48351b2a6e08a0c7539bca1852b7b3e48` |
| `SIM_EARTH_7_08_Linux_7.0.8.AppImage` | Linux x86-64 AppImage | `dfcf11301adc459585c226e0518c17a36bcb9929bc2ebfe4fc50d59c7ff9722a` |
| `SIM_EARTH_7_08_Linux_amd64_7.0.8.deb` | Debian/Ubuntu amd64 package | `20a452d8821dd66fbeb1961b637cd461e4998749b84f54cd1e38684adf6c4eef` |

## 7. Distribution boundaries

- **Android:** the verified package is a debug APK. It is not a Play Store release-signed AAB.
- **iOS:** the verified package is an unsigned Simulator build. It is not a physical-device/TestFlight/App Store `.ipa`; those require the publisher's Apple Developer signing certificate/profile.
- **macOS:** the produced desktop build is ARM64/Apple Silicon. It is not an Intel/universal macOS desktop build and is not Developer-ID signed/notarized.
- **Windows:** the NSIS installer is not code-signed, so SmartScreen warnings may occur during direct distribution.
- **Linux:** the produced AppImage/DEB are x86-64/amd64.
- **PWA:** the engine/package path is verified, but a public GitHub Pages URL still depends on the repository-level Pages setting being enabled for GitHub Actions.

## 8. Scientific/visual boundary

Reality Body is a compact procedural 3D game/visualization renderer. The successful WebGL2 and cross-platform builds demonstrate implemented software behavior; they do not demonstrate a survey-derived Earth digital twin, literal reproduction of every real organism, new physical spacetime dimensions, medical/consciousness sensing, or physical control of Earth/remote planets.

The 7.08 graphics are a real 3D upgrade and a deliberately unusual one-file implementation. They should not be described as cinematic UE5-class photorealism unless a future renderer objectively reaches and documents that standard.
