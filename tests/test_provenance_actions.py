"""v4.6: provenance integrity, no fake skill use, contextual action hypotheses."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from design_engineering import cli, evaluation, provenance, action_guidance
from validate_install import REQUIRED_FILES, REQUIRED_DIRS


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.base = Path(d.name)
        self.skill = self.base / "design-engineering"
        self.skill.mkdir()
        for name in REQUIRED_FILES:
            target = self.skill / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("sample file for identity check\n", encoding="utf-8")
        for name in REQUIRED_DIRS:
            (self.skill / name).mkdir(parents=True, exist_ok=True)
        self._git("init", "-q")
        self._git("remote", "add", "origin",
                  "https://github.com/ByeonDoHyeon06/design-engineering.git")
        self._git("add", ".")
        self._git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                  "commit", "-q", "-m", "fixture")
        self.agent_log = self.base / "execution.log"
        self.agent_log.write_text("Operator observed actual skill invocation in this fixture.\n",
                                  encoding="utf-8")
        self.brief_path = self.base / "tasks.json"
        catalog = json.loads((ROOT / "benchmarks" / "design-tasks.json").read_text(encoding="utf-8"))
        catalog["tasks"] = catalog["tasks"][:2]
        self.brief_path.write_text(json.dumps(catalog), encoding="utf-8")
        self.run = self.base / "pilot"

    def _git(self, *args):
        proc = subprocess.run(["git", "-C", str(self.skill), *args],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_identity_is_exact_repo_path_commit_and_clean_tree(self):
        data = provenance.source_identity(self.skill)
        self.assertTrue(data["source_verified"], data)
        self.assertEqual(data["status"], "VERIFIED_SOURCE_IDENTITY")
        self.assertEqual(len(data["skill_sha256"]), 64)
        self.assertEqual(len(data["git_commit"]), 40)
        self.assertEqual(data["root"], str(self.skill.resolve()))
        mismatch = provenance.source_identity(self.skill, expected_repository="AgentsORG/design-engineering")
        self.assertEqual(mismatch["status"], "MISMATCHED_REPOSITORY")
        self.assertFalse(mismatch["source_verified"])

    def test_not_executed_cannot_be_mistaken_for_loaded_skill(self):
        output = self.base / "unused.json"
        status = provenance.capture(skill_root=self.skill, out=output, usage="not_executed")
        self.assertFalse(status["attribution_eligible"])
        data = provenance.verify(output)
        self.assertTrue(data["ok"])
        self.assertFalse(data["attribution_eligible"])
        with self.assertRaisesRegex(provenance.ProvenanceError, "execution log"):
            provenance.capture(skill_root=self.skill,out=self.base/"bad.json",usage="skill_invoked")
        with self.assertRaisesRegex(FileExistsError, "exists"):
            provenance.capture(skill_root=self.skill,out=output)

    def test_git_remote_and_changed_skill_invalidate_provenance(self):
        path = self.base / "executed.json"
        status = provenance.capture(skill_root=self.skill, out=path,
                                    usage="skill_invoked", execution_log=self.agent_log)
        self.assertTrue(status["attribution_eligible"])
        self.assertTrue(provenance.verify(path)["attribution_eligible"])
        (self.skill / "SKILL.md").write_text("modified instructions\n", encoding="utf-8")
        changed = provenance.verify(path)
        self.assertFalse(changed["ok"])
        self.assertTrue(any("changed" in e for e in changed["errors"]))
        self.assertFalse(changed["attribution_eligible"])

    def test_external_material_disqualifies_exclusive_skill_attribution(self):
        path = self.base / "alternate.json"
        status = provenance.capture(skill_root=self.skill,out=path,
                                    usage="skill_invoked",execution_log=self.agent_log,
                                    alternate_material=self.agent_log)
        self.assertFalse(status["attribution_eligible"])
        self.assertFalse(provenance.verify(path)["attribution_eligible"])

    def test_eval_attribution_is_private_and_opt_in(self):
        evaluation.init_run(tasks_file=self.brief_path, out=self.run,
                            seed=7,agent="test",model="test",effort="test")
        before = evaluation.validate_run(self.run, require_provenance=True)
        self.assertFalse(before["ok"])
        self.assertEqual(len(before["missing_provenance"]), 4)
        empty = self.base / "unused.json"
        loaded = self.base / "used.json"
        provenance.capture(skill_root=self.skill, out=empty, usage="not_executed")
        provenance.capture(skill_root=self.skill, out=loaded, usage="skill_invoked",
                           execution_log=self.agent_log)
        with self.assertRaisesRegex(evaluation.EvaluationError, "Skill arm requires"):
            evaluation.attach_provenance(run=self.run,task_id="corporate-home",
                                        condition="skill",manifest_file=empty)
        with self.assertRaisesRegex(evaluation.EvaluationError, "NOT_EXECUTED"):
            evaluation.attach_provenance(run=self.run,task_id="corporate-home",
                                        condition="baseline",manifest_file=loaded)
        for task in json.loads(self.brief_path.read_text())["tasks"]:
            evaluation.attach_provenance(run=self.run,task_id=task["id"],
                                        condition="skill",manifest_file=loaded)
            evaluation.attach_provenance(run=self.run,task_id=task["id"],
                                        condition="baseline",manifest_file=empty)
        checked = evaluation.validate_run(self.run, require_provenance=True)
        self.assertTrue(checked["ok"],checked)
        self.assertTrue(checked["attribution_ready"])
        self.assertFalse(checked["ready_for_attributed_review"])  # no images yet
        public = (self.run/"blind/packet.json").read_text(encoding="utf-8")
        self.assertNotIn("provenance",public)
        self.assertNotIn("skill_invoked",public)
        self.agent_log.write_text("altered\n")
        broken = evaluation.validate_run(self.run)
        self.assertFalse(broken["ok"])
        self.assertTrue(broken["invalid_provenance"])

    def test_provenance_cli_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["provenance","inspect","--skill-root",str(self.skill),"--json"])
        self.assertEqual(code,0)
        self.assertTrue(json.loads(stdout.getvalue())["source_verified"])


class ActionGuidanceTests(unittest.TestCase):
    def test_all_practice_references_are_real_and_separate(self):
        catalog = action_guidance.load(ROOT)
        self.assertEqual(len(catalog["practices"]),7)
        for row in catalog["practices"]:
            self.assertTrue(row["countercases"])
            self.assertTrue(row["checks"])
            self.assertEqual(row["guidance_kind"],"practitioner_design_hypothesis")

    def test_contextual_dense_schedule_hypothesis(self):
        research=[{"id":"K06","evidence_status":"no_explicit_reviewed_claim_link",
                   "verified_claim_ids":[],"source_ids":["S1"]}]
        data=action_guidance.suggest("72개 세션의 프로그램에서 연사를 어떻게 찾을까?",
                                     research,root=ROOT)
        self.assertEqual(data["state"],"matched_practice_hypotheses")
        first=data["suggestions"][0]
        self.assertEqual(first["id"],"AG01")
        self.assertEqual(first["practice_type"],"design_hypothesis_not_research_finding")
        self.assertIn("K06",[p["id"] for p in first["linked_retrieved_cards"]])
        self.assertTrue(first["countercases"])
        self.assertTrue(first["checks"])

    def test_no_retrieved_evidence_or_unrelated_question_never_fills_slots(self):
        none=action_guidance.suggest("72개 세션이 너무 많아",[],root=ROOT)
        self.assertEqual(none["suggestions"],[])
        unknown=action_guidance.suggest("How to optimize spacecraft propellant?",
                                        [{"id":"K06"}],root=ROOT)
        self.assertEqual(unknown["suggestions"],[])
        self.assertEqual(unknown["state"],"no_contextual_practice_match")
        self.assertEqual(action_guidance.suggest("",[{"id":"K06"}],root=ROOT)["suggestions"],[])
        other=action_guidance.suggest("72개 세션을 분류하고 싶어",
                                     [{"id":"K16"}],root=ROOT)
        self.assertEqual(other["suggestions"],[])

    def test_search_actions_are_additive_not_a_scientific_score(self):
        def call(*args):
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                code=cli.main(["search","한글 폰트 줄바꿈","--scope","core","--json",*args])
            self.assertEqual(code,0)
            return json.loads(output.getvalue())
        original=call()
        augmented=call("--actions","--explain")
        self.assertEqual(original["research"],augmented["research"])
        self.assertIn("practice_guidance",augmented)
        self.assertIn("coverage",augmented)
        for item in augmented["practice_guidance"]["suggestions"]:
            self.assertEqual(item["practice_type"],"design_hypothesis_not_research_finding")
        self.assertNotIn("practice_guidance",original)


if __name__=="__main__":
    unittest.main()
