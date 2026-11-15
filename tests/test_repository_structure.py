"""Repository hygiene checks for the canonical v4 layout."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import knowledge_health

class RepositoryStructureTests(unittest.TestCase):
    def test_one_canonical_skill_and_complete_install(self):
        self.assertEqual([p.relative_to(ROOT).as_posix() for p in ROOT.rglob("SKILL.md")],
                         ["SKILL.md"])
        for name in (
            "README.md", "CONTRIBUTING.md", "pyproject.toml", "scripts/de.py",
            "design_engineering/cli.py", "design_engineering/local_knowledge.py",
            "knowledge/catalog.json", "knowledge/concepts.json",
            "knowledge/sources.json", "knowledge/claims.json",
            "knowledge/governance.json", "scripts/knowledge_index.py",
            "scripts/knowledge_graph.py", "docs/architecture.md",
            "docs/knowledge-management.md",
            ".claude-plugin/plugin.json", "agents/openai.yaml"
        ):
            self.assertTrue((ROOT/name).is_file(),name)

    def test_deleted_versioned_and_compatibility_artifacts_stay_deleted(self):
        retired = [
            "knowledge/" + "verified/claims.json",
            "knowledge/" + "v4/governance.json",
            "knowledge/" + "v4/schema.json",
            "docs/" + "IMPLEMENTATION-QA.md",
            "docs/" + "v4-knowledge-architecture.md",
            "knowledge/" + "references.bib",
            "scripts/" + "browser_smoke.py",
            "scripts/" + "knowledge_lookup.py",
            "scripts/" + "retrieval_benchmark.py",
            "benchmarks/" + "retrieval-v38.json",
            "benchmarks/" + "retrieval-v39.json",
            "benchmarks/" + "retrieval-v4.json",
            "tests/" + "test_v38.py",
            "tests/" + "test_v39.py",
            "tests/" + "test_v40.py",
        ]
        for name in retired:
            self.assertFalse((ROOT/name).exists(),name)

    def test_no_stale_paths_in_live_code_and_docs(self):
        stale = [
            "knowledge/" + "verified/claims.json",
            "knowledge/" + "v4/",
            "scripts/" + "knowledge_lookup.py",
            "scripts/" + "retrieval_benchmark.py",
            "scripts/" + "browser_smoke.py",
            "docs/" + "v4-knowledge-architecture.md",
            "docs/" + "IMPLEMENTATION-QA.md",
            "benchmarks/" + "retrieval-v38.json",
            "benchmarks/" + "retrieval-v39.json",
            "benchmarks/" + "retrieval-v4.json",
        ]
        paths = [ROOT/"README.md",ROOT/"SKILL.md",ROOT/"CONTRIBUTING.md"]
        for directory in ("scripts","docs","tests","knowledge/cards"):
            paths.extend(p for p in (ROOT/directory).rglob("*")
                         if p.is_file() and p.suffix in (".md",".py")
                         and p.name != "test_repository_structure.py")
        for path in paths:
            content=path.read_text(encoding="utf-8")
            for name in stale:
                self.assertNotIn(name,content,f"{path.relative_to(ROOT)} has stale reference {name}")

    def test_internal_document_links_resolve(self):
        docs = [ROOT/"README.md",ROOT/"knowledge/README.md",
                ROOT/"docs/architecture.md",ROOT/"docs/knowledge-management.md"]
        for file in docs:
            text=file.read_text(encoding="utf-8")
            for path in re.findall(r"\]\(([^)]+)\)",text):
                if "://" in path or path.startswith("#"):
                    continue
                target=file.parent/path.split("#",1)[0]
                self.assertTrue(target.is_file(),f"{file}: broken Markdown link: {path}")

    def test_source_registry_has_no_orphans_or_duplicate_aliases(self):
        result=knowledge_health.inspect(ROOT)
        self.assertEqual(result["errors"],[],result)
        self.assertEqual(result["warnings"],[],result)
        self.assertEqual(result["counts"]["potential_duplicate_source_groups"],0)

if __name__=="__main__":
    unittest.main()
