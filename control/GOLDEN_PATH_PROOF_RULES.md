# Weekly ETF EU Golden Path proof rules

Status: current truth for WEEU-GOLDEN-PATH-20.

## Purpose

Keep candidate proving simple, exact-head and non-mutating. The proof process must never create the candidate drift it is supposed to detect.

## Rules

1. **Proof is read-only to repository contents.** Candidate generation and validation may create files in the workflow workspace, but proof jobs never commit or push generated files to the governed branch.
2. **Proof is exact-head.** The workflow checks out `github.sha`. Before completion it verifies that the checked-out SHA still equals the live source branch head. If the branch moved, the run fails closed as stale.
3. **Generated outputs are evidence, not source authority.** PDFs, HTML, Markdown, pricing output, review pages and validation JSON are uploaded as GitHub Actions artifacts. They are not committed merely to preserve proof evidence.
4. **Post-gate current truth is explicit.** Generation may create pending readiness/run-manifest state, but after strict NL/EN, Markdown and routine machine gates pass, the existing package/readiness/run-manifest artifacts are finalized to `PRE_SEND_READY`. `PRE_SEND_READY` never grants delivery, send, broker, funding or portfolio-mutation authority. The exact-head Actions conclusion plus the frozen artifact bundle is the proof evidence for that SHA.
5. **A deliberate source change naturally requires a fresh proof.** No separate proof-epoch object or state machine exists; Git commit identity already provides this boundary.
6. **Blocking review findings are durable and SHA-bound.** Before a repair cycle, record the concrete finding as a normal PR comment with the candidate SHA and required remediation. Control may cite that comment; no findings service or additional state plane is required.
7. **Scheduled generation remains separate from delivery.** The canonical weekly schedule may generate and validate on `main` only. Controlled transport remains a different owner/assurance-gated workflow and is never invoked by the scheduled generation workflow.

## Golden Path use

The mission is `prove -> purge -> clean-checkout prove -> scheduled PRE_SEND_READY -> exact-head assurance`.

- Pre-purge proof establishes that the production path works before cleanup.
- Purge is a deliberate source change and therefore creates a new candidate SHA.
- The post-purge workflow proves a clean exact-head checkout before generating any run-scoped evidence.
- Candidate/manual proof runs are non-main; scheduled generation is main-only.
- Any later repair changes the SHA and requires the affected proof to be repeated.

## Boundaries

This rule set adds no queue, database, state plane, proof-epoch abstraction, findings service, renderer framework or assurance framework. Scheduling uses the native GitHub Actions schedule trigger. Proof removes branch-write authority and relies on Git/GitHub primitives already in use.
