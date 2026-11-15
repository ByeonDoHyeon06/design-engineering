"""Content-first design plan: evidence-aware scaffold and deterministic readiness audit.

This is an edit/validation workflow, NOT a model designer or an aesthetic ranker.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re
import os
import tempfile

ROLES = ("hero", "explanation", "comparison", "proof", "task", "navigation", "form",
         "editorial", "pricing", "faq", "contact", "other")
ASSET_KINDS = ("none", "photo", "illustration", "diagram", "icon", "video", "other")
ORIGINS = ("original", "user_supplied", "generated", "licensed", "undecided")
VIEWPORTS = (320, 390, 1440)


class DesignPlanError(ValueError):
    pass


def load(path):
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise DesignPlanError(f"Cannot load JSON plan: {path}: {exc}") from exc
    if not isinstance(doc, dict):
        raise DesignPlanError("Plan must be a JSON object.")
    return doc


def _nonempty(value, n=1):
    return isinstance(value, str) and len(value.strip()) >= n


def _asset_defaults(block):
    return {
        "block_id": block["id"], "kind": "undecided", "purpose": "",
        "origin": "undecided", "rights_or_source": "",
        "alt_or_decorative": "",
        "responsive_behavior": "", "state": "needs_decision"
    }


def scaffold(brief):
    if not isinstance(brief, dict) or brief.get("schema_version") != 1:
        raise DesignPlanError("Brief needs schema_version=1.")
    if not all(_nonempty(brief.get(k), 5) for k in ("goal", "audience", "primary_action")):
        raise DesignPlanError("Brief needs a concrete goal, audience and primary_action.")
    blocks = brief.get("content_blocks")
    if not isinstance(blocks, list) or not 2 <= len(blocks) <= 30:
        raise DesignPlanError("Provide 2-30 real content blocks before composing the layout.")
    seen = set()
    for block in blocks:
        if (not isinstance(block, dict)
            or not isinstance(block.get("id"), str)
            or not re.fullmatch(r"[a-z][a-z0-9_-]{1,39}", block["id"])):
            raise DesignPlanError("Content block IDs must be safe lowercase slugs.")
        if block["id"] in seen:
            raise DesignPlanError("Duplicate content block ID.")
        seen.add(block["id"])
        if block.get("role") not in ROLES or not _nonempty(block.get("content"), 4):
            raise DesignPlanError("Each block needs an allowed role and real copy (not placeholder labels).")
    constraints = brief.get("constraints", [])
    if not isinstance(constraints, list) or not all(_nonempty(s) for s in constraints):
        raise DesignPlanError("Constraints must be a list of nonempty strings.")
    return {
        "schema_version": 1, "status": "draft", "brief": brief,
        "principles": {
            "selected_user_goal": brief["goal"], "content_roles_reviewed": False,
            "research_refs": [], "personal_preference_refs": [],
            "evidence_note": "References must be checked manually. No claim or preference has been retrieved by this template."
        },
        "directions": [
            {"id": "direction-a", "content_order": [b["id"] for b in blocks],
             "information_relationship": "", "layout_strategy": "",
             "tradeoffs": "", "primary_action_visibility": ""},
            {"id": "direction-b", "content_order": [b["id"] for b in blocks],
             "information_relationship": "", "layout_strategy": "",
             "tradeoffs": "", "primary_action_visibility": ""}
        ],
        "selected_direction": None, "selection_rationale": "",
        "visual_assets": [_asset_defaults(block) for block in blocks],
        "quality_checks": {
            "viewports": list(VIEWPORTS),
            "content_fidelity": "", "keyboard_and_focus": "",
            "contrast_and_legibility": "", "image_cropping": "",
            "localized_copy": "", "interaction_states": ""
        },
        "limitations": [
            "Draft is not a design solution. An agent or person must inspect actual content and fill decisions.",
            "The validator checks completeness and relationships, not perceived quality or actual accessibility."
        ]
    }


def _save_new(out, data):
    out = Path(out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with os.fdopen(os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as f:
        f.write(content)
    return str(out)


def create(brief_file, out):
    brief = load(brief_file)
    obj = scaffold(brief)
    return {"plan": _save_new(out, obj), "state": "draft",
            "note": "No style preference, factual claim or asset license was inferred automatically."}


def inspect(plan, *, require_ready=False):
    errors, warnings = [], []
    if plan.get("schema_version") != 1:
        return {"ok": False, "ready": False, "errors": ["Unsupported plan schema."], "warnings": []}
    try:
        proposed = scaffold(plan["brief"])
    except (KeyError, DesignPlanError) as exc:
        return {"ok": False, "ready": False, "errors": ["Invalid brief: " + str(exc)], "warnings": []}
    base = proposed["brief"]
    ids = {b["id"] for b in base["content_blocks"]}
    dirs = plan.get("directions")
    if not isinstance(dirs, list) or len(dirs) < 2 or len(dirs) > 5:
        errors.append("Provide between two and five distinct design directions.")
        dirs = []
    styles = set()
    for i, d in enumerate(dirs):
        tag = f"directions[{i}]"
        if not isinstance(d, dict):
            errors.append(tag + " must be an object.")
            continue
        order = d.get("content_order")
        if (not isinstance(order, list) or set(order) != ids
            or len(order) != len(ids) or len(set(order)) != len(order)):
            errors.append(tag + ": content_order must include each brief block exactly once.")
        for key in ("information_relationship", "layout_strategy", "tradeoffs", "primary_action_visibility"):
            if not _nonempty(d.get(key), 12):
                warnings.append(tag + ": " + key + " needs a concrete explanation.")
        if _nonempty(d.get("information_relationship")) and _nonempty(d.get("layout_strategy")):
            fingerprint = (d["information_relationship"].strip().casefold(),
                           d["layout_strategy"].strip().casefold(), tuple(order or []))
            if fingerprint in styles:
                warnings.append("Two directions have identical relationships, layouts and order; explore distinct meanings.")
            styles.add(fingerprint)
    chosen = plan.get("selected_direction")
    if not chosen or chosen not in [d.get("id") for d in dirs if isinstance(d, dict)]:
        warnings.append("No valid selected_direction.")
    if not _nonempty(plan.get("selection_rationale"), 18):
        warnings.append("Selection rationale must explain the decision and rejected alternatives.")
    principles = plan.get("principles", {})
    if not isinstance(principles, dict) or principles.get("content_roles_reviewed") is not True:
        warnings.append("Real content roles have not been reviewed by a human or agent.")
    if not isinstance(principles, dict):
        principles = {}
    for ref in principles.get("research_refs", []):
        if not isinstance(ref, str) or not re.fullmatch(r"(source|method|claim):[A-Za-z0-9_-]+", ref):
            errors.append("research_refs must use typed registered IDs, not invented source titles.")
    for ref in principles.get("personal_preference_refs", []):
        if not isinstance(ref, str) or not ref.startswith("local:"):
            errors.append("personal_preference_refs must be local:* IDs, never verified claims.")
    assets = plan.get("visual_assets")
    if not isinstance(assets, list):
        errors.append("visual_assets must be a list.")
        assets = []
    if Counter(a.get("block_id") for a in assets if isinstance(a, dict)) != Counter(ids):
        errors.append("Define exactly one visual asset decision for each content block.")
    for i, asset in enumerate(assets):
        tag = f"visual_assets[{i}]"
        if not isinstance(asset, dict):
            errors.append(tag + ": must be an object.")
            continue
        kind = asset.get("kind")
        origin = asset.get("origin")
        if kind not in ASSET_KINDS and kind != "undecided":
            errors.append(tag + ": invalid asset kind.")
        if origin not in ORIGINS:
            errors.append(tag + ": invalid asset origin.")
        if kind == "undecided" or origin == "undecided":
            warnings.append(tag + ": asset direction remains undecided.")
        if kind not in ("none", "undecided"):
            for key in ("purpose", "responsive_behavior", "alt_or_decorative"):
                if not _nonempty(asset.get(key), 7):
                    warnings.append(tag + ": " + key + " missing.")
            if origin in ("licensed", "user_supplied") and not _nonempty(asset.get("rights_or_source"), 7):
                warnings.append(tag + ": source or rights record missing.")
            if origin == "generated" and not _nonempty(asset.get("rights_or_source"), 7):
                warnings.append(tag + ": record generator and rights assumptions.")
        if kind == "none" and origin != "original":
            warnings.append(tag + ": for no asset use origin='original' to indicate intentional omission.")
    checks = plan.get("quality_checks")
    if not isinstance(checks, dict):
        errors.append("quality_checks must be an object.")
        checks = {}
    widths = checks.get("viewports")
    if not isinstance(widths, list) or not set(VIEWPORTS).issubset(widths):
        errors.append("Plan for 320, 390 and 1440 px viewports.")
    for key in ("content_fidelity", "keyboard_and_focus", "contrast_and_legibility",
                "image_cropping", "localized_copy", "interaction_states"):
        if not _nonempty(checks.get(key), 12):
            warnings.append("quality_checks." + key + " not planned.")
    ready = not errors and not warnings
    if require_ready and not ready:
        errors.append("Plan is not ready; resolve the warnings before implementation.")
    return {"ok": not errors, "ready": ready, "errors": errors, "warnings": warnings,
            "content_blocks": len(ids), "directions": len(dirs),
            "statement": "Completeness audit only; implementation and screenshot review remain separate."}


def validate(path, *, require_ready=False):
    return inspect(load(path), require_ready=require_ready)
