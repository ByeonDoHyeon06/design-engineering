"""Current design-engineering behavior tests, no network or browser required."""
import json,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import knowledge_index,query_understanding,decision_trace,concept_exploration,visual_critique,ux_scenarios

class RetrievalWorkflowTests(unittest.TestCase):
    def test_original_missing_natural_language_question(self):
        hits=knowledge_index.search('행사 홈페이지에서 정보를 명확하게 전달하는 방법',top=3)
        self.assertIn('P05',[x['id'] for x in hits])
        self.assertIn('P06',[x['id'] for x in hits])

    def test_query_expansion_not_page_template(self):
        a=query_understanding.analyze('행사 홈페이지 정보를 명확하게 전달하고 싶다')
        self.assertIn('information_clarity',[x['id'] for x in a['concepts']])
        self.assertIn('information hierarchy',a['expansions'])

    def test_small_retrieval_regression_set(self):
        from retrieval_evaluation import evaluate
        data=json.loads((ROOT/'benchmarks/retrieval-core.json').read_text(encoding='utf8'))
        result=evaluate(data,3)
        self.assertEqual(result['queries'],20)
        self.assertGreaterEqual(result['positive_hit_at_k'],0.8)

    def test_verified_filter_has_explicit_claims(self):
        hits=knowledge_index.search('시각적 미학 색채',top=10,verified_only=True)
        self.assertTrue(hits)
        self.assertTrue(all(x['verified_claim_ids'] for x in hits))
        self.assertTrue(all(x['evidence_status']=='source_claims_checked' for x in hits))
        for item in hits:
            for c in item['verified_claims']:
                self.assertTrue(c['source_scope'])
                self.assertTrue(c['do_not_infer'])

    def _isolation_root(self,t):
        root=Path(t)
        (root/'knowledge/cards').mkdir(parents=True)
        
        for name in ['sources.json','concepts.json']:
            shutil.copy2(ROOT/'knowledge'/name,root/'knowledge'/name)
        shutil.copy2(ROOT/'knowledge/claims.json',root/'knowledge/claims.json')
        record=next(r for r in json.loads((ROOT/'knowledge/catalog.json').read_text())['records'] if r['id']=='K01')
        text=(ROOT/record['path']).read_text(encoding='utf8')
        return root,record,text

    def test_verified_is_not_id_prefix(self):
        with tempfile.TemporaryDirectory() as t:
            root,r,body=self._isolation_root(t)
            r['id']='Z99';r['path']='knowledge/cards/Z99.md'
            (root/r['path']).write_text(body,encoding='utf8')
            (root/'knowledge/catalog.json').write_text(json.dumps({'records':[r]}),encoding='utf8')
            hits=knowledge_index.search('미학 색채',root=root,db_path=root/'i.sqlite',verified_only=True)
            self.assertEqual([x['id'] for x in hits],['Z99'])
            self.assertIn('VC01',hits[0]['verified_claim_ids'])

    def test_claim_source_mismatch_is_not_verified(self):
        with tempfile.TemporaryDirectory() as t:
            root,r,body=self._isolation_root(t)
            r['source_ids']=['THIS-IS-NOT-A-VALID-SOURCE']
            (root/r['path']).write_text(body,encoding='utf8')
            (root/'knowledge/catalog.json').write_text(json.dumps({'records':[r]}),encoding='utf8')
            hits=knowledge_index.search('미학 색채',root=root,db_path=root/'i.sqlite',verified_only=True)
            self.assertEqual(hits,[])

    def test_index_rebuilds_after_card_change(self):
        with tempfile.TemporaryDirectory() as t:
            root,r,body=self._isolation_root(t)
            (root/r['path']).write_text(body,encoding='utf8')
            (root/'knowledge/catalog.json').write_text(json.dumps({'records':[r]}),encoding='utf8')
            db=root/'i.sqlite'
            knowledge_index.rebuild(db,root)
            self.assertEqual(knowledge_index.search('uniquezzzzzword',root=root,db_path=db),[])
            (root/r['path']).write_text(body+'\n uniquezzzzzword',encoding='utf8')
            self.assertEqual(knowledge_index.search('uniquezzzzzword',root=root,db_path=db)[0]['id'],'K01')

    def test_only_local_embedding_path(self):
        with self.assertRaises(ValueError):
            knowledge_index.search('hierarchy',embedding_model='/missing/model/path')

    def test_trace_rejects_unproven_validation(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);d=decision_trace.skeleton('Find event program')['decisions'][0]
            d.update({'problem':'Navigation comprehension unclear','selected_hypothesis':'Clear program entry improves findability',
                      'why_this_interpretation':'Site mission includes program discovery','implemented_in':['index.html'],
                      'status':'validated','alternatives':[{'meaning_relation':'timeline'},{'meaning_relation':'menu'}]})
            (root/'index.html').write_text('x');(root/'capture.png').write_bytes(b'PNG stub')
            check=d['review_rounds'][0]['checks'][0]
            check.update({'outcome':'pass','observation':'After clicking program, label is visible',
                          'artifact':'capture.png'})
            self.assertTrue(decision_trace.verify_trace({'decisions':[d]},root)['ok'])
            check['artifact']='missing.png'
            self.assertFalse(decision_trace.verify_trace({'decisions':[d]},root)['ok'])

    def test_visual_critique_requires_after_capture_for_fix(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'390-viewport.png').write_bytes(b'PNG')
            report={'results':[{'width':390,'horizontal_overflow':True,'anchor_review':[],
                                'screenshots':['390-viewport.png']}], 'scope':'browser'}
            doc=visual_critique.scaffold(report,'page.html')
            self.assertTrue(visual_critique.audit(doc,root)['ok'])
            issue=doc['observations'][0];issue['status']='fixed'
            self.assertFalse(visual_critique.audit(doc,root)['ok'])
            (root/'after.png').write_bytes(b'PNG altered after a real revision');issue['after_screenshot']='after.png'
            issue['after_observation']='Actual screenshot inspected: no overflow'
            self.assertTrue(visual_critique.audit(doc,root)['ok'])

    def test_conceptual_duplication_is_review_flag(self):
        a=[{'id':'a','meaning_interpretation':'Same idea','visual_relationship':'same grouping','design_tradeoff':'a'},
           {'id':'b','meaning_interpretation':'Same idea','visual_relationship':'same grouping','design_tradeoff':'b'}]
        self.assertTrue(concept_exploration.compare(a)['review_flags'])

    def test_task_scenarios_need_observable_success(self):
        data={'scenarios':[{'id':'x','user_goal':'Find session','success_criterion':'Locate date',
              'steps':[{'action':'click','selector':'button'}]}]}
        self.assertTrue(ux_scenarios.validate(data))
        data['scenarios'][0]['steps'].append({'action':'assert_text','selector':'#date','value':'June'})
        self.assertFalse(ux_scenarios.validate(data))

if __name__=='__main__':unittest.main()
