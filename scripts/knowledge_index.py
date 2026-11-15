#!/usr/bin/env python3
"""Knowledge Retrieval 2.0: offline concept expansion + FTS + weighted char-grams,
plus optional *local* sentence-embedding reranking (no implicit model downloads).

Inclusion in a verified search requires an explicit reviewed claim linked in the
card body and a reverified source, never an ID prefix. A claim's publication
verification does NOT establish its transfer to a particular interface.
"""
import argparse, hashlib, json, math, re, sqlite3
from collections import Counter
from pathlib import Path
from knowledge_lookup import ROOT
from query_understanding import analyze, norm

INDEX=ROOT/'.cache'/'knowledge.sqlite'
CAT=ROOT/'knowledge/catalog.json'
CLAIMS=ROOT/'knowledge/verified/claims.json'
SOURCES=ROOT/'knowledge/sources.json'


def db_open(path=INDEX):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(path)


def _load_registry(root):
    cats=json.loads((root/'knowledge/catalog.json').read_text(encoding='utf-8'))['records']
    claims={c['id']:c for c in json.loads((root/'knowledge/verified/claims.json').read_text(encoding='utf-8'))['claims']}
    sources={s['id']:s for s in json.loads((root/'knowledge/sources.json').read_text(encoding='utf-8'))['records']}
    return cats,claims,sources


def _claim_ids(body):
    match=re.search(r'\*\*Verified claim IDs?:\*\*\s*([^\n]+)',body,flags=re.I)
    return re.findall(r'\bVC\d+\b',match.group(1)) if match else []


def _proof_for_card(row, body, claims, sources):
    ids=[]; issues=[]
    for cid in _claim_ids(body):
        c=claims.get(cid)
        if not c:
            issues.append('unregistered claim '+cid);continue
        sid=c.get('source_id')
        if sid not in row.get('source_ids',[]):
            issues.append('source mismatch '+cid);continue
        if not sources.get(sid,{}).get('reverified_at'):
            issues.append('unreverified source '+cid);continue
        ids.append(cid)
    return ids,issues


def _signature(root):
    paths=[root/'knowledge/catalog.json',root/'knowledge/verified/claims.json',root/'knowledge/sources.json',root/'knowledge/concepts.json']
    cat=json.loads(paths[0].read_text(encoding='utf-8'))['records']
    paths.extend(root/r['path'] for r in cat)
    h=hashlib.sha256()
    # Cheap cache-invalidating fingerprint; this is not a security digest of sources.
    # Knowledge ingestion independently validates source-document SHA-256.
    for path in paths:
        h.update(str(path.relative_to(root)).encode()); h.update(b'\0')
        try:
            st=path.stat();h.update(f'{st.st_size}:{st.st_mtime_ns}'.encode())
        except FileNotFoundError:h.update(b'[missing]')
    return h.hexdigest()


def rebuild(db_path=INDEX,root=ROOT):
    root=Path(root);db_path=Path(db_path)
    cards,claims,sources=_load_registry(root)
    if db_path.exists():db_path.unlink()
    db=db_open(db_path)
    try:
        db.execute('CREATE TABLE cards (id TEXT PRIMARY KEY, title TEXT, path TEXT, kind TEXT, source_ids TEXT, claim_ids TEXT, body TEXT, hints TEXT, verification_issues TEXT)')
        db.execute('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)')
        try:
            db.execute("CREATE VIRTUAL TABLE card_fts USING fts5(id UNINDEXED, title, body, hints, tokenize='trigram')")
            tokenizer='trigram'
        except sqlite3.OperationalError:
            db.execute('CREATE VIRTUAL TABLE card_fts USING fts5(id UNINDEXED, title, body, hints)')
            tokenizer='unicode61'
        for row in cards:
            path=root/row['path']
            if not path.is_file():continue
            body=path.read_text(encoding='utf-8')
            hints=' '.join(row.get('queries',[])+row.get('signals',[]))
            claim_ids,issues=_proof_for_card(row,body,claims,sources)
            db.execute('INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?)',
                (row['id'],row['title'],row['path'],row['kind'],json.dumps(row.get('source_ids',[])),
                 json.dumps(claim_ids),body,hints,json.dumps(issues)))
            db.execute('INSERT INTO card_fts(id,title,body,hints) VALUES(?,?,?,?)',
                (row['id'],row['title'],body,hints))
        db.execute('INSERT INTO meta VALUES (?,?)',('signature',_signature(root)))
        db.execute('INSERT INTO meta VALUES (?,?)',('tokenizer',tokenizer))
        db.commit()
        return {'indexed':db.execute('SELECT COUNT(*) FROM cards').fetchone()[0],
                'verified_claim_linked':db.execute("SELECT COUNT(*) FROM cards WHERE claim_ids != '[]'").fetchone()[0],
                'tokenizer':tokenizer,'signature':'stat-metadata-cache-fingerprint'}
    finally:db.close()


