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


# A subset of short generic words cannot establish a UI-design intent by themselves.
# This is a lexical safeguard, NOT a semantic topic classifier.
CONTEXT_DEPENDENT_CUES=frozenset(("구조","표현","의미","관계","역할","분류","비교","문제","상태","동작","완료"))

def _cue_matches(q, cue):
    c=norm(cue)
    if not c:return False
    if " " in c:return c in q
    # Latin single words: don't match infixes like "form" inside "performance".
    if re.fullmatch(r"[a-z0-9_-]+",c):
        return bool(re.search(r"(?<![a-z0-9_])"+re.escape(c)+r"(?![a-z0-9_])",q))
    # Short Korean cues: reject unrelated compounds such as 구조 in 구조론.
    if re.fullmatch(r"[가-힣]+",c) and len(c)<=2:
        allowed=("은","는","이","가","을","를","과","와","에","에서","으로",
                 "로","의","도","만","에게","에선","이다","인지","에도")
        return any(t==c or any(t==c+suffix for suffix in allowed) for t in q.split())
    if c in q:return True
    # Conservative basic inflection for noun-form verb cues such as 찾기 -> 찾는.
    if re.fullmatch(r"[가-힣]+",c) and len(c)>=2 and c.endswith(("기","다")):
        stem=c[:-1]
        endings=("는","기","다","아","어","아서","어서","고","을","으려","으려면","으면","도록","는데","게")
        return any(t==stem+ending for t in q.split() for ending in endings)
    return False

def analyze(question, concepts_path=CONCEPTS):
    data=json.loads(Path(concepts_path).read_text(encoding='utf-8'))
    q=norm(question)
    matches=[]
    for concept in data['concepts']:
        cues=[norm(c) for c in concept['cues']]
        found=[c for c in cues if _cue_matches(q,c)]
        if found:
            matches.append({'id':concept['id'],'matched':found,'expand':concept['expand'],
                            'cards':concept['cards'],'strength':min(3,len(found)),
                            'has_domain_anchor':any(c not in CONTEXT_DEPENDENT_CUES for c in found)})
    matches.sort(key=lambda x:(-x['strength'],x['id']))
    expanded=[]
    for concept in matches[:6]:
        for term in concept['expand']:
            if term not in expanded: expanded.append(term)
    return {'original':question,'parts':parts(question),'concepts':matches,
            'expansions':expanded[:35], 'mode':'offline_rule_based_concept_expansion'}
