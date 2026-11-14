import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_research import resolve,has_secret
from gemini_client import generate_json, GeminiError
class GeminiResearchTests(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads((ROOT/'config.example.json').read_text());self.cfg['gemini']['mode']='ask';self.cfg['cache']['enabled']=False
    def test_local_without_key(self):
        r=resolve('비례와 리듬',config_obj=self.cfg)
        self.assertEqual(r['retrieval_method'],'local')
        self.assertTrue(r['cards'])
    def test_denied_by_default(self):
        with self.assertRaises(PermissionError):
            resolve('비례와 리듬',provider='gemini',config_obj=self.cfg)
    def test_unknown_id_discarded(self):
        f=lambda *args,**kwargs:{'selections':[{'id':'NOT-REAL','reason':'invented'},{'id':'P07','reason':'composition'},{'id':'P07','reason':'duplicate'}]}
        r=resolve('비례와 리듬',provider='gemini',approve_external=True,gemini_func=f,config_obj=self.cfg)
        self.assertEqual([x['id'] for x in r['cards']],['P07'])
        self.assertTrue(r['requires_codex_review'])
    def test_key_protection(self):
        self.assertTrue(has_secret('api_key = ABCDEFGHIJKLMNOPQRST'))
        with self.assertRaises(PermissionError):
            resolve('password=supersecretpassword',provider='gemini',approve_external=True,gemini_func=lambda *_: {},config_obj=self.cfg)
    def test_remote_response_invalid(self):
        with self.assertRaises(GeminiError):
            resolve('작업 흐름',provider='gemini',approve_external=True,gemini_func=lambda *a,**kw:{'foo':[]},config_obj=self.cfg)
    def test_rest_request_mock_without_network(self):
        import json
        class FakeResponse:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):return json.dumps({'candidates':[{'content':{'parts':[{'text':'{"selections":[]}' }]}}]}).encode()
        def fake_open(req,timeout=1):
            self.assertTrue(req.full_url.endswith('/models/gemini-3.6-flash:generateContent'))
            self.assertIn(b'responseMimeType',req.data)
            self.assertEqual(req.get_method(),'POST')
            return FakeResponse()
        self.assertEqual(generate_json('Please select cards',api_key='test-placeholder',opener=fake_open),{'selections':[]})
    def test_rest_client_no_key(self):
        with self.assertRaises(GeminiError):
            generate_json('hello',api_key='') if __import__('os').environ.get('GEMINI_API_KEY') is None else generate_json('hello',model='bad model',api_key='test')
if __name__=='__main__':unittest.main()
