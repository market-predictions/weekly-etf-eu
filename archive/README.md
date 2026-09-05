# Weekly ETF EU — Forensic Archive

This namespace contains a **small, explicit, non-authoritative forensic subset** of retired implementation artifacts whose historical value exceeds what is conveniently recoverable from ordinary current documentation.

## Policy

1. Files here are **never current executors, routing authority, portfolio authority, pricing authority or delivery authority**.
2. Archived workflows live outside `.github/workflows/` and therefore cannot execute as GitHub Actions workflows.
3. Archived Python, if retained, must sit outside current production import paths and may not be imported by current entrypoints.
4. Most retired implementation files should be deleted and recovered from Git history when needed. Archive retention is exceptional, not the default.
5. A current document may cite an archived artifact only for historical/incident explanation and must label it non-authoritative.
6. Removal/archive actions under Architecture V2 are explicitly authorized by the principal realization instruction and still require reachability/reference evidence; filenames that merely look old are not sufficient proof.

## Historical context

The repository was originally cloned from a U.S. ETF implementation and historically accumulated U.S./donor workflows, sender variants, preview paths and one-off repair executors. Earlier archive notes therefore used a conservative non-destructive quarantine policy. Architecture V2 supersedes that temporary migration posture with three explicit dispositions:

- `CURRENT/SUPPORTING ACTIVE`;
- `FORENSIC ARCHIVE`;
- `DELETE` with Git history as provenance.

The 2026-08-10 donor/U.S. runtime leakage incident is the main reason to retain a small forensic workflow subset. The retired pricing-audit/runtime-validation/lane-breadth workflows document what leaked and how the product boundary was repaired. Other disabled one-shot workflows should leave the current tree unless a concrete audit dependency proves otherwise.

## Authority reminder

Archive documentation and artifacts do not grant pricing authority, funding authority, portfolio mutation, PDF rendering, email delivery, broker execution, merge authority or independent-assurance authority.