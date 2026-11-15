"""Design execution contract: preserve content, distinct composition and actual revision evidence."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/"scripts"))
from design_engineering import cli, design_plan
from visual_critique import audit


class DesignExecutionTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base=Path(temp.name)
        self.brief={"schema_version":1,"goal":"Help prospective buyers understand two services",
            "audience":"Developers evaluating technical tooling",
            "primary_action":"Request a guided product conversation",
            "constraints":["No invented security certifications","320px typography and interaction"],
            "content_blocks":[
                {"id":"intro","role":"hero","content":"Real-world product text supplied by the customer"},
                {"id":"services","role":"comparison","content":"A genuine comparison of the available services"},
                {"id":"contact","role":"contact","content":"Speak with the engineering support team"}]}
        self.brief_file=self.base/"brief.json"
        self.brief_file.write_text(json.dumps(self.brief),encoding="utf-8")
        self.plan_file=self.base/"plan.json"

    def _ready_plan(self):
        plan=design_plan.scaffold(self.brief)
        plan["principles"]["content_roles_reviewed"]=True
        plan["principles"]["research_refs"]=["source:N39","method:K18"]
        plan["principles"]["personal_preference_refs"]=["local:abc123"]
        a,b=plan["directions"]
        a.update({"information_relationship":"Prioritize the user need and then explain the offerings",
                  "layout_strategy":"Asymmetric introductory column with a compact comparison table",
                  "tradeoffs":"High upfront clarity but less visual immersion for first-time users",
                  "primary_action_visibility":"Show contact after the short explicit overview"})
        b.update({"information_relationship":"Lead with product differences to answer practical selection questions",
                  "layout_strategy":"Progressive two-stage comparison with contextual examples",
                  "tradeoffs":"Strong comparison but the first proposition may be delayed",
                  "primary_action_visibility":"Show contact alongside the comparison conclusion"})
        b["content_order"]=["services","intro","contact"]
        plan["selected_direction"]="direction-a"
        plan["selection_rationale"]="The target audience needs an immediate product overview before comparing options."
        for asset in plan["visual_assets"]:
            asset.update({"kind":"none","origin":"original","state":"reviewed"})
        plan["quality_checks"].update({
            "content_fidelity":"Verify that supplied service descriptions are maintained intact",
            "keyboard_and_focus":"Test all interactive components using keyboard focus",
            "contrast_and_legibility":"Inspect heading and body contrast on rendered screenshots",
            "image_cropping":"No image is used, so no crop risks remain in this plan",
            "localized_copy":"Check real English and Korean titles at narrow widths",
            "interaction_states":"Inspect contact form success, errors and empty state"})
        return plan

    def test_scaffold_does_not_guess_design_or_provenance(self):
        made=design_plan.create(self.brief_file,self.plan_file)
        self.assertEqual(made["state"],"draft")
        plan=json.loads(self.plan_file.read_text(encoding="utf-8"))
        self.assertEqual(len(plan["directions"]),2)
        self.assertEqual(plan["directions"][0]["layout_strategy"],"")
        self.assertIsNone(plan["selected_direction"])
        self.assertEqual(plan["visual_assets"][0]["origin"],"undecided")
        self.assertFalse(design_plan.validate(self.plan_file)["ready"])
        with self.assertRaises(FileExistsError):
            design_plan.create(self.brief_file,self.plan_file)

    def test_completed_plan_passes_and_invalid_claims_are_rejected(self):
        plan=self._ready_plan()
        self.assertTrue(design_plan.inspect(plan,require_ready=True)["ok"])
        plan["principles"]["research_refs"]=["a fabricated citation without an ID"]
        self.assertFalse(design_plan.inspect(plan)["ok"])
        plan["principles"]["research_refs"]=["source:N39"]
        plan["visual_assets"][0].update({"kind":"photo","origin":"licensed"})
        result=design_plan.inspect(plan)
        self.assertTrue(result["ok"])
        self.assertFalse(result["ready"])
        self.assertTrue(any("rights" in w or "source" in w for w in result["warnings"]))

    def test_duplicate_directions_and_missing_blocks_are_not_ready(self):
        plan=self._ready_plan()
        plan["directions"][1]=dict(plan["directions"][0])
        plan["directions"][1]["id"]="direction-b"
        self.assertFalse(design_plan.inspect(plan)["ready"])
        plan=self._ready_plan()
        plan["directions"][1]["content_order"]=["intro","intro","contact"]
        self.assertFalse(design_plan.inspect(plan)["ok"])

    def test_screenshot_revision_requires_different_actual_bytes(self):
        before=self.base/"before.png"
        after=self.base/"after.png"
        before.write_bytes(b"\x89PNG\r\n\x1a\n" + b"before capture content")
        after.write_bytes(before.read_bytes())
        critique={
            "screenshots":["before.png","after.png"],"manual_review":"COMPLETE",
            "observations":[{
                "id":"VIS-001","dimension":"hierarchy","viewport":390,
                "observation":"Important contact action is visually buried.",
                "before_screenshot":"before.png",
                "after_screenshot":"after.png",
                "after_observation":"The action now has clear visual emphasis.",
                "status":"fixed","detected_by":"manual",
                "proposed_change":"Improve action grouping"}]}
        result=audit(critique,self.base)
        self.assertFalse(result["ok"])
        self.assertEqual(result["confirmed_fixes"],0)
        self.assertTrue(any("identical bytes" in e for e in result["errors"]))
        after.write_bytes(b"\x89PNG\r\n\x1a\n" + b"new capture after actual editing")
        result=audit(critique,self.base)
        self.assertTrue(result["ok"],result)
        self.assertEqual(result["confirmed_fixes"],1)
        critique["observations"][0]["after_screenshot"]="../outside.png"
        self.assertFalse(audit(critique,self.base)["ok"])

    def test_cli_plan_validate_and_visual_review(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            code=cli.main(["design","plan","--brief",str(self.brief_file),
                           "--out",str(self.plan_file),"--json"])
        self.assertEqual(code,0,out.getvalue())
        self.assertTrue(self.plan_file.exists())
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            code=cli.main(["design","validate",str(self.plan_file),"--json"])
        self.assertEqual(code,0,out.getvalue())
        self.assertFalse(json.loads(out.getvalue())["ready"])
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            code=cli.main(["design","validate",str(self.plan_file),"--require-ready","--json"])
        self.assertEqual(code,1)
        self.plan_file.write_text(json.dumps(self._ready_plan()),encoding="utf-8")
        self.assertEqual(cli.main(["design","validate",str(self.plan_file),"--require-ready"]),0)


if __name__=="__main__":
    unittest.main()