def _grams(text,n=3):
    text=norm(text)
    return Counter(text[i:i+n] for i in range(len(text)-n+1) if not text[i:i+n].isspace())


def _similarities(query, documents):
    # Character n-gram TF-IDF cosine is a local *lexical resemblance* signal,
    # not a substitute for cross-lingual sentence embeddings.
    corpus=[_grams(x) for x in documents]
    q=_grams(query)
    df=Counter(k for grams in corpus for k in grams)
    total=len(corpus)
    def vector(grams):
        return {k:(1+math.log(n))*math.log(1+(total+1)/(df.get(k,0)+1)) for k,n in grams.items()}
    vq=vector(q);qnorm=math.sqrt(sum(v*v for v in vq.values())) or 1
    result=[]
    for grams in corpus:
        v=vector(grams);den=qnorm*(math.sqrt(sum(z*z for z in v.values())) or 1)
        result.append(sum(vq.get(k,0)*z for k,z in v.items())/den)
    return result


def _embedding_similarities(query,documents,model_path):
    model_path=Path(model_path)
    if not model_path.is_dir():raise ValueError('Embedding model must be an existing LOCAL directory; no model download is allowed.')
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError as e:
        raise RuntimeError('Optional local embeddings require sentence-transformers and numpy.') from e
    model=SentenceTransformer(str(model_path),local_files_only=True)
    vectors=model.encode([query]+documents,normalize_embeddings=True)
    return (np.asarray(vectors[1:])@np.asarray(vectors[0])).tolist()


def _fts(db,terms,top=100):
    tokens=[]
    for term in terms:
        for tok in re.findall(r'[\w가-힣]+',str(term).casefold()):
            if len(tok)>=3 and tok not in tokens:tokens.append(tok)
    if not tokens:return {}
    expr=' OR '.join('"'+t.replace('"','')+'"' for t in tokens[:28])
    try:
        return {id_:index for index,(id_,_) in enumerate(db.execute(
            'SELECT id,bm25(card_fts) FROM card_fts WHERE card_fts MATCH ? ORDER BY bm25(card_fts) LIMIT ?',
            (expr,top)).fetchall())}
    except sqlite3.OperationalError:return {}


