#!/usr/bin/env python3
"""Design Engineering v4: typed, read-only Knowledge graph over the v3 registries.

Existing cards/sources/claims/concepts remain authoritative. governance.json holds only
lifecycle/review relationships, avoiding a second copy of research and search metadata.
No network, external database, automatic fact verification or private project ingestion.
"""
import argparse
from collections import Counter, defaultdict, deque
from datetime import date
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = "knowledge/v4/governance.json"
VALID_STATES = {"active", "needs_review", "superseded", "archived"}
PREFIXES = ("source:", "claim:", "concept:", "method:", "practice:", "observation:")


def read_json(root, relative):
    return json.loads((Path(root) / relative).read_text(encoding="utf-8"))


def empty_governance():
    return {"schema_version": 4, "status_overrides": {}, "aliases": {},
            "equivalences": [], "concept_relations": [], "observations": []}


def _date(value):
    if value in (None, ""):
        return True
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def build(root=ROOT, governance=None):
    """Return deterministic typed graph + diagnostics, with zero writes."""
    root = Path(root).resolve()
    cards = read_json(root, "knowledge/catalog.json")["records"]
    sources = read_json(root, "knowledge/sources.json")["records"]
    claims = read_json(root, "knowledge/verified/claims.json")["claims"]
    concepts = read_json(root, "knowledge/concepts.json")["concepts"]
    practices = read_json(root, "methods/designer-methods.json")["methods"]
    if governance is None:
        file = root / GOVERNANCE
        governance = read_json(root, GOVERNANCE) if file.exists() else empty_governance()
    errors, warnings = [], []
    if governance.get("schema_version") != 4:
        errors.append("governance schema_version must be 4")
    nodes = {}
    edge_set = set()

    def node(kind, identity, label, metadata):
        if not isinstance(identity, str) or not identity.strip():
            errors.append(f"{kind}: missing ID")
            return
        full = kind + ":" + identity
        if full in nodes:
            errors.append(f"duplicate node {full}")
            return
        nodes[full] = {"id": full, "type": kind, "label": label,
                       "status": "active", "metadata": metadata}

    def edge(source, target, rel):
        if source not in nodes or target not in nodes:
            errors.append(f"dangling {rel}: {source} -> {target}")
        else:
            edge_set.add((source, target, rel))

    for record in sources:
        node("source", record.get("id"), record.get("title",""),
             {"url": record.get("url",""), "access_level": record.get("access_level"),
              "reviewed_at": record.get("reverified_at"),
              "source_type": record.get("type")})
    for record in claims:
        node("claim", record.get("id"), record.get("source_supported_summary",""),
             {"scope": record.get("source_scope"), "do_not_infer": record.get("do_not_infer"),
              "verification_basis": record.get("verification_basis")})
    for record in cards:
        node("method", record.get("id"), record.get("title",""),
             {"path": record.get("path"), "kind": record.get("kind"),
              "review": record.get("review")})
    for record in concepts:
        node("concept", record.get("id"), record.get("id",""),
             {"labels": record.get("cues",[]), "hints": record.get("expand",[])})
    for record in practices:
        node("practice", record.get("id"), record.get("name",""),
             {"lens": record.get("reasoning_lens"),
              "provenance_url": record.get("primary_or_institutional_url"),
              "access_level": record.get("access_level")})
    for record in governance.get("observations",[]):
        node("observation", record.get("id"), record.get("task",""),
             {"date": record.get("observed_at"), "outcome": record.get("outcome"),
              "artifact": record.get("artifact"), "reviewer": record.get("reviewer")})
        if not _date(record.get("observed_at")) or not record.get("observed_at"):
            errors.append("observation requires ISO date: " + str(record.get("id")))
        if not record.get("reviewer") or not record.get("outcome"):
            errors.append("observation requires outcome and reviewer: " + str(record.get("id")))

    for record in claims:
        edge("claim:" + str(record.get("id")), "source:" + str(record.get("source_id")), "supported_by")
    for record in cards:
        ident = "method:" + str(record.get("id"))
        path = (root / str(record.get("path", ""))).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f"{ident}: unsafe or missing card path {record.get('path')}")
        for sid in record.get("source_ids",[]):
            edge(ident, "source:" + str(sid), "cites")
        for cid in record.get("claims",[]):
            edge(ident, "claim:" + str(cid), "supported_by")
    for record in concepts:
        for mid in record.get("cards",[]):
            edge("concept:" + str(record.get("id")), "method:" + str(mid), "retrieves")
    for record in governance.get("observations",[]):
        obs = "observation:" + str(record.get("id"))
        edge(obs, str(record.get("method_id")), "observed_method")
        for cid in record.get("claim_ids",[]):
            edge(obs, "claim:" + str(cid), "observed_claim")

    overrides = governance.get("status_overrides",{})
    if not isinstance(overrides, dict):
        errors.append("status_overrides must be an object")
        overrides = {}
    supersessions = {}
    for full,meta in overrides.items():
        if full not in nodes:
            errors.append(f"status override for missing node: {full}")
            continue
        if not isinstance(meta,dict):
            errors.append(f"status override must be an object: {full}")
            continue
        state = meta.get("status")
        if state not in VALID_STATES:
            errors.append(f"invalid lifecycle state: {full} => {state}")
            continue
        if state != "active" and not (meta.get("reason") and meta.get("reviewer")):
            errors.append(f"non-active state requires reason and reviewer: {full}")
        if not _date(meta.get("review_due")):
            errors.append(f"invalid review_due date: {full}")
        target = meta.get("superseded_by")
        if state == "superseded" and not target:
            errors.append(f"superseded node requires successor: {full}")
        if target:
            if target not in nodes:
                errors.append(f"missing successor {full} -> {target}")
            elif nodes[target]["type"] != nodes[full]["type"]:
                errors.append(f"successor type mismatch {full} -> {target}")
            supersessions[full] = target
        nodes[full]["status"] = state
        nodes[full]["lifecycle"] = meta

    aliases = governance.get("aliases",{})
    if not isinstance(aliases,dict):
        errors.append("aliases must be an object")
        aliases = {}
    for alias,meta in aliases.items():
        if alias in nodes:
            errors.append("alias shadows canonical node: " + alias)
            continue
        if not isinstance(meta,dict):
            errors.append("invalid alias record: " + alias)
            continue
        if not alias.startswith(PREFIXES):
            errors.append("alias missing type namespace: " + alias)
        dest = meta.get("target")
        if dest not in nodes:
            errors.append(f"alias {alias} targets missing node {dest}")
        elif alias.split(":",1)[0] != dest.split(":",1)[0]:
            errors.append(f"alias {alias} has mismatched target type")
        if not (meta.get("reason") and meta.get("reviewer")):
            errors.append("alias requires reviewer and reason: " + alias)

    equivalents = governance.get("equivalences",[])
    pairs = set()
    for record in equivalents:
        a,b = record.get("a"), record.get("b")
        if a not in nodes or b not in nodes or a == b:
            errors.append(f"invalid equivalence: {a} / {b}")
            continue
        if nodes[a]["type"] != nodes[b]["type"]:
            errors.append(f"equivalence type mismatch: {a} / {b}")
        key = tuple(sorted((a,b)))
        if key in pairs:
            errors.append(f"duplicate equivalence: {a} / {b}")
        pairs.add(key)
        if not (record.get("reviewer") and record.get("reason")):
            errors.append(f"equivalence needs reviewer and reason: {a}/{b}")

    broader = defaultdict(set)
    relations = set()
    for record in governance.get("concept_relations",[]):
        a,b,rel=record.get("source"),record.get("target"),record.get("relation")
        if rel not in ("broader","related") or (a,b,rel) in relations:
            errors.append(f"invalid or duplicate concept relation: {a}/{b}/{rel}")
            continue
        relations.add((a,b,rel))
        if a == b or not a.startswith("concept:") or not b.startswith("concept:"):
            errors.append(f"concept relation must link two different concepts: {a}/{b}")
            continue
        edge(a,b,rel)
        if rel == "broader": broader[a].add(b)

    def reject_cycles(adjacency,label):
        visited=set(); active=set()
        def walk(current):
            if current in active:
                errors.append(f"{label} cycle through {current}")
                return
            if current in visited:return
            visited.add(current);active.add(current)
            for nxt in adjacency.get(current,[]):walk(nxt)
            active.remove(current)
        for current in adjacency:walk(current)
    reject_cycles(broader,"broader")
    reject_cycles({a:[b] for a,b in supersessions.items()},"supersession")

    # Inactive or overdue sources need explicit human reassessment of dependents.
    # These are warnings, not automatic retractions of scientific claims.
    today=date.today()
    for full,meta in overrides.items():
        if not isinstance(meta,dict) or full not in nodes:continue
        due=meta.get("review_due")
        if due and _date(due) and date.fromisoformat(due)<today:
            warnings.append("review overdue: "+full+" (due "+due+")")
    for origin,target,relation in edge_set:
        if relation not in ("cites","supported_by"):continue
        if not origin.startswith(("method:","claim:")):continue
        if target.startswith("source:") and nodes[target]["status"] in ("archived","superseded"):
            if nodes[origin]["status"]=="active":
                warnings.append("active dependency on inactive source: "+origin+" -> "+target)

    # Deduplicated URLs are candidates only; editions and translations may differ.
    try:
        from knowledge_health import inspect
        health = inspect(root)
        errors.extend(health["errors"])
        # A manually reviewed same-work link resolves the immediate duplicate
        # warning without destroying either source. Other URLs still need review.
        equivalents_reviewed={frozenset((x["a"],x["b"])) for x in equivalents
                              if x.get("reviewer") and x.get("reason")}
        for warning in health["warnings"]:
            if warning.startswith("potential source alias: "):
                identifiers=warning.split(" => ",1)[0].split(": ",1)[1].split(", ")
                if len(identifiers)==2 and frozenset("source:"+v for v in identifiers) in equivalents_reviewed:
                    continue
            warnings.append(warning)
    except (FileNotFoundError,ValueError,KeyError) as exc:
        errors.append("legacy health audit failed: " + str(exc))

    return {"schema_version":4,"nodes":[nodes[k] for k in sorted(nodes)],
            "edges":[{"from":a,"to":b,"relation":rel}
                     for a,b,rel in sorted(edge_set)],
            "aliases":aliases,"equivalences":equivalents,
            "errors":sorted(set(errors)),"warnings":sorted(set(warnings)),
            "counts":dict(sorted(Counter(n["type"] for n in nodes.values()).items())),
            "scope":"Structural and provenance-relationship checks only; source claims and design efficacy remain unverified unless independently reviewed."}


