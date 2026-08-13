from pathlib import Path
import base64, hashlib, shutil

ROOT = Path('.')
CANON = ROOT / 'standalone' / 'SIM_EARTH_7_07_ALIEN_CONTROL_CENTER.html'
VERIFY = ROOT / 'scripts' / 'verify.mjs'
CHANGELOG = ROOT / 'CHANGELOG.md'
README = ROOT / 'README.md'
RECEIPT = ROOT / 'BUILD_VERIFICATION_7.07.md'
DOC = ROOT / 'docs' / 'VISUAL_REALISM.md'
TRANSFER = ROOT / '.visual-transfer'
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-visual-realism.yml'
SELF = ROOT / 'scripts' / 'apply_visual_realism.py'
EXPECTED_OLD = '62a2bb449abc28a0860fdaeec15ba4c5b53ae8199679029f97e7270cb4a90647'
EXPECTED_NEW = '39278ea52ab10d80cf874ccb8fea8f2937cb19b1036f9d5e90007a01a9f53e5b'

parts = sorted(TRANSFER.glob('part-*'))
if len(parts) != 7:
    raise SystemExit(f'expected 7 renderer transfer parts, found {len(parts)}')
payload = ''.join(''.join(p.read_text(encoding='utf-8').split()) for p in parts)
renderer = base64.b64decode(payload).decode('utf-8')
if not renderer.startswith('class SimRenderer{'):
    raise SystemExit('renderer payload did not decode to SimRenderer')

text = CANON.read_text(encoding='utf-8').replace('\r\n', '\n')
old_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
if old_hash != EXPECTED_OLD:
    raise SystemExit(f'unexpected baseline canonical hash {old_hash}')
start = text.index('class SimRenderer{')
end = text.index('\nclass SimEarth707App{', start)
text = text[:start] + renderer.rstrip() + text[end:]

old_readout = "document.getElementById('s707-readout-b').textContent=`POS ${fmt(this.player.x,1)}, ${fmt(this.player.z,1)} // ALT ${fmt(this.player.y,1)} m // V ${fmt(this.player.speed,1)} m/s // g ${fmt(this.planet.gravityG,2)}`;"
new_readout = "const groundH=this.renderer.terrain(this.player.x,this.player.z),biome=this.renderer.biomeAt(this.player.x,this.player.z,groundH).replaceAll('_',' ').toUpperCase();document.getElementById('s707-readout-b').textContent=`POS ${fmt(this.player.x,1)}, ${fmt(this.player.z,1)} // ALT ${fmt(this.player.y,1)} m // V ${fmt(this.player.speed,1)} m/s // ${biome}`;"
if old_readout not in text:
    raise SystemExit('baseline readout signature missing')
text = text.replace(old_readout, new_readout, 1)
new_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
if new_hash != EXPECTED_NEW:
    raise SystemExit(f'visual renderer reconstruction hash mismatch {new_hash}')
CANON.write_text(text, encoding='utf-8', newline='\n')

verify = VERIFY.read_text(encoding='utf-8')
if EXPECTED_OLD not in verify:
    raise SystemExit('verify.mjs baseline hash missing')
VERIFY.write_text(verify.replace(EXPECTED_OLD, EXPECTED_NEW), encoding='utf-8', newline='\n')

changelog = CHANGELOG.read_text(encoding='utf-8')
visual_bullets = """\n- visual-realism ecology pass: climate-derived biomes, richer terrain materials, layered atmospheric haze, water shimmer, precipitation, dust/pollen, moon/stars, and cloud-depth rendering;\n- deterministic vegetation ecology expanded across broadleaf/conifer forests, rainforest, wetlands, grasslands, scrub, desert, tundra, alpine, shallow water, and barren worlds;\n- added procedural morphology families for oak/maple/beech/birch, pine/spruce/cedar, palms, mangroves/willows, ferns, reeds/cattails, flowers/orchids/lilies, mushrooms, vines, cactus/succulents/agave, coral, shrubs and ground grasses;\n- added ambient birds/gliders/fireflies, denser ground micro-detail, object shadows, adaptive mobile rendering, gas-giant cloud-deck visuals, and live biome HUD readout.\n"""
if 'visual-realism ecology pass' not in changelog:
    CHANGELOG.write_text(changelog.rstrip() + visual_bullets + '\n', encoding='utf-8', newline='\n')