def search(q,top=5,db_path=INDEX,root=ROOT,verified_only=False,embedding_model=None,semantic_scores=None,relative_cutoff=0.20):
    if not 0 <= relative_cutoff <= 1:raise ValueError('relative_cutoff must be between 0 and 1')
    if not str(q).strip():return []
    root=Path(root);db_path=Path(db_path)
    if not db_path.exists():rebuild(db_path,root)
    db=db_open(db_path)
    try:
        meta=dict(db.execute('SELECT key,value FROM meta').fetchall())
        if meta.get('signature')!=_signature(root):
            db.close();rebuild(db_path,root);db=db_open(db_path)
        entries=db.execute('SELECT id,title,path,kind,source_ids,claim_ids,body,hints,verification_issues FROM cards').fetchall()
        if not entries:return []
        analysis=analyze(q,root/'knowledge/concepts.json')
        expansions=analysis['expansions']
        fts=_fts(db,[q]+expansions[:14])
        docs=[f'{row[1]} {row[1]} {row[7]} {row[6][:2200]}' for row in entries]
        char=_similarities(q+' '+' '.join(expansions[:10]),docs)
        embed=list(semantic_scores) if semantic_scores is not None else (
              _embedding_similarities(q,docs,embedding_model) if embedding_model else None)
        if embed is not None and len(embed)!=len(entries):raise ValueError('Embedding score length mismatch.')
        sources={s['id']:s for s in json.loads((root/'knowledge/sources.json').read_text(encoding='utf-8'))['records']}
        claims={c['id']:c for c in json.loads((root/'knowledge/verified/claims.json').read_text(encoding='utf-8'))['claims']}
        res=[]
        for i,row in enumerate(entries):
            id_,title,path,kind,src_json,claim_json,body,hints,issue_json=row
            claim_ids=json.loads(claim_json);issues=json.loads(issue_json)
            if verified_only and not claim_ids:continue
            concept_matches=[(c,pos) for c in analysis['concepts'] for pos,card_id in enumerate(c['cards']) if card_id==id_]
            conceptual=sum((2.2*c['strength'])/(2+pos) for c,pos in concept_matches)
            fts_score=1.3/(2+fts[id_]) if id_ in fts else 0
            char_score=char[i]*1.6
            embedding_score=max(0,float(embed[i]))*1.6 if embed is not None else 0
            direct_tokens=[x for x in re.findall(r'[\w가-힣]+',norm(q)) if len(x)>=2]
            meta_norm=norm(title+' '+hints)
            direct_score=min(1.5,sum(0.15 for tok in direct_tokens if tok in meta_norm))
            score=conceptual+fts_score+char_score+direct_score+embedding_score
            if not concept_matches and id_ not in fts and char[i]<0.12 and (embed is None or embed[i]<0.44):continue
            if score<0.14:continue
            details=[]
            for cid in claim_ids:
                cl=claims.get(cid)
                if cl:
                    details.append({'id':cid,'source_id':cl['source_id'], 'evidence_type':cl.get('evidence_type'),
                                    'verification_basis':cl.get('verification_basis'),
                                    'source_scope':cl.get('source_scope'),
                                    'do_not_infer':cl.get('do_not_infer')})
            status='source_claims_checked' if details and not issues else 'no_explicit_reviewed_claim_link'
            res.append({'id':id_,'title':title,'path':path,'kind':kind,'source_ids':json.loads(src_json),
                        'verified_claim_ids':claim_ids,'verified_claims':details,
                        'evidence_status':status,'source_context':[
                            {'id':sid,'type':sources.get(sid,{}).get('type'),
                             'access_level':sources.get(sid,{}).get('access_level'),
                             'reverified_at':sources.get(sid,{}).get('reverified_at')}
                            for sid in json.loads(src_json)],
                        'score':round(score,5),
                        'why_matched':{'concepts':[c['id'] for c,_ in concept_matches],
                                       'fts':id_ in fts,'character_similarity':round(char[i],3),
                                       'local_embeddings':embed is not None}})
        res.sort(key=lambda r:(-r['score'],r['id']))
        # Query-relative noise suppression, NOT calibrated relevance or evidence quality.
        # Only apply if one result has a strong lexical/conceptual match.
        # Keep --relative-cutoff 0 for diagnostics and broad recall.
        if res and relative_cutoff and res[0]['score']>=2.0:
            threshold=res[0]['score']*relative_cutoff
            res=[r for r in res if r['score']>=threshold]
        return res[:max(1,top)]
    finally:db.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('rebuild');a=sub.add_parser('search')
    a.add_argument('query');a.add_argument('--top',type=int,default=5);a.add_argument('--json',action='store_true')
    a.add_argument('--verified-only',action='store_true',help='Requires explicit claim linked to verified source, not card ID prefix')
    a.add_argument('--embedding-model',help='Optional already-downloaded LOCAL sentence-transformers model directory')
    a.add_argument('--relative-cutoff',type=float,default=0.20,
                   help='Query-relative weak-match suppression when best score >= 2; 0 disables it. Heuristic, not probability.')
    opts=p.parse_args()
    if opts.cmd=='rebuild':print(json.dumps(rebuild(),ensure_ascii=False))
    else:
        results=search(opts.query,opts.top,verified_only=opts.verified_only,embedding_model=opts.embedding_model,relative_cutoff=opts.relative_cutoff)
        if opts.json:print(json.dumps(results,ensure_ascii=False,indent=2))
        else:
            for r in results:
                print(f"{r['id']} [{r['evidence_status']}] score={r['score']}: {r['title']}  {r['path']}")
            if not results:print('No matching evidence found; refine question or use opt-in Gemini after permission.')
if __name__=='__main__':main()
