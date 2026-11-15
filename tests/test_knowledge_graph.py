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
import query_understanding
from knowledge_ingest import prepare, commit, IngestError

class KnowledgeGraphTests(unittest.TestCase):
    def test_authoritative_graph_is_valid_and_nonduplicated(self):
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

    def test_archive_source_flags_active_dependents_and_overdue_reviews(self):
        state=knowledge_graph.read_json(ROOT,knowledge_graph.GOVERNANCE)
        state["status_overrides"]["source:N39"]={"status":"archived",
            "reason":"Simulated retraction review","reviewer":"tester","review_due":"2020-01-01"}
        graph=knowledge_graph.build(ROOT,state)
        self.assertEqual(graph["errors"],[])
        self.assertTrue(any("review overdue: source:N39" in v for v in graph["warnings"]))
        self.assertTrue(any("active dependency on inactive source: method:K16" in v
                            for v in graph["warnings"]))

    def test_reviewed_equivalence_resolves_warning_but_not_records(self):
        state=knowledge_graph.read_json(ROOT,knowledge_graph.GOVERNANCE)
        state["equivalences"].append({"a":"source:E4","b":"source:A7",
            "reviewer":"tester","reason":"Matching DOI inspected"})
        graph=knowledge_graph.build(ROOT,state)
        self.assertEqual(graph["errors"],[])
        self.assertFalse(any("potential source alias: E4, A7" in w for w in graph["warnings"]))
        self.assertEqual(sum(1 for n in graph["nodes"] if n["id"] in ("source:E4","source:A7")),2)

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

    def test_bilingual_topic_guard_avoids_generic_out_of_domain_matches(self):
        negatives=("지구 맨틀의 광물 결정과 판 구조론",
                   "코드 컴파일러의 SSA 중간 표현 최적화")
        for question in negatives:
            self.assertEqual(knowledge_index.search(question,top=5),[])

    def test_korean_verb_nominalization_in_findability_queries(self):
        question="프로그램이 많은 행사에서 관심 있는 발표를 빨리 찾는 방법"
        result=query_understanding.analyze(question)
        self.assertIn("navigation_findability",[c["id"] for c in result["concepts"]])
        found=[x["id"] for x in knowledge_index.search(question,top=5)]
        self.assertTrue(set(found)&{"P06","K06"},found)

    def test_archived_source_is_not_returned_as_current_verified_evidence(self):
        root=self._sandbox()
        file=root/knowledge_graph.GOVERNANCE
        state=json.loads(file.read_text(encoding="utf-8"))
        state["status_overrides"]["source:S1"]={"status":"archived","reviewer":"researcher",
            "reason":"Simulated official source withdrawal"}
        file.write_text(json.dumps(state),encoding="utf-8")
        query="모바일 앵커 도착점이 고정 헤더 뒤에 가려짐"
        db=root/"search.sqlite"
        current=knowledge_index.search(query,root=root,db_path=db,top=15,verified_only=True)
        historic=knowledge_index.search(query,root=root,db_path=db,top=15,
                                        verified_only=True,include_inactive=True)
        self.assertNotIn("K14",[r["id"] for r in current])
        older=next(r for r in historic if r["id"]=="K14")
        self.assertEqual(older["evidence_status"],"source_claims_checked_inactive_provenance")
        self.assertTrue(any(s["id"]=="S1" and s["lifecycle_status"]=="archived"
                            for s in older["source_context"]))

    def test_duplicate_doi_ingestion_is_rejected_before_catalog_mutation(self):
        root=self._sandbox()
        sample=root/"paper.md"
        sample.write_text("Test participants compared two different interfaces. "*6,encoding="utf-8")
        review=prepare(sample,title="Candidate duplicate",authors="Researcher",
                       url="https://www.w3.org/TR/klreq/",local_dir=root/"review-queue")
        data=json.loads(review.read_text(encoding="utf-8"))
        data["candidates"][0].update(status="approved",
            claim_text="A narrow hypothetical claim",
            limitations="Synthetic test data only",
            queries=["interface comparison"],problem_signals=["test"])
        review.write_text(json.dumps(data),encoding="utf-8")
        before=(root/"knowledge/catalog.json").read_bytes()
        with self.assertRaisesRegex(IngestError,"already registered"):
            commit(review,root=root,confirm=True,reviewer="human")
        self.assertEqual((root/"knowledge/catalog.json").read_bytes(),before)

    def test_local_graph_does_not_promote_unreviewed_claims(self):
        g=knowledge_graph.build(ROOT)
        unreviewed=next(n for n in g["nodes"] if n["id"]=="source:N39")
        self.assertEqual(unreviewed["metadata"]["access_level"],"official_group_note_draft_reviewed")
        self.assertEqual(unreviewed["status"],"active")
        k16=next(n for n in g["nodes"] if n["id"]=="method:K16")
        self.assertNotIn("verified_claims",k16["metadata"])

if __name__=="__main__":
    unittest.main()
