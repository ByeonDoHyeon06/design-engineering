#!/usr/bin/env python3
"""Small offline bilingual design-question interpreter.

Concepts are retrieval hints, not design prescriptions. It does not claim neural
semantic understanding. External providers are never called by this module.
"""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONCEPTS=ROOT/'knowledge/concepts.json'


def norm(s):
    return ' '.join(re.findall(r'[\w가-힣]+',str(s).casefold()))


def parts(question):
    chunks=re.split(r'[\n.;?!]|\s+(?:그리고|하지만|또는|versus|vs)\s+', question)
    return [x.strip() for x in chunks if x.strip()] or [question.strip()]


def analyze(question, concepts_path=CONCEPTS):
    data=json.loads(Path(concepts_path).read_text(encoding='utf-8'))
    q=norm(question)
    matches=[]
    for concept in data['concepts']:
        cues=[norm(c) for c in concept['cues']]
        found=[c for c in cues if c and c in q]
        if found:
            matches.append({'id':concept['id'],'matched':found,'expand':concept['expand'],
                            'cards':concept['cards'],'strength':min(3,len(found))})
    matches.sort(key=lambda x:(-x['strength'],x['id']))
    expanded=[]
    for concept in matches[:6]:
        for term in concept['expand']:
            if term not in expanded: expanded.append(term)
    return {'original':question,'parts':parts(question),'concepts':matches,
            'expansions':expanded[:35], 'mode':'offline_rule_based_concept_expansion'}