readme = README.read_text(encoding='utf-8')
section = """\n## Visual realism ecology\n\nThe surface renderer now treats a world as an ecosystem rather than a single terrain palette. Local temperature, moisture, elevation, atmosphere, water fraction, wind, biosphere state and deterministic world noise select a biome; the biome selects ground material, vegetation density, morphology families, ambient life and weather behavior. Earth-like worlds can move through rainforest, temperate and conifer forest, wetland, grassland, scrub, desert, tundra, alpine, snow/ice and ocean states, while gas giants render as atmospheric cloud decks instead of pretending they have a normal walkable rocky surface.\n\nThe renderer is still procedural simulation, not a claim that every real plant species or every square meter of Earth is literally reconstructed from survey data. Its goal is coherent high-detail world generation inside the self-contained browser engine.\n"""
if '## Visual realism ecology' not in readme:
    README.write_text(readme.rstrip() + '\n' + section + '\n', encoding='utf-8', newline='\n')

DOC.parent.mkdir(parents=True, exist_ok=True)
DOC.write_text(f"""# SIM EARTH 7.07 — Visual Realism Ecology\n\nCanonical LF SHA-256 after this pass: `{EXPECTED_NEW}`.\n\n## What changed\n\nThe visual renderer now derives scene appearance from the same persistent planet/world state rather than drawing generic decorative objects. The rendering stack includes:\n\n- climate-derived biome selection from temperature, latitude proxy, moisture, elevation, atmosphere and water;\n- biome-specific surface palettes and deterministic micro-material grain;\n- ocean depth states, wave variation and screen-space water glints;\n- layered atmospheric gradients, horizon haze, stars, lunar detail, multi-layer clouds and planet weather shells;\n- rain/snow, dust, pollen, lightning and storm-darkening behavior;\n- deterministic plant families spanning trees, palms, ferns, reeds, flowers, mushrooms, vines, cacti, succulents, shrubs, grasses and coral;\n- near-ground blades, stones and micro-detail for depth;\n- ambient birds/gliders and dusk fireflies when biosphere conditions support them;\n- gas-giant cloud-deck rendering for Jupiter/Saturn/Uranus/Neptune-like worlds;\n- adaptive surface column resolution to preserve mobile frame budget;\n- a live biome label in the surface HUD.\n\n## Scientific boundary\n\nThese systems increase visual and ecological coherence. They are procedural simulation rules, not a botanical census, satellite-derived digital twin, or proof that CST variables are physical laws. A literal reconstruction of every plant and every square meter would require continuously updated geospatial, ecological, seasonal and species-distribution datasets far beyond a self-contained HTML file.\n""", encoding='utf-8', newline='\n')

if RECEIPT.exists():
    receipt = RECEIPT.read_text(encoding='utf-8')
    notice = f"> **Visual realism source update:** the current canonical source hash is `{EXPECTED_NEW}`. The native artifacts recorded below were built from the earlier verified baseline `{EXPECTED_OLD}` and remain historical build evidence until the visual-realism source is rebuilt across those targets.\n\n"
    if '**Visual realism source update:**' not in receipt:
        RECEIPT.write_text(receipt.replace('# SIM EARTH 7.07 — Build Verification Receipt\n\n', '# SIM EARTH 7.07 — Build Verification Receipt\n\n' + notice, 1), encoding='utf-8', newline='\n')

# Transfer scaffolding must not survive in the branch's final tree.
if TRANSFER.exists():
    shutil.rmtree(TRANSFER)
for disposable in (WORKFLOW, SELF):
    if disposable.exists():
        disposable.unlink()

print(f'VISUAL_REALISM_APPLIED {new_hash}')
