"""Repository hygiene checks for the canonical v4 layout."""
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
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
        docs = [ROOT/"README.md",ROOT/"i18n/README.ko.md",ROOT/"knowledge/README.md",
                ROOT/"docs/architecture.md",ROOT/"docs/knowledge-management.md"]
        for file in docs:
            text=file.read_text(encoding="utf-8")
            for path in re.findall(r"\]\(([^)]+)\)",text) + re.findall(r'<a\s+[^>]*href="([^"]+)"', text):
                if "://" in path or path.startswith("#"):
                    continue
                target=file.parent/path.split("#",1)[0]
                self.assertTrue(target.is_file(),f"{file}: broken Markdown link: {path}")

    def test_bilingual_readmes_share_the_same_local_safe_artwork(self):
        expected = {
            "design-engineering-mark.svg",
            "hero-system.svg",
            "process-loop.svg",
            "knowledge-context.svg",
            "validation-study.svg",
        }
        svg_ns = "{http://www.w3.org/2000/svg}"
        for path,prefix in [
            (ROOT/"README.md", "assets/"),
            (ROOT/"i18n/README.ko.md", "../assets/"),
        ]:
            content = path.read_text(encoding="utf-8")
            images = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', content)
            self.assertEqual(set(images), {prefix + name for name in expected})
            self.assertEqual(len(images), len(expected))
            self.assertEqual(len(re.findall(r'<img\s+[^>]*alt="[^"]+"',content)),
                             len(images), "Image alt text is required for both languages.")
            for src in images:
                asset = (path.parent / src).resolve()
                self.assertTrue(asset.is_file(), src)
                text = asset.read_text(encoding="utf-8")
                self.assertNotIn("<script", text.lower())
                self.assertNotIn("<foreignobject", text.lower())
                self.assertNotIn("<image ", text.lower())
                self.assertNotIn("https://", text.replace('https://www.w3.org/2000/svg',''))
                self.assertNotIn("http://", text.replace('http://www.w3.org/2000/svg',''))
                tree = ET.fromstring(text)
                self.assertEqual(tree.tag, svg_ns + "svg")
                self.assertTrue(tree.attrib.get("viewBox"))
                self.assertIsNotNone(tree.find(svg_ns + "title"))
                self.assertIsNotNone(tree.find(svg_ns + "desc"))
                self.assertGreater(asset.stat().st_size, 500)

    def test_default_readme_is_english_and_korean_translation_is_linked(self):
        english = (ROOT/"README.md").read_text(encoding="utf-8")
        korean = (ROOT/"i18n/README.ko.md").read_text(encoding="utf-8")
        self.assertIn('href="i18n/README.ko.md"', english)
        self.assertIn('href="../README.md"', korean)
        self.assertIn("## Overview", english)
        self.assertIn("## Getting started", english)
        self.assertIn("## 프로젝트 소개", korean)
        self.assertIn("## 시작하기", korean)
        self.assertEqual(english.count('assets/hero-system.svg'),
                         korean.count('../assets/hero-system.svg'))

    def test_source_registry_has_no_orphans_or_duplicate_aliases(self):
        result=knowledge_health.inspect(ROOT)
        self.assertEqual(result["errors"],[],result)
        self.assertEqual(result["warnings"],[],result)
        self.assertEqual(result["counts"]["potential_duplicate_source_groups"],0)

if __name__=="__main__":
    unittest.main()
