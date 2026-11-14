#!/usr/bin/env python3
"""Compatible CLI and API for Knowledge Retrieval 2.0.
Uses hybrid local retrieval, not an obsolete keyword-only or ID-prefix filter.
"""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'knowledge/catalog.json'


def rank(query,catalog=None,verified_only=False):
    from knowledge_index import search
    result=search(query,top=38,verified_only=verified_only)
    if catalog is None:catalog=json.loads(CAT.read_text(encoding='utf-8'))
    by_id={r['id']:r for r in catalog['records']}
    return [dict(by_id[r['id']],**{k:v for k,v in r.items() if k not in by_id[r['id']]})
            for r in result if r['id'] in by_id]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('question');p.add_argument('--top',type=int,default=5)
    p.add_argument('--json',action='store_true');p.add_argument('--verified-only',action='store_true')
    p.add_argument('--embedding-model')
    a=p.parse_args()
    if a.embedding_model:
        from knowledge_index import search
        matches=search(a.question,a.top,verified_only=a.verified_only,embedding_model=a.embedding_model)
    else: matches=rank(a.question,verified_only=a.verified_only)[:max(1,a.top)]
    if a.json:print(json.dumps(matches,ensure_ascii=False,indent=2))
    elif matches:
        for m in matches:
            print(f"{m['id']} [{m.get('evidence_status')}] {m['title']} (score={m['score']})\n  {m['path']}")
    else:print('No matching card. Clarify the unresolved design uncertainty; optional Gemini is opt-in.')
if __name__=='__main__':main()
