"""Design Engineering — unified CLI, local-first Knowledge and a complete skill bundle."""
from pathlib import Path

__version__ = "4.6.0"


def resource_root():
    """Locate the canonical repository resources or built-wheel offline bundle."""
    path = Path(__file__).resolve()
    checkout = path.parents[1]
    if (checkout / "SKILL.md").is_file() and (checkout / "knowledge/catalog.json").is_file():
        return checkout
    bundled = path.parent / "_bundled"
    if (bundled / "SKILL.md").is_file() and (bundled / "knowledge/catalog.json").is_file():
        return bundled
    raise RuntimeError("Design Engineering skill data was not packaged: reinstall the full skill.")
