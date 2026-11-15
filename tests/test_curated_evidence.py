import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class CuratedEvidenceTests(unittest.TestCase):
    def test_claim_integrity(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/audit_evidence.py')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        report=json.loads(p.stdout)
        self.assertEqual(report['added_curated_cards'],15)
        self.assertEqual(report['curated_claims'],18)
        self.assertGreater(report['legacy_sources_without_reverification'],0)
    def test_bilingual_retrieval(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        import knowledge_index
        cases={
          '대시보드 데이터 비교 정확도':'K03',
          '시각화 도메인 작업 데이터 추상화':'K04',
          '독창성과 미학 색채':'K01',
          '디자인 아이디어 고착 발산':'K08',
          'WCAG 터치 대상 초점':'K11',
        }
        for query,target in cases.items():
            found=[r['id'] for r in knowledge_index.rank(query)[:10]]
            self.assertIn(target,found,(query,found))
    def test_verified_only_search(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        import knowledge_index, knowledge_index
        self.assertTrue(all(x['id'].startswith('K') for x in knowledge_index.rank('미학 색채',verified_only=True)))
        self.assertTrue(all(x['id'].startswith('K') for x in knowledge_index.search('대시보드 데이터 비교 정확도',verified_only=True)))

    def test_no_unreviewed_claims_promoted(self):
        claims=json.loads((ROOT/'knowledge/claims.json').read_text())['claims']
        sources={x['id']:x for x in json.loads((ROOT/'knowledge/sources.json').read_text())['records']}
        for c in claims:
            self.assertTrue(sources[c['source_id']].get('reverified_at'))
            self.assertIn(c['verification_basis'],['publisher_or_institution_abstract','official_standard_text','official_scope_abstract'])
    def test_no_external_pdfs_or_references(self):
        self.assertFalse(list(ROOT.rglob('*.pdf')))
        self.assertFalse((ROOT/'inspiration').exists())
        self.assertFalse((ROOT/'references').exists())

if __name__=='__main__':unittest.main()
