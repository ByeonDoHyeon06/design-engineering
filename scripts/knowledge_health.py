#!/usr/bin/env python3
"""Read-only Knowledge registry health audit (not a literature or correctness review).

Errors = broken local graph integrity; warnings = human review candidates.
No files are rewritten, merged, discarded or automatically reclassified.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]

def _json(root, path):
    return json.loads((root / path).read_text(encoding="utf-8"))

def _canonical_url(url):
    """Normalize obvious DOI/URL aliases for review, not definitive identity."""
    if not url:
        return ""
    url = url.strip()
    if url.lower().startswith("doi:"):
        url = "https://doi.org/" + url[4:].strip()
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = parsed.path.rstrip("/").lower()
    if host in ("dx.doi.org", "doi.org"):
        host = "doi.org"
    return urlunsplit(("https", host, path, "", "")) if host else url.casefold()

def inspect(root=ROOT):
    root=Path(root).resolve()
    catalog=_json(root,"knowledge/catalog.json")["records"]
    sources=_json(root,"knowledge/sources.json")["records"]
    claims=_json(root,"knowledge/claims.json")["claims"]
    concepts=_json(root,"knowledge/concepts.json")["concepts"]
    errors=[]; warnings=[]
    def duplicates(rows,name):
        count=Counter(row.get("id") for row in rows)
        for id_,n in sorted(count.items(), key=lambda kv:str(kv[0])):
            if not isinstance(id_,str) or not id_:errors.append("missing "+name+" id")
            elif n>1:errors.append("duplicate "+name+" id: "+id_)
    for rows,name in [(catalog,"card"),(sources,"source"),(claims,"claim"),(concepts,"concept")]:
        duplicates(rows,name)
    card_ids={r.get("id") for r in catalog}
    src_ids={r.get("id") for r in sources}
    claim_ids={r.get("id") for r in claims}
    concept_ids={r.get("id") for r in concepts}
    source_users=Counter()
    for row in catalog:
        cid=row.get("id","?")
        p=(root / row.get("path","")).resolve()
        if not p.is_relative_to(root) or not p.is_file():
            errors.append(f"{cid}: missing or unsafe card path: {row.get('path')}")
        for sid in row.get("source_ids",[]):
            source_users[sid]+=1
            if sid not in src_ids:errors.append(f"{cid}: unknown source {sid}")
        for claim in row.get("claims",[]):
            if claim not in claim_ids:errors.append(f"{cid}: unknown claim {claim}")
    by_source={r["id"]:r for r in sources if r.get("id")}
    for c in claims:
        sid=c.get("source_id")
        if sid not in src_ids:errors.append(f"claim {c.get('id')}: unknown source {sid}")
        elif not by_source[sid].get("reverified_at"):
            warnings.append(f"claim {c.get('id')}: source not recently reverified")
    for c in concepts:
        for cid in c.get("cards",[]):
            if cid not in card_ids:errors.append(f"concept {c.get('id')}: unknown card {cid}")
        for rel in ("broader","related"):
            for dest in c.get(rel,[]):
                if dest not in concept_ids:errors.append(f"concept {c.get('id')}: unknown {rel} {dest}")
        if c.get("id") in c.get("broader",[]):
            errors.append(f"concept {c.get('id')}: self-broader link")
    by_url=defaultdict(list)
    for s in sources:
        key=_canonical_url(s.get("url",""))
        if key:by_url[key].append(s["id"])
    for url,ids in sorted(by_url.items()):
        if len(ids)>1:warnings.append(f"potential source alias: {', '.join(ids)} => {url}")
    for sid in sorted(src_ids - set(source_users)):
        warnings.append(f"source not referenced by a card: {sid}")
    legacy=sum(not bool(s.get("reverified_at")) for s in sources)
    counts={"cards":len(catalog),"sources":len(sources),"claims":len(claims),
            "concepts":len(concepts),"sources_without_reverification":legacy,
            "potential_duplicate_source_groups":sum(len(ids)>1 for ids in by_url.values())}
    return {"root":str(root),"counts":counts,"errors":errors,"warnings":warnings,
            "limitations":"Structural checks only. Duplicate URLs are review candidates; unused sources may be intentional. No scientific or visual-quality validation."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",default=str(ROOT));p.add_argument("--json",action="store_true")
    a=p.parse_args();r=inspect(a.root)
    if a.json:print(json.dumps(r,ensure_ascii=False,indent=2))
    else:
        print(json.dumps(r["counts"],ensure_ascii=False))
        for kind in ("errors","warnings"):
            for entry in r[kind]:print(kind.upper()+": "+entry)
    return int(bool(r["errors"]))

if __name__=="__main__":
    raise SystemExit(main())
