#!/usr/bin/env python3
"""Review meaningfully different design hypotheses; does not prescribe visual styles."""
import argparse,json,re
from pathlib import Path


def tokens(s):
    return set(x for x in re.findall(r'[\w가-힣]+',str(s).casefold()) if len(x)>2)


def compare(alternatives):
    issues=[]; pairs=[]
    for i,a in enumerate(alternatives):
        for j,b in enumerate(alternatives[:i]):
            t1=tokens(a.get('meaning_interpretation','')+' '+a.get('visual_relationship',''))
            t2=tokens(b.get('meaning_interpretation','')+' '+b.get('visual_relationship',''))
            similarity=len(t1&t2)/len(t1|t2) if t1|t2 else 1
            pairs.append({'pair':[b.get('id',j),a.get('id',i)],'token_jaccard':round(similarity,3)})
            if similarity>.72:issues.append(f"Conceptual similarity risk between {a.get('id',i)} and {b.get('id',j)}: {similarity:.2f}")
            if a.get('visual_relationship')==b.get('visual_relationship') and a.get('visual_relationship'):
                issues.append(f"Same visual relationship for {a.get('id',i)} and {b.get('id',j)}")
    for a in alternatives:
        if not a.get('meaning_interpretation'):issues.append(f"Missing meaning interpretation: {a.get('id')}")
        if not a.get('design_tradeoff'):issues.append(f"Missing tradeoff: {a.get('id')}")
    return {'alternatives':len(alternatives),'similarity_pairs':pairs,'review_flags':issues,
            'warning':'Token overlap is only a surface-level cue; independent interpretation requires human/AI critique.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('file')
    a=ap.parse_args();data=json.loads(Path(a.file).read_text(encoding='utf8'))
    print(json.dumps(compare(data.get('alternatives',[])),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
