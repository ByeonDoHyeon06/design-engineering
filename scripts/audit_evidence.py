#!/usr/bin/env python3
"""Offline structural integrity audit for curated knowledge. Not a replication of primary-source research."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'knowledge/catalog.json').read_text(encoding='utf8'))
SRC=json.loads((ROOT/'knowledge/sources.json').read_text(encoding='utf8'))
CLAIMS=json.loads((ROOT/'knowledge/claims.json').read_text(encoding='utf8'))
byid={s['id']:s for s in SRC['records']}; claims={c['id']:c for c in CLAIMS['claims']}
errors=[]; seen=set(); updated=0
for row in CAT['records']:
    id_=row['id']; path=ROOT/row['path']
    if id_ in seen: errors.append('duplicate card '+id_)
    seen.add(id_)
    if not path.is_file():errors.append('missing card '+id_);continue
    body=path.read_text(encoding='utf8')
    # K IDs are card identifiers, not evidence grades. Only cards explicitly
    # linked to curated verified claims receive the claim-specific audit.
    if id_.startswith('K') and row.get('claims'):
        updated+=1
        for need in ('When to retrieve','study scope','derived design advice','Verification in a live design','Provenance'):
            if need.lower() not in body.lower():errors.append(id_+': missing '+need)
        for clid in row.get('claims',[]):
            if clid not in claims:errors.append(id_+': unknown claim '+clid)
            elif claims[clid]['source_id'] not in row['source_ids']:errors.append(id_+': claim source mismatch '+clid)
    if id_.startswith('K') and not row.get('claims'):
        for need in ('When to retrieve','Verification level:', 'Countercases','Provenance'):
            if need.lower() not in body.lower():errors.append(id_+': missing '+need)
        if 'verified claim ids:** none' not in body.lower():
            errors.append(id_+': missing explicit unverified-claims disclosure')
    for sid in row['source_ids']:
        if sid not in byid:errors.append(id_+': unknown source '+sid)
for c in CLAIMS['claims']:
    if c['source_id'] not in byid:errors.append('claim source absent '+c['id'])
    for required in ('source_scope','do_not_infer','source_supported_summary','verification_basis'):
        if not c.get(required):errors.append('claim missing '+required+': '+c['id'])
    s=byid.get(c['source_id'],{})
    if not s.get('reverified_at'):errors.append('claim source not reverified '+c['id'])
report={'cards':len(CAT['records']),'added_curated_cards':updated,'sources':len(byid),'curated_claims':len(CLAIMS['claims']),'legacy_sources_without_reverification':sum(not bool(x.get('reverified_at')) for x in byid.values()),'errors':errors,'audit_scope':'local link/schema/provenance integrity only; web source verification requires manual review'}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
