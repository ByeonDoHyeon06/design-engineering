"""Knowledge governance and retrieval noise tests; no web/browser required."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import knowledge_index
import knowledge_health

class KnowledgeGovernanceTests(unittest.TestCase):
    def test_registry_graph_has_no_broken_references(self):
        result = knowledge_health.inspect(ROOT)
        self.assertEqual(result["errors"], [], result)
        self.assertGreater(result["counts"]["cards"], 30)
        self.assertEqual(result["counts"]["concepts"], 22)

    def test_warns_about_potential_source_aliases_without_auto_merging(self):
        result = knowledge_health.inspect(ROOT)
        self.assertGreaterEqual(result["counts"]["potential_duplicate_source_groups"], 1)
        self.assertTrue(any("E4" in v and "A7" in v for v in result["warnings"]))
        self.assertTrue(any("source not referenced" in v for v in result["warnings"]))

    def test_can_disable_relative_cutoff_for_diagnostics(self):
        question = "한글 폰트 줄바꿈과 타이포그래피"
        broad = knowledge_index.search(question, top=10, relative_cutoff=0)
        focused = knowledge_index.search(question, top=10)
        self.assertTrue(broad)
        self.assertEqual(broad[0]["id"], "K16")
        self.assertEqual(focused[0]["id"], "K16")
        self.assertLessEqual(len(focused), len(broad))
        self.assertTrue(all(x["score"] >= focused[0]["score"] * 0.20 for x in focused))
        self.assertTrue(any(x["id"] == "P16" for x in broad))
        self.assertFalse(any(x["id"] == "P16" for x in focused))

    def test_explicit_source_scope_is_not_equated_to_claim_verification(self):
        results = knowledge_index.search("한글 폰트 줄바꿈과 타이포그래피", top=5)
        card = next(x for x in results if x["id"] == "K16")
        self.assertEqual(card["verified_claim_ids"], [])
        self.assertEqual(card["evidence_status"], "no_explicit_reviewed_claim_link")
        level = {s["id"]:s["access_level"] for s in card["source_context"]}
        self.assertEqual(level["N39"], "official_group_note_draft_reviewed")
        self.assertIn("S1", level)

    def test_bad_relative_cutoff_is_rejected(self):
        with self.assertRaises(ValueError):
            knowledge_index.search("any", relative_cutoff=-0.1)
        with self.assertRaises(ValueError):
            knowledge_index.search("any", relative_cutoff=1.1)

if __name__ == "__main__":
    unittest.main()
