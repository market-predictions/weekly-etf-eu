# Weekly ETF EU Golden Path proof rules

Status: current truth for WEEU-GOLDEN-PATH-20.

## Purpose

Keep candidate proving simple, exact-head and non-mutating. The proof process must never create the candidate drift it is supposed to detect.

## Rules

1. **Proof is read-only to repository contents.** Candidate generation and validation may create files in the workflow workspace, but proof jobs never commit or push those generated files to the governed branch.
2. **Proof is exact-head.** The workflow checks out `github.sha`. Before completion it verifies that the checked-out SHA still equals the live candidate branch head. If the branch moved, the run fails closed as stale.
3. **Generated outputs are evidence, not source authority.** PDFs, HTML, Markdown, pricing output, review pages and validation JSON are uploaded as GitHub Actions artifacts. They are not committed merely to preserve proof evidence.
4. **The GitHub Actions run conclusion is the final proof verdict for that exact SHA.** Generation-stage readiness/run manifests may describe intermediate state. They are not a second global PASS/FAIL authority.
5. **A deliberate source change naturally requires a fresh proof.** No separate proof-epoch object or state machine exists; Git commit identity already provides this boundary.
6. **Blocking review findings are durable and SHA-bound.** Before a repair cycle, record the concrete finding as a normal PR comment with the candidate SHA and required remediation. Control may cite that comment; no findings service or additional state plane is required.

## Golden Path use

The mission remains `prove -> purge -> prove again -> scheduled PRE_SEND_READY proof -> exact-head assurance`.

- Pre-purge proof establishes that the current production path works before cleanup.
- Purge is a deliberate source change and therefore creates a new candidate SHA.
- Clean-checkout and scheduled proofs apply only to the post-purge SHA they actually test.
- Any later repair changes the SHA and requires the affected proof to be repeated.

## Boundaries

This rule set adds no queue, scheduler, database, state plane, proof-epoch abstraction, findings service, renderer framework or assurance framework. It removes branch-write authority from proof and relies on Git/GitHub primitives already in use.
