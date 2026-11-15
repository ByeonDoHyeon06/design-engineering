"""Read-only Knowledge diagnostic tests: no invented certainty or automatic changes."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from design_engineering import knowledge_intelligence as ki, local_knowledge, cli


class KnowledgeIntelligenceTests(unittest.TestCase):
    def test_explain_abstains_without_inventing_evidence(self):
        unknown=ki.explain("unregistered question",[],[])
        self.assertEqual(unknown["state"],"no_registered_card_match")
        self.assertEqual(unknown["core_matches"],0)
        self.assertEqual(unknown["personal_matches"],0)
        self.assertIn("installed library",unknown["recommendation"])
        practitioner=ki.explain("Korean typography",[{
            "id":"K16","evidence_status":"no_explicit_reviewed_claim_link",
            "why_matched":{"fts":True,"concepts":["hangul_typography"]},
            "verified_claim_ids":[],"source_ids":["N39"]}],[])
        self.assertEqual(practitioner["state"],"matched_cards_without_explicit_checked_claim")
        self.assertTrue(practitioner["matched_research"][0]["matching_signals"]["fts"])
        self.assertEqual(practitioner["explicit_claim_linked_matches"],0)
        cited=ki.explain("responsive",[{"id":"K14","verified_claim_ids":["VC14"],
                    "source_ids":["S1"],"why_matched":{"fts":True}}],[])
        self.assertEqual(cited["state"],"registered_claim_linked_match")
        self.assertEqual(cited["explicit_claim_linked_matches"],1)

    def test_conflicts_are_only_lexical_review_candidates(self):
        rows=[
            {"id":"local:1","scope":"user","kind":"preference","status":"active",
             "text":"Prefer square corners for navigation cards","tags":["cards"]},
            {"id":"local:2","scope":"project","kind":"preference","status":"active",
             "text":"Avoid square corners on navigation cards","tags":["cards"]},
            {"id":"local:3","scope":"session","kind":"observation","status":"active",
             "text":"Avoid square corners on navigation cards","tags":[]},
            {"id":"local:4","scope":"project","kind":"preference","status":"archived",
             "text":"Prefer square corners on navigation cards","tags":[]},
            {"id":"local:5","scope":"project","kind":"preference","status":"active",
             "text":"Avoid intense red warning banners","tags":[]}
        ]
        data=ki.conflict_candidates(rows)
        self.assertEqual(data["candidate_count"],1,data)
        self.assertEqual(set(data["candidates"][0]["ids"]),{"local:1","local:2"})
        self.assertIn("square",data["candidates"][0]["common_terms"])
        self.assertIn("not_verified",data["candidates"][0]["status"])
        self.assertEqual(len(rows),5)
        self.assertEqual(rows[0]["status"],"active")

    def test_review_queue_reads_explicit_dates_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"knowledge").mkdir()
            (root/"knowledge/governance.json").write_text(json.dumps({
                "status_overrides":{
                    "source:S1":{"status":"active","review_due":"2026-01-04","reviewer":"tester"},
                    "method:K14":{"status":"needs_review","reviewer":"owner"},
                    "source:S2":{"status":"active"},
                    "source:S3":{"status":"active","review_due":"2027-01-04"},
                    "source:S4":{"status":"active","review_due":"not-a-date"}
                }
            }),encoding="utf-8")
            report=ki.source_review_queue(root,today="2026-11-15")
            self.assertEqual(report["date"],"2026-11-15")
            self.assertEqual(set(x["id"] for x in report["items"]),
                             {"source:S1","method:K14","source:S4"})
            self.assertTrue(any(x["reason"]=="invalid_explicit_review_due"
                                for x in report["items"]))
            self.assertNotIn("source:S2",str(report))

    def test_unified_cli_explanation_conflict_and_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"project").mkdir()
            home=root/"home"
            common=["--project",str(root/"project"),"--user-home",str(home)]
            def invoke(*args):
                output=io.StringIO()
                with contextlib.redirect_stdout(output):
                    status=cli.main(common+list(args))
                return status,json.loads(output.getvalue())
            a=local_knowledge.propose("Prefer square corners for navigation cards",
                                       scope="project",project=root/"project",home=home)
            local_knowledge.approve(a["proposal"],reviewer="owner",
                                     project=root/"project",home=home)
            b=local_knowledge.propose("Avoid square corners for navigation cards",
                                       scope="user",project=root/"project",home=home)
            local_knowledge.approve(b["proposal"],reviewer="owner",
                                     project=root/"project",home=home)
            status,report=invoke("context","--conflicts","--json")
            self.assertEqual(status,0)
            self.assertEqual(report["conflict_review"]["candidate_count"],1)
            status,explain=invoke("search","한글 타이포그래피","--scope","core",
                                  "--explain","--json")
            self.assertEqual(status,0)
            self.assertEqual(explain["personal_guidance"],[])
            self.assertEqual(explain["coverage"]["query"],"한글 타이포그래피")
            self.assertEqual(explain["coverage"]["core_matches"],len(explain["research"]))
            status,check=invoke("check","--review-due","--json")
            self.assertEqual(status,0)
            self.assertIn("recorded_review_queue",check)
            self.assertEqual(check["recorded_review_queue"]["items"],[])


if __name__=="__main__":
    unittest.main()
