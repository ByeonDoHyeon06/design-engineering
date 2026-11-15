"""v4.1 CLI and personal Knowledge isolation/security contract."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from design_engineering import cli, local_knowledge as local


class LocalKnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.project=self.base/"project"
        self.project.mkdir()
        self.other=self.base/"other"
        self.other.mkdir()
        self.home=self.base/"user"
        self.kw={"project":self.project,"home":self.home}

    def test_preference_draft_requires_explicit_approval(self):
        draft=local.propose("나는 정교한 사각형 타이포그래피를 선호해",tags=["타이포그래피"],
                            **self.kw)
        self.assertEqual(draft["state"],"pending_review")
        self.assertEqual(local.records(**self.kw,scopes=("project",)),[])
        self.assertTrue(Path(draft["proposal"]).is_file())
        applied=local.approve(draft["proposal"],reviewer="human",**self.kw)
        self.assertEqual(applied["registered"]["kind"],"preference")
        self.assertEqual(applied["registered"]["scope"],"project")
        self.assertEqual(applied["registered"]["provenance"],"user_or_agent_supplied_not_scientifically_verified")
        self.assertIn("사각형",local.search("사각형 타이포그래피",**self.kw,scopes=("project",))[0]["text"])
        self.assertEqual(local.records(**self.kw,scopes=("user",)),[])
        with self.assertRaises(local.LocalKnowledgeError):
            local.approve(draft["proposal"],reviewer="human",**self.kw)

    def test_duplicate_and_related_are_not_silently_overwritten(self):
        first=local.propose("동그란 버튼보다 사각형 버튼이 좋아",**self.kw)
        local.approve(first["proposal"],reviewer="owner",**self.kw)
        second=local.propose("동그란 버튼보다 사각형 버튼이 좋아",**self.kw)
        self.assertTrue(second["related_candidates"])
        with self.assertRaisesRegex(local.LocalKnowledgeError,"duplicate"):
            local.approve(second["proposal"],reviewer="owner",**self.kw)
        rows=local.records(**self.kw,scopes=("project",))
        self.assertEqual(len(rows),1)

    def test_revision_rejected_after_concurrent_change(self):
        a=local.propose("사각형을 선호함",**self.kw)
        b=local.propose("줄 간격을 넉넉하게",**self.kw)
        local.approve(a["proposal"],reviewer="owner",**self.kw)
        with self.assertRaisesRegex(local.LocalKnowledgeError,"changed since drafting"):
            local.approve(b["proposal"],reviewer="owner",**self.kw)

    def test_observation_requires_proof_context(self):
        with self.assertRaisesRegex(local.LocalKnowledgeError,"--context and --outcome"):
            local.propose("제목이 잘려서 불편했음",kind="observation",**self.kw)
        item=local.propose("모바일 제목이 잘림",kind="observation",
                           context="390px 너비 Safari에서 확인",
                           outcome="제목이 두 번째 줄에서 잘림",**self.kw)
        result=local.approve(item["proposal"],reviewer="tester",**self.kw)
        self.assertEqual(result["registered"]["outcome"],"제목이 두 번째 줄에서 잘림")

    def test_personal_reference_is_never_verified_core_research(self):
        source=self.base/"research.md"
        source.write_text("# Private source\nTest information goes here.",encoding="utf-8")
        draft=local.propose("나중에 검토할 디자인 자료",kind="reference",
                            source_file=source,title="Private design notes",**self.kw)
        source.write_text("Changed document",encoding="utf-8")
        with self.assertRaisesRegex(local.LocalKnowledgeError,"changed or disappeared"):
            local.approve(draft["proposal"],reviewer="tester",**self.kw)
        self.assertEqual(local.records(**self.kw,scopes=("project",)),[])

    def test_project_reviewer_cannot_approve_other_project_draft(self):
        draft=local.propose("레이아웃은 수평 리듬이 중요해",**self.kw)
        with self.assertRaisesRegex(local.LocalKnowledgeError,"scope/project mismatch"):
            local.approve(draft["proposal"],reviewer="human",project=self.other,home=self.home)

    def test_session_is_isolated_and_requires_explicit_id(self):
        with patch.dict(os.environ,{"DE_SESSION_ID":""}):
            with self.assertRaisesRegex(local.LocalKnowledgeError,"DE_SESSION_ID"):
                local.location("session",project=self.project,home=self.home)
        with patch.dict(os.environ,{"DE_SESSION_HOME":str(self.base)}):
            one=local.propose("이번 시안에는 보라색을",scope="session",session_id="case_1001",**self.kw)
            local.approve(one["proposal"],reviewer="owner",session_id="case_1001",**self.kw)
            self.assertEqual(len(local.records(scopes=("session",),session_id="case_1001",**self.kw)),1)
            self.assertEqual(local.records(scopes=("session",),session_id="case_2002",**self.kw),[])

    def test_archive_hides_entry_but_keeps_history(self):
        d=local.propose("카드 둥글게 하지 말기",**self.kw)
        item=local.approve(d["proposal"],reviewer="owner",**self.kw)["registered"]
        local.archive(item["id"],scope="project",reviewer="owner",**self.kw)
        self.assertEqual(local.records(scopes=("project",),**self.kw),[])
        self.assertEqual(local.records(scopes=("project",),include_archived=True,**self.kw)[0]["status"],"archived")

    def test_research_and_personal_scopes_never_share_a_store(self):
        d=local.propose("내 취향: 얇은 테두리를 선호함",scope="user",**self.kw)
        local.approve(d["proposal"],reviewer="owner",**self.kw)
        self.assertEqual(local.records(scopes=("project",),**self.kw),[])
        self.assertEqual(len(local.records(scopes=("user",),**self.kw)),1)
        self.assertFalse((ROOT/"knowledge/individual.json").exists())
        with self.assertRaisesRegex(local.LocalKnowledgeError,"core"):
            local.propose("이 논문은 효과가 있다",scope="core",**self.kw)


class CLIContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.project=self.base/"project"
        self.project.mkdir()
        self.home=self.base/"home"
        self.prefix=["--project",str(self.project),"--user-home",str(self.home)]

    def call(self,*args):
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=cli.main(self.prefix+list(args))
        return code,out.getvalue(),err.getvalue()

    def test_cli_add_review_context_json_workflow(self):
        code,out,err=self.call("add","나는 정교한 사각형 UI가 좋아","--scope","user","--json")
        self.assertEqual(code,0,err)
        draft=json.loads(out)
        self.assertEqual(draft["kind"],"preference")
        code,out,err=self.call("review",draft["proposal"],"--approve","--reviewer","owner","--json")
        self.assertEqual(code,0,err)
        self.assertIn("registered",json.loads(out))
        code,out,err=self.call("context","--scope","user","--json")
        self.assertEqual(code,0,err)
        data=json.loads(out)
        self.assertEqual(len(data["guidance"]),1)
        self.assertEqual(data["guidance"][0]["evidence_status"],"personal_guidance_not_verified")
        code,out,err=self.call("search","사각형 UI","--scope","user","--json")
        self.assertEqual(code,0,err)
        result=json.loads(out)
        self.assertEqual(result["research"],[])
        self.assertTrue(result["personal_guidance"])

    def test_core_and_personal_guidance_are_separated_in_json(self):
        draft=local.propose("한글 타이포그래피는 라운드를 적게 쓰기",project=self.project,home=self.home)
        local.approve(draft["proposal"],reviewer="human",project=self.project,home=self.home)
        code,out,err=self.call("search","한글 타이포그래피","--json")
        self.assertEqual(code,0,err)
        result=json.loads(out)
        self.assertTrue(result["research"])
        self.assertTrue(result["personal_guidance"])
        self.assertEqual(result["personal_guidance"][0]["evidence_status"],
                         "personal_guidance_not_verified")
        self.assertTrue(all("score" in x for x in result["research"]))

    def test_unverified_cannot_be_added_to_core_as_preference(self):
        code,out,err=self.call("add","근거 없이 추정한 주장","--scope","core","--type","preference")
        self.assertEqual(code,2)
        self.assertIn("core",err.lower())

    def test_cli_check_and_portable_module(self):
        code,out,err=self.call("check","--json")
        self.assertEqual(code,0,err)
        self.assertTrue(json.loads(out)["ok"])
        run=subprocess.run([sys.executable,"-m","design_engineering","--version"],
                           cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn("4.6.0",run.stdout)
        portable=subprocess.run([sys.executable,str(ROOT/"scripts/de.py"),"--version"],
                                cwd=self.project,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.assertEqual(portable.returncode,0,portable.stderr)

    def test_cli_review_draft_cannot_be_implicitly_committed(self):
        code,out,_=self.call("add","모바일에선 여백이 많으면 좋다","--json")
        self.assertEqual(code,0)
        proposal=json.loads(out)["proposal"]
        code,out,_=self.call("review",proposal,"--json")
        self.assertEqual(code,0)
        self.assertIn("Preview only",out)
        self.assertEqual(local.records(project=self.project,home=self.home,scopes=("project",)),[])

    def test_cli_archive_is_explicit(self):
        code,out,_=self.call("add","선명한 텍스트 위주","--json")
        draft=json.loads(out)["proposal"]
        code,out,_=self.call("review",draft,"--approve","--reviewer","owner","--json")
        identity=json.loads(out)["registered"]["id"]
        code,out,err=self.call("review","--archive",identity,"--scope","project","--approve",
                               "--reviewer","owner","--json")
        self.assertEqual(code,0,err)
        self.assertEqual(json.loads(out)["archived"],identity)
        self.assertEqual(local.records(project=self.project,home=self.home,scopes=("project",)),[])

if __name__ == "__main__":
    unittest.main()