def impact(graph, identity, limit=1000):
    """Reverse-dependency walk: which nodes mention this source/claim/method?"""
    aliases = graph.get("aliases",{})
    if identity in aliases:identity=aliases[identity]["target"]
    node_ids={n["id"] for n in graph["nodes"]}
    if identity not in node_ids:raise KeyError("Unknown node: " + identity)
    reverse=defaultdict(set)
    for e in graph["edges"]:reverse[e["to"]].add(e["from"])
    result=[]; seen={identity}; queue=deque([(identity,0)])
    while queue:
        cur,dist=queue.popleft()
        for nxt in sorted(reverse[cur]):
            if nxt in seen:continue
            seen.add(nxt);result.append({"id":nxt,"distance":dist+1})
            if len(result) >= limit:
                return {"origin":identity,"affected":result,"truncated":True}
            queue.append((nxt,dist+1))
    return {"origin":identity,"affected":result,"truncated":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    a=sub.add_parser("validate");a.add_argument("--strict-warnings",action="store_true")
    b=sub.add_parser("impact");b.add_argument("id")
    c=sub.add_parser("export");c.add_argument("--out",required=True)
    opts=parser.parse_args();graph=build()
    if opts.command=="impact":
        if graph["errors"]:parser.error("Graph has invalid references; validate first.")
        try:report=impact(graph,opts.id)
        except KeyError as exc:parser.error(str(exc))
    elif opts.command=="export":
        if graph["errors"]:parser.error("Invalid graph cannot be exported.")
        target=Path(opts.out).resolve()
        if target == (ROOT / GOVERNANCE).resolve():parser.error("Cannot overwrite governance source.")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        report={"export":str(target),"nodes":len(graph["nodes"]),"edges":len(graph["edges"])}
    else:
        report={"counts":graph["counts"],"nodes":len(graph["nodes"]),
                "edges":len(graph["edges"]),"errors":graph["errors"],
                "warnings":graph["warnings"],"scope":graph["scope"]}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if opts.command=="validate":return int(bool(graph["errors"]) or (opts.strict_warnings and bool(graph["warnings"])))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
