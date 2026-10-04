"""Content Bible contracts, art safety, and native RPG behavior."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'content/v11_1_catalog.json').read_text())

    def test_original_catalog_has_100_entries_in_each_category(self):
        for key in ('items', 'characters', 'skills'):
            entries = self.data[key]
            self.assertEqual(len(entries), 100, key)
            self.assertEqual(len({e['id'] for e in entries}), 100)
            self.assertTrue(all(e['name'] and e['description'] for e in entries))
        self.assertEqual(self.data['items'][0]['id'], 'ITM_W001')
        self.assertEqual(self.data['skills'][-1]['id'], 'SKL_U010')
        self.assertEqual(self.data['characters'][-1]['name'], 'THE QUIET')

    def test_effects_are_executable_and_world_ids_are_valid(self):
        for entry in self.data['items']:
            self.assertIn(entry['kind'], ('weapon','armor','charm','consumable','key'))
            self.assertIn(entry['world'], range(8))
        for entry in self.data['skills']:
            self.assertIn(entry['kind'], ('spell','buddy','passive','ultimate','utility'))
            self.assertLess(entry['mp'], 256)
        for entry in self.data['characters']:
            self.assertIn(entry['kind'], ('npc','mob','elite','boss'))
            self.assertIn(entry['world'], range(8))
        self.assertEqual(self.data['characters'][90]['hp'], 600)
        self.assertEqual(self.data['items'][0]['str'], 1)

    def test_native_assets_are_individually_mapped(self):
        art = json.loads((ROOT / 'content/v11_1_art_manifest.json').read_text())
        self.assertEqual(len(art['characters']), 100)
        self.assertEqual(len(art['items']), 100)
        self.assertEqual(len(art['skills']), 100)
        for key in ('characters','items','skills'):
            for asset in art[key]:
                self.assertEqual(asset['palette_colors'], 16)
                self.assertTrue(asset['visible_pixels'])
                self.assertLessEqual(asset['visible_width'], 24 if key == 'characters' else 16)
                self.assertLessEqual(asset['visible_height'], 24 if key == 'characters' else 16)

if __name__ == '__main__':
    unittest.main()
