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
            "design_engineering/evaluation.py", "docs/design-evaluation.md",
            "benchmarks/design-tasks.json",
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

    def test_bilingual_readmes_share_local_responsive_artwork(self):
        # Full-width desktop art, portrait mobile variants, and recognizable agent marks.
        primary = {
            "design-engineering-mark.webp",
            "hero-system.svg", "process-loop.svg",
            "knowledge-context.svg", "validation-study.svg",
            "integrations/claude.svg", "integrations/codex.svg",
        }
        mobile = {
            "hero-system-mobile.svg", "process-loop-mobile.svg",
            "knowledge-context-mobile.svg", "validation-study-mobile.svg",
        }
        svg_ns = "{http://www.w3.org/2000/svg}"
        for path,prefix in (
            (ROOT/"README.md","assets/"),
            (ROOT/"i18n/README.ko.md","../assets/"),
        ):
            content = path.read_text(encoding="utf-8")
            images = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>',content)
            sources = re.findall(r'<source\s+[^>]*srcset="([^"]+)"[^>]*>',content)
            self.assertEqual(set(images), {prefix + n for n in primary})
            self.assertEqual(set(sources), {prefix + n for n in mobile})
            self.assertEqual(len(images),len(primary))
            self.assertEqual(len(sources),len(mobile))
            self.assertEqual(len(re.findall(r'<picture>',content)),4)
            # Empty alt is correct for decorative logos beside explicit agent names.
            self.assertEqual(len(re.findall(r'<img\s+[^>]*alt="[^"]*"',content)),
                             len(images))
            self.assertEqual(len(re.findall(r'<source\s+media="\(max-width: 640px\)"',content)),
                             len(mobile))
            for name in primary | mobile:
                asset=(path.parent / prefix / name).resolve()
                self.assertTrue(asset.is_file(),name)
                if asset.suffix == ".webp":
                    data=asset.read_bytes()
                    self.assertTrue(data.startswith(b"RIFF"),name)
                    self.assertEqual(data[8:12],b"WEBP")
                    self.assertGreater(len(data),1000)
                    continue
                raw=asset.read_text(encoding="utf-8")
                self.assertNotIn("<script",raw.lower())
                self.assertNotIn("<foreignobject",raw.lower())
                self.assertNotIn("<image ",raw.lower())
                self.assertNotIn("http://",raw.replace("http://www.w3.org/2000/svg",""))
                self.assertNotIn("https://",raw.replace("https://www.w3.org/2000/svg",""))
                root=ET.fromstring(raw)
                self.assertEqual(root.tag,svg_ns+"svg")
                self.assertTrue(root.attrib.get("viewBox"))
                self.assertIsNotNone(root.find(svg_ns+"title"))
                if "integrations/" not in name:
                    self.assertIsNotNone(root.find(svg_ns+"desc"))
                if name.endswith("-mobile.svg"):
                    dims=[float(n) for n in root.attrib["viewBox"].split()]
                    self.assertLess(dims[2],dims[3],name)
                self.assertGreater(asset.stat().st_size,500,name)
        self.assertFalse((ROOT/"assets/design-engineering-mark.svg").exists(),
                         "Unused previous project mark must be removed.")

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
