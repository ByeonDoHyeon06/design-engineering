#!/usr/bin/env python3
"""Trace major design decisions to evidence, hypothesis, implementation and real QA.
This validates *records*, not the truth of observations or success with real users.
"""
import argparse, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TYPES={'SOURCE_FINDING','FRAMEWORK','STANDARD','PRACTITIONER','DESIGN_HYPOTHESIS'}
METHODS={'screenshot_review','browser_assertion','task_simulation','contrast_measurement',
         'keyboard_check','manual_review','user_observation','screen_reader_check'}
OUTCOMES={'pass','fail','not_tested','needs_review'}


def skeleton(goal):
    return {'schema_version':1,'user_goal':goal,'protected_requirements':[],
        'unknowns':[], 'decisions':[{
            'id':'DEC-001','problem':'','interpretation':'',
            'alternatives':[{'concept':'','meaning_relation':'','risk':''}],
            'selected_hypothesis':'','why_this_interpretation':'',
            'evidence':[{'type':'DESIGN_HYPOTHESIS','ref_id':None,'claim_scope':'','transfer_rationale':''}],
            'implemented_in':[], 'review_rounds':[{'iteration':1,'observation':'',
                'issue_id':None,'hypothesis_revision':None,'change':'',
                'checks':[{'method':'screenshot_review','outcome':'not_tested',
                           'observation':'','artifact':None}]}],
            'status':'draft'}], 'limits':[]}


def verify_trace(data,base=Path('.')):
    errors=[]; warnings=[]
    if not isinstance(data,dict) or not isinstance(data.get('decisions'),list):
        return {'ok':False,'errors':['Missing decisions array'],'warnings':[]}
    ids=set()
    for n,d in enumerate(data['decisions'],1):
        loc=f'decisions[{n}]';did=d.get('id')
        if not did or did in ids:errors.append(loc+': missing/duplicate ID')
        ids.add(did)
        if not d.get('problem','').strip():errors.append(loc+': problem required')
        if not d.get('selected_hypothesis','').strip():errors.append(loc+': selected_hypothesis required')
        if not d.get('why_this_interpretation','').strip():warnings.append(loc+': rationale missing')
        alts=d.get('alternatives',[])
        if len(alts)<2:warnings.append(loc+': fewer than two concept alternatives; okay for a narrowly scoped fix, explain why')
        concepts=[norm_text(x.get('meaning_relation','')) for x in alts if x.get('meaning_relation')]
        if len(concepts)>1 and len(set(concepts))==1:
            warnings.append(loc+': concept alternatives have identical meaning relations')
        for e in d.get('evidence',[]):
            typ=e.get('type')
            if typ not in TYPES:errors.append(loc+': invalid evidence type '+str(typ))
            if typ not in {'DESIGN_HYPOTHESIS'} and not e.get('ref_id'):
                errors.append(loc+': sourced claim without ref_id')
            if typ=='SOURCE_FINDING' and not e.get('claim_scope'):
                warnings.append(loc+': missing source claim scope')
        if d.get('status') not in {'draft','implemented','reviewed','validated'}:
            errors.append(loc+': invalid status')
        if d.get('status') in {'implemented','reviewed','validated'} and not d.get('implemented_in'):
            errors.append(loc+': implementation path missing')
        real_checks=[]
        for r in d.get('review_rounds',[]):
            for chk in r.get('checks',[]):
                method=chk.get('method');outcome=chk.get('outcome')
                if method not in METHODS:errors.append(loc+': invalid check method')
                if outcome not in OUTCOMES:errors.append(loc+': invalid check outcome')
                if outcome in {'pass','fail'}:
                    real_checks.append(chk)
                    if not chk.get('observation','').strip():errors.append(loc+': passing/failing check missing observation')
                    if method in {'browser_assertion','task_simulation','screenshot_review','screen_reader_check'}:
                        art=chk.get('artifact')
                        if not art:errors.append(loc+': check requires evidence artifact')
                        elif not (base/art).is_file():errors.append(loc+': evidence artifact missing '+str(art))
        if d.get('status')=='validated' and not real_checks:
            errors.append(loc+': validated status requires a real pass/fail check')
        if not d.get('review_rounds'):warnings.append(loc+': no critique/revision rounds recorded')
    return {'ok':not errors,'errors':errors,'warnings':warnings,'decision_count':len(data['decisions'])}


def norm_text(s):
    return re.sub(r'\W+','',s.casefold())


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('new');a.add_argument('path');a.add_argument('--goal',required=True)
    b=sub.add_parser('validate');b.add_argument('path');b.add_argument('--base',help='Root of evidence artifacts (defaults to trace directory)')
    args=ap.parse_args();path=Path(args.path).resolve()
    if args.cmd=='new':
        if path.exists():raise SystemExit(f'Refusing to overwrite {path}')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(skeleton(args.goal),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(path);return
    data=json.loads(path.read_text(encoding='utf-8'))
    report=verify_trace(data,Path(args.base).resolve() if args.base else path.parent)
    print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['ok'] else 1)
if __name__=='__main__':main()
