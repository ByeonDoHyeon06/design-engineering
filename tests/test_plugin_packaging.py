"""Installation scope and packaging regression checks, no network required."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_install import inspect

class PluginPackagingTests(unittest.TestCase):
    def test_full_repo_has_required_resources(self):
        result=inspect(ROOT)
        self.assertTrue(result["complete"],result)
        self.assertGreater(result["skill_bytes"],3000)

    def test_single_skill_file_is_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/"SKILL.md").write_text("demo",encoding="utf-8")
            self.assertFalse(inspect(folder)["complete"])

    def test_plugin_manifest_uses_root_skill(self):
        manifest=json.loads((ROOT/".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        marketplace=json.loads((ROOT/".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["skills"],["."])
        self.assertEqual(marketplace["plugins"][0]["source"],"./")
        self.assertEqual(manifest["name"],marketplace["plugins"][0]["name"])
        self.assertNotIn("skills",marketplace["plugins"][0])
        self.assertNotIn("strict",marketplace["plugins"][0])
        self.assertFalse((ROOT/"skills/design-engineering/SKILL.md").exists())

if __name__=="__main__":unittest.main()
