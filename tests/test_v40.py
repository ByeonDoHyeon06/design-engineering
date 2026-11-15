"""Design Engineering v4: graph, human-governed changes, archive-aware search."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import knowledge_graph
import knowledge_governance
import knowledge_index

class V40Tests(unittest.TestCase):
    def test_full_legacy_graph_is_valid_and_nonduplicated(self):
        graph=knowledge_graph.build(ROOT)
        self.assertEqual(graph["errors"],[],graph["errors"])
        self.assertEqual(graph["counts"]["method"],41)
        self.assertEqual(graph["counts"]["source"],55)
        self.assertEqual(graph["counts"]["claim"],18)
        self.assertEqual(graph["counts"]["concept"],22)
        self.assertEqual(graph["counts"]["practice"],7)
        self.assertEqual(len({n["id"] for n in graph["nodes"]}),len(graph["nodes"]))
        self.assertGreater(len(graph["edges"]),100)

    def test_source_impact_traverses_claims_methods_concepts(self):
        graph=knowledge_graph.build(ROOT)
        affected={x["id"] for x in knowledge_graph.impact(graph,"source:N39")["affected"]}
        self.assertIn("method:K16",affected)
        self.assertIn("concept:hangul_typography",affected)

    def test_alias_and_cycle_rejections(self):
        base=knowledge_graph.read_json(ROOT,knowledge_graph.GOVERNANCE)
        invalid=copy.deepcopy(base)
        invalid["aliases"]={"method:K16":{"target":"method:K17","reviewer":"reviewer","reason":"bad shadow"}}
        self.assertTrue(any("shadows" in x for x in knowledge_graph.build(ROOT,invalid)["errors"]))
        invalid=copy.deepcopy(base)
        invalid["concept_relations"].append({"source":"concept:visual_composition",
                                               "target":"concept:hangul_typography","relation":"broader"})
        self.assertTrue(any("cycle" in x for x in knowledge_graph.build(ROOT,invalid)["errors"]))

    def _sandbox(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        shutil.copytree(ROOT/"knowledge",root/"knowledge",
                        ignore=shutil.ignore_patterns(".cache"))
        shutil.copytree(ROOT/"methods",root/"methods")
        return root

    def test_lifecycle_archive_is_explicit_and_searchable_for_audit(self):
        root=self._sandbox()
        proposed=knowledge_governance.propose(root,"status",reviewer="test-reviewer",
             reason="Explicit deprecation test",id="method:K16",status="archived")
        path=root/"proposal.json";path.write_text(json.dumps(proposed),encoding="utf-8")
        with self.assertRaises(knowledge_governance.GovernanceError):
            knowledge_governance.approve(root,path,"test-reviewer")
        with self.assertRaises(knowledge_governance.GovernanceError):
            knowledge_governance.approve(root,path,"other",confirm=True)
        result=knowledge_governance.approve(root,path,"test-reviewer",confirm=True)
        self.assertEqual(result["applied"],"status")
        with self.assertRaises(knowledge_governance.GovernanceError):
            knowledge_governance.approve(root,path,"test-reviewer",confirm=True)
        query="한글 폰트 줄바꿈과 타이포그래피"
        db=root/"search.sqlite"
        regular=knowledge_index.search(query,db_path=db,root=root,top=10)
        audit=knowledge_index.search(query,db_path=db,root=root,top=10,include_inactive=True)
        self.assertNotIn("K16",[x["id"] for x in regular])
        self.assertIn("K16",[x["id"] for x in audit])
        self.assertEqual(next(x for x in audit if x["id"]=="K16")["lifecycle_status"],"archived")

    def test_proposal_rejects_stale_governance(self):
        root=self._sandbox()
        p=knowledge_governance.propose(root,"alias",reviewer="human",reason="legacy alias",
                                       alias="source:oldN39",target="source:N39")
        old=root/knowledge_graph.GOVERNANCE
        changed=json.loads(old.read_text(encoding="utf-8"))
        changed["description"]+=" review"
        old.write_text(json.dumps(changed),encoding="utf-8")
        proposal=root/"proposal.json";proposal.write_text(json.dumps(p),encoding="utf-8")
        with self.assertRaisesRegex(knowledge_governance.GovernanceError,"changed"):
            knowledge_governance.approve(root,proposal,"human",confirm=True)

    def test_equivalence_needs_human_and_preserves_both_sources(self):
        root=self._sandbox()
        p=knowledge_governance.propose(root,"equivalence",reviewer="researcher",
             reason="same DOI, editions still kept separately pending review",
             a="source:E4",b="source:A7")
        target=root/"eq.json";target.write_text(json.dumps(p),encoding="utf-8")
        knowledge_governance.approve(root,target,"researcher",confirm=True)
        graph=knowledge_graph.build(root)
        self.assertEqual(graph["errors"],[])
        self.assertEqual(len(graph["equivalences"]),1)
        self.assertIn("source:E4",{x["id"] for x in graph["nodes"]})
        self.assertIn("source:A7",{x["id"] for x in graph["nodes"]})

    def test_graph_export_is_deterministic(self):
        a=knowledge_graph.build(ROOT)
        b=knowledge_graph.build(ROOT)
        self.assertEqual(a,b)
        self.assertEqual(a["schema_version"],4)
        self.assertNotIn("model_prediction",a)

    def test_missing_source_is_blocking_not_inferred(self):
        state=knowledge_graph.read_json(ROOT,knowledge_graph.GOVERNANCE)
        state["status_overrides"]["source:NOTREAL"]={"status":"needs_review",
              "reason":"injected","reviewer":"test"}
        self.assertTrue(any("missing node" in s for s in knowledge_graph.build(ROOT,state)["errors"]))

    def test_local_graph_does_not_promote_unreviewed_claims(self):
        g=knowledge_graph.build(ROOT)
        unreviewed=next(n for n in g["nodes"] if n["id"]=="source:N39")
        self.assertEqual(unreviewed["metadata"]["access_level"],"official_group_note_draft_reviewed")
        self.assertEqual(unreviewed["status"],"active")
        k16=next(n for n in g["nodes"] if n["id"]=="method:K16")
        self.assertNotIn("verified_claims",k16["metadata"])

if __name__=="__main__":
    unittest.main()
