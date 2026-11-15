"""Local Knowledge edits preserve review consent, history, scope and fingerprints."""
from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from design_engineering import resource_root, cli, local_knowledge as lk


class KnowledgeLifecycleTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root=Path(d.name)
        self.project=self.root/"project"
        self.project.mkdir()
        self.home=self.root/"home"
        self.kw={"project":self.project,"home":self.home}

    def call(self,*args):
        stdout=io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code=cli.main(["--project",str(self.project),"--user-home",str(self.home)]+list(args))
        return code,json.loads(stdout.getvalue())

    def initial(self):
        d=lk.propose("Prefer square interface cards",scope="project",**self.kw)
        return lk.approve(d["proposal"],reviewer="owner",**self.kw)["registered"]

    def test_revision_is_draft_until_approval_and_preserves_archived_entry(self):
        record=self.initial()
        draft=lk.propose_revision(record["id"],"Prefer rectangular cards with crisp geometry",
                                  scope="project",**self.kw)
        unchanged=lk.records(scopes=("project",),**self.kw)
        self.assertEqual([r["id"] for r in unchanged],[record["id"]])
        revised=lk.approve(draft["proposal"],reviewer="owner",**self.kw)["registered"]
        self.assertEqual(revised["replaces"],record["id"])
        active=lk.records(scopes=("project",),**self.kw)
        self.assertEqual([r["id"] for r in active],[revised["id"]])
        history=lk.records(scopes=("project",),include_archived=True,**self.kw)
        self.assertEqual(len(history),2)
        self.assertEqual(history[0]["status"],"archived")
        self.assertEqual(history[0]["replaced_by"],revised["id"])
        self.assertEqual(history[1]["status"],"active")

    def test_stale_revision_and_cross_project_are_rejected(self):
        initial=self.initial()
        draft=lk.propose_revision(initial["id"],"Use compact rectangular cards",
                                  scope="project",**self.kw)
        with self.assertRaisesRegex(lk.LocalKnowledgeError,"mismatch"):
            other=self.root/"other"
            other.mkdir()
            lk.approve(draft["proposal"],reviewer="owner",project=other,home=self.home)
        unrelated=lk.propose("Use contrasting headline sizes",scope="project",**self.kw)
        lk.approve(unrelated["proposal"],reviewer="owner",**self.kw)
        with self.assertRaisesRegex(lk.LocalKnowledgeError,"changed since drafting"):
            lk.approve(draft["proposal"],reviewer="owner",**self.kw)

    def test_editing_reference_requires_new_source_review(self):
        source=self.root/"source.md"
        source.write_text("Text provided by a customer.",encoding="utf-8")
        draft=lk.propose("Local licensed reference",kind="reference",
                         source_file=source,scope="project",**self.kw)
        item=lk.approve(draft["proposal"],reviewer="owner",**self.kw)["registered"]
        with self.assertRaisesRegex(lk.LocalKnowledgeError,"new source fingerprint"):
            lk.propose_revision(item["id"],"Changed reference",scope="project",**self.kw)

    def test_cli_knowledge_group_is_consistent_and_review_gated(self):
        initial=self.initial()
        code,r=self.call("knowledge","list","--scope","project","--json")
        self.assertEqual(code,0)
        self.assertEqual(r["count"],1)
        code,draft=self.call("knowledge","edit",initial["id"],
                    "Prefer rectangular cards and careful typography",
                    "--scope","project","--json")
        self.assertEqual(code,0)
        self.assertEqual(draft["replaces"],initial["id"])
        code,d=self.call("knowledge","list","--scope","project","--json")
        self.assertEqual(d["records"][0]["id"],initial["id"])
        code,approved=self.call("review",draft["proposal"],"--reviewer","owner","--approve","--json")
        self.assertEqual(code,0)
        new=approved["registered"]["id"]
        code,r=self.call("knowledge","list","--scope","project","--include-archived","--json")
        self.assertEqual(r["count"],2)
        code,r=self.call("knowledge","archive",new,"--scope","project",
                         "--reviewer","owner","--approve","--json")
        self.assertEqual(code,0)
        self.assertEqual(r["archived"],new)
        code,r=self.call("knowledge","list","--scope","project","--json")
        self.assertEqual(r["count"],0)

    def test_resource_root_is_source_checkout_in_repo(self):
        self.assertEqual(resource_root(),ROOT)
        self.assertTrue((resource_root()/"knowledge/catalog.json").is_file())


if __name__=="__main__":
    unittest.main()
