"""Read-only Knowledge diagnostics: query coverage, source review cues, preference clashes.

All results are heuristic *review candidates*, never verified research conclusions.
"""
from __future__ import annotations

from datetime import date
from itertools import combinations
import json
from pathlib import Path
import re
import unicodedata

POSITIVE = ("prefer", "like", "use", "favor", "retain", "keep", "선호", "좋아", "사용", "적용", "유지")
NEGATIVE = ("avoid", "dislike", "never", "do not", "don't", "exclude", "ban", "no ",
            "지양", "피하", "피해", "싫어", "않", "금지", "제외")
IGNORE = set("i we want a an the these for in with design ui and to of my it from would should".split())


def _norm(s):
    return unicodedata.normalize("NFKC", str(s or "")).casefold().strip()


def _polarity(text):
    q = _norm(text)
    pos = any(x in q for x in POSITIVE)
    neg = any(x in q for x in NEGATIVE)
    if pos == neg:
        return "ambiguous"
    return "positive" if pos else "negative"


def _topic_words(text):
    text = _norm(text)
    # This uses conservative lexical cues only; language morphology is not solved.
    for word in sorted(POSITIVE + NEGATIVE, key=len, reverse=True):
        text = text.replace(word, " ")
    parts = set(re.findall(r"[가-힣]{2,}|[a-z0-9][a-z0-9_-]{2,}", text))
    return {word for word in parts if word not in IGNORE}


def conflict_candidates(records, *, limit=30):
    """Flag polarity-opposed, topic-overlapping preferences; never auto-delete."""
    relevant = [r for r in records
                if r.get("status") == "active"
                and r.get("kind") in ("preference", "principle")
                and isinstance(r.get("id"), str)
                and isinstance(r.get("text"), str)]
    relevant.sort(key=lambda r: (r.get("scope", ""), r["id"]))
    candidates = []
    for left, right in combinations(relevant, 2):
        if left["id"] == right["id"]:
            continue
        polarities = (_polarity(left["text"]), _polarity(right["text"]))
        if set(polarities) != {"positive", "negative"}:
            continue
        a = _topic_words(left["text"]) | set(map(_norm, left.get("tags", [])))
        b = _topic_words(right["text"]) | set(map(_norm, right.get("tags", [])))
        common = sorted(a & b)
        if not common:
            continue
        candidates.append({
            "ids": [left["id"], right["id"]],
            "scopes": [left.get("scope"), right.get("scope")],
            "common_terms": common[:10],
            "texts": [left["text"], right["text"]],
            "status": "possible_lexical_conflict_not_verified",
            "action": "Review task context and scope. Do not automatically overwrite or delete either preference."
        })
        if len(candidates) >= limit:
            break
    return {"candidate_count": len(candidates), "candidates": candidates,
            "limitations": "Keyword polarity and token overlap only. False negatives/positives and mixed-language misses are expected; no contradiction is automatically settled."}


def explain(query, core_results, personal_results):
    """Explain coverage without inferring that no published evidence exists."""
    core = list(core_results)
    personal = list(personal_results)
    with_claims = [r for r in core if r.get("verified_claim_ids")]
    if not core:
        state = "no_registered_card_match"
        action = ("No relevant card was found in this installed library under the current retrieval settings. "
                  "Reformulate the question, check inactive/filtered cards or propose a source for manual review.")
    elif not with_claims:
        state = "matched_cards_without_explicit_checked_claim"
        action = ("Read the matched cards and source limitations. They may inform a hypothesis, "
                  "but do not imply a source-verified UI outcome.")
    else:
        state = "registered_claim_linked_match"
        action = ("Inspect each linked claim's population, limitation and do_not_infer field before transfer. "
                  "Claim registration does not verify the proposed design.")
    return {
        "query": query, "state": state, "core_matches": len(core),
        "explicit_claim_linked_matches": len(with_claims),
        "personal_matches": len(personal),
        "matched_research": [
            {"id": row["id"], "evidence_status": row.get("evidence_status"),
             "matching_signals": row.get("why_matched", {}),
             "source_ids": row.get("source_ids", []),
             "verified_claim_ids": row.get("verified_claim_ids", []),
             "lifecycle_status": row.get("lifecycle_status", "unknown")}
            for row in core
        ],
        "recommendation": action,
        "limitations": [
            "This describes the installed library and current search threshold, not all published research.",
            "A relevance rank is not a scientific confidence score or observed design quality.",
            "Personal preference matches never increase source-verified claim coverage."
        ]
    }


def source_review_queue(root, *, today=None):
    """Only explicit lifecycle due dates and states; does not guess source staleness."""
    root = Path(root)
    path = root / "knowledge/governance.json"
    if not path.is_file():
        return {"items": [], "date": str(today or date.today()), "notice": "Governance file unavailable."}
    data = json.loads(path.read_text(encoding="utf-8"))
    overrides = data.get("status_overrides", {})
    current = date.fromisoformat(str(today)) if today is not None else date.today()
    result = []
    for identifier, row in sorted(overrides.items()):
        status = row.get("status")
        raw_due = row.get("review_due")
        due = None
        if raw_due:
            try:
                due = date.fromisoformat(raw_due)
            except (TypeError, ValueError):
                result.append({"id": identifier, "reason": "invalid_explicit_review_due",
                               "status": status, "review_due": raw_due})
                continue
        if status == "needs_review" or (due is not None and due <= current):
            result.append({"id": identifier, "reason": "marked_needs_review" if status == "needs_review" else "explicit_due_date_reached",
                           "status": status, "review_due": raw_due,
                           "reviewer": row.get("reviewer")})
    return {"date": current.isoformat(), "items": result,
            "notice": "Only recorded review_due/status entries are considered; absence does not imply a source is current, verified or safe to use."}
