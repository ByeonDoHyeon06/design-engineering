#!/usr/bin/env python3
"""Transparent local regression metrics: hit@k and MRR, not proof of user outcomes."""
import argparse,json,statistics
from pathlib import Path
from knowledge_index import search
ROOT=Path(__file__).resolve().parents[1]

def benchmark(data,k=3):
    results=[]
    for case in data['cases']:
        found=[x['id'] for x in search(case['question'],top=k)]
        ranks=[i+1 for i,item in enumerate(found) if item in set(case['relevant'])]
        results.append({'question':case['question'],'expected':case['relevant'],
                        'retrieved':found,'hit':bool(ranks),'reciprocal_rank':1/min(ranks) if ranks else 0})
    return {'queries':len(results),'top_k':k,'hit_rate':round(statistics.mean(x['hit'] for x in results),4),
            'mrr':round(statistics.mean(x['reciprocal_rank'] for x in results),4),
            'results':results,'limitations':'Curated, in-domain examples; may overestimate unseen-query effectiveness.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',default=str(ROOT/'benchmarks/retrieval-v38.json'))
    p.add_argument('--top',type=int,default=3);p.add_argument('--out');a=p.parse_args()
    report=benchmark(json.loads(Path(a.dataset).read_text(encoding='utf8')),a.top)
    if a.out:Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False,indent=2))
    for r in report['results']:
        if not r['hit']:print('MISS:',r['question'], 'got',r['retrieved'])
if __name__=='__main__':main()
