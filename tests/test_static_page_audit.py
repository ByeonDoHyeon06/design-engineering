"""Run: python -m unittest discover -s tests -v"""
import importlib.util
from pathlib import Path
import unittest

mod_path=Path(__file__).resolve().parents[1]/'scripts/static_page_audit.py'
spec=importlib.util.spec_from_file_location('static_page_audit',mod_path)
audit_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

class AuditTests(unittest.TestCase):
    def test_missing_anchor_and_duplicate_id_are_errors(self):
        html='<html><body><main id="x"></main><div id="x"></div><a href="#ghost">go</a></body></html>'
        findings=audit_module.audit(html)['findings']
        self.assertEqual({f['code'] for f in findings if f['level']=='ERROR'}, {'DUPLICATE_ID','MISSING_ANCHOR'})

    def test_duplicate_product_heading_different_sections_is_review_only(self):
        html='<main id="main"><section id="catalog"><h3>Solen Fetch</h3></section><section id="more"><h3>Solen Fetch</h3></section></main>'
        findings=audit_module.audit(html)['findings']
        self.assertIn('REPEATED_HEADING',[f['code'] for f in findings])
        self.assertFalse([f for f in findings if f['level']=='ERROR'])

    def test_repetition_same_context_not_flagged(self):
        html='<main id="main"><section id="list"><h3>Known</h3><h3>Known</h3></section></main>'
        findings=audit_module.audit(html)['findings']
        self.assertNotIn('REPEATED_HEADING',[f['code'] for f in findings])

    def test_valid_skip_link_and_anchor(self):
        html='<a class="skip-link" href="#content">Skip</a><nav><a href="#products">Products</a></nav><main id="content"><section id="products"><h2>Work</h2></section></main>'
        findings=audit_module.audit(html)['findings']
        self.assertEqual(findings,[])

if __name__=='__main__': unittest.main()
