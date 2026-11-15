"""current registry integrity and curated natural-language retrieval smoke tests."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import knowledge_index
from retrieval_evaluation import evaluate

class TypographyWritingTests(unittest.TestCase):
    def test_new_cards_have_grounded_sources_and_explicit_scope(self):
        catalog=json.loads((ROOT/'knowledge/catalog.json').read_text(encoding='utf8'))['records']
        sources={r['id']:r for r in json.loads((ROOT/'knowledge/sources.json').read_text(encoding='utf8'))['records']}
        for cid in ('K16','K17','K18'):
            row=next((r for r in catalog if r['id']==cid),None)
            self.assertIsNotNone(row,cid)
            self.assertTrue(row['source_ids'])
            body=(ROOT/row['path']).read_text(encoding='utf8')
            self.assertIn('Countercases',body)
            self.assertIn('Verification level:',body)
            for sid in row['source_ids']:
                self.assertIn(sid,sources)
                self.assertTrue(sources[sid].get('verification_url'))

    def test_new_cards_are_not_mislabeled_empirically_verified(self):
        queries=['한글 폰트 줄바꿈 타이포그래피','자연스러운 한국어 버튼 문구','콘텐츠 레이아웃 정보 구조']
        for question in queries:
            for item in knowledge_index.search(question,top=12):
                if item['id'] in ('K16','K17','K18'):
                    self.assertEqual(item['verified_claim_ids'],[])
                    self.assertNotEqual(item['evidence_status'],'source_claims_checked')

    def test_curated_queries_retrieve_v39_topics(self):
        data=json.loads((ROOT/'benchmarks/retrieval-typography.json').read_text(encoding='utf8'))
        result=evaluate(data,5)
        self.assertEqual(result['queries'],9)
        self.assertGreaterEqual(result['positive_hit_at_k'],0.8,result['results'])

if __name__=='__main__':
    unittest.main()
