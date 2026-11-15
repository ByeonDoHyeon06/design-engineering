"""Paired, blinded design evaluation foundation (no agent runs or invented scores).

Run outputs are local and split into private assignments and a shareable blind packet.
A/B is balanced and randomized. Judgments are supplied by actual reviewers only.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import struct
import tempfile
import uuid
import zlib

SCHEMA_VERSION = 1
DIMENSIONS = ("visual_hierarchy", "task_clarity", "responsive_craft", "originality")
ARMS = ("baseline", "skill")
SIDES = ("A", "B")
MAX_PNG = 25 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class EvaluationError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot read valid JSON: {path}: {exc}") from exc


def _private_json(path, data, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if exclusive:
        with os.fdopen(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb") as handle:
            handle.write(payload)
        return
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".de-eval-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def load_tasks(path):
    data = _load(path)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise EvaluationError("Task catalog must use schema_version=1.")
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not 2 <= len(tasks) <= 100:
        raise EvaluationError("Task catalog needs 2-100 distinct tasks.")
    ids = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise EvaluationError("Each task must be an object.")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", task_id):
            raise EvaluationError("Task ID must be a safe 3-64-character slug.")
        if task_id in ids:
            raise EvaluationError(f"Duplicate task ID: {task_id}")
        ids.add(task_id)
        if (not isinstance(task.get("category"), str) or not task["category"].strip()
            or not isinstance(task.get("audience"), str) or len(task["audience"].strip()) < 6
            or not isinstance(task.get("brief"), str) or len(task["brief"].strip()) < 12):
            raise EvaluationError(f"Missing category, audience or full brief: {task_id}")
        for key in ("task_goals", "required_states", "review_checks"):
            vals = task.get(key)
            if not isinstance(vals, list) or not vals or not all(
                    isinstance(x, str) and x.strip() for x in vals):
                raise EvaluationError(f"{task_id}: {key} must be a nonempty string list.")
    return data


def init_run(*, tasks_file, out, seed, agent, model, effort, protocol_note=""):
    catalog = load_tasks(tasks_file)
    if not isinstance(seed, int) or seed < 0:
        raise EvaluationError("Seed must be a nonnegative integer.")
    if not agent or not model or not effort:
        raise EvaluationError("Record the agent, model and effort before starting paired runs.")
    folder = Path(out).expanduser().resolve()
    if folder.exists():
        raise EvaluationError("Evaluation directory already exists. Use a new --out path.")
    folder.mkdir(parents=True)
    (folder / "private").mkdir(mode=0o700)
    (folder / "blind").mkdir()
    tasks = catalog["tasks"]
    rng = random.Random(seed)
    # Balanced across tasks (exactly half for even sample sizes).
    skill_a = [True] * (len(tasks) // 2) + [False] * (len(tasks) - len(tasks) // 2)
    rng.shuffle(skill_a)
    run_id = uuid.uuid4().hex
    assignments = []
    packet = []
    for task, on_left in zip(tasks, skill_a):
        task_id = task["id"]
        assignments.append({
            "task_id": task_id,
            "A": {"condition": "skill" if on_left else "baseline", "images": {"desktop": None, "mobile": None}, "metrics": None},
            "B": {"condition": "baseline" if on_left else "skill", "images": {"desktop": None, "mobile": None}, "metrics": None}
        })
        packet.append({
            "task_id": task_id, "category": task["category"], "brief": task["brief"],
            "audience": task["audience"], "task_goals": task["task_goals"],
            "required_states": task["required_states"], "review_checks": task["review_checks"],
            "screenshots": {side: {v: task_id + "/" + side + "-" + v + ".png"
                                   for v in ("desktop", "mobile")} for side in SIDES}
        })
        (folder / "blind" / task_id).mkdir()
    secret = {
        "schema_version": SCHEMA_VERSION, "run_id": run_id, "created_at": _now(),
        "catalog_sha256": _sha((json.dumps(catalog, sort_keys=True, ensure_ascii=False)).encode()),
        "seed": seed, "agent": agent, "model": model, "effort": effort,
        "protocol_note": protocol_note, "assignments": assignments
    }
    public = {
        "schema_version": SCHEMA_VERSION, "run_id": run_id,
        "description": "Blind review tasks and screenshots. No assignment or outcome data.",
        "dimensions": list(DIMENSIONS), "pairs": packet,
        "warning": "No results or judgments were generated by this initialization."
    }
    _private_json(folder / "private" / "assignments.json", secret, exclusive=True)
    _private_json(folder / "blind" / "packet.json", public, exclusive=True)
    return {
        "run_dir": str(folder), "run_id": run_id, "task_count": len(tasks),
        "blind_packet": str(folder / "blind" / "packet.json"),
        "private_assignments": str(folder / "private" / "assignments.json"),
        "notice": "No agents were run and no design outcomes were scored. Do not share private/ with blind judges."
    }


def _run(folder):
    folder = Path(folder).expanduser().resolve()
    private = _load(folder / "private" / "assignments.json")
    public = _load(folder / "blind" / "packet.json")
    if (not isinstance(private, dict) or not isinstance(public, dict)
        or private.get("run_id") != public.get("run_id")
        or private.get("schema_version") != 1 or public.get("schema_version") != 1):
        raise EvaluationError("Run assignment and blind packet do not match.")
    assignments = private.get("assignments", [])
    pairs = public.get("pairs", [])
    if not isinstance(assignments, list) or not isinstance(pairs, list) or len(assignments) != len(pairs):
        raise EvaluationError("Task counts differ between private assignment and blind packet.")
    if [x.get("task_id") for x in assignments] != [x.get("task_id") for x in pairs]:
        raise EvaluationError("Blind packet task IDs or order have changed.")
    for pair in assignments:
        if {pair[side]["condition"] for side in SIDES} != set(ARMS):
            raise EvaluationError("Each pair requires exactly one baseline and one skill condition.")
    return folder, private, public


def _scrub_png(path):
    """Copy PNG pixels while dropping text/EXIF and other ancillary metadata chunks."""
    path = Path(path).expanduser().resolve()
    if not path.is_file() or not 8 <= path.stat().st_size <= MAX_PNG:
        raise EvaluationError("Screenshot must be an existing PNG under 25 MiB.")
    raw = path.read_bytes()
    if not raw.startswith(PNG_SIGNATURE):
        raise EvaluationError("Screenshot is not a PNG.")
    chunks = []
    at = 8
    seen = []
    while at < len(raw):
        if at + 12 > len(raw):
            raise EvaluationError("Truncated PNG chunk.")
        count = struct.unpack(">I", raw[at:at + 4])[0]
        tag = raw[at + 4:at + 8]
        if count > MAX_PNG or at + 12 + count > len(raw):
            raise EvaluationError("Invalid PNG chunk length.")
        chunk = raw[at:at + 12 + count]
        if zlib.crc32(raw[at + 4:at + 8 + count]) & 0xFFFFFFFF != struct.unpack(">I", chunk[-4:])[0]:
            raise EvaluationError("PNG chunk CRC mismatch.")
        seen.append(tag)
        # Keep pixel data and essential rendering chunks; remove comments,
        # software identity, EXIF and ICC metadata that could unblind reviewer.
        if tag in (b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"sRGB", b"cHRM"):
            chunks.append(chunk)
        at += 12 + count
        if tag == b"IEND":
            if at != len(raw):
                raise EvaluationError("Unexpected bytes after PNG end.")
            break
    if not seen or seen[0] != b"IHDR" or seen[-1] != b"IEND" or b"IDAT" not in seen:
        raise EvaluationError("Screenshot PNG lacks required chunks.")
    return PNG_SIGNATURE + b"".join(chunks)


def attach(*, run, task_id, condition, desktop, mobile, duration_seconds=None,
           input_tokens=None, output_tokens=None, cost_usd=None):
    folder, secret, packet = _run(run)
    if condition not in ARMS:
        raise EvaluationError("Condition must be baseline or skill.")
    pairs = [a for a in secret["assignments"] if a["task_id"] == task_id]
    if len(pairs) != 1:
        raise EvaluationError("Unknown task ID in this evaluation run.")
    if duration_seconds is not None and (not math.isfinite(duration_seconds) or duration_seconds < 0):
        raise EvaluationError("Duration must be a nonnegative finite number.")
    if cost_usd is not None and (not math.isfinite(cost_usd) or cost_usd < 0):
        raise EvaluationError("Cost must be a nonnegative finite number.")
    for count in (input_tokens, output_tokens):
        if count is not None and (not isinstance(count, int) or count < 0):
            raise EvaluationError("Token counts must be nonnegative integers.")
    pair = pairs[0]
    side = next(label for label in SIDES if pair[label]["condition"] == condition)
    if any(pair[side]["images"].values()):
        raise EvaluationError("Screenshots already attached for this task/condition. Create a new run for changed outputs.")
    captures = {"desktop": _scrub_png(desktop), "mobile": _scrub_png(mobile)}
    targets = {v: folder / "blind" / task_id / (side + "-" + v + ".png")
               for v in captures}
    if any(path.exists() for path in targets.values()):
        raise EvaluationError("A blind screenshot file already exists; inspect or create a new run.")
    written = []
    try:
        for viewport, data in captures.items():
            target = targets[viewport]
            with os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as handle:
                handle.write(data)
            written.append(target)
            pair[side]["images"][viewport] = _sha(data)
        pair[side]["metrics"] = {
            "duration_seconds": duration_seconds,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost_usd
        }
        _private_json(folder / "private" / "assignments.json", secret)
    except Exception:
        for target in written:
            target.unlink(missing_ok=True)
        raise
    return {"attached": task_id,
            "blind_artifacts": {v: str(path) for v, path in targets.items()},
            "sha256": pair[side]["images"],
            "notice": "PNG metadata was removed. Share blind/ only; never private/."}



def attach_provenance(*, run, task_id, condition, manifest_file):
    """Add a private source-identity record, never to the public blind packet."""
    from . import provenance
    folder, secret, _ = _run(run)
    if condition not in ARMS:
        raise EvaluationError("Condition must be baseline or skill.")
    pair = next((a for a in secret["assignments"] if a["task_id"] == task_id), None)
    if pair is None:
        raise EvaluationError("Unknown task for provenance.")
    manifest = Path(manifest_file).expanduser().resolve()
    verified = provenance.verify(manifest)
    if not verified["ok"]:
        raise EvaluationError("Provenance manifest is invalid: " + "; ".join(verified["errors"]))
    data = provenance._read_json(manifest)
    if data["source"]["expected_repository"].casefold() != provenance.DEFAULT_REPOSITORY.casefold():
        raise EvaluationError("This study requires the designated Design Engineering repository identity.")
    if condition == "skill" and not verified["attribution_eligible"]:
        raise EvaluationError("Skill arm requires matched/complete source and operator-reported execution log.")
    if condition == "baseline" and data["usage_reported_by_operator"] != "not_executed":
        raise EvaluationError("Baseline arm must explicitly report NOT_EXECUTED.")
    if data["evidence"]["alternate_material"]["recorded"]:
        raise EvaluationError("Alternate material was recorded; do not attribute this run to only the selected skill.")
    side = next(k for k in SIDES if pair[k]["condition"] == condition)
    if pair[side].get("provenance"):
        raise EvaluationError("Provenance already recorded for this task/condition.")
    pair[side]["provenance"] = {"file": str(manifest), "sha256": _sha(manifest.read_bytes()),
                               "source_status": verified["source_status"],
                               "reported_usage": verified["reported_usage"]}
    _private_json(folder / "private" / "assignments.json", secret)
    return {"task_id": task_id, "condition": condition, "status": "PRIVATE_ATTRIBUTION_RECORDED",
            "notice": "Private/ was updated, blind/ was not. Agent invocation is operator-reported, not attested."}


def validate_run(run, *, require_complete=False, require_provenance=False):
    folder, secret, packet = _run(run)
    missing = []
    modified = []
    for assignment in secret["assignments"]:
        for side in SIDES:
            for viewport in ("desktop", "mobile"):
                task_id = assignment["task_id"]
                label = task_id + "/" + side + "-" + viewport
                image = folder / "blind" / (label + ".png")
                expected = assignment[side]["images"][viewport]
                if expected is None or not image.is_file():
                    missing.append(label)
                elif _sha(image.read_bytes()) != expected:
                    modified.append(label)
    problems = list(modified)
    missing_provenance = []
    invalid_provenance = []
    from . import provenance
    for assignment in secret["assignments"]:
        for side in SIDES:
            task_id = assignment["task_id"]
            entry = assignment[side].get("provenance")
            label = task_id + "/" + side
            if not entry:
                missing_provenance.append(label)
                continue
            try:
                path = Path(entry["file"])
                if not path.is_file() or _sha(path.read_bytes()) != entry["sha256"]:
                    raise EvaluationError("Manifest bytes differ from recorded hash.")
                verified = provenance.verify(path)
                usage = verified["reported_usage"]
                condition = assignment[side]["condition"]
                if (not verified["ok"]
                    or (condition == "skill" and not verified["attribution_eligible"])
                    or (condition == "baseline" and usage != "not_executed")):
                    raise EvaluationError("Source identity or declared usage no longer passes validation.")
            except (OSError, KeyError, ValueError) as exc:
                invalid_provenance.append(label + ": " + str(exc))
    problems.extend(invalid_provenance)
    if require_provenance:
        problems.extend("missing provenance: " + label for label in missing_provenance)
    # Blinded material must never include the hidden condition keys/assignments.
    public = json.dumps(packet, ensure_ascii=False).casefold()
    if any(word in public for word in ('"condition":', '"baseline"', '"skill"')):
        problems.append("Blind packet accidentally includes condition mappings.")
    if require_complete and missing:
        problems.extend("missing: " + label for label in missing)
    return {
        "ok": not problems,
        "ready_for_review": not problems and not missing,
        "tasks": len(secret["assignments"]),
        "attached": len(secret["assignments"]) * 4 - len(missing),
        "missing": missing, "modified": modified, "errors": problems,
        "missing_provenance": missing_provenance, "invalid_provenance": invalid_provenance,
        "attribution_ready": not missing_provenance and not invalid_provenance,
        "ready_for_attributed_review": not problems and not missing and not missing_provenance,
        "note": ("Ready for review means screenshots exist, not verified invocation or usability. "
                 "Attribution requires separate private provenance records and remains operator-reported.")
    }


def scorecard(*, run, judge, out):
    folder, secret, packet = _run(run)
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,48}", judge):
        raise EvaluationError("Reviewer ID must be 2-48 alphanumeric, '_' or '-'.")
    status = validate_run(folder, require_complete=True)
    if not status["ok"]:
        raise EvaluationError("Complete and verify all blinded screenshots before creating a scorecard.")
    judgment = {
        "schema_version": 1, "run_id": secret["run_id"], "judge_id": judge,
        "review_protocol": "Open blind/packet.json and images; do not access private/assignments.json.",
        "dimensions": list(DIMENSIONS),
        "judgments": [
            {"task_id": row["task_id"], "preferred": None,
             "reason": "", "artifacts_reviewed": False,
             "ratings": {side: {dim: None for dim in DIMENSIONS} for side in SIDES}}
            for row in packet["pairs"]
        ]
    }
    path = Path(out).expanduser().resolve()
    _private_json(path, judgment, exclusive=True)
    return {"scorecard": str(path), "judge_id": judge,
            "notice": "Blank scorecard only. No scores or preferences have been inferred."}


def _ratings(judgment, *, task_id):
    scores = judgment.get("ratings")
    if not isinstance(scores, dict) or set(scores) != set(SIDES):
        raise EvaluationError(f"{task_id}: ratings must include A and B.")
    for side in SIDES:
        item = scores[side]
        if not isinstance(item, dict) or set(item) != set(DIMENSIONS):
            raise EvaluationError(f"{task_id}: {side} must rate the four defined dimensions.")
        for dim, value in item.items():
            if type(value) is not int or not 1 <= value <= 5:
                raise EvaluationError(f"{task_id}: {side}.{dim} must be an integer 1–5.")


def report(*, run, judgment_files):
    folder, secret, packet = _run(run)
    state = validate_run(folder)
    if not state["ok"]:
        raise EvaluationError("Screenshot files were modified or the evaluation run is invalid.")
    expected = {row["task_id"] for row in packet["pairs"]}
    map_ = {item["task_id"]: item for item in secret["assignments"]}
    judge_ids = set()
    judgments = defaultdict(list)
    for path in judgment_files:
        data = _load(path)
        if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("run_id") != secret["run_id"]:
            raise EvaluationError("Judge file does not match evaluation run.")
        judge = data.get("judge_id")
        if not isinstance(judge, str) or not re.fullmatch(r"[A-Za-z0-9_-]{2,48}", judge):
            raise EvaluationError("Each scorecard must identify a reviewer.")
        if judge in judge_ids:
            raise EvaluationError("Duplicate judge ID; submit each independent review once.")
        judge_ids.add(judge)
        rows = data.get("judgments")
        if not isinstance(rows, list):
            raise EvaluationError("Judgments must be a list.")
        seen = set()
        for item in rows:
            tid = item.get("task_id") if isinstance(item, dict) else None
            if tid not in expected or tid in seen:
                raise EvaluationError("Unknown or duplicated task in judge file.")
            seen.add(tid)
            choice = item.get("preferred")
            if choice is None:
                if item.get("artifacts_reviewed") or item.get("reason"):
                    raise EvaluationError(f"{tid}: incomplete judgment has review fields.")
                continue
            if choice not in ("A", "B", "tie"):
                raise EvaluationError(f"{tid}: preferred must be A, B or tie.")
            if not item.get("artifacts_reviewed") or not isinstance(item.get("reason"), str) or len(item["reason"].strip()) < 20:
                raise EvaluationError(f"{tid}: reviewer must confirm images and provide a meaningful explanation.")
            _ratings(item, task_id=tid)
            assignment = map_[tid]
            if any(not all(assignment[side]["images"].values()) for side in SIDES):
                raise EvaluationError(f"{tid}: cannot rate a task without both desktop and mobile captures.")
            decision = "tie" if choice == "tie" else assignment[choice]["condition"]
            judgments[tid].append({"judge": judge, "decision": decision, "choice": choice,
                                   "reason": item["reason"].strip(), "ratings": item["ratings"]})
    outcomes = []
    counts = Counter()
    dimension_diffs = defaultdict(list)
    for pair in packet["pairs"]:
        tid = pair["task_id"]
        votes = judgments.get(tid, [])
        if not votes:
            counts["unrated"] += 1
            outcomes.append({"task_id": tid, "status": "unrated", "judge_count": 0})
            continue
        counted = Counter(v["decision"] for v in votes)
        best = max(counted.values())
        winners = [key for key, n in counted.items() if n == best]
        verdict = winners[0] if len(winners) == 1 else "unresolved"
        counts[verdict] += 1
        outcomes.append({"task_id": tid, "status": verdict,
                         "judge_count": len(votes), "votes": dict(counted)})
        assignment = map_[tid]
        skill_side = next(s for s in SIDES if assignment[s]["condition"] == "skill")
        base_side = next(s for s in SIDES if assignment[s]["condition"] == "baseline")
        for item in votes:
            for dim in DIMENSIONS:
                dimension_diffs[dim].append(
                    item["ratings"][skill_side][dim] - item["ratings"][base_side][dim])
    assessed = len(packet["pairs"]) - counts["unrated"]
    definite = counts["skill"] + counts["baseline"]
    paired = {
        dim: {"n_judgments": len(diffs), "mean_skill_minus_baseline": (
            round(sum(diffs) / len(diffs), 3) if diffs else None)}
        for dim, diffs in ((dim, dimension_diffs.get(dim, [])) for dim in DIMENSIONS)
    }
    # Only compare observed execution costs where BOTH arms provide real values.
    # Never turn missing cost/latency measurements into zeros.
    resource_metrics = {}
    for field in ("duration_seconds", "input_tokens", "output_tokens", "cost_usd"):
        comparisons = []
        for assignment in secret["assignments"]:
            skill_data = next(assignment[side] for side in SIDES
                              if assignment[side]["condition"] == "skill")
            base_data = next(assignment[side] for side in SIDES
                             if assignment[side]["condition"] == "baseline")
            if skill_data["metrics"] is None or base_data["metrics"] is None:
                continue
            skill_val, base_val = skill_data["metrics"].get(field), base_data["metrics"].get(field)
            if skill_val is None or base_val is None:
                continue
            comparisons.append((skill_val, base_val))
        resource_metrics[field] = {
            "paired_cases": len(comparisons),
            "mean_skill": (round(sum(a for a, _ in comparisons)/len(comparisons), 4)
                           if comparisons else None),
            "mean_baseline": (round(sum(b for _, b in comparisons)/len(comparisons), 4)
                              if comparisons else None),
            "mean_difference_skill_minus_baseline":
                (round(sum(a-b for a,b in comparisons)/len(comparisons), 4)
                 if comparisons else None)
        }
    summary = {
        "total_tasks": len(packet["pairs"]), "rated_tasks": assessed,
        "unrated_tasks": counts["unrated"], "independent_judges": len(judge_ids),
        "skill_preferred_tasks": counts["skill"],
        "baseline_preferred_tasks": counts["baseline"],
        "tie_tasks": counts["tie"], "unresolved_tasks": counts["unresolved"],
        "skill_win_share_excluding_ties": (round(counts["skill"] / definite, 4) if definite else None),
        "paired_rating_differences": paired,
        "effort_metrics": resource_metrics
    }
    if assessed == 0:
        status = "NO_OBSERVATIONS"
    elif state["missing"] or counts["unrated"]:
        status = "INCOMPLETE"
    else:
        status = "PILOT_REVIEWED"
    return {
        "run_id": secret["run_id"], "status": status,
        "study": {"agent": secret["agent"], "model": secret["model"], "effort": secret["effort"],
                  "seed": secret["seed"], "protocol_note": secret["protocol_note"]},
        "summary": summary, "task_outcomes": outcomes,
        "evidence": {"provided_judgment_files": len(judgment_files),
                     "missing_blind_screenshots": state["missing"],
                     "missing_private_provenance": state["missing_provenance"],
                     "attribution_ready": state["attribution_ready"]},
        "limitations": [
            "This tool does not generate designs or user studies. Every score requires an actual supplied review.",
            "Blind labels conceal assignments in the packet but cannot rule out visual/style clues or judge bias.",
            "Source provenance is not proof of an agent actually executing the designated skill; usage remains operator-reported.",
            "Curated tasks, small sample sizes, model/tool variability, and reviewer judgment limit generalization.",
            "Subjective 1–5 ratings are descriptive; avoid treating them as universally calibrated quality scores.",
            "No claim of causal improvement, WCAG compliance, or user-task success is established by this report alone."
        ]
    }
