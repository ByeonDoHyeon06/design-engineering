# Contributing

- Keep `SKILL.md` current and concise; Git commits/releases, not historical prose, track versions.
- Do not add third-party design galleries, unlicensed fonts, copied layouts or style presets.
- Every verified research finding must link to a source, real review scope, `do_not_infer`, and the actual card's verified claim IDs.
- Novel design prescriptions derived from papers remain `DESIGN_HYPOTHESIS` until independently tested.
- For retrieval changes, extend `benchmarks/retrieval-v38.json` with new natural queries, include negative examples, and run `python scripts/retrieval_benchmark.py`.
- For each new test or script, avoid network calls, secret exposure, forced style branches, fabricated UX outcomes, or version records in the runtime package.
- Run `python -m unittest discover -s tests -q` and `python scripts/audit_evidence.py`. Browser tests are optional and should report NOT TESTED if unavailable.
- Do not commit `.cache`, `.local`, API keys, collected copyrighted PDFs or user data.
