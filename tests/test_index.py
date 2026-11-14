import tempfile, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_index import rebuild,search
class IndexTests(unittest.TestCase):
    def test_index_and_search_no_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'index.sqlite';result=rebuild(db,ROOT)
            self.assertGreaterEqual(result['indexed'],23)
            hits=search('composition and layout',top=8,db_path=db,root=ROOT)
            self.assertTrue(hits)
            self.assertTrue(all((ROOT/x['path']).is_file() for x in hits))
    def test_unknown_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'i.db';rebuild(p,ROOT)
            self.assertEqual(search('qwertylongunknownxyz',db_path=p,root=ROOT),[])
if __name__=='__main__':unittest.main()
