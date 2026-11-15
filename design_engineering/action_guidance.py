"""Context-gated translation of retrieved Knowledge into practice hypotheses.

Deliberately separate from source-scoped research: no research result is changed,
no UI outcome is certified, and no advice is returned without query + card support.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata


class PracticeError(ValueError):
    pass


def _norm(text):
    return unicodedata.normalize("NFKC", str(text or "")).casefold()


def _cues(query, cues):
    q = _norm(query)
    matching = []
    for term in cues:
        term = _norm(term).strip()
        if not term:
            continue
        # Avoid accidental English partial-word matches such as "card" in "discard".
        if re.search(r"[a-z]", term):
            hit = bool(re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", q))
        else:
            hit = term in q
        if hit:
            matching.append(term)
    return matching


def load(root):
    root = Path(root)
    path = root / "methods" / "action-guidance.json"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        catalog = json.loads((root / "knowledge" / "catalog.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise PracticeError(f"Action guidance or catalog unavailable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise PracticeError("Unsupported practice schema_version.")
    records = doc.get("practices", [])
    if not isinstance(records, list) or not records:
        raise PracticeError("Practice library must contain entries.")
    valid = {entry["id"] for entry in catalog.get("records", [])}
    ids = set()
    required_strings = ("id", "name", "problem", "when", "guidance_kind")
    required_lists = ("topic_cues", "linked_card_ids", "options", "failure_modes", "countercases", "checks")
    for row in records:
        if not isinstance(row, dict) or any(not isinstance(row.get(key), str) or not row[key].strip()
                                             for key in required_strings):
            raise PracticeError("Practice needs a unique ID, title, problem, applicability and type.")
        if not re.fullmatch(r"AG[0-9]{2,3}", row["id"]) or row["id"] in ids:
            raise PracticeError("Duplicate or invalid practice ID.")
        ids.add(row["id"])
        for key in required_lists:
            values = row.get(key)
            if not isinstance(values, list) or not values or not all(
                    isinstance(v, str) and v.strip() for v in values):
                raise PracticeError(f"{row['id']}: {key} requires nonempty text items.")
        if not set(row["linked_card_ids"]).issubset(valid):
            raise PracticeError(f"{row['id']}: every linked card must exist in Knowledge catalog.")
        if row["guidance_kind"] != "practitioner_design_hypothesis":
            raise PracticeError("Practice suggestions must never be labeled verified research.")
    return doc


def suggest(query, retrieved, *, root, max_results=3):
    """Return bounded, query-specific *candidate actions*, not research conclusions."""
    if max_results < 1 or max_results > 10:
        raise PracticeError("max_results must be 1..10.")
    if not str(query).strip():
        return {"query": query, "state": "empty_query", "suggestions": [],
                "notice": "No practice guidance without a specific design question."}
    if not isinstance(retrieved, list):
        raise PracticeError("Retrieved Knowledge must be a list.")
    matches = {item["id"]: item for item in retrieved
               if isinstance(item, dict) and isinstance(item.get("id"), str)}
    if not matches:
        return {"query": query, "state": "no_retrieved_knowledge", "suggestions": [],
                "notice": "No matched research; do not invent guidance by genre alone."}
    catalog = load(root)
    output = []
    for rule in catalog["practices"]:
        hit_terms = _cues(query, rule["topic_cues"])
        hit_cards = [identifier for identifier in rule["linked_card_ids"] if identifier in matches]
        if not hit_terms or not hit_cards:
            continue
        linked = [{"id": identifier, "evidence_status": matches[identifier].get("evidence_status", "unknown"),
                   "source_ids": matches[identifier].get("source_ids", []),
                   "verified_claim_ids": matches[identifier].get("verified_claim_ids", [])}
                  for identifier in hit_cards]
        output.append({
            "id": rule["id"], "name": rule["name"],
            "practice_type": "design_hypothesis_not_research_finding",
            "problem": rule["problem"], "when": rule["when"],
            "options_to_consider": rule["options"],
            "failure_modes": rule["failure_modes"],
            "countercases": rule["countercases"], "checks": rule["checks"],
            "matched_cues": hit_terms,
            "linked_retrieved_cards": linked,
            "link_scope": ("Cards were retrieved for the question. This link helps select a hypothesis; "
                           "it does NOT establish that any proposed UI choice is experimentally proven."),
            "_sort": (-len(hit_cards), -len(hit_terms), rule["id"])
        })
    output.sort(key=lambda x: x.pop("_sort"))
    return {
        "query": query,
        "state": "matched_practice_hypotheses" if output else "no_contextual_practice_match",
        "suggestions": output[:max_results],
        "notice": ("Research remains in the separate research field. Suggestions are heuristic implementation "
                   "candidates selected by both query cues and retrieved card IDs, with countercases and checks."),
        "limitations": [
            "This is deterministic lexical matching, not model-generated context understanding.",
            "The linked research does not directly validate a specific implementation or design outcome.",
            "If nothing matches, do not pad the answer with unrelated style rules."
        ]
    }
