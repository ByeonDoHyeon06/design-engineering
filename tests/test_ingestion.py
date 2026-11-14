import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_ingest import extract_file,prepare,commit,IngestError

class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.sample=self.base/'research.md'
        self.sample.write_text('# Design research\n\n'+('Users in the pilot study compared grouped items to ungrouped items. '\
          'The study only sampled 12 people and did not include keyboard tasks. ')*10,encoding='utf8')
        self.kw=dict(title='A sample design study',authors='A. Example',local_dir=self.base/'queue')
    def test_utf8_extract(self):
        sha,pages=extract_file(self.sample);self.assertEqual(len(sha),64);self.assertEqual(pages[0]['page'],1)
    def test_default_draft_has_no_fact_claim(self):
        f=prepare(self.sample,**self.kw)
        data=json.loads(f.read_text());self.assertEqual(data['status'],'pending_review')
        self.assertFalse(data['candidates'][0]['claim_text'])
        self.assertEqual(data['candidates'][0]['status'],'pending')
    def test_requires_explicit_external_doc_consent(self):
        with self.assertRaises(PermissionError):
            prepare(self.sample,mode='gemini',**self.kw,call=lambda p: {'candidates':[]})
    def test_reject_fabricated_quote_and_preserve_review_status(self):
        f=prepare(self.sample,mode='gemini',approve_external=True,allow_private_content=True,
                  call=lambda p: {'candidates':[{'claim_text':'Invented','evidence_quote':'Something not in the file'}]},**self.kw)
        o=json.loads(f.read_text());self.assertFalse(o['candidates'][0]['quote_verified'])
        o['candidates'][0].update(status='approved',limitations='pilot only',queries=['grouping'],problem_signals=['discovery'])
        f.write_text(json.dumps(o))
        with self.assertRaises(IngestError):
            import shutil
            (self.base/'knowledge').mkdir()
            shutil.copy(ROOT/'knowledge/catalog.json',self.base/'knowledge/catalog.json')
            shutil.copy(ROOT/'knowledge/sources.json',self.base/'knowledge/sources.json')
            commit(f,confirm=True,reviewer='human',root=self.base)
    def test_no_publish_without_human_review(self):
        f=prepare(self.sample,**self.kw)
        with self.assertRaises(PermissionError):commit(f,reviewer='human',root=self.base)
        with self.assertRaises(IngestError):commit(f,confirm=True,reviewer='human',root=self.base)
    def test_commit_and_duplicate_block(self):
        f=prepare(self.sample,**self.kw)
        o=json.loads(f.read_text());c=o['candidates'][0]
        c.update(status='approved',claim_text='Pilot participants compared grouped and ungrouped items',
            limitations='Small 12-person pilot. No keyboard tasks.',queries=['grouping','비교'],
            problem_signals=['Difficult to compare grouped items'],reasoning_moves=['Test alternatives in the actual task'])
        f.write_text(json.dumps(o,ensure_ascii=False))
        import shutil
        (self.base/'knowledge').mkdir()
        shutil.copy(ROOT/'knowledge/catalog.json',self.base/'knowledge/catalog.json')
        shutil.copy(ROOT/'knowledge/sources.json',self.base/'knowledge/sources.json')
        result=commit(f,confirm=True,reviewer='Human Reviewer',root=self.base)
        self.assertEqual(len(result),1)
        catalog=json.loads((self.base/'knowledge/catalog.json').read_text())
        self.assertIn(result[0]['id'],[r['id'] for r in catalog['records']])
        self.assertTrue((self.base/result[0]['path']).is_file())
        with self.assertRaises(IngestError):commit(f,confirm=True,reviewer='human',root=self.base)
    def test_quote_flag_tampering_fails(self):
        f=prepare(self.sample,**self.kw)
        o=json.loads(f.read_text());c=o['candidates'][0]
        c.update(status='approved',quote_verified=True,evidence_quote='A fabricated excerpt not in paper',
            claim_text='Unsupported inference',limitations='unknown',queries=['study'],problem_signals=['research'])
        f.write_text(json.dumps(o))
        import shutil
        (self.base/'knowledge').mkdir()
        shutil.copy(ROOT/'knowledge/catalog.json',self.base/'knowledge/catalog.json')
        shutil.copy(ROOT/'knowledge/sources.json',self.base/'knowledge/sources.json')
        with self.assertRaises(IngestError):commit(f,confirm=True,reviewer='human',root=self.base)
    def test_source_change_after_prepare_fails(self):
        f=prepare(self.sample,**self.kw)
        o=json.loads(f.read_text());c=o['candidates'][0]
        c.update(status='approved',claim_text='A source-specific, manually reviewed claim',limitations='pilot only',
            queries=['study'],problem_signals=['research'])
        f.write_text(json.dumps(o))
        self.sample.write_text(self.sample.read_text()+' changed!')
        with self.assertRaises(IngestError):commit(f,confirm=True,reviewer='human',root=self.base)
    def test_unsupported_extension(self):
        f=self.base/'t.exe';f.write_text('x')
        with self.assertRaises(IngestError):extract_file(f)
if __name__=='__main__':unittest.main()
