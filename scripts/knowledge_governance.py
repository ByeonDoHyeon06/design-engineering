#!/usr/bin/env python3
"""Explicit human-reviewed v4 Knowledge lifecycle changes.

Proposals are local files. Applying them requires --confirm, matching reviewer and
the unchanged governance SHA-256. No research claims or card bodies are rewritten.
"""
import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import tempfile

from knowledge_graph import ROOT, GOVERNANCE, VALID_STATES, build

class GovernanceError(ValueError):
    pass


def _read(root):
    path=Path(root)/GOVERNANCE
    raw=path.read_bytes()
    return json.loads(raw),hashlib.sha256(raw).hexdigest()


def propose(root, operation, *, reviewer, reason, **kwargs):
    if not reviewer.strip() or not reason.strip():
        raise GovernanceError("Reviewer and substantive reason are required.")
    root=Path(root).resolve();old,digest=_read(root)
    draft={"schema_version":4,"operation":operation,"reviewer":reviewer.strip(),
           "reason":reason.strip(),"expected_sha256":digest,"change":kwargs,
           "state":"pending_explicit_approval"}
    _project(root,old,draft)
    return draft


def _project(root, old, proposal):
    obj=json.loads(json.dumps(old))
    op=proposal["operation"]
    change=proposal["change"]
    reviewer=proposal["reviewer"]
    reason=proposal["reason"]
    if op=="status":
        identifier=change["id"];status=change["status"]
        if status not in VALID_STATES:raise GovernanceError("Invalid status: " + str(status))
        record={"status":status,"reason":reason,"reviewer":reviewer}
        if change.get("successor"):record["superseded_by"]=change["successor"]
        if change.get("review_due"):record["review_due"]=change["review_due"]
        obj["status_overrides"][identifier]=record
    elif op=="alias":
        alias=change["alias"]
        if alias in obj["aliases"]:
            raise GovernanceError("Alias already registered: " + alias)
        obj["aliases"][alias]={"target":change["target"],"reason":reason,"reviewer":reviewer}
    elif op=="equivalence":
        a,b=change["a"],change["b"]
        pair=set((a,b))
        if any(set((r["a"],r["b"]))==pair for r in obj["equivalences"]):
            raise GovernanceError("Equivalence already recorded.")
        obj["equivalences"].append({"a":a,"b":b,"reason":reason,"reviewer":reviewer})
    else:raise GovernanceError("Unsupported operation: " + str(op))
    graph=build(root,governance=obj)
    if graph["errors"]:
        raise GovernanceError("Rejected invalid graph change: " + "; ".join(graph["errors"][:8]))
    return obj


def approve(root, proposal_path, reviewer, *, confirm=False):
    if not confirm:raise GovernanceError("No mutation without --confirm.")
    root=Path(root).resolve();proposal=json.loads(Path(proposal_path).read_text(encoding="utf-8"))
    if proposal.get("state")!="pending_explicit_approval" or proposal.get("schema_version")!=4:
        raise GovernanceError("Only pending v4 proposals can be applied.")
    if not reviewer or proposal.get("reviewer")!=reviewer:
        raise GovernanceError("The specified reviewer must match the proposal reviewer.")
    existing,digest=_read(root)
    if digest != proposal.get("expected_sha256"):
        raise GovernanceError("Governance file changed after proposal; inspect/re-propose before retry.")
    changed=_project(root,existing,proposal)
    # A prospective write is valid only when all referential/lifecycle rules pass.
    target=root/GOVERNANCE
    content=(json.dumps(changed,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    fd,name=tempfile.mkstemp(prefix=".governance-",suffix=".tmp",dir=str(target.parent))
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(content);stream.flush();os.fsync(stream.fileno())
        # Re-check race if another process edited between initial read and write.
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise GovernanceError("Concurrent governance modification detected.")
        os.replace(name,target)
    finally:
        if os.path.exists(name):os.unlink(name)
    return {"applied":proposal["operation"],"reviewer":reviewer,
            "governance_sha256":hashlib.sha256(content).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",default=str(ROOT))
    sub=parser.add_subparsers(dest="cmd",required=True)
    status=sub.add_parser("propose-status")
    status.add_argument("id");status.add_argument("--status",required=True,choices=sorted(VALID_STATES))
    status.add_argument("--successor");status.add_argument("--review-due")
    alias=sub.add_parser("propose-alias")
    alias.add_argument("alias");alias.add_argument("target")
    same=sub.add_parser("propose-equivalence")
    same.add_argument("a");same.add_argument("b")
    for cmd in (status,alias,same):
        cmd.add_argument("--reviewer",required=True);cmd.add_argument("--reason",required=True)
        cmd.add_argument("--out",required=True)
    apply=sub.add_parser("apply")
    apply.add_argument("proposal");apply.add_argument("--reviewer",required=True)
    apply.add_argument("--confirm",action="store_true")
    args=parser.parse_args()
    try:
        if args.cmd=="apply":
            result=approve(args.root,args.proposal,args.reviewer,confirm=args.confirm)
        else:
            kw={}
            if args.cmd=="propose-status":
                op="status";kw=dict(id=args.id,status=args.status,successor=args.successor,review_due=args.review_due)
            elif args.cmd=="propose-alias":
                op="alias";kw=dict(alias=args.alias,target=args.target)
            else:
                op="equivalence";kw=dict(a=args.a,b=args.b)
            result=propose(args.root,op,reviewer=args.reviewer,reason=args.reason,**kw)
            target=Path(args.out)
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                raise GovernanceError("Proposal file exists; do not overwrite: " + str(target))
            target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            result={"proposal":str(target),"state":"pending_explicit_approval"}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (GovernanceError,ValueError,OSError,KeyError,json.JSONDecodeError) as exc:
        parser.exit(status=2,message="Knowledge governance error: "+str(exc)+"\n")


if __name__=="__main__":
    raise SystemExit(main())
