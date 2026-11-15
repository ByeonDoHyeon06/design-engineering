"""User/project/session Knowledge: explicit drafts, local-only approval and scoped retrieval.

This store NEVER writes into the skill's scholarly catalog. Preferences, user-authored
principles, observations and reference bookmarks are not verified scientific claims.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
import uuid

SCHEMA_VERSION = 1
KINDS = ("preference", "principle", "observation", "reference")
SCOPES = ("user", "project", "session")
MAX_TEXT = 6000
MAX_RECORDS = 5000


class LocalKnowledgeError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def _clean(text):
    return " ".join(unicodedata.normalize("NFKC", str(text)).casefold().split())


def _terms(text):
    return set(re.findall(r"[가-힣]{2,}|[a-z0-9][a-z0-9_-]{1,}", _clean(text)))


def _similarity(a, b):
    a, b = _clean(a), _clean(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    aa, bb = _terms(a), _terms(b)
    tokens = len(aa & bb) / max(1, len(aa | bb))
    grams = lambda s: {s[i:i+2] for i in range(len(s)-1)}
    ga, gb = grams(a), grams(b)
    chars = len(ga & gb) / max(1, len(ga | gb))
    return round(max(tokens, chars), 4)


def location(scope, *, project=None, home=None, session_id=None):
    """Scope output lives outside the installed skill. No auto-upload to GitHub."""
    if scope not in SCOPES:
        raise LocalKnowledgeError("core research is not personal Knowledge: use user, project or session scope.")
    if scope == "project":
        folder = Path(project or Path.cwd()).expanduser().resolve()
        if not folder.is_dir():
            raise LocalKnowledgeError("Project directory does not exist: " + str(folder))
        return folder / ".design-engineering"
    if scope == "user":
        if home is not None:
            base = Path(home).expanduser()
        elif os.environ.get("DE_HOME"):
            base = Path(os.environ["DE_HOME"]).expanduser()
        elif os.environ.get("XDG_CONFIG_HOME"):
            base = Path(os.environ["XDG_CONFIG_HOME"]).expanduser() / "design-engineering"
        elif os.name == "nt" and os.environ.get("APPDATA"):
            base = Path(os.environ["APPDATA"]) / "design-engineering"
        else:
            base = Path.home() / ".config" / "design-engineering"
        return base.resolve()
    sid = session_id or os.environ.get("DE_SESSION_ID")
    if not sid or not re.fullmatch(r"[A-Za-z0-9_-]{4,80}", sid):
        raise LocalKnowledgeError("Session scope needs --session-id or DE_SESSION_ID (4-80 safe characters).")
    base = Path(os.environ.get("DE_SESSION_HOME", tempfile.gettempdir()))
    return (base / "design-engineering-sessions" / sid).resolve()


def _data_path(folder):
    return folder / "knowledge.json"


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _load(folder):
    path = _data_path(folder)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "records": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LocalKnowledgeError(f"Invalid local Knowledge store: {path}: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != 1 or not isinstance(raw.get("records"), list):
        raise LocalKnowledgeError("Unsupported local Knowledge schema; do not overwrite it.")
    if len(raw["records"]) > MAX_RECORDS:
        raise LocalKnowledgeError("Local Knowledge store exceeds configured safety cap.")
    return raw


def _private_write(path, data, *, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if exclusive:
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
            stream.write(content)
        return
    fd, tmp = tempfile.mkstemp(prefix=".de-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _validate_input(kind, scope, text, *, context=None, outcome=None, source=None):
    if kind not in KINDS:
        raise LocalKnowledgeError("Unknown Knowledge type.")
    if scope not in SCOPES:
        raise LocalKnowledgeError("Personal Knowledge cannot be published into the core research library.")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
        raise LocalKnowledgeError("Text must be 1-6000 characters.")
    if kind == "observation" and not (context and outcome):
        raise LocalKnowledgeError("Observation requires both --context and --outcome.")
    if kind == "reference" and not source:
        raise LocalKnowledgeError("Reference requires --file. It will not be marked as verified research.")
    if kind != "reference" and source:
        raise LocalKnowledgeError("File-backed notes require --type reference.")
    if context and len(context) > 1000:
        raise LocalKnowledgeError("Context must be at most 1000 characters.")
    if outcome and len(outcome) > 1000:
        raise LocalKnowledgeError("Outcome must be at most 1000 characters.")


def _source_info(path, *, title=None, authors=None, url=None):
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise LocalKnowledgeError(f"Source file does not exist: {source}")
    if source.stat().st_size > 16 * 1024 * 1024:
        raise LocalKnowledgeError("Source file exceeds 16 MiB.")
    if source.suffix.lower() not in (".pdf", ".md", ".txt", ".html", ".htm"):
        raise LocalKnowledgeError("Source extension must be PDF, Markdown, TXT or HTML.")
    if url and not str(url).startswith(("https://", "http://", "doi:")):
        raise LocalKnowledgeError("URL must be http(s) or doi:.")
    return {"path": str(source), "sha256": _digest(source),
            "title": (title or source.name)[:300], "authors": (authors or "unknown")[:300],
            "url": (url or "")[:1200], "access_level": "user_reference_not_claim_verified"}


def _related(folder, text, kind, *, threshold=0.25):
    data = _load(folder)
    results = []
    for row in data["records"]:
        if row.get("status") != "active":
            continue
        score = _similarity(text, row.get("text", ""))
        if score >= threshold:
            results.append({"id": row["id"], "kind": row["kind"], "text": row["text"],
                            "similarity": score, "same_kind": row["kind"] == kind})
    return sorted(results, key=lambda item: (-item["similarity"], item["id"]))[:8]


def propose(text, *, kind="preference", scope="project", project=None, home=None,
            session_id=None, context=None, outcome=None, tags=(),
            source_file=None, title=None, authors=None, url=None, origin="human_or_agent"):
    folder = location(scope, project=project, home=home, session_id=session_id)
    source = _source_info(source_file, title=title, authors=authors, url=url) if source_file else None
    _validate_input(kind, scope, text, context=context, outcome=outcome, source=source)
    if not isinstance(tags, (list, tuple)) or len(tags) > 20:
        raise LocalKnowledgeError("Use at most 20 tags.")
    tags = [str(t).strip()[:80] for t in tags if str(t).strip()]
    proposal = {
        "schema_version": 1, "status": "pending_review", "id": "local:" + uuid.uuid4().hex,
        "scope": scope, "kind": kind, "text": text.strip(), "context": context or "",
        "outcome": outcome or "", "tags": tags, "source": source,
        "created_at": _now(), "origin": origin,
        "provenance": "user_or_agent_supplied_not_scientifically_verified",
        "target_folder": str(folder.resolve()), "expected_store_sha256": _digest(_data_path(folder)),
        "related_candidates": _related(folder, text, kind),
        "review_notice": "This is a draft, not saved guidance. Check scope, privacy, duplicates and meaning before explicit approval."
    }
    path = folder / "drafts" / (proposal["id"].replace(":", "-") + ".json")
    _private_write(path, proposal, exclusive=True)
    return {"proposal": str(path), "kind": kind, "scope": scope,
            "related_candidates": proposal["related_candidates"], "state": "pending_review"}


def read_proposal(path):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise LocalKnowledgeError("Proposal not found: " + str(path))
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LocalKnowledgeError("Invalid proposal JSON.") from exc
    if not isinstance(doc, dict) or doc.get("status") != "pending_review":
        raise LocalKnowledgeError("Only pending review proposals may be applied.")
    return path, doc


def approve(path, *, reviewer, project=None, home=None, session_id=None):
    if not str(reviewer).strip():
        raise LocalKnowledgeError("A reviewer is required for explicit approval.")
    path, proposal = read_proposal(path)
    scope = proposal.get("scope")
    folder = location(scope, project=project, home=home, session_id=session_id)
    if path.parent != (folder / "drafts").resolve() or proposal.get("target_folder") != str(folder.resolve()):
        raise LocalKnowledgeError("Proposal scope/project mismatch; no cross-project imports.")
    kind = proposal.get("kind")
    source = proposal.get("source")
    _validate_input(kind, scope, proposal.get("text"), context=proposal.get("context"),
                    outcome=proposal.get("outcome"), source=source)
    if source and (_digest(Path(source["path"])) != source["sha256"]):
        raise LocalKnowledgeError("Referenced file changed or disappeared after proposal.")
    store_path = _data_path(folder)
    if _digest(store_path) != proposal.get("expected_store_sha256"):
        raise LocalKnowledgeError("Knowledge changed since drafting. Re-create the proposal to avoid overwriting updates.")
    data = _load(folder)
    if any(_clean(row.get("text", "")) == _clean(proposal["text"])
           and row.get("kind") == kind and row.get("status") == "active"
           for row in data["records"]):
        raise LocalKnowledgeError("Exact duplicate entry exists in this scope; review it instead.")
    if len(data["records"]) >= MAX_RECORDS:
        raise LocalKnowledgeError("Local Knowledge limit reached.")
    row = {key: proposal.get(key) for key in
           ("id", "kind", "scope", "text", "context", "outcome", "tags", "source", "created_at", "origin", "provenance")}
    row.update({"status": "active", "reviewer": str(reviewer).strip(), "approved_at": _now()})
    data["records"].append(row)
    _private_write(store_path, data)
    proposal["status"] = "approved"
    proposal["approved_at"] = row["approved_at"]
    proposal["approved_by"] = row["reviewer"]
    _private_write(path, proposal)
    return {"registered": row, "path": str(store_path),
            "warning": "Personal guidance; never presented as scientific verification."}


def archive(identity, *, scope, reviewer, project=None, home=None, session_id=None):
    if not str(reviewer).strip():
        raise LocalKnowledgeError("Reviewer required to archive a local record.")
    folder = location(scope, project=project, home=home, session_id=session_id)
    data = _load(folder)
    found = [r for r in data["records"] if r.get("id") == identity and r.get("status") == "active"]
    if len(found) != 1:
        raise LocalKnowledgeError("Active record ID not found in scope.")
    found[0].update({"status": "archived", "archived_at": _now(), "archived_by": str(reviewer).strip()})
    _private_write(_data_path(folder), data)
    return {"archived": identity, "scope": scope}


def records(*, project=None, home=None, session_id=None, scopes=("session", "project", "user"),
            include_archived=False):
    out = []
    for scope in scopes:
        try:
            folder = location(scope, project=project, home=home, session_id=session_id)
        except LocalKnowledgeError:
            if scope == "session" and not session_id and not os.environ.get("DE_SESSION_ID"):
                continue
            raise
        for row in _load(folder)["records"]:
            if row.get("status") == "active" or include_archived:
                out.append(dict(row, storage_path=str(_data_path(folder))))
    return out


def search(question, *, project=None, home=None, session_id=None, scopes=("session", "project", "user"),
           top=12, include_all=False):
    found = []
    for row in records(project=project, home=home, session_id=session_id, scopes=scopes):
        if include_all:
            score = 1.0
        else:
            score = _similarity(question, " ".join([row["text"], row.get("context", ""),
                                                    " ".join(row.get("tags", [])),
                                                    (row.get("source") or {}).get("title", "")]))
        if score >= (0 if include_all else 0.08):
            found.append(dict(row, relevance=score,
                              evidence_status="personal_guidance_not_verified"))
    priority = {"session": 0, "project": 1, "user": 2}
    found.sort(key=lambda r: (priority.get(r["scope"], 3) if include_all else -r["relevance"],
                              -r["relevance"] if include_all else priority.get(r["scope"], 3),
                              r["created_at"], r["id"]))
    return found[:max(1, top)]


def drafts(*, project=None, home=None, session_id=None, scopes=("project", "user", "session")):
    out = []
    for scope in scopes:
        try:
            folder = location(scope, project=project, home=home, session_id=session_id)
        except LocalKnowledgeError:
            continue
        folder = folder / "drafts"
        if not folder.exists():
            continue
        for path in sorted(folder.glob("local-*.json")):
            try:
                content = json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                continue
            if content.get("status") == "pending_review":
                out.append({"proposal": str(path), "scope": scope, "kind": content.get("kind"),
                            "text": str(content.get("text", ""))[:300],
                            "related_candidates": content.get("related_candidates", [])})
    return out
