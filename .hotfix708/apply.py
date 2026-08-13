from pathlib import Path
from html.parser import HTMLParser
import base64, zlib, json, hashlib, re

root = Path('.')
engine = root / 'standalone' / 'SIM_EARTH_7_08_REALITY_BODY.html'
expected_base = '68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295'
expected_new = 'cc6e1c116d703019f4b7a5dce6330897a0b47cdcf62a4018b95b2f24c2ac5084'
base = engine.read_text(encoding='utf-8').replace('\r\n', '\n')
got = hashlib.sha256(base.encode()).hexdigest()
if got != expected_base:
    raise SystemExit(f'baseline hash mismatch: {got}')

payload = ''.join((root / '.hotfix708' / f'patch-{i:02d}').read_text().strip() for i in range(2))
ops = json.loads(zlib.decompress(base64.b64decode(payload)).decode())
lines = base.splitlines(keepends=True)
for i1, i2, text in reversed(ops):
    lines[i1:i2] = [text]
new = ''.join(lines)
sha = hashlib.sha256(new.encode()).hexdigest()
if sha != expected_new:
    raise SystemExit(f'hotfix reconstruction hash mismatch: {sha}')
engine.write_text(new, encoding='utf-8', newline='\n')

verify_path = root / 'scripts' / 'verify.mjs'
verify = verify_path.read_text()
verify = verify.replace(expected_base, expected_new)
needle = "  ['mobile Reality Body ship control', 's708-touch-ship']"
extra = "\n".join([
    "  ['mobile Reality Body ship control', 's708-touch-ship'],",
    "  ['closable control panel', 'sim707-panel-close'],",
    "  ['full HUD close', 'sim707-ui-close'],",
    "  ['persistent UI restore control', 'sim707-ui-reopen'],",
    "  ['active visual settings tab', 'sim707-pane-visuals'],",
    "  ['graphics quality bridge', 'setGraphicsQuality'],",
    "  ['world visual invalidation', 'invalidateWorldVisuals'],",
    "  ['WebGL live daylight calculation', 'baseDay=a.renderer.skyInfo().day']",
])
if needle not in verify:
    raise SystemExit('verify token insertion point missing')
verify = verify.replace(needle, extra)
verify = verify.replace('7.08 verification receipt present.', '7.08 verification receipt + UI/graphics hotfix controls present.')
verify_path.write_text(verify, encoding='utf-8', newline='\n')

pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text())
pkg['version'] = '7.0.9'
pkg['description'] = 'Cosmic Synapse Living Universe Simulation Engine — SIM EARTH 7.08 Reality Body UI/graphics hotfix'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')

changelog_path = root / 'CHANGELOG.md'
changelog = changelog_path.read_text()
entry = """## 7.0.9 — 7.08 Reality Body UI/graphics hotfix — 2026-08-13
- added a dedicated close button to the SIM EARTH control panel plus a full HUD hide/restore flow that cannot trap the player behind an overlay;
- added an active VISUALS tab for Reality Body quality, look, brightness, renderer switching and explicit world-visual refresh;
- bridged legacy Genesis quality/filter/brightness controls into the active SIM EARTH Reality Body renderer;
- fixed WebGL daylight so it derives live solar/day state instead of relying on the hidden Canvas renderer to refresh `lightFactor`;
- corrected `day` and `night` commands to true noon/midnight phases and added smooth atmosphere transitions;
- added visual invalidation so biosphere growth/reset immediately rebuilds terrain coloration and vegetation instead of waiting for movement;
- made living-biome surface palettes respond to biosphere state, so ecological growth visibly greens the world over time.

"""
if entry.splitlines()[0] not in changelog:
    changelog = changelog.replace('# Changelog\n\n', '# Changelog\n\n' + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8', newline='\n')

doc = f"""# SIM EARTH 7.08 — UI / Dynamic Graphics Hotfix

Canonical LF SHA-256 after hotfix: `{expected_new}`.

## UI fixes

- The large SIM EARTH control panel now has an explicit `×` close button.
- `CONTROL` reopens the panel and reports its expanded state for accessibility.
- `× UI` hides the full desktop HUD; a persistent `☰ RESTORE UI` pill brings it back.
- `Esc` closes the panel first, then minimizes the HUD when the panel is already closed.
- Mobile movement controls remain available while the HUD is minimized.

## Dynamic graphics fixes

- A native **VISUALS** tab controls Reality Body quality, visual look, brightness, renderer/fallback selection and manual visual refresh.
- Legacy Genesis quality/filter/brightness controls are bridged into the active Reality Body renderer.
- WebGL daylight is calculated from the current simulated solar phase every frame; it no longer depends on the hidden Canvas renderer.
- `day` maps to simulated noon and `night` maps to simulated midnight.
- Atmosphere values interpolate rather than snapping.
- Biosphere changes invalidate/rebuild the local WebGL terrain/flora buffers immediately.
- Living-biome material palettes transition from dormant/barren tones toward their mature biome palette as biosphere strength rises.

## Validation

The source gate refuses this patch unless it reconstructs the exact canonical SHA above. JavaScript syntax, duplicate IDs, literal DOM references and repository verification are checked in CI before publication.

The renderer remains a procedural real-time WebGL2/Canvas simulation, not a survey-derived digital twin.
"""
(root / 'docs' / 'HOTFIX_7_08_UI_GRAPHICS.md').write_text(doc, encoding='utf-8', newline='\n')

readme_path = root / 'README.md'
readme = readme_path.read_text()
note = """
## 🛠 7.0.9 Reality Body hotfix

The 7.08 engine now includes a closable/minimizable control HUD and active Reality Body visual controls. Use the panel `×` to close the control deck, `× UI` for a clean immersive view, and `☰ RESTORE UI` to bring the HUD back. The new **VISUALS** tab directly controls the WebGL/Canvas renderer, quality, look and brightness. Day/night, biosphere growth and renderer-state changes now propagate into the graphics immediately. See [`docs/HOTFIX_7_08_UI_GRAPHICS.md`](docs/HOTFIX_7_08_UI_GRAPHICS.md).
"""
if '## 🛠 7.0.9 Reality Body hotfix' not in readme:
    readme_path.write_text(readme.rstrip() + note + '\n', encoding='utf-8', newline='\n')

# Static DOM/reference audit and script extraction for node --check.
class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'id' and value:
                self.ids.append(value)

parser = IdParser()
parser.feed(new)
duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
if duplicates:
    raise SystemExit(f'duplicate DOM ids: {duplicates}')
ids = set(parser.ids)
refs = set(re.findall(r"getElementById\(['\"]([^'\"]+)", new))
missing = sorted(refs - ids)
if missing:
    raise SystemExit(f'missing literal DOM references: {missing}')
scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', new, re.S | re.I)
js_dir = root / '.hotfix708' / 'js-check'
js_dir.mkdir(exist_ok=True)
for index, body in enumerate(scripts):
    (js_dir / f'{index}.js').write_text(body, encoding='utf-8')

print('HOTFIX_RECONSTRUCTED', sha)
print('DOM_IDS', len(ids), 'LITERAL_REFS', len(refs), 'SCRIPTS', len(scripts))
