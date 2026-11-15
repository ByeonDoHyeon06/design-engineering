import json, re, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'knowledge/catalog.json').read_text(encoding='utf8'))
SRC=json.loads((ROOT/'knowledge/sources.json').read_text(encoding='utf8'))
sys.path.insert(0,str(ROOT/'scripts'))
import knowledge_index as mod

class KnowledgeIntegrityTests(unittest.TestCase):
    def test_registry_paths_and_references(self):
        sources={s['id'] for s in SRC['records']}
        ids=[]
        for row in CAT['records']:
            ids.append(row['id'])
            self.assertTrue((ROOT/row['path']).is_file(), row['id'])
            self.assertTrue(set(row['source_ids'])<=sources, row['id'])
            self.assertGreater(len(row['queries']),1)
        self.assertEqual(len(ids),len(set(ids)))
    def test_no_visual_reference_atlas_or_old_references(self):
        for folder in ('inspiration','references'):
            self.assertFalse((ROOT/folder).exists(), folder)
        self.assertFalse((ROOT/'scripts/reference_selector.py').exists())
    def test_retrieval_korean_and_english(self):
        self.assertIn('P07',[r['id'] for r in mod.rank('화면의 비례와 리듬')[:8]])
        self.assertIn('P11',[r['id'] for r in mod.rank('폼 상태 일관성')[:8]])
        self.assertIn('P14',[r['id'] for r in mod.rank('evaluation rubric')[:8]])
    def test_no_generic_style_recipes(self):
        skill=(ROOT/'SKILL.md').read_text(encoding='utf8').lower()
        self.assertIn('no canonical aesthetic',skill)
        self.assertIn('no forced branch',skill)
    def test_references_are_papers_not_pictures(self):
        self.assertGreaterEqual(len(SRC['records']),40)
        self.assertFalse(list(ROOT.rglob('*.png')))
        self.assertFalse(list(ROOT.rglob('*.jpg')))

if __name__=='__main__': unittest.main()
