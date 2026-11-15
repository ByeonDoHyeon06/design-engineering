#!/usr/bin/env python3
"""Synthetic relationship-index benchmark; measures local graph mechanics only.

Does NOT benchmark language retrieval quality, browser rendering or real papers.
No network/LLM required. Sizes 1k/10k represent generated, not reviewed, data.
"""
import argparse
from collections import defaultdict,deque
import json
from pathlib import Path
import tempfile
import time
import tracemalloc


def trial(n):
    tracemalloc.start();started=time.perf_counter()
    # 1 source per 4 methods, 1 concept per 20 methods.
    sources=[f"source:synthetic-{i}" for i in range(max(1,n//4))]
    methods=[f"method:synthetic-{i}" for i in range(n)]
    concepts=[f"concept:synthetic-{i}" for i in range(max(1,n//20))]
    reverse=defaultdict(list)
    for i,method in enumerate(methods):
        reverse[sources[i%len(sources)]].append(method)
        reverse[method].append(concepts[i%len(concepts)])
    built=time.perf_counter()
    seen={sources[0]};queue=deque([sources[0]])
    while queue:
        for item in reverse[queue.popleft()]:
            if item not in seen:
                seen.add(item);queue.append(item)
    done=time.perf_counter();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {"methods":n,"sources":len(sources),"concepts":len(concepts),
            "index_build_ms":round((built-started)*1000,2),
            "one_source_impact_ms":round((done-built)*1000,2),
            "peak_mib":round(peak/1048576,2),"affected_nodes":len(seen)-1}

def search_trial(n):
    """Actual isolated local FTS index build + one query, using synthetic cards."""
    from knowledge_index import rebuild, search
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory); cards=root/"knowledge/cards";cards.mkdir(parents=True)
        target=n//2
        token="syntheticneedle"+str(target)+"key"
        records=[]
        for i in range(n):
            cid=f"T{i:06d}";relative=f"knowledge/cards/{cid}.md"
            unique=token if i==target else f"item{i:06d}"
            (root/relative).write_text(
                f"# Synthetic type specimen {i}\n\nComparison layout note {unique}. "
                "This is synthetic benchmark text, not research evidence.\n",encoding="utf-8")
            records.append({"id":cid,"name":"synthetic-record","title":f"Synthetic {i}",
                            "kind":"METHOD","path":relative,"source_ids":["SYN"],
                            "signals":["Synthetic benchmark"],"queries":[unique,"design comparison"]})
        (root/"knowledge/catalog.json").write_text(
            json.dumps({"schema_version":1,"records":records}),encoding="utf-8")
        (root/"knowledge/sources.json").write_text(
            json.dumps({"records":[{"id":"SYN","type":"synthetic",
                   "access_level":"generated_not_reviewed"}]}),encoding="utf-8")
        (root/"knowledge/verified").mkdir()
        (root/"knowledge/verified/claims.json").write_text('{"claims":[]}',encoding="utf-8")
        (root/"knowledge/concepts.json").write_text('{"concepts":[]}',encoding="utf-8")
        db=root/"index.sqlite"
        tracemalloc.start();begin=time.perf_counter()
        result=rebuild(db_path=db,root=root)
        built=time.perf_counter()
        found=search(token,root=root,db_path=db,top=5,relative_cutoff=0)
        searched=time.perf_counter()
        _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        return {"synthetic_cards":n,"index_build_ms":round((built-begin)*1000,2),
                "search_ms":round((searched-built)*1000,2),
                "peak_mib":round(peak/1048576,2),"tokenizer":result["tokenizer"],
                "expected":f"T{target:06d}","found":[r["id"] for r in found],
                "target_found":any(r["id"]==f"T{target:06d}" for r in found)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--size",type=int,action="append")
    p.add_argument("--search-size",type=int,action="append",
                   help="Also benchmark actual synthetic SQLite FTS indexing and query latency")
    args=p.parse_args()
    sizes=args.size or [1000,10000]
    if any(x<1 or x>100000 for x in sizes):p.error("size must be 1-100000")
    sizes_search=args.search_size or []
    if any(n<1 or n>20000 for n in sizes_search):
        p.error("search-size must be 1-20000")
    print(json.dumps({"runs":[trial(x) for x in sizes],
        "search_runs":[search_trial(n) for n in sizes_search],
        "limitations":"All records are synthetic; index and retrieval timings are environment-dependent. Not real-paper semantic quality or throughput SLA."},
        ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":raise SystemExit(main())
