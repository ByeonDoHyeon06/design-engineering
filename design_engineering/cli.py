"""Single user-facing CLI for Design Engineering. Underlying tools remain modular."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from . import __version__, resource_root
from . import local_knowledge as personal

ROOT = resource_root()
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _print(result, as_json=False):
    if as_json or isinstance(result, (dict, list)):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


def _scope_paths(args):
    return dict(project=args.project, home=args.user_home, session_id=args.session_id)


def _format_research(results):
    for item in results:
        print(f"  {item['id']} [{item.get('evidence_status','unknown')}] {item['title']}")
        print(f"    {item['path']}")


def _format_guidance(results):
    for item in results:
        print(f"  {item['id']} [{item['scope']}/{item['kind']}; personal, not evidence] {item['text']}")


def _search(args):
    from knowledge_index import search
    scoped = args.scope
    scientific = [] if scoped not in ("all", "core") else search(
        args.query, top=args.top, verified_only=args.verified_only,
        relative_cutoff=args.relative_cutoff,
        include_inactive=args.include_inactive)
    scopes = ("session", "project", "user") if scoped == "all" else (
        () if scoped == "core" else (scoped,))
    guidance = personal.search(
        args.query, **_scope_paths(args), scopes=scopes,
        top=args.top) if scopes and not args.verified_only else []
    result = {"query": args.query, "research": scientific, "personal_guidance": guidance,
              "notice": "Personal guidance is user supplied, not peer-reviewed evidence; research scores are relevance heuristics."}
    if args.explain:
        from .knowledge_intelligence import explain
        result["coverage"] = explain(args.query,scientific,guidance)
    if args.json:
        _print(result, True)
    else:
        print("RESEARCH (core, source-scoped):")
        _format_research(scientific)
        if not scientific:
            print("  No relevant research found.")
        print("PERSONAL GUIDANCE (separate from research):")
        _format_guidance(guidance)
        if not guidance:
            print("  No matching user/project/session guidance.")
        if args.explain:
            print("COVERAGE:",result["coverage"]["state"])
            print("  "+result["coverage"]["recommendation"])
    return 0


def _add(args):
    from knowledge_ingest import prepare
    from pathlib import Path
    kind = args.type or ("evidence" if args.scope == "core" else
                         "reference" if args.file else "preference")
    if kind == "evidence":
        if args.scope != "core" or not args.file or not args.title or not args.authors:
            raise personal.LocalKnowledgeError(
                "Core evidence needs --scope core --file FILE --title TITLE --authors AUTHORS.")
        path = prepare(args.file, title=args.title, authors=args.authors, url=args.url or "",
                       rights=args.rights, mode=args.mode,
                       approve_external=args.approve_external,
                       allow_private_content=args.allow_private_content,
                       local_dir=ROOT/".local"/"ingestion")
        result = {"proposal": str(path), "kind": "evidence", "scope": "core",
                  "status": "pending_human_source_review",
                  "notice": "Review actual excerpts and claims in JSON. No source or verified claim published."}
    else:
        if args.scope == "core":
            raise personal.LocalKnowledgeError(
                "Do not insert personal preferences/principles directly into core scientific Knowledge.")
        if args.mode != "local" or args.approve_external or args.allow_private_content:
            raise personal.LocalKnowledgeError(
                "Optional external extraction applies only to document-based core evidence.")
        if kind not in personal.KINDS:
            raise personal.LocalKnowledgeError("Use preference, principle, observation, reference, or evidence.")
        note = args.text or (args.title or Path(args.file).name if args.file else None)
        result = personal.propose(
            note, kind=kind, scope=args.scope, **_scope_paths(args),
            context=args.context, outcome=args.outcome, tags=args.tag or (),
            source_file=args.file, title=args.title,
            authors=args.authors, url=args.url)
    _print(result, args.json)
    return 0


def _review(args):
    from knowledge_ingest import commit
    if args.list:
        pending = personal.drafts(**_scope_paths(args))
        directory = ROOT/".local"/"ingestion"
        if directory.exists():
            for path in sorted(directory.glob("*.review.json")):
                try:
                    doc=json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if doc.get("status") == "pending_review":
                    pending.append({"proposal": str(path), "scope": "core",
                                    "kind": "evidence", "text": doc.get("source",{}).get("title")})
        _print({"pending": pending}, args.json)
        return 0
    if args.archive:
        if args.scope == "core":
            raise personal.LocalKnowledgeError("Use the reviewed core governance workflow for core source archival.")
        if not args.approve or not args.reviewer:
            raise personal.LocalKnowledgeError("Archival requires --approve and --reviewer.")
        result=personal.archive(args.archive, scope=args.scope, reviewer=args.reviewer,
                                **_scope_paths(args))
        _print(result,args.json)
        return 0
    if not args.proposal:
        raise personal.LocalKnowledgeError("Provide a proposal path, --list, or --archive ID.")
    if not args.approve:
        path=Path(args.proposal).expanduser()
        if not path.is_file():
            raise personal.LocalKnowledgeError("Draft file not found: "+str(path))
        doc=json.loads(path.read_text(encoding="utf-8"))
        view = {k:v for k,v in doc.items() if k not in ("source_path",)}
        _print({"proposal": str(path.resolve()), "draft": view,
                "notice": "Preview only. Use --approve --reviewer NAME to commit."},args.json)
        return 0
    if not args.reviewer:
        raise personal.LocalKnowledgeError("Explicit approval requires --reviewer.")
    doc=json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    if doc.get("source") and isinstance(doc.get("candidates"), list) and doc.get("schema_version")==1:
        # Only maintainers working from an editable repository should publish core research.
        result=commit(args.proposal, reviewer=args.reviewer, confirm=True, root=ROOT)
        _print({"published_core_cards":[x["id"] for x in result],
                "notice":"Human-reviewed excerpt claims, not independently replicated research."},args.json)
    else:
        result=personal.approve(args.proposal, reviewer=args.reviewer,
                                **_scope_paths(args))
        _print(result,args.json)
    return 0


def _context(args):
    if args.scope == "core":
        raise personal.LocalKnowledgeError("Use de search for core research; context is for scoped user guidance.")
    scopes=("session","project","user") if args.scope=="all" else (args.scope,)
    rows=personal.search(args.query or "", **_scope_paths(args), scopes=scopes,
                         include_all=not args.query,top=args.top)
    result={"scope":args.scope,"guidance":rows,
            "notice":"User-authored preferences/principles, not verified research."}
    if args.conflicts:
        from .knowledge_intelligence import conflict_candidates
        result["conflict_review"] = conflict_candidates(rows)
        result["conflict_review"]["scope_notice"] = "Only displayed, active records were scanned; max 100 by default."
    if args.json:
        _print(result, True)
    else:
        _format_guidance(rows)
        if not rows:
            print("No saved guidance. Use de add to propose a new item.")
        if args.conflicts:
            print("Potential preference clashes:",result["conflict_review"]["candidate_count"])
            for item in result["conflict_review"]["candidates"]:
                print("  "+", ".join(item["ids"])+" — common terms: "+", ".join(item["common_terms"]))
    return 0


def _inspect(args):
    if args.id.startswith("local:"):
        entries=personal.records(**_scope_paths(args),include_archived=True)
        row=next((r for r in entries if r["id"]==args.id),None)
        if not row:
            raise personal.LocalKnowledgeError("Personal record not found in visible scopes.")
        _print(row,args.json)
        return 0
    from knowledge_graph import build, impact
    graph=build(ROOT)
    if graph["errors"]:
        raise personal.LocalKnowledgeError("Core graph invalid: "+"; ".join(graph["errors"][:4]))
    row=next((r for r in graph["nodes"] if r["id"]==args.id),None)
    if not row:
        raise personal.LocalKnowledgeError("Unknown node; use typed ID such as source:N39 or method:K16.")
    result={"node":row,"dependencies":impact(graph,args.id)["affected"]}
    _print(result,args.json)
    return 0


def _check(args):
    from validate_install import inspect
    from knowledge_health import inspect as health
    from knowledge_graph import build
    inst=inspect(ROOT)
    if not inst["complete"]:
        _print({"installation":inst,"status":"INCOMPLETE"},True)
        return 1
    h=health(ROOT)
    graph=build(ROOT)
    result={"installation":inst,"knowledge_health":h,"graph":{
        "counts":graph["counts"],"errors":graph["errors"],"warnings":graph["warnings"]}}
    issues=h["errors"]+graph["errors"]
    if args.smoke:
        run=subprocess.run([sys.executable,str(SCRIPTS/"validate_install.py"),
                            "--root",str(ROOT),"--smoke","--json"],
                           cwd=ROOT,capture_output=True,text=True)
        try:
            result["smoke"]=json.loads(run.stdout)
        except json.JSONDecodeError:
            result["smoke"]={"error":run.stderr or run.stdout}
        if run.returncode:
            issues.append("Knowledge smoke failed")
    if args.review_due:
        from .knowledge_intelligence import source_review_queue
        result["recorded_review_queue"] = source_review_queue(ROOT)
    result["ok"]=not bool(issues)
    if args.json:
        _print(result,True)
    else:
        print("Installation:", "OK" if inst["complete"] else "INCOMPLETE")
        print("Knowledge:", len(h["errors"]), "errors,",len(h["warnings"]),"warnings")
        print("Graph:",len(graph["errors"]),"errors,",len(graph["warnings"]),"warnings")
        if args.smoke:
            print("Smoke:", "PASS" if result["smoke"].get("complete") else "FAIL")
        if args.review_due:
            print("Recorded review candidates:", len(result["recorded_review_queue"]["items"]))
    return int(bool(issues))


def _qa(args):
    if args.mode=="visual":
        if not args.out:
            raise personal.LocalKnowledgeError("Visual QA needs --out PATH.")
        cmd=[str(SCRIPTS/"visual_critique.py"),"start",args.html,"--out",args.out]
    elif args.mode=="tasks":
        if not args.tasks or not args.out:
            raise personal.LocalKnowledgeError("Task QA needs --tasks JSON --out PATH.")
        cmd=[str(SCRIPTS/"ux_scenarios.py"),"run",args.html,args.tasks,"--out",args.out,
             "--width",str(args.width)]
    else:
        cmd=[str(SCRIPTS/"static_page_audit.py"),args.html]
        if args.json:
            cmd.append("--json")
    result=subprocess.run([sys.executable]+cmd,cwd=Path.cwd())
    return result.returncode


def _evaluation(args):
    """Paired design study: no models or reviewers are simulated by the CLI."""
    from . import evaluation as ev
    if args.eval_action == "tasks":
        catalog = ev.load_tasks(args.tasks)
        _print({"tasks": catalog["tasks"],
                "limitations": catalog.get("description", "")}, args.json)
        return 0
    if args.eval_action == "init":
        result = ev.init_run(tasks_file=args.tasks, out=args.out,
                             seed=args.seed, agent=args.agent, model=args.model,
                             effort=args.effort, protocol_note=args.protocol_note)
    elif args.eval_action == "attach":
        result = ev.attach(run=args.run, task_id=args.task, condition=args.condition,
                           desktop=args.desktop, mobile=args.mobile, duration_seconds=args.seconds,
                           input_tokens=args.input_tokens, output_tokens=args.output_tokens,
                           cost_usd=args.cost_usd)
    elif args.eval_action == "validate":
        result = ev.validate_run(args.run, require_complete=args.require_complete)
        _print(result, args.json)
        return 0 if result["ok"] else 1
    elif args.eval_action == "scorecard":
        result = ev.scorecard(run=args.run, judge=args.judge, out=args.out)
    elif args.eval_action == "report":
        result = ev.report(run=args.run, judgment_files=args.judgments or [])
        if args.out:
            ev._private_json(args.out, result)
    else:
        raise ev.EvaluationError("Unknown evaluation action.")
    _print(result, args.json)
    return 0


def _design(args):
    from . import design_plan
    if args.design_action == "plan":
        result = design_plan.create(args.brief, args.out)
    elif args.design_action == "validate":
        result = design_plan.validate(args.file, require_ready=args.require_ready)
        _print(result, args.json)
        return 0 if result["ok"] else 1
    elif args.design_action == "review":
        from visual_critique import audit
        doc = json.loads(Path(args.file).read_text(encoding="utf-8"))
        result = audit(doc, Path(args.file).resolve().parent)
        _print(result, args.json)
        return 0 if result["ok"] else 1
    else:
        raise design_plan.DesignPlanError("Unknown design action.")
    _print(result, args.json)
    return 0


def _knowledge(args):
    """Consistent local Knowledge CRUD, always with explicit review for writes."""
    if args.knowledge_action == "list":
        scope = ("session","project","user") if args.scope == "all" else (args.scope,)
        items = personal.records(**_scope_paths(args), scopes=scope,
                                 include_archived=args.include_archived)
        result = {"records": items, "count": len(items),
                  "notice": "Local context only; never registered scientific claims."}
    elif args.knowledge_action == "conflicts":
        from .knowledge_intelligence import conflict_candidates
        scopes = ("session","project","user") if args.scope == "all" else (args.scope,)
        rows = personal.records(**_scope_paths(args), scopes=scopes)
        result = conflict_candidates(rows)
    elif args.knowledge_action == "edit":
        if args.scope == "all":
            raise personal.LocalKnowledgeError("Select one scope before proposing a revision.")
        result = personal.propose_revision(
            args.id, args.text, scope=args.scope, **_scope_paths(args),
            context=args.context, outcome=args.outcome, tags=args.tag)
    elif args.knowledge_action == "archive":
        if args.scope == "all" or not args.approve or not args.reviewer:
            raise personal.LocalKnowledgeError("Archival needs one scope, --approve and --reviewer.")
        result = personal.archive(args.id, scope=args.scope, reviewer=args.reviewer,
                                  **_scope_paths(args))
    else:
        raise personal.LocalKnowledgeError("Unknown local Knowledge operation.")
    _print(result, args.json)
    return 0


def parser():
    p=argparse.ArgumentParser(prog="de",
        description="Design Engineering — research, personal Knowledge, and real UI validation.")
    p.add_argument("--project",default=None,help="Consumer project root; defaults to current working directory.")
    p.add_argument("--user-home",default=None,help="Override personal Knowledge root (useful for tests).")
    p.add_argument("--session-id",default=None,help="Required for ephemeral session-scoped Knowledge.")
    p.add_argument("--version",action="version",version="Design Engineering "+__version__)
    sub=p.add_subparsers(dest="command",required=True)

    s=sub.add_parser("search",help="Search research and separate scoped guidance.")
    s.add_argument("query")
    s.add_argument("--scope",choices=("all","core","user","project","session"),default="all")
    s.add_argument("--top",type=int,default=5)
    s.add_argument("--verified-only",action="store_true",help="Show only explicitly verified core claims.")
    s.add_argument("--explain",action="store_true",help="Explain registered coverage, match signals and knowledge gaps.")
    s.add_argument("--relative-cutoff",type=float,default=0.2)
    s.add_argument("--include-inactive",action="store_true")
    s.add_argument("--json",action="store_true")
    s.set_defaults(func=_search)

    a=sub.add_parser("add",help="Create a draft from natural text or a local source file.")
    a.add_argument("text",nargs="?",help="Natural-language preference, principle, observation or note.")
    a.add_argument("--type",choices=("preference","principle","observation","reference","evidence"))
    a.add_argument("--scope",choices=("user","project","session","core"),default="project")
    a.add_argument("--file",help="Local document to bookmark (reference) or review (core evidence).")
    a.add_argument("--title");a.add_argument("--authors");a.add_argument("--url")
    a.add_argument("--context",help="When it applies, or observation conditions.")
    a.add_argument("--outcome",help="Required for observation.")
    a.add_argument("--tag",action="append",default=[])
    a.add_argument("--mode",choices=("local","gemini"),default="local")
    a.add_argument("--approve-external",action="store_true")
    a.add_argument("--allow-private-content",action="store_true")
    a.add_argument("--rights",default="user-provided-unverified")
    a.add_argument("--json",action="store_true")
    a.set_defaults(func=_add)

    r=sub.add_parser("review",help="List, preview, approve or archive Knowledge entries.")
    r.add_argument("proposal",nargs="?")
    r.add_argument("--list",action="store_true")
    r.add_argument("--approve",action="store_true",help="Explicit approval; requires reviewer.")
    r.add_argument("--archive",metavar="LOCAL_ID",help="Archive approved local guidance.")
    r.add_argument("--scope",choices=("user","project","session"),default="project")
    r.add_argument("--reviewer")
    r.add_argument("--json",action="store_true")
    r.set_defaults(func=_review)

    c=sub.add_parser("context",help="Show active personal/project guidance in scope priority.")
    c.add_argument("--scope",choices=("all","user","project","session"),default="all")
    c.add_argument("--query",default="")
    c.add_argument("--conflicts",action="store_true",help="Show lexical preference conflicts for human review.")
    c.add_argument("--top",type=int,default=100)
    c.add_argument("--json",action="store_true")
    c.set_defaults(func=_context)

    i=sub.add_parser("inspect",help="Inspect typed core dependencies or a local item.")
    i.add_argument("id")
    i.add_argument("--json",action="store_true")
    i.set_defaults(func=_inspect)

    check=sub.add_parser("check",help="Inspect installation and core Knowledge health.")
    check.add_argument("--smoke",action="store_true")
    check.add_argument("--review-due",action="store_true",help="Show explicitly registered source/card review-due items.")
    check.add_argument("--json",action="store_true")
    check.set_defaults(func=_check)

    qa=sub.add_parser("qa",help="Run visual, task or static HTML checks.")
    qa.add_argument("html")
    qa.add_argument("--mode",choices=("visual","tasks","static"),default="visual")
    qa.add_argument("--tasks",help="Required for mode=tasks.")
    qa.add_argument("--out",help="Output directory.")
    qa.add_argument("--width",type=int,default=390)
    qa.add_argument("--json",action="store_true")
    qa.set_defaults(func=_qa)

    evaluation = sub.add_parser(
        "eval", help="Prepare blinded design A/B studies and summarize real reviews.")
    esub = evaluation.add_subparsers(dest="eval_action", required=True)
    tasks = esub.add_parser("tasks", help="Inspect the curated design-task catalog.")
    tasks.add_argument("--tasks", default=str(ROOT/"benchmarks/design-tasks.json"))
    tasks.add_argument("--json", action="store_true")
    tasks.set_defaults(func=_evaluation)

    init = esub.add_parser("init", help="Create balanced randomized A/B assignments and blind packet.")
    init.add_argument("--tasks", default=str(ROOT/"benchmarks/design-tasks.json"))
    init.add_argument("--out", required=True, help="New directory for the local study.")
    init.add_argument("--seed", type=int, default=42)
    init.add_argument("--agent", required=True, help="Record the actual agent product/version.")
    init.add_argument("--model", required=True, help="Record the same model for both conditions.")
    init.add_argument("--effort", required=True, help="Record the same thinking effort/budget.")
    init.add_argument("--protocol-note", default="", help="Extra controlled-run setup details.")
    init.add_argument("--json", action="store_true")
    init.set_defaults(func=_evaluation)

    attach = esub.add_parser("attach", help="Strip screenshot metadata and attach under blind A/B label.")
    attach.add_argument("--run", required=True)
    attach.add_argument("--task", required=True)
    attach.add_argument("--condition", choices=("baseline","skill"), required=True)
    attach.add_argument("--desktop", required=True, help="Actual desktop PNG screenshot.")
    attach.add_argument("--mobile", required=True, help="Actual mobile PNG screenshot.")
    attach.add_argument("--seconds", type=float, default=None)
    attach.add_argument("--input-tokens", type=int, default=None)
    attach.add_argument("--output-tokens", type=int, default=None)
    attach.add_argument("--cost-usd", type=float, default=None)
    attach.add_argument("--json", action="store_true")
    attach.set_defaults(func=_evaluation)

    check_eval = esub.add_parser("validate", help="Check task pairs, screenshot hashes and blind packet.")
    check_eval.add_argument("--run", required=True)
    check_eval.add_argument("--require-complete", action="store_true")
    check_eval.add_argument("--json", action="store_true")
    check_eval.set_defaults(func=_evaluation)

    scorecard = esub.add_parser("scorecard", help="Create an explicitly blank human-review template.")
    scorecard.add_argument("--run", required=True)
    scorecard.add_argument("--judge", required=True)
    scorecard.add_argument("--out", required=True)
    scorecard.add_argument("--json", action="store_true")
    scorecard.set_defaults(func=_evaluation)

    report = esub.add_parser("report", help="Aggregate actual blind judgments, report all missing evidence.")
    report.add_argument("--run", required=True)
    report.add_argument("--judgments", nargs="*", default=[])
    report.add_argument("--out", help="Optional location to save full JSON report.")
    report.add_argument("--json", action="store_true")
    report.set_defaults(func=_evaluation)

    design = sub.add_parser("design", help="Content-led design planning and source-aware visual review.")
    dsub = design.add_subparsers(dest="design_action", required=True)
    plan = dsub.add_parser("plan", help="Create an editable design and visual asset direction plan.")
    plan.add_argument("--brief", required=True, help="JSON with real content roles and constraints.")
    plan.add_argument("--out", required=True)
    plan.add_argument("--json", action="store_true")
    plan.set_defaults(func=_design)

    check_plan = dsub.add_parser("validate", help="Audit real content, concept contrast, image rights and viewport plan.")
    check_plan.add_argument("file")
    check_plan.add_argument("--require-ready", action="store_true")
    check_plan.add_argument("--json", action="store_true")
    check_plan.set_defaults(func=_design)

    review = dsub.add_parser("review", help="Validate screenshot-anchored critique and revision evidence.")
    review.add_argument("file", help="Existing visual-critique JSON file.")
    review.add_argument("--json", action="store_true")
    review.set_defaults(func=_design)

    knowledge = sub.add_parser("knowledge", help="Manage locally reviewed design guidance.")
    ksub = knowledge.add_subparsers(dest="knowledge_action", required=True)
    kl = ksub.add_parser("list", help="List active personal/user/project records.")
    kl.add_argument("--scope", choices=("all","user","project","session"), default="all")
    kl.add_argument("--include-archived", action="store_true")
    kl.add_argument("--json",action="store_true")
    kl.set_defaults(func=_knowledge)
    kc = ksub.add_parser("conflicts", help="Review possible opposing preferences; no automatic resolution.")
    kc.add_argument("--scope", choices=("all","user","project","session"), default="all")
    kc.add_argument("--json",action="store_true")
    kc.set_defaults(func=_knowledge)
    ke = ksub.add_parser("edit", help="Draft a revision. Use de review --approve to apply.")
    ke.add_argument("id")
    ke.add_argument("text")
    ke.add_argument("--scope", choices=("user","project","session"), default="project")
    ke.add_argument("--context")
    ke.add_argument("--outcome")
    ke.add_argument("--tag",action="append",default=None)
    ke.add_argument("--json",action="store_true")
    ke.set_defaults(func=_knowledge)
    ka = ksub.add_parser("archive", help="Archive one active local note, retaining its history.")
    ka.add_argument("id")
    ka.add_argument("--scope",choices=("user","project","session"),default="project")
    ka.add_argument("--approve",action="store_true")
    ka.add_argument("--reviewer")
    ka.add_argument("--json",action="store_true")
    ka.set_defaults(func=_knowledge)

    return p


def main(argv=None):
    args=parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (personal.LocalKnowledgeError,ValueError,PermissionError,
            FileNotFoundError,KeyError, OSError, json.JSONDecodeError) as exc:
        print("de:",str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
