"""Local-only provenance capture for a real skill installation and operator evidence.

Source identity and operator-reported execution are separate. Never equate a
filesystem hash, CLI invocation, or arbitrary log path with proof of skill use.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from . import __version__

DEFAULT_REPOSITORY = "ByeonDoHyeon06/design-engineering"
USAGE = ("not_executed", "documentation_only", "skill_invoked")
MAX_LOG = 25 * 1024 * 1024


class ProvenanceError(ValueError):
    pass


def _read_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ProvenanceError(f"Cannot read provenance JSON: {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ProvenanceError("Expected a provenance object with schema_version=1.")
    return value


def _digest(path):
    file = Path(path)
    if not file.is_file() or not 0 < file.stat().st_size <= MAX_LOG:
        raise ProvenanceError(f"Evidence file must exist and be under 25 MiB: {file}")
    return hashlib.sha256(file.read_bytes()).hexdigest()


def _git(root, *args):
    try:
        proc = subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def _repo_name(remote):
    if not remote:
        return None
    # GitHub HTTPS, SSH SCP, and ssh:// forms only. No network calls.
    match = re.fullmatch(
        r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
        r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", remote.strip(), re.I)
    return match.group(1) if match else None


def source_identity(root, *, expected_repository=DEFAULT_REPOSITORY):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ProvenanceError(f"Skill installation directory does not exist: {root}")
    from validate_install import inspect
    installed = inspect(root)
    skill = root / "SKILL.md"
    skill_sha = _digest(skill) if skill.is_file() else None
    git_root = _git(root, "rev-parse", "--show-toplevel")
    git_is_root = git_root is not None and Path(git_root).resolve() == root
    remote = _git(root, "remote", "get-url", "origin") if git_is_root else None
    repository = _repo_name(remote)
    commit = _git(root, "rev-parse", "HEAD") if git_is_root else None
    if commit and not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        commit = None
    tracked_status = _git(root, "status", "--porcelain", "--untracked-files=no") if git_is_root else None
    clean = (tracked_status == "") if tracked_status is not None else None
    expected_matches = bool(repository and repository.casefold() == expected_repository.casefold())
    source_verified = bool(installed["complete"] and git_is_root and expected_matches
                           and commit and clean is True and skill_sha)
    if repository and not expected_matches:
        status = "MISMATCHED_REPOSITORY"
    elif not installed["complete"]:
        status = "INCOMPLETE_INSTALLATION"
    elif source_verified:
        status = "VERIFIED_SOURCE_IDENTITY"
    else:
        status = "UNVERIFIED_SOURCE_IDENTITY"
    return {
        "root": str(root), "skill_path": str(skill), "skill_sha256": skill_sha,
        "expected_repository": expected_repository, "repository": repository,
        "git_commit": commit, "git_root_matches_installation": git_is_root,
        "tracked_tree_clean": clean, "installation_complete": installed["complete"],
        "status": status, "source_verified": source_verified,
        "limitations": [
            "Git origin/commit and tracked cleanliness are local read-only checks, not independent attestation.",
            "A complete installed wheel without .git can be valid software but cannot prove a repository commit.",
            "Untracked files or later runtime changes may affect behavior; do not infer actual agent tool use from identity."
        ]
    }


def _evidence_file(path):
    if path is None:
        return {"recorded": False, "file": None, "sha256": None}
    file = Path(path).expanduser().resolve()
    return {"recorded": True, "file": str(file), "sha256": _digest(file)}


def capture(*, skill_root, out, expected_repository=DEFAULT_REPOSITORY,
            usage="not_executed", execution_log=None, knowledge_log=None,
            browser_log=None, alternate_material=None):
    if usage not in USAGE:
        raise ProvenanceError("usage must be not_executed, documentation_only or skill_invoked.")
    if usage == "skill_invoked" and not execution_log:
        raise ProvenanceError("Skill invocation can only be operator-reported with a real execution log.")
    if usage == "not_executed" and execution_log:
        raise ProvenanceError("An execution log cannot be supplied while claiming NOT_EXECUTED.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", expected_repository):
        raise ProvenanceError("Expected repository must be in owner/repository format.")
    src = source_identity(skill_root, expected_repository=expected_repository)
    logs = {"execution": _evidence_file(execution_log),
            "knowledge_search": _evidence_file(knowledge_log),
            "browser_validation": _evidence_file(browser_log),
            "alternate_material": _evidence_file(alternate_material)}
    record = {
        "schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
        "tool_version": __version__, "source": src,
        "usage_reported_by_operator": usage, "evidence": logs,
        "execution_verification": (
            "OPERATOR_REPORTED_NOT_ATTESTED" if usage == "skill_invoked"
            else "DOCUMENTATION_ONLY_NOT_EXECUTED" if usage == "documentation_only"
            else "NOT_EXECUTED"
        ),
        "attribution_eligible": bool(src["source_verified"] and usage == "skill_invoked"
                                    and logs["execution"]["recorded"]
                                    and not logs["alternate_material"]["recorded"]),
        "limitations": [
            "Recording a log is not proof that an agent actually loaded the requested SKILL.md.",
            "Attribution eligibility checks reported usage, source identity, and file fingerprints only.",
            "If alternate material was used, the result must not be attributed solely to the selected skill."
        ]
    }
    from .evaluation import _private_json
    out = Path(out).expanduser().resolve()
    _private_json(out, record, exclusive=True)
    return {"manifest": str(out), "source_status": src["status"],
            "usage": usage, "attribution_eligible": record["attribution_eligible"],
            "warning": "Source verified locally; actual skill execution remains operator-reported."}


def verify(path):
    manifest = _read_json(path)
    problems = []
    source = manifest.get("source")
    if not isinstance(source, dict) or not source.get("root"):
        raise ProvenanceError("Manifest has no source identity.")
    current = source_identity(source["root"],
                              expected_repository=source.get("expected_repository", DEFAULT_REPOSITORY))
    for k in ("skill_sha256", "repository", "git_commit", "git_root_matches_installation",
              "tracked_tree_clean", "installation_complete"):
        if current.get(k) != source.get(k):
            problems.append("Source identity changed since capture: " + k)
    logs = manifest.get("evidence")
    if not isinstance(logs, dict):
        raise ProvenanceError("Manifest evidence section missing.")
    for key in ("execution", "knowledge_search", "browser_validation", "alternate_material"):
        item = logs.get(key)
        if not isinstance(item, dict):
            problems.append("Missing evidence field: " + key)
            continue
        if item.get("recorded"):
            try:
                if not item.get("file") or _digest(item["file"]) != item.get("sha256"):
                    problems.append("Evidence file changed: " + key)
            except ProvenanceError:
                problems.append("Evidence file unavailable: " + key)
    usage = manifest.get("usage_reported_by_operator")
    if usage not in USAGE:
        problems.append("Invalid reported usage.")
    elif usage == "skill_invoked" and not logs.get("execution", {}).get("recorded"):
        problems.append("Claimed invocation without an execution log.")
    if usage == "not_executed" and logs.get("execution", {}).get("recorded"):
        problems.append("Conflicting non-execution and execution claims.")
    attribution = bool(not problems and current["source_verified"]
                       and usage == "skill_invoked" and logs.get("execution", {}).get("recorded")
                       and not logs.get("alternate_material", {}).get("recorded"))
    return {"ok": not problems, "source_status": current["status"],
            "reported_usage": usage, "attribution_eligible": attribution,
            "errors": problems,
            "limitations": "File integrity and declared provenance are checked, not actual agent runtime invocation."}
