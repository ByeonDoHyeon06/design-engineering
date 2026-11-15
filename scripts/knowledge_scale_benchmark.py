#!/usr/bin/env python3
"""Synthetic relationship-index benchmark; measures local graph mechanics only.

Does NOT benchmark language retrieval quality, browser rendering or real papers.
No network/LLM required. Sizes 1k/10k represent generated, not reviewed, data.
"""
import argparse
from collections import defaultdict,deque
import json
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

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--size",type=int,action="append")
    args=p.parse_args()
    sizes=args.size or [1000,10000]
    if any(x<1 or x>100000 for x in sizes):p.error("size must be 1-100000")
    print(json.dumps({"runs":[trial(x) for x in sizes],
        "limitations":"Synthetic relationship edges only. Not real FTS, knowledge quality or a speed guarantee."},
        ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":raise SystemExit(main())
