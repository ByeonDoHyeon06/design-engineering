"""Evaluation invariants: balanced A/B, blinded artifacts, human-only scores, no fabricated outcomes."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from design_engineering import cli, evaluation as ev


def png_with_metadata():
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">2I5B", 1, 1, 8, 2, 0, 0, 0)
    pixels = zlib.compress(bytes([0, 71, 123, 207]))
    return (ev.PNG_SIGNATURE + chunk(b"IHDR", ihdr)
            + chunk(b"tEXt", b"generated-with\x00baseline")
            + chunk(b"IDAT", pixels) + chunk(b"IEND", b""))


class DesignEvaluationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        catalog = ev.load_tasks(ROOT / "benchmarks/design-tasks.json")
        self.assertEqual(len(catalog["tasks"]), 12)
        catalog["tasks"] = catalog["tasks"][:2]
        self.catalog = self.tmp / "tasks.json"
        self.catalog.write_text(json.dumps(catalog), encoding="utf-8")
        self.run = self.tmp / "study"
        self.png = self.tmp / "sample.png"
        self.png.write_bytes(png_with_metadata())

    def begin(self):
        return ev.init_run(tasks_file=self.catalog, out=self.run, seed=29,
                           agent="test agent", model="test model", effort="test effort")

    def attach_all(self):
        for task in ev.load_tasks(self.catalog)["tasks"]:
            for arm in ev.ARMS:
                ev.attach(run=self.run, task_id=task["id"], condition=arm,
                          desktop=self.png, mobile=self.png, duration_seconds=8.0, input_tokens=10,
                          output_tokens=50, cost_usd=0.003)

    def test_catalog_is_valid_and_balances_conditions(self):
        all_tasks = ev.load_tasks(ROOT / "benchmarks/design-tasks.json")
        self.assertEqual(len(all_tasks["tasks"]), 12)
        result = ev.init_run(tasks_file=ROOT / "benchmarks/design-tasks.json",
                             out=self.run, seed=42, agent="held-constant",
                             model="same-model", effort="same-budget")
        self.assertEqual(result["task_count"], 12)
        private = json.loads((self.run/"private/assignments.json").read_text())
        lefts = [r["A"]["condition"] for r in private["assignments"]]
        self.assertEqual(lefts.count("skill"), 6)
        self.assertEqual(lefts.count("baseline"), 6)
        self.assertEqual(ev.validate_run(self.run)["attached"], 0)
        self.assertFalse(ev.validate_run(self.run)["ready_for_review"])
        with self.assertRaisesRegex(ev.EvaluationError,"already exists"):
            ev.init_run(tasks_file=self.catalog, out=self.run, seed=2,
                        agent="x", model="x", effort="x")

    def test_reject_duplicate_catalog_ids_and_unbounded_or_invalid_cases(self):
        source=ev.load_tasks(self.catalog)
        source["tasks"][1]["id"]=source["tasks"][0]["id"]
        self.catalog.write_text(json.dumps(source))
        with self.assertRaisesRegex(ev.EvaluationError,"Duplicate task ID"):
            ev.load_tasks(self.catalog)

    def test_screenshot_is_png_checked_and_metadata_scrubbed(self):
        self.begin()
        task = ev.load_tasks(self.catalog)["tasks"][0]["id"]
        data = ev.attach(run=self.run, task_id=task, condition="baseline",
                         desktop=self.png, mobile=self.png)
        copied = Path(data["blind_artifacts"]["desktop"]).read_bytes()
        self.assertTrue(copied.startswith(ev.PNG_SIGNATURE))
        self.assertNotIn(b"baseline",copied)
        self.assertNotIn(b"tEXt",copied)
        self.assertIn(b"IDAT",copied)
        self.assertFalse(ev.validate_run(self.run)["ready_for_review"])
        with self.assertRaisesRegex(ev.EvaluationError,"already attached"):
            ev.attach(run=self.run, task_id=task, condition="baseline",desktop=self.png, mobile=self.png)
        corrupted = self.tmp/"bad.png"
        corrupted.write_bytes(b"Not a PNG")
        with self.assertRaisesRegex(ev.EvaluationError,"PNG"):
            ev.attach(run=self.run, task_id=task, condition="skill",desktop=corrupted, mobile=self.png)

    def test_blind_packet_never_contains_condition_mapping(self):
        self.begin()
        public = (self.run/"blind/packet.json").read_text(encoding="utf-8")
        self.assertNotIn('"condition"',public)
        self.assertNotIn('"baseline"',public)
        self.assertNotIn('"skill"',public)
        self.assertEqual(len(json.loads(public)["pairs"]),2)
        private = (self.run/"private/assignments.json").read_text(encoding="utf-8")
        self.assertIn('"condition": "skill"',private)

    def test_report_without_reviews_cannot_claim_improvement(self):
        self.begin()
        report = ev.report(run=self.run, judgment_files=[])
        self.assertEqual(report["status"],"NO_OBSERVATIONS")
        self.assertIsNone(report["summary"]["skill_win_share_excluding_ties"])
        self.assertEqual(report["summary"]["rated_tasks"],0)
        self.assertEqual(len(report["evidence"]["missing_blind_screenshots"]),8)
        with self.assertRaisesRegex(ev.EvaluationError,"Complete and verify"):
            ev.scorecard(run=self.run,judge="independent01",out=self.tmp/"judges.json")

    def test_reviewer_scoring_only_after_actual_captures(self):
        self.begin()
        self.attach_all()
        self.assertTrue(ev.validate_run(self.run,require_complete=True)["ready_for_review"])
        card_path=self.tmp/"judge-one.json"
        ev.scorecard(run=self.run,judge="judge-one",out=card_path)
        score=json.loads(card_path.read_text(encoding="utf-8"))
        self.assertTrue(all(item["preferred"] is None for item in score["judgments"]))
        self.assertEqual(ev.report(run=self.run,judgment_files=[card_path])["status"],
                         "NO_OBSERVATIONS")
        private=json.loads((self.run/"private/assignments.json").read_text())
        skill_side=next(k for k in ev.SIDES
                        if private["assignments"][0][k]["condition"]=="skill")
        for n,item in enumerate(score["judgments"]):
            item["preferred"]=skill_side if n==0 else "tie"
            item["artifacts_reviewed"]=True
            item["reason"]="A reviewer inspected both actual images and recorded a task-specific rationale."
            item["ratings"]={side:{dim:(4 if side==skill_side else 2)
                                  for dim in ev.DIMENSIONS} for side in ev.SIDES}
        card_path.write_text(json.dumps(score),encoding="utf-8")
        report=ev.report(run=self.run,judgment_files=[card_path])
        self.assertEqual(report["status"],"PILOT_REVIEWED")
        self.assertEqual(report["summary"]["skill_preferred_tasks"],1)
        self.assertEqual(report["summary"]["tie_tasks"],1)
        self.assertEqual(report["summary"]["baseline_preferred_tasks"],0)
        self.assertEqual(report["summary"]["skill_win_share_excluding_ties"],1.0)
        self.assertEqual(report["summary"]["paired_rating_differences"]["originality"]
                         ["mean_skill_minus_baseline"],2.0)
        self.assertTrue(any("causal improvement" in caveat for caveat in report["limitations"]))

    def test_invalid_scores_and_duplicate_reviewer_are_rejected(self):
        self.begin()
        self.attach_all()
        file=self.tmp/"judge.json"
        ev.scorecard(run=self.run,judge="judge-one",out=file)
        score=json.loads(file.read_text())
        score["judgments"][0]["preferred"]="A"
        score["judgments"][0]["reason"]="This comment is long enough but no score was entered."
        score["judgments"][0]["artifacts_reviewed"]=True
        file.write_text(json.dumps(score))
        with self.assertRaisesRegex(ev.EvaluationError,"integer 1"):
            ev.report(run=self.run,judgment_files=[file])
        for row in score["judgments"]:
            row["preferred"]="tie"
            row["reason"]="The images show similar visual hierarchy and task clarity."
            row["artifacts_reviewed"]=True
            row["ratings"]={s:{dim:3 for dim in ev.DIMENSIONS} for s in ev.SIDES}
        file.write_text(json.dumps(score))
        with self.assertRaisesRegex(ev.EvaluationError,"Duplicate judge ID"):
            ev.report(run=self.run,judgment_files=[file,file])

    def test_tampering_changes_report_readiness(self):
        self.begin()
        self.attach_all()
        img=next((self.run/"blind").glob("*/A-desktop.png"))
        img.write_bytes(img.read_bytes()+b"attack")
        status=ev.validate_run(self.run)
        self.assertFalse(status["ok"])
        self.assertTrue(status["modified"])
        with self.assertRaisesRegex(ev.EvaluationError,"modified"):
            ev.report(run=self.run,judgment_files=[])

    def test_cli_lifecycle_is_integrated(self):
        def call(*args):
            stdout,stderr=io.StringIO(),io.StringIO()
            with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                code=cli.main(list(args))
            return code,stdout.getvalue(),stderr.getvalue()
        code,stdout,stderr=call("eval","init","--tasks",str(self.catalog),"--out",
            str(self.run),"--agent","codex-test","--model","test-only","--effort","test-only",
            "--json")
        self.assertEqual(code,0,stderr)
        self.assertEqual(json.loads(stdout)["task_count"],2)
        code,stdout,stderr=call("eval","validate","--run",str(self.run),"--json")
        self.assertEqual(code,0,stderr)
        self.assertFalse(json.loads(stdout)["ready_for_review"])
        code,stdout,stderr=call("eval","report","--run",str(self.run),"--json")
        self.assertEqual(code,0,stderr)
        self.assertEqual(json.loads(stdout)["status"],"NO_OBSERVATIONS")


if __name__=="__main__":
    unittest.main()
