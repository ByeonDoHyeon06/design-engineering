"""Build full offline skill resources into wheel without duplicating source-tree data."""
from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class BundleSkillResources(_build_py):
    def run(self):
        super().run()
        repo = Path(__file__).resolve().parent
        dest = Path(self.build_lib) / "design_engineering" / "_bundled"
        dest.mkdir(parents=True, exist_ok=True)
        # These directories are the canonical source; _bundled exists only in build output.
        for name in ("scripts", "knowledge", "methods", "templates",
                     "docs", "benchmarks", "assets", "i18n"):
            origin = repo / name
            if not origin.is_dir():
                raise RuntimeError("Cannot package missing skill resource: " + name)
            shutil.copytree(origin, dest / name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.sqlite",
                                                          ".cache", ".local", "*.egg-info"))
        for name in ("SKILL.md", "pyproject.toml", "README.md"):
            source = repo / name
            if not source.is_file():
                raise RuntimeError("Cannot package missing skill document: " + name)
            shutil.copy2(source, dest / name)


setup(cmdclass={"build_py": BundleSkillResources})
