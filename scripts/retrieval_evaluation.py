#!/usr/bin/env python3
"""Diagnostic retrieval evaluation with positive and explicit negative queries.

Never call these curated queries representative held-out user data. The output includes
weak-result padding and false-positive no-answer detection, not only hit@k.
"""
import argparse
import json
import statistics
from pathlib import Path
from knowledge_index import search

ROOT=Path(__file__).resolve().parents[1]

def evaluate(dataset,top=3,root=ROOT):
    rows=[]
    for item in dataset["cases"]:
        expected=set(item["relevant"])
        found=search(item["question"],top=top,root=root)
        returned=[x["id"] for x in found]
        ranks=[i+1 for i,id_ in enumerate(returned) if id_ in expected]
        rows.append({"question":item["question"],"expected":sorted(expected),
                     "returned":returned,"negative":not bool(expected),
                     "hit":bool(ranks),"reciprocal_rank":(1/min(ranks) if ranks else 0),
                     "precision_at_returned":(len([x for x in returned if x in expected])/len(returned)
                                              if returned else (1 if not expected else 0)),
                     "false_positive_no_answer":not bool(expected) and bool(returned)})
    positive=[r for r in rows if not r["negative"]]
    negative=[r for r in rows if r["negative"]]
    mean=lambda xs: round(statistics.mean(xs),4) if xs else None
    return {"queries":len(rows),"positive_queries":len(positive),"negative_queries":len(negative),
            "top_k":top,"positive_hit_at_k":mean([r["hit"] for r in positive]),
            "positive_mrr":mean([r["reciprocal_rank"] for r in positive]),
            "precision_at_returned":mean([r["precision_at_returned"] for r in positive]),
            "negative_false_positive_rate":mean([r["false_positive_no_answer"] for r in negative]),
            "results":rows,
            "limitations":"Curated prompts, not blinded real-user queries or measured usability. Relevance annotation incomplete by nature."}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset",default=str(ROOT/"benchmarks/retrieval-relevance.json"))
    ap.add_argument("--top",type=int,default=3);ap.add_argument("--out")
    args=ap.parse_args()
    data=json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    report=evaluate(data,args.top)
    if args.out:Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="results"},ensure_ascii=False,indent=2))
    for r in report["results"]:
        if r["negative"] and r["returned"]:print("FALSE POSITIVE:",r["question"],r["returned"])
        if not r["negative"] and not r["hit"]:print("MISS:",r["question"],r["returned"])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
