# SIM EARTH 7.07 — Player Manual

## 1. Start
Open the standalone HTML or the installed PWA and select **INITIATE SIM EARTH 7.07**. Sensor permissions are optional. Denying a sensor does not stop the core procedural simulation; it reduces live environmental inputs.

## 2. Your three viewing layers
**Surface** is first-person traversal. **Orbit** is the planetary observation/navigation layer. **Reality Lens** uses available camera/environment signals as an input surface while preserving the simulation HUD.

## 3. Worlds
Known reference worlds ship with anchored values. New named planets are generated deterministically: the same name maps back to the same seed and local persistent history. This is a procedural simulation, not a live telescope feed.

## 4. Growth
World state evolves as you explore. Scans, outposts, seeded biospheres, anomalies, storms, and time spent on a world feed the persistent local ledger. Browser storage is used so the universe can remember between sessions on the same device/browser profile.

## 5. Command deck
Try: `goto Mars`, `fold Europa`, `create Aurora-9`, `seed life`, `outpost`, `storm`, `anomaly`, `scan`, `orbit`, `surface`, `reality`, `day`, `night`, `time`.

## 6. Sensors
Microphone input is summarized into spectral bands. Camera frames can be sampled for luminance and motion. Geolocation/orientation/motion are used only when the browser/device exposes them and permission is granted. The canonical build does not require a cloud account.

## 7. Save/export
World history is local. Use the in-engine ledger/state export tools when you want a portable record. Clearing site data can erase local persistent worlds.

## 8. Performance
On older phones, reduce visual intensity and avoid running multiple sensor-heavy tabs. Mobile browsers may pause audio/sensors when backgrounded.
