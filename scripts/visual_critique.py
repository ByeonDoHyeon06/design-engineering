#!/usr/bin/env python3
"""Visual Critique Loop scaffold + evidence audit. Never automatically judges beauty.
`start` captures real screenshots; `validate` audits human/AI observations and revisions.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from visual_qa_capture import run as screenshot_run

DIMENSIONS={
 'hierarchy':'Where does the eye enter; are the user goal and next action legible?',
 'composition':'Are proportion, visual weight, alignment and negative space intentional?',
 'density':'Are text/graphics crowded or oddly sparse at each viewport?',
 'rhythm':'Do section transitions have coherent but not mechanical repetition?',
 'visual_meaning':'Do symbols/illustrations explain the subject rather than fill space?',
 'craft':'Inspect typography rendering, contrast, cropping, details and motion meaning.',
 'responsive':'Check the same meaning and tasks at 1440/390/320 and intermediate widths.'}


def scaffold(report,site):
    obs=[]
    for entry in report.get('results',[]):
        w=entry['width']
        if entry.get('horizontal_overflow'):
            obs.append({'id':f'AUTO-{w}-OVERFLOW','dimension':'responsive','viewport':w,
             'severity':'needs_review','observation':'Automated geometry reports horizontal overflow',
             'before_screenshot':f'{w}-viewport.png','proposed_change':'Inspect responsible element; do not hide overflow without considering content',
             'status':'open','after_screenshot':None,'after_observation':None,'linked_decision':None,'detected_by':'browser_geometry'})
        for issue in entry.get('anchor_review',[]):
            obs.append({'id':f'AUTO-{w}-{issue["id"]}','dimension':'responsive','viewport':w,
             'severity':'needs_review','observation':f'Anchor overlap candidate: {issue["metrics"]["overlap"]}px',
             'before_screenshot':f'{w}-viewport.png','proposed_change':'Test anchor click and target readability beneath sticky header',
             'status':'open','after_screenshot':None,'after_observation':None,'linked_decision':None,'detected_by':'browser_geometry'})
    return {'schema_version':1,'source_page':str(site),'capture_scope':report.get('scope'),
        'design_critique_dimensions':DIMENSIONS,'screenshots':[x for r in report.get('results',[]) for x in r['screenshots']],
        'observations':obs,'manual_review':'PENDING',
        'instructions':'View screenshots yourself. Add observations with dimensions, screenshot evidence, hypothesis and proposed change. Mark fixed only when a revised screenshot is inspected. No automatic aesthetic score.'}


def _capture(root, shot):
    """Reject absolute/escaping screenshot refs and missing files."""
    if not isinstance(shot, str) or not shot.strip():
        return None
    root = Path(root).resolve()
    candidate = (root / shot).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        return None
    return candidate


def audit(doc,root):
    errors=[];warnings=[];closed=0
    screenshots={s for s in doc.get('screenshots',[]) if isinstance(s,str)}
    for shot in screenshots:
        if not _capture(root,shot):warnings.append('Missing or unsafe capture '+shot)
    for i,obs in enumerate(doc.get('observations',[]),1):
        label=f'observations[{i}]'
        if obs.get('dimension') not in DIMENSIONS:errors.append(label+': invalid dimension')
        if not obs.get('observation','').strip():errors.append(label+': description required')
        before=obs.get('before_screenshot')
        before_path=_capture(root,before)
        if not before_path:errors.append(label+': before screenshot missing or unsafe')
        if obs.get('status')=='fixed':
            after=obs.get('after_screenshot')
            after_path=_capture(root,after)
            if not after_path:
                errors.append(label+': fixed without actual after screenshot')
            elif before_path:
                # A copied or renamed unchanged image is NOT evidence of a successful revision.
                if hashlib.sha256(after_path.read_bytes()).digest()==hashlib.sha256(before_path.read_bytes()).digest():
                    errors.append(label+': before and after screenshots have identical bytes')
            if after_path and before_path and after_path==before_path:
                errors.append(label+': before and after reference the same file')
            if not obs.get('after_observation'):errors.append(label+': missing after observation')
            if before_path and after_path and before_path!=after_path and hashlib.sha256(after_path.read_bytes()).digest()!=hashlib.sha256(before_path.read_bytes()).digest() and obs.get('after_observation'):
                closed+=1
        elif obs.get('status') not in {'open','rejected','not_tested'}:
            errors.append(label+': invalid issue status')
        if obs.get('detected_by')=='manual' and not obs.get('proposed_change'):
            warnings.append(label+': no proposed revision')
    if doc.get('manual_review')!='COMPLETE':warnings.append('Visual judgment not yet completed')
    if doc.get('manual_review')=='COMPLETE' and not doc.get('observations'):
        warnings.append('Manual review marked complete with no observations; add reviewed checks even if no issues')
    return {'ok':not errors,'errors':errors,'warnings':warnings,'issues':len(doc.get('observations',[])),
            'confirmed_fixes':closed,'manually_reviewed':doc.get('manual_review')=='COMPLETE'}


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('start');a.add_argument('html');a.add_argument('--out',required=True)
    b=sub.add_parser('validate');b.add_argument('review_file')
    args=ap.parse_args()
    if args.cmd=='start':
        out=Path(args.out).resolve(); report=screenshot_run(args.html,out)
        review=scaffold(report,args.html)
        path=out/'critique.json';path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'review_file':str(path),'screenshots':review['screenshots'],'geometry_issues':len(review['observations']),
           'manual_visual_review':'NOT_PERFORMED'},ensure_ascii=False,indent=2))
    else:
        path=Path(args.review_file).resolve()
        result=audit(json.loads(path.read_text(encoding='utf8')),path.parent)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        raise SystemExit(0 if result['ok'] else 1)
if __name__=='__main__':main()
